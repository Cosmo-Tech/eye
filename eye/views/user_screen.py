from textual.screen import Screen
from textual.widgets import Header, Footer
from textual.containers import Horizontal, Vertical, Container
import logging
from eye.views.users_widget import UsersWidget
from eye.widgets.status import ConnectionStatus
from eye.widgets.config_label import ConfigLabel

logger = logging.getLogger("back.front")


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
                ConfigLabel("host", self.manager.configuration.host),
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
