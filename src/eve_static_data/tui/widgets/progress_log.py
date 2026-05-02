"""Worker activity log widget."""

from textual.widgets import RichLog


class ProgressLog(RichLog):
    """A small helper around ``RichLog`` with convenience methods."""

    def add_info(self, message: str) -> None:
        """Append an informational message to the log.

        Args:
            message: Log line to display.
        """
        self.write(f"[cyan]{message}[/cyan]")

    def add_error(self, message: str) -> None:
        """Append an error message to the log.

        Args:
            message: Error line to display.
        """
        self.write(f"[red]{message}[/red]")
