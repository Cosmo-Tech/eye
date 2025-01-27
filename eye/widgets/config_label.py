from textual.widgets import Label


class ConfigLabel(Label):
    def __init__(self, name: str, value: str):
        super().__init__(f"{name}: {value}")
