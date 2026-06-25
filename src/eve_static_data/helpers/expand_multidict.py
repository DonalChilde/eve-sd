# """Helper function to expand a CIMultiDict into key-value pairs."""

# from multidict import MultiDict

# type ExpandedHeaders = tuple[tuple[str, str], ...]


# def expand_multi_dict(
#     multidict: MultiDict[str],
# ) -> ExpandedHeaders:
#     """Expand a CIMultiDict into a tuple of key-value pairs."""
#     keys = multidict.keys()
#     result: list[tuple[str, str]] = []
#     for key in keys:
#         values = multidict.getall(key)
#         for value in values:
#             result.append((key, value))
#     tupled_result = tuple(result)
#     return tupled_result
