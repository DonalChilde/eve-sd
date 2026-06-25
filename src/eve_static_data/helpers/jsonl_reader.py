# """Utilities for reading and transforming JSONL data."""

# from __future__ import annotations

# import json
# from collections.abc import Iterator
# from pathlib import Path
# from typing import Protocol, TypeVar

# from pydantic import BaseModel, TypeAdapter

# type JsonScalar = str | int | float | bool | None
# type JsonObject = dict[str, JsonValue]
# type JsonArray = list[JsonValue]
# type JsonValue = JsonScalar | JsonObject | JsonArray

# T = TypeVar("T", covariant=True)
# BASE_MODELS = TypeVar("BASE_MODELS", bound=BaseModel)


# class TransformerProtocol(Protocol[T]):
#     """Protocol for transforming indexed JSONL lines into typed values."""

#     def __call__(self, value: tuple[int, str]) -> tuple[int, T | None]:
#         """Transform an indexed raw JSONL line.

#         Args:
#             value: Tuple containing the line number and raw line text.

#         Returns:
#             Transformed value or ``None`` to skip the record.
#         """
#         ...


# class PydanticTransformer(TransformerProtocol[BASE_MODELS]):
#     """Base class for transformers that convert JSONL lines into Pydantic models."""

#     def __init__(self, model: type[BASE_MODELS]):
#         """Initialize the transformer with a specific Pydantic model.

#         Args:
#             model: The Pydantic model class to use for validation.
#         """
#         self.model = model

#     def __call__(self, value: tuple[int, str]) -> tuple[int, BASE_MODELS | None]:
#         """Transform an indexed raw JSONL line into a Pydantic model instance."""
#         line_number, raw_line = value
#         try:
#             inspected_line = self._inspect_string(line_number, raw_line)
#             return line_number, self._text_to_model(line_number, inspected_line)
#         except Exception as e:
#             raise ValueError(
#                 f"Invalid data at line {line_number}: {raw_line}:\n{e}"
#             ) from e

#     def _inspect_string(self, index: int, text: str) -> str:
#         """Inspect the string before model creation."""
#         return text

#     def _text_to_model(self, index: int, text: str) -> BASE_MODELS | None:
#         """Convert the text to a model instance."""
#         return self.model.model_validate_json(text)


# class JsonTransformer:
#     """Transformer that parses each JSONL line into any valid JSON value."""

#     def __call__(self, value: tuple[int, str]) -> tuple[int, JsonValue | None]:
#         """Parse raw JSON text into a JSON-compatible Python value.

#         Args:
#             value: Tuple containing the line number and raw JSON text.

#         Returns:
#             Parsed JSON value, including objects, arrays, scalars, and null.

#         Raises:
#             ValueError: If the input line contains invalid JSON.
#         """
#         line_number, raw_line = value
#         try:
#             inspected_line = self._inspect_string(line_number, raw_line)
#             return line_number, self._text_to_model(line_number, inspected_line)
#         except Exception as e:
#             raise ValueError(f"Invalid data at line {line_number}: {e}") from e

#     def _inspect_string(self, index: int, text: str) -> str:
#         """Inspect the string before model creation."""
#         return text

#     def _text_to_model(self, index: int, text: str) -> JsonValue | None:
#         """Convert the text to a model instance."""
#         return json.loads(text)


# def index_file_lines(file_path: str | Path) -> Iterator[tuple[int, str]]:
#     """Yield non-empty JSONL lines with their 1-based line numbers.

#     Strips leading and trailing whitespace from each line and skips empty lines.

#     Args:
#         file_path: Path to the JSONL file.

#     Yields:
#         Tuples containing ``(line_number, raw_line)``.
#     """
#     path = Path(file_path)
#     with path.open("r", encoding="utf-8") as handle:
#         for line_number, line in enumerate(handle, start=1):
#             raw_line = line.strip()
#             if not raw_line:
#                 continue
#             yield line_number, raw_line


# def read_jsonl_file[T](
#     file_path: str | Path,
#     transformer: TransformerProtocol[T],
# ) -> Iterator[tuple[int, T | None]]:
#     """Read a JSONL file and yield transformed records.

#     Args:
#         file_path: Path to the JSONL file.
#         transformer: Callable that converts each indexed raw line into ``T``.

#     Yields:
#         Transformed records of type ``T``.
#     """
#     for indexed_line in index_file_lines(file_path):
#         transformed = transformer(indexed_line)
#         yield transformed


# def read_records_from_file_type_adaptor[T](
#     file_path: Path, model: type[T]
# ) -> Iterator[tuple[int, T]]:
#     """Read records from a JSONL file and convert them to dataclass instances."""
#     adapter = TypeAdapter(model)
#     with file_path.open() as f:
#         for index, line in enumerate(f):
#             try:
#                 result: T = adapter.validate_json(line)
#             except Exception as e:
#                 raise ValueError(f"Invalid data at line {index}: {line}:\n{e}") from e
#             yield index, result


# def read_records_from_file_base_model[BASE_MODELS: BaseModel](
#     file_path: Path, model: type[BASE_MODELS]
# ) -> Iterator[tuple[int, BASE_MODELS]]:
#     """Read records from a JSONL file and convert them to Pydantic model instances."""
#     with file_path.open() as f:
#         for index, line in enumerate(f):
#             try:
#                 result: BASE_MODELS = model.model_validate_json(line)
#             except Exception as e:
#                 raise ValueError(f"Invalid data at line {index}: {line}:\n{e}") from e
#             yield index, result
