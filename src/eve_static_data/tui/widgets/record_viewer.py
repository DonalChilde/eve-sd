"""Record viewer widget for file browsing with paging."""

from textual.widgets import TextArea


class RecordViewer(TextArea):
    """Read-only viewer that supports line-based page rendering."""

    def __init__(
        self,
        text: str = "",
        *,
        page_size: int = 50,
        id: str | None = None,
    ) -> None:
        """Create a record viewer.

        Args:
            text: Initial content.
            page_size: Number of lines displayed per page.
            id: Optional widget identifier.
        """
        super().__init__(text=text, id=id, read_only=True)
        self.page_size = page_size
        self._lines: list[str] = []
        self._page_index = 0

    def set_content(self, text: str) -> None:
        """Set entire content and reset paging state.

        Args:
            text: Full viewer content.
        """
        self._lines = text.splitlines()
        self._page_index = 0
        self._render_page()

    def next_page(self) -> None:
        """Advance to the next page when available."""
        if not self._lines:
            return
        max_page = max((len(self._lines) - 1) // self.page_size, 0)
        self._page_index = min(self._page_index + 1, max_page)
        self._render_page()

    def previous_page(self) -> None:
        """Move to the previous page when available."""
        if not self._lines:
            return
        self._page_index = max(self._page_index - 1, 0)
        self._render_page()

    def _render_page(self) -> None:
        """Render the currently selected page into the widget."""
        if not self._lines:
            self.load_text("")
            return
        start = self._page_index * self.page_size
        end = start + self.page_size
        page_text = "\n".join(self._lines[start:end])
        self.load_text(page_text)
