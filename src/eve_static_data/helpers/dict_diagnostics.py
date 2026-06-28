# """Functions for analyzing dictionaries and generating TypedDict definitions."""

# from collections.abc import Iterable
# from typing import Any, TypedDict

# type TypeName = str
# type TypeCount = int
# type DictTypes = dict[TypeName, TypeCount]
# type DictKey = str
# type KeyInfo = dict[DictKey, DictTypes]


# class DatasetKeyInfo(TypedDict):
#     count: int
#     key_info: KeyInfo


# class DictField:
#     name: str
#     type_str: str
#     is_optional: bool


# def collect_dict_keys_and_types(dict_data: Iterable[dict[str, Any]]) -> DatasetKeyInfo:
#     """Analyze a list of dictionaries and return the keys and their associated value types.

#     Args:
#         dict_data: An iterable of dictionaries to analyze.

#     Returns:
#         A dictionary where each key is a key from the input dictionaries, and the value is another dictionary
#         mapping type names to their occurrence counts for that key.
#     """
#     key_info: KeyInfo = {}
#     count = 0
#     for entry in dict_data:
#         count += 1
#         for key, value in entry.items():
#             type_name = type(value).__name__
#             if key not in key_info:
#                 key_info[key] = {}
#             if type_name not in key_info[key]:
#                 key_info[key][type_name] = 0
#             key_info[key][type_name] += 1
#     result: DatasetKeyInfo = {
#         "count": count,
#         "key_info": key_info,
#     }
#     return result


# def make_typed_dict_definition(
#     dict_name: str,
#     key_info: DatasetKeyInfo,
#     source_info: str | None = None,
# ) -> str:
#     """Generate a TypedDict definition from key information.

#     Args:
#         dict_name: The name of the TypedDict to generate.
#         key_info: The key information as returned by `dict_keys_and_types`.
#         source_info: Optional string providing source information for the TypedDict.

#     Returns:
#         A string representing the TypedDict definition.
#     """
#     class_header = f'''
# class {dict_name}(TypedDict):
# {" " * 4}"""TypeDict definition for {dict_name}.

# Total entries analyzed: {key_info["count"]}.
# This TypedDict was auto-generated and only considers top-level keys.
# Source info: {source_info}.
# """

# '''
#     lines: list[str] = []
#     # doc_string = f"TypeDict definition for {dict_name}.\n\n{' ' * 4}Total entries analyzed: {key_info['count']}.\n{' ' * 4}This TypedDict was auto-generated and only considers top-level keys."
#     # lines.append(f'{" " * 4}"""{doc_string}\n{" " * 4}"""')
#     total_count = key_info["count"]

#     for key, types in key_info["key_info"].items():
#         type_names = list(types.keys())
#         key_count = sum(types.values())
#         is_optional = key_count < total_count

#         if len(type_names) == 1:
#             type_str = type_names[0]
#         else:
#             type_str = f"Union[{', '.join(type_names)}]"

#         if is_optional:
#             new_type_str = f"NotRequired[{type_str}]"
#         else:
#             new_type_str = type_str

#         lines.append(f"{' ' * 4}{key}: {new_type_str}")

#     return f"{class_header}{'\n'.join(lines)}"


# class RecursiveKeyInfo(TypedDict):
#     dict_count: int
#     source_info: str
#     key_info: KeyInfo


# def collect_dict_keys_and_types_recursive(
#     dict_data: Iterable[tuple[dict[str, Any], int]], source_info: str
# ) -> RecursiveKeyInfo:
#     """Recursively analyze dictionaries and return all keys with their associated value types.

#     This function examines an iterable of dictionaries and recursively processes nested
#     dictionaries and lists. For each key encountered at any level, it tracks the types
#     of values associated with that key and counts their occurrences.

#     Args:
#         dict_data: An iterable of dictionaries to analyze recursively.
#         source_info: A string providing source information for the dataset.

#     Returns:
#         A dictionary where each key (from any nesting level) maps to a dictionary
#         of type names and their occurrence counts. Nested paths are represented
#         with dot notation (e.g., "parent.child.grandchild").
#     """
#     key_info: KeyInfo = {}
#     dict_count = 0

#     def process_value(key_path: str, value: object) -> None:
#         """Process a single value and update key_info recursively.

#         Args:
#             key_path: The dot-separated path to this key (e.g., "parent.child").
#             value: The value to process.
#         """
#         type_name = type(value).__name__

#         # Initialize key_path in key_info if not present
#         if key_path not in key_info:
#             key_info[key_path] = {}

#         # Initialize type_name count if not present
#         if type_name not in key_info[key_path]:
#             key_info[key_path][type_name] = 0

#         # Increment count for this type
#         key_info[key_path][type_name] += 1

#         # Recursively process nested structures
#         if isinstance(value, dict):
#             for nested_key, nested_value in value.items():
#                 nested_path = f"{key_path}.{nested_key}" if key_path else nested_key
#                 process_value(nested_path, nested_value)
#         elif isinstance(value, list):
#             for item in value:
#                 # For lists, we process each item but keep the same key_path
#                 # to indicate this is a list of items at this path
#                 if isinstance(item, (dict, list)):
#                     process_value(key_path, item)

#     # Process each dictionary in the input iterable
#     for entry, line_number in dict_data:
#         _ = line_number
#         if isinstance(entry, dict):
#             dict_count += 1
#             for key, value in entry.items():
#                 process_value(key, value)
#     result: RecursiveKeyInfo = {
#         "dict_count": dict_count,
#         "source_info": source_info,
#         "key_info": key_info,
#     }

#     return result


# prompt = """
# Assuming a arbitrary json dictionary, create a set of functions that can result in
# a TypedDict class definition. The first function should analyze a list of dictionaries
# and collect the keys and their associated value types. The second function should take
# the output of the first function and generate a TypedDict class definition as a string.
# """
# prompt_2 = """
# write a function that will recursively examine an iterable of json dictionaries,
# and return a dict that contains all the keys, and for each key, a dict of types and their counts.
# dictionary keys can be assumed to be strings, and values can be of any json type.
# The iterable of dictionaries can be assumed to be a list of similar data, but some keys may be missing in some dictionaries.

# """
