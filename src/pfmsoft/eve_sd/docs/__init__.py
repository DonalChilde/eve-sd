"""Contains the documentation for the eve_sd package for display via cli."""

from importlib.resources import files as resource_files


# Access the docs via function to support future changes to the docs file location or
# name without breaking the cli command.
def get_docs_text() -> str:
    """Get the documentation text for the eve_sd package.

    Returns:
        str: The documentation text.
    """
    _doc_parent = "pfmsoft.eve_sd.docs"
    _doc_file = "eve_sd_docs.md"
    doc_text = resource_files(_doc_parent).joinpath(_doc_file).read_text()
    return doc_text
