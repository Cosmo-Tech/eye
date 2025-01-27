from textual.app import App
from textual.widgets import (
    Label,
    Static,
)
from textual.reactive import reactive
from eye.main import RUON
from pathlib import Path
import logging
from eye.views.users_widget import UsersWidget
from eye.views.user_screen import UserScreen
from eye.views.object_screen import ObjectScreen

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
