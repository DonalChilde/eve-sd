"""Functions for downloading files using httpx2.

Simple wrapper functions for downloading files, text, or JSON data from a URL using
httpx2, with support for query parameters and headers.
"""

import logging
import os
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import perf_counter
from typing import Any

from httpx2 import Client

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


# Refactor plan: stream downloads to disk instead of buffering the full response.

# Goals:

# Avoid loading the entire response body into memory for large SDE archives.
# Make the final write atomic by replacing the destination only after a full successful download.
# Keep current overwrite semantics and error reporting behavior.
# Planned steps:

# Keep the existing path validation at the start of download_bytes_to_file.

# Reject directory targets.
# Reject existing files when overwrite is False.
# Ensure the parent directory exists.
# Replace the full-body read path.

# Remove the await response.read() call.
# Iterate over response.content in fixed-size chunks.
# Write each chunk directly to a temporary file.
# Create the temporary file in the destination directory.

# Use a temp file under file_path.parent, not the system temp directory.
# This keeps the final replace on the same filesystem.
# Finalize writes safely.

# Flush and close the temp file after the stream completes.
# Promote the temp file to the final path with an atomic replace operation.
# Only replace the destination after the full download succeeds.
# Add robust cleanup.

# If the request or file write fails, close and delete the temp file.
# Log cleanup failures separately without hiding the original exception.
# Preserve function behavior.

# Still call response.raise_for_status() before writing output.
# Still return response headers.
# Keep logging around start/end timing, but avoid per-chunk logging.
# Optional follow-up improvements.

# Choose and document a chunk size suitable for large archives.
# Consider fsync if stronger durability guarantees are needed.
# Add tests for overwrite=False, partial-failure cleanup, and successful replacement.
# Short version:

# TODO: Refactor download_bytes_to_file to stream response chunks to a temp file in file_path.parent, then atomically replace the destination on success. Remove the full in-memory response read, preserve overwrite checks, and guarantee temp-file cleanup on failure.

# Test plan:

# Successful large-file download writes in chunks and returns headers.
# Existing target with overwrite=False fails before network write.
# Failed download leaves no partial destination file behind.
# Temp file is created in the destination directory and cleaned up on error.


def download_bytes_to_file(
    url: str,
    file_path: Path,
    *,
    session: Client,
    params: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
    overwrite: bool = False,
) -> list[tuple[str, str]]:
    """Download a file from a URL and save it to disk.

    File is first written to a temporary file, then moved to the final location to ensure atomicity.

    Args:
        url: The URL to download the file from.
        headers: The headers to include in the request.
        params: The query parameters to include in the request.
        file_path: The path to save the downloaded file to.
        overwrite: Whether to overwrite the file if it already exists.
        session: An httpx2 Client session to use for the request.

    Returns:
        The headers from the response as a tuple of key-value pairs.
    """
    logger.info(f"Downloading file from {url}")

    if file_path.is_dir():
        logger.error(f"File path {file_path} is a directory. {url=}")
        raise IsADirectoryError(f"File path {file_path} is a directory.")
    if file_path.is_file() and not overwrite:
        logger.error(f"File {file_path} already exists and overwrite is False. {url=}")
        raise FileExistsError(
            f"File {file_path} already exists and overwrite is False."
        )
    file_path.parent.mkdir(parents=True, exist_ok=True)
    start = perf_counter()

    query_params = params if params else {}
    response = session.get(url, params=query_params, headers=headers)

    logger.debug(
        "Received response with status %s, reason %s from %s, headers=%r",
        response.status_code,
        response.reason_phrase,
        response.url,
        response.headers,
    )
    response.raise_for_status()
    resp_headers = response.headers
    # atomic write to temp file, then move to final location
    try:
        with NamedTemporaryFile() as tmp_file:
            tmp_file.write(response.read())
            tmp_file.flush()
            shutil.copyfile(tmp_file.name, file_path)
    except Exception as e:
        logger.exception(f"Error writing file to {file_path}: {e}")
        raise e
    finally:
        try:
            if tmp_file:  # pyright: ignore[reportPossiblyUnboundVariable]
                tmp_file.close()
                if os.path.exists(tmp_file.name):
                    os.remove(tmp_file.name)
        except UnboundLocalError as e:
            logger.exception(
                f"Temporary file was never created, tmp_file is undefined: {e}"
            )
            pass
        except Exception as e:
            logger.exception(
                f"Error cleaning up temporary file {tmp_file.name}: {e}"  # pyright: ignore[reportPossiblyUnboundVariable]
            )

    logger.info(
        f"Downloaded and wrote file from {url} to {file_path} in {perf_counter() - start:.2f} seconds"
    )

    return resp_headers.multi_items()


def download_text(
    url: str,
    *,
    session: Client,
    params: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[str, list[tuple[str, str]]]:
    """Download a text file from a URL and return its content as a string.

    Args:
        url: The URL to download the text from.
        params: The query parameters to include in the request.
        headers: The headers to include in the request.

    Returns:
        A tuple containing the downloaded text and the headers.
    """
    logger.info(f"Downloading text from {url}")
    start = perf_counter()
    query_params = params if params else {}
    response = session.get(url, params=query_params, headers=headers)
    logger.debug(
        "Received response with status %s, reason %s from %s, headers=%r",
        response.status_code,
        response.reason_phrase,
        response.url,
        response.headers,
    )
    response.raise_for_status()
    text = response.text
    logger.info(f"Downloaded text from {url} in {perf_counter() - start:.2f} seconds")
    resp_headers = response.headers

    return (text, resp_headers.multi_items())


def download_json(
    url: str,
    *,
    session: Client,
    params: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[Any, list[tuple[str, str]]]:
    """Download JSON data from a URL.

    Args:
        url: The URL to download the JSON from.
        params: The query parameters to include in the request.
        headers: The headers to include in the request.

    Returns:
        A tuple containing the downloaded JSON data and the headers.
    """
    logger.info(f"Downloading JSON from {url}")
    start = perf_counter()
    query_params = params if params else {}
    response = session.get(url, params=query_params, headers=headers)
    logger.debug(
        "Received response with status %s, reason %s from %s, headers=%r",
        response.status_code,
        response.reason_phrase,
        response.url,
        response.headers,
    )
    response.raise_for_status()
    json_data = response.json()
    logger.info(f"Downloaded json from {url} in {perf_counter() - start:.2f} seconds")
    resp_headers = response.headers
    return (json_data, resp_headers.multi_items())
