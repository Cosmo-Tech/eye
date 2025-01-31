from textual.widgets import Tree
from textual.notifications import Notify
from cosmotech_api.models.organization import Organization
from cosmotech_api.models.workspace import Workspace
import logging
logger = logging.getLogger(__name__)

class ObjectTreeWidget(Tree):
    BINDINGS = [
        ("n", "new", "New Item"),
        ("d", "delete", "Delete")
    ]
    def action_new(self):
        if not self.cursor_node:
            self.notify("Select a parent node first", severity="error")
            return

        parent_data = self.cursor_node.data
        new_node = None
        try:
            if self.cursor_node.parent is None:
                # Create organization template at root
                org_template = Organization.from_dict({
                    "name":"New Organization",
                    "id":"new-org",
                    "ownerId":"new-org",
                    "security":{"default":"",
                                "accessControlList":[]}}
                )
                new_node = self.cursor_node.add("New Organization", data=org_template)

            elif isinstance(parent_data, Organization):
                # Create a workspace template under organization
                workspace_template = Workspace.from_dict({
                    "name":"New Workspace",
                    "id":"new-workspace",
                    "key":"sd",
                    "solution":{},
                    "organization_id":parent_data.id
                }
                )
                new_node = self.cursor_node.add("New Workspace", data=workspace_template)
                
            elif isinstance(parent_data, Workspace):
                # Create a runner template under workspace
                runner_template = {
                    "name": "New Runner",
                    "workspaceId": parent_data.id,
                    "status": "draft"
                }
                new_node = self.cursor_node.add("New Runner", data=runner_template)
                
            else:
                self.notify("Cannot create child for this type", severity="error")
                return

            if new_node:
                self.notify("Created new item", severity="information")

        except Exception as e:
            self.notify(f"Error creating new item: {str(e)}", severity="error")

    def action_delete(self):
        self.notify("Not implemented yet", severity="information")
        pass

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
