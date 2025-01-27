from textual.widgets import Label


class ConfigLabel(Label):
    def __init__(self, label_text: str, value_text: str) -> None:
        super().__init__("")
        self.label_text = label_text
        self.value_text = value_text

    def on_mount(self):
        self.mount(Label(f"[bold]{self.label_text}:[/] {self.value_text}"))
