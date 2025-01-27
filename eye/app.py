from textual.app import App, ComposeResult
from textual.widgets import (
    Footer,
    Header,
    Label,
    Static,
)
from textual.containers import Horizontal, Container, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from eye.main import RUON
from pathlib import Path
import logging
from eye.views.users_widget import UsersWidget
from eye.views.object_explore_widget import ObjectExplorerWidget

# Create loggers

logger = logging.getLogger("back.front")
action_logger = logging.getLogger("back.front.actions")


class UserScreen(Screen):
    def __init__(self, manager, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager
        self.status_indicator = ConnectionStatus(id="connection-indicator")

    def compose(self):
        yield Header(
            icon="⏿",
            show_clock=True,
        )
        yield Horizontal(
            Vertical(
                ConfigLabel("host", self.manager.config["host"]),
                ConfigLabel("server_url", self.manager.config["server_url"]),
                ConfigLabel("client_id", self.manager.config["client_id"]),
                ConfigLabel("realm_name", self.manager.config["realm_name"]),
                id="config-parameters",
            ),
            self.status_indicator,
            id="config-info",
        )
        self.users_widget = UsersWidget(self.manager)
        yield Container(self.users_widget)
        yield Footer()

    def on_mount(self):
        try:
            self.manager.update_summary_data()
            self.status_indicator.is_connected = True
            self.refresh_data()
        except Exception as e:
            logger.error(e)

    def refresh_data(self):
        """Refresh all data and views"""
        logger.info("Refreshing application data")
        self.users_widget.reload()


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


class ObjectScreen(Screen):
    def __init__(self, manager, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager

    def compose(self):
        self.objects_widget = ObjectExplorerWidget(self.manager)
        yield Header(icon="⏿", show_clock=True)
        yield self.objects_widget
        yield Footer()

    def on_mount(self):
        try:
            self.manager.update_summary_data()
            self.refresh_data()
        except Exception as e:
            logger.error(e)

    def refresh_data(self):
        self.objects_widget.reload()


class TUI(App):
    """Main TUI application class"""

    BINDINGS = [
        ("h", "help", "Help"),
        ("q", "quit", "Quit"),
        ("u", "users", "Users"),
        ("o", "objects", "Objects"),
    ]

    CSS_PATH = Path(__file__).parent / "styles.tcss"
    connection_status = reactive(False)  # start offline
    data_refreshed = reactive(False)  # Track refresh state

    def __init__(self) -> None:
        logger.info("Initializing TUI application")
        super().__init__()
        self.manager = RUON()
        self.status_indicator = ConnectionStatus(id="connection-indicator")
        self.screens = {
            "user_screen": UserScreen(self.manager),
            "object_screen": ObjectScreen(self.manager),
        }

    def on_mount(self) -> None:
        """Handle mount event"""
        self.manager.connect()
        logger.info("TUI mounted")
        try:
            for screen_name, screen in self.screens.items():
                logger.info(f"Installing screen: {screen_name}")
                try:
                    self.install_screen(screen, screen_name)
                    logger.info(f"Successfully installed screen: {screen_name}")
                except Exception as e:
                    logger.error(f"Failed to install screen {screen_name}: {str(e)}")
                    raise
            try:
                logger.info("Switching to user_screen")
                self.push_screen("user_screen")
            except Exception as e:
                logger.error(f"Failed to switch screen: {str(e)}")
                raise
        except Exception as e:
            logger.error(e)

    def action_users(self):
        self.switch_screen("user_screen")

    def action_objects(self):
        self.switch_screen("object_screen")

    def action_help(self) -> None:
        print("Need some help!")


if __name__ == "__main__":
    app = TUI()
    app.run()
