from textual.widgets import Static
from textual.reactive import reactive


class ConnectionStatus(Static):
    is_connected = reactive(False)

    def watch_is_connected(self, value: bool) -> None:
        self.update(content="Connected" if value else "Disconnected")
