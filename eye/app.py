from textual.app import App, ComposeResult
from textual.widgets import (
    Footer,
    Header,
    Label,
    Static,
)
from textual.containers import Horizontal, Container, Vertical
from textual.reactive import reactive
from eye.main import RUON
from pathlib import Path
import logging
from eye.views.users_widget import UsersWidget

# Create loggers

logger = logging.getLogger("back.front")
action_logger = logging.getLogger("back.front.actions")


class ConnectionStatus(Static):
    is_connected = reactive(False)

    def watch_is_connected(self, connected: bool) -> None:
        """React to connection status changes"""
        self.update(
            f"[{'green' if connected else 'red'}]●[/] {'Connected' if connected else 'Disconnected'}"
        )


class ConfigLabel(Label):
    def __init__(self, label_text: str, value_text: str) -> None:
        super().__init__("")
        self.label_text = label_text
        self.value_text = value_text

    def on_mount(self):
        self.mount(Label(f"[bold]{self.label_text}:[/] {self.value_text}"))


class TUI(App):
    """Main TUI application class"""

    BINDINGS = [("h", "help", "Help"), ("q", "quit", "Quit")]
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    connection_status = reactive(False)  # start offline
    data_refreshed = reactive(False)  # Track refresh state

    def __init__(self) -> None:
        logger.info("Initializing TUI application")
        super().__init__()
        host = "http://localhost:8080"
        self.manager = RUON(host=host)
        self.status_indicator = ConnectionStatus(id="connection-indicator")

    def compose(self) -> ComposeResult:
        """Create children for layout"""
        yield Header(
            icon="⏿",
            show_clock=True,
        )
        yield Horizontal(
            Vertical(
                ConfigLabel("host", self.manager.configuration.host),
                ConfigLabel("server_url", self.manager.config["server_url"]),
                ConfigLabel("client_id", self.manager.config["client_id"]),
                ConfigLabel("realm_name", self.manager.config["realm_name"]),
                id="config-parameters",
            ),
            self.status_indicator,
            id="config-info",
        )
        yield Footer()
        self.users_widget = UsersWidget(self.manager)
        yield Container(self.users_widget)
        logger.info("UI layout completed")

    def on_mount(self) -> None:
        """Handle mount event"""
        logger.info("TUI mounted")
        try:
            self.manager.connect()
            self.manager.update_summary_data()
            self.status_indicator.is_connected = True
            self.refresh_data()
        except Exception as e:
            logger.error(e)

    def refresh_data(self):
        """Refresh all data and views"""
        logger.info("Refreshing application data")
        self.users_widget.reload()

    def action_help(self) -> None:
        print("Need some help!")

if __name__ == "__main__":
    app = TUI()
    app.run()
