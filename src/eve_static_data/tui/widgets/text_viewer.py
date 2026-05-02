"""Simple scrollable text viewer widget."""

from textual.widgets import TextArea


class TextViewer(TextArea):
    """Read-only text viewer used by screen workflows."""

    def __init__(self, text: str = "", *, id: str | None = None) -> None:
        """Create a read-only text viewer.

        Args:
            text: Initial viewer contents.
            id: Optional widget identifier.
        """
        super().__init__(text=text, id=id, read_only=True)

    def set_text(self, text: str) -> None:
        """Replace the viewer contents.

        Args:
            text: New text value.
        """
        self.load_text(text)
