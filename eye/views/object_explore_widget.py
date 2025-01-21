from textual.containers import Horizontal
from textual.widget import Widget
from eye.views.object_tree_widget import ObjectTreeWidget
from eye.views.object_viewer_widget import ObjectViewerWidget


class ObjectExplorerWidget(Widget):
    def __init__(self, manager, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager
        self.tree = ObjectTreeWidget(self.manager)
        self.viewer = ObjectViewerWidget()

    def compose(self):
        with Horizontal():
            yield self.tree
            yield self.viewer

    def on_mount(self):
        # Subscribe to tree's NodeSelected events
        self.tree.watch(ObjectTreeWidget.NodeSelected, self.handle_node_selected)

    def handle_node_selected(self, event):
        """Update viewer when a tree node is selected"""
        if event.node.data:
            self.viewer.update_content(event.node.data)
