from textual.widgets import Pretty
from textual.containers import ScrollableContainer
from textual.widget import Widget


class ObjectViewerWidget(Widget):
    def __init__(self, data: dict = None, **kwargs):
        super().__init__(**kwargs)
        self.data = data or {}
        self.view = Pretty(self.data)

    def compose(self):
        with ScrollableContainer():
            yield self.view

    def update_content(self, data: dict):
        self.data = data
        self.view.update(data)
