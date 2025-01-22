from textual.containers import Horizontal
from textual import on
from textual.widget import Widget
from eye.views.object_tree_widget import ObjectTreeWidget
from eye.views.object_viewer_widget import ObjectViewerWidget


class ObjectExplorerWidget(Widget):
    def __init__(self, manager, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager
        self.object_tree = ObjectTreeWidget(self.manager, id="tree-view")
        self.viewer = ObjectViewerWidget(id="detail-view")

    def compose(self):
        with Horizontal():
            yield self.object_tree
            yield self.viewer

    @on(ObjectTreeWidget.NodeSelected)
    def handle_node_selected(self, event):
        """Update viewer when a tree node is selected"""
        if event.node.data:
            self.viewer.update_content(event.node.data)

    def reload(self):
        self.object_tree.reload()
