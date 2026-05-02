"""Home screen for the Eve Static Data TUI."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static


class HomeScreen(Screen[None]):
    """Landing screen with navigation shortcuts to all workflows."""

    def compose(self) -> ComposeResult:
        """Compose the home screen layout."""
        yield Header()
        yield Static("EVE Static Data", classes="section-title")
        yield Static("Select a workflow or use keyboard shortcuts.")
        yield Button("Network", id="network")
        yield Button("Unpack", id="unpack")
        yield Button("Browse", id="browse")
        yield Button("Validate", id="validate")
        yield Button("Export", id="export")
        yield Button("Schema", id="schema")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Route button presses to app actions.

        Args:
            event: Button pressed event.
        """
        if event.button.id == "network":
            self.app.action_network()
        elif event.button.id == "unpack":
            self.app.action_unpack()
        elif event.button.id == "browse":
            self.app.action_browse()
        elif event.button.id == "validate":
            self.app.action_validate()
        elif event.button.id == "export":
            self.app.action_export()
        elif event.button.id == "schema":
            self.app.action_schema()
