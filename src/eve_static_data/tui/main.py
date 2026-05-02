"""Main Textual application entry point for Eve Static Data."""

from textual.app import App
from textual.binding import Binding

from eve_static_data.settings import get_settings
from eve_static_data.tui.screens.browser import BrowserScreen
from eve_static_data.tui.screens.export import ExportScreen
from eve_static_data.tui.screens.home import HomeScreen
from eve_static_data.tui.screens.network import NetworkScreen
from eve_static_data.tui.screens.schema_inspect import SchemaInspectScreen
from eve_static_data.tui.screens.unpack import UnpackScreen
from eve_static_data.tui.screens.validate import ValidateScreen


class EsdTuiApp(App[None]):
    """Primary Textual application for interacting with SDE workflows."""

    TITLE = "Eve Static Data"
    SUB_TITLE = "Textual TUI"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("h", "home", "Home"),
        Binding("n", "network", "Network"),
        Binding("u", "unpack", "Unpack"),
        Binding("b", "browse", "Browse"),
        Binding("v", "validate", "Validate"),
        Binding("e", "export", "Export"),
        Binding("s", "schema", "Schema"),
    ]

    CSS = """
    Screen {
        layout: vertical;
    }

    #content {
        height: 1fr;
        padding: 1;
    }

    .section-title {
        text-style: bold;
        margin-bottom: 1;
    }

    .error {
        color: red;
    }

    .muted {
        color: #b3b3b3;
    }
    """

    def on_mount(self) -> None:
        """Configure shared app state and open the home screen."""
        self.settings = get_settings()
        self.sde_tools = self.settings.sde_tools()
        self.push_screen(HomeScreen())

    def action_home(self) -> None:
        """Open the home screen."""
        self.push_screen(HomeScreen())

    def action_network(self) -> None:
        """Open the network screen."""
        self.push_screen(NetworkScreen())

    def action_unpack(self) -> None:
        """Open the unpack screen."""
        self.push_screen(UnpackScreen())

    def action_browse(self) -> None:
        """Open the browser screen."""
        self.push_screen(BrowserScreen())

    def action_validate(self) -> None:
        """Open the validate screen."""
        self.push_screen(ValidateScreen())

    def action_export(self) -> None:
        """Open the export screen."""
        self.push_screen(ExportScreen())

    def action_schema(self) -> None:
        """Open the schema inspection screen."""
        self.push_screen(SchemaInspectScreen())


def run() -> None:
    """Run the Eve Static Data Textual application."""
    EsdTuiApp().run()
