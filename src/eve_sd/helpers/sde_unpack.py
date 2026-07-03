import shutil
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

from eve_sd.helpers.sde_metadata import (
    SdeMetadata,
    load_sde_metadata,
    load_sde_metadata_from_zipfile,
)

# Refactor note: avoid using ZipFile.extractall() directly on unvalidated archive members.
# Why this should change:
# - extractall() trusts member paths from the archive.
# - Unsafe members can use absolute paths or ".." segments to escape the target directory.
# - This is the classic zip-slip risk.
# - The current implementation also only moves top-level files after extraction, so nested archive content would be silently ignored.
# Safer approach:
# 1. Inspect each ZipInfo/member before extraction.
# 2. Reject unsafe names:
# - absolute paths
# - paths that resolve outside the temp extraction directory
# - optionally symlinks or other unsupported member types
# 3. Extract members one at a time only after validating the destination path.
# 4. Decide whether nested directories are supported:
# - if yes, preserve directory structure when moving into the final output dir
# - if no, fail fast when a member is not a top-level regular file
# 5. Only publish/move the unpacked result after the full archive has been validated.
# Goals:
# - make archive extraction path-safe
# - keep unpack behavior aligned with the expected archive layout
# - avoid silently dropping nested content
# Test plan:
# - valid flat archive extracts successfully
# - archive member with ".." is rejected
# - archive member with absolute path is rejected
# - nested directories either extract correctly or fail explicitly, depending on the chosen policy
# Short version:

# TODO: Replace extractall() with per-member validated extraction. Reject absolute
# and escaping paths, decide whether nested directories are supported, and avoid the
# current behavior where only top-level extracted files are moved into the output dir.


def unpack(
    input_path: Path, output_path: Path, use_build_number: bool = True
) -> tuple[Path, SdeMetadata]:
    """Unpack the static data.

    Unzip the input file and save the unpacked data to the output path.

    If use_build_number is True, the unpacked data will be saved to
    `<output_path>/<build_number>/`. Otherwise, it will be saved to `<output_path>/`.

    Checks for the presence of the _sde.jsonl or _sde.yaml file in the unpacked files.
    If the file is not found, raises a FileNotFoundError.


    Args:
        input_path: The path to the static data jsonl or yaml zip file.
        output_path: The path to the directory where the unpacked data should be saved.
        use_build_number: Whether to use the build number from the _sde.jsonl file to
            create the output directory.


    Returns:
        A tuple containing the path to the directory where the unpacked data is saved
            and the SdeMetadata object.
    """
    if not input_path.is_file():
        raise FileNotFoundError(f"Input path {input_path} is not a file.")
    if input_path.suffix != ".zip":
        raise ValueError(f"Input file {input_path} is not a zip file.")
    if output_path.exists() and not output_path.is_dir():
        raise FileExistsError(
            f"Output path {output_path} already exists and is not a directory."
        )
    sde_metadata = load_sde_metadata_from_zipfile(input_path)
    unpack_dir = (
        output_path / str(sde_metadata.buildNumber) if use_build_number else output_path
    )
    if unpack_dir.exists() and not unpack_dir.is_dir():
        raise FileExistsError(
            f"Output directory {unpack_dir} already exists and is not a directory."
        )
    with TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(input_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        # Check that there is an _sde.jsonl or _sde.yaml file in the extracted files to
        # confirm this is a valid SDE zip file by loading SdeMetadata
        try:
            _ = load_sde_metadata(Path(temp_dir))
        except Exception as e:
            raise FileNotFoundError(
                f"Failed to load SDE info from the extracted files in {temp_dir}. "
                f"Is this a valid SDE zip file? Original error: {e}"
            ) from e

        unpack_dir.mkdir(parents=True, exist_ok=True)
        for file in Path(temp_dir).iterdir():
            if file.is_file():
                target_file = unpack_dir / file.name
                if target_file.exists():
                    raise FileExistsError(
                        f"Target file {target_file} already exists. Cannot move processed "
                        f"data to {target_file}"
                    )
                shutil.move(file, target_file)
        return unpack_dir, sde_metadata
