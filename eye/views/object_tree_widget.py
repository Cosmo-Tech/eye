from textual.widgets import Tree


class ObjectTreeWidget(Tree):
    def __init__(self, manager, **kwargs):
        super().__init__("Objects", **kwargs)
        self.manager = manager
        self.border_title = "Object tree"
        self.reload()

    def reload(self):
        self.clear()
        self.root.expand()
        for organization in self.manager.organizations:
            organization_node = self.root.add(organization.id)
            organization_node.data = organization
            for workspace in self.manager.workspaces.get(organization.id):
                workspace_node = organization_node.add(workspace.id)
                workspace_node.data = workspace
                for runner in self.manager.runners.get(
                    (organization.id, workspace.id), []
                ):
                    runner_node = workspace_node.add(runner.id)
                    runner_node.data = runner
            for solution in self.manager.solutions.get(organization.id):
                solution_node = self.root.add(solution.id)
                solution_node.data = solution
