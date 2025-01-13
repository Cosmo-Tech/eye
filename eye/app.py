from textual.app import App, ComposeResult
from textual.widgets import DataTable, Pretty, Tree, Footer, Header, ListView, ListItem, Label, Static
from textual.containers import Horizontal, Container
from textual.widget import Widget
from textual.reactive import reactive
from textual import on
from eye.main import RUON


class Solution(Widget):
    def __init__(self, manager, organization,**kwargs):
        super().__init__(**kwargs)
        self.manager = manager
        self.organization = organization

    def compose(self) -> ComposeResult:
        solutions = [ListItem(Label(item)) for item in self.manager.get_solution_list(self.organization)]
        self.solution_view = ListView(*solutions)
        yield self.solution_view

    def update_solutions(self, organization):
        self.organization = organization
        solutions = self.manager.get_solution_list(self.organization)
        self.solution_view.clear()
        for item in solutions:
            self.solution_view.append(ListItem(Label(item)))

class Workspace(Widget):
    def __init__(self, manager, organization,**kwargs):
        super().__init__(**kwargs)
        self.manager = manager
        self.organization = organization

    def compose(self) -> ComposeResult:
        workspaces = [ListItem(Label(item)) for item in self.manager.get_workspace_list(self.organization)]
        self.workspace_view = ListView(*workspaces)
        yield self.workspace_view

    def update_workspaces(self, organization):
        self.organization = organization
        workspaces = self.manager.get_workspace_list(self.organization)
        self.workspace_view.clear()
        for item in workspaces:
            self.workspace_view.append(ListItem(Label(item)))

class PlaceholderView(Container):
    def __init__(self, manager, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager

    def compose(self) -> ComposeResult:
        # Create DataTable widget
        table = DataTable()
        
        # Get security data
        df = self.manager.get_security_dataframe()
        
        # Add columns (including index)
        table.add_columns("User", *df.columns.tolist())
        
        # Add rows
        for idx, row in df.iterrows():
            table.add_row(idx, *row.tolist())
            
        yield table

class TUI(App):
    BINDINGS = [
        ("h", "help", "Help"),
        ("q", "quit", "Quit"),
        ("s", "switch_view", "Switch View")
    ]
    active_organization = reactive("")
    
    def __init__(self, manager) -> None:
        super().__init__()
        self.organization_view = ListView()
        self.manager = manager
        self.is_main_view = True

    def compose(self) -> ComposeResult:
        """Create children for layout"""
        yield Header()
        yield Footer()
        
        organizations = [ListItem(Label(item)) for item in self.manager.get_organization_list()]
        self.organization_view = ListView(*organizations, id="organizations_view")
        self.workspace_view = Workspace(self.manager, self.active_organization, id="workspaces")
        self.solution_view = Solution(self.manager, self.active_organization, id="solutions")
        self.tree_view = self.build_tree()
        self.pretty_view = Pretty({}, id = "pretty")
        
        # Main view components
        self.main_container = Container(
            Horizontal(
                Container(self.tree_view),
                Container(
                    self.organization_view,
                    self.pretty_view,
                    self.workspace_view,
                    self.solution_view
                                    )
            ),
            id="main_view"
        )
        
        # Alternative view
        self.alt_container = PlaceholderView(self.manager, id="alt_view")
        self.alt_container.display = False
        
        yield self.main_container
        yield self.alt_container

    def build_tree(self):
      tree = Tree("Objects", id="object_view")
      tree.root.expand()
      for organization in self.manager.organizations:
        org_node = tree.root.add(organization.id, expand=True)
        for workspace in self.manager.workspaces.get(organization.id, []):
          workspace_node = org_node.add(workspace.id)
          workspace_node.data = {"organization":organization.id}
          for runner in self.manager.runners.get((organization.id, workspace.id), []):
            runner_node = workspace_node.add(runner.id)
            runner_node.data = {"organization":organization.id,
                                "workspace":workspace.id}
        for solution in self.manager.solutions.get(organization.id, []):
          solution_node = org_node.add(solution.id)
          solution_node.data = {"organization":organization.id}
      return tree


    @on(ListView.Highlighted, "#organizations_view")
    def organization_changed(self, message: ListView.Highlighted) -> None:
        organization = message.item.query_one(Label).renderable
        self.active_organization = message.item.name
        self.workspace_view.update_workspaces(organization)
        self.solution_view.update_solutions(organization)

    @on(Tree.NodeSelected, "#object_view")
    def node_selected(self, message: Tree.NodeSelected) -> None:
        self.pretty_view.update(message.node.data)

    def action_help(self) -> None:
        print("Need some help!")

    def action_switch_view(self) -> None:
        """Toggle between main and alternative views"""
        self.is_main_view = not self.is_main_view
        self.main_container.display = self.is_main_view
        self.alt_container.display = not self.is_main_view

if __name__ == "__main__":
    host = 'http://localhost:8080'
    manager = RUON(host=host)
    manager.update_organizations()
    for organization in manager.organizations:
      manager.update_workspaces(organization.id)
      manager.update_solutions(organization.id)
      for workspace in manager.workspaces[organization.id]:
        manager.update_runners(organization.id, workspace.id)
    app = TUI(manager)
    app.run()