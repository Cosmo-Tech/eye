from textual.widgets import Tree
from textual.widget import Widget
import logging
from textual import on

logger = logging.getLogger(__name__)


class ObjectTreeWidget(Widget):
    """Tree widget to display organization objects"""

    def __init__(self, manager, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager
        self.mytree = Tree("root")
        self.border_title = "Object tree"

    def on_mount(self):
        self.build()

    def compose(self):
        yield self.mytree

    def build(self) -> None:
        """Build the tree structure"""
        self.mytree.clear()
        root = self.mytree.root
        root.expand()

        for solution in self.manager.get_solutions():
            solution_node = root.add(solution.name, data=solution.data)
            for workspace in solution.workspaces:
                workspace_node = solution_node.add(workspace.name, data=workspace.data)
                for scenario in workspace.scenarios:
                    scenario_node = workspace_node.add(
                        scenario.name, data=scenario.data
                    )
                    for run in scenario.runs:
                        scenario_node.add(run.name, data=run.data)

    @on(Tree.NodeSelected)
    def handle_tree_select(self, event: Tree.NodeSelected) -> None:
        """Handle tree node selection"""
        node = event.node
        if node.data:
            logger.info(f"Selected node: {node.label} with data: {node.data}")
            self.notify("eftase")

    def reload(self) -> None:
        """Reload tree data"""
        self.build()
