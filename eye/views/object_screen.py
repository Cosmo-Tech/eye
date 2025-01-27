from textual.screen import Screen
from textual.widgets import Header, Footer
import logging
from eye.views.object_explore_widget import ObjectExplorerWidget

logger = logging.getLogger("back.front")


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
