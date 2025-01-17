from textual.app import App, ComposeResult
from textual.widgets import (
    DataTable,
    Pretty,
    Tree,
    Footer,
    Header,
    ListView,
    ListItem,
    Label,
    Static,
)
from textual.containers import Horizontal, Container, Vertical, VerticalScroll
from textual.widget import Widget
from textual.reactive import reactive
from textual import on
from eye.main import RUON
from pathlib import Path
from rich.text import Text
from rich.logging import RichHandler
import logging


# Create loggers

logger = logging.getLogger("back.front")
action_logger = logging.getLogger("back.front.actions")


class ConnectionStatus(Static):
    is_connected = reactive(False)

    def watch_is_connected(self, connected: bool) -> None:
        """React to connection status changes"""
        self.update(
            f"[{'green' if connected else 'red'}]●[/] {'Connected' if connected else 'Disconnected'}"
        )


class Security(Container):
    def __init__(self, manager, organization, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager
        self.organization = organization

    def compose(self) -> ComposeResult:
        table = DataTable(id="security")
        table.border_title = "Security"
        df = self.manager.get_security_dataframe(self.organization)
        table.add_columns("User", *df.columns.tolist())
        for idx, row in df.iterrows():
            table.add_row(idx, *row.tolist())
        yield table

    def update_security(self, organization) -> None:
        self.organization = organization
        table = self.query_one("#security", DataTable)
        df = self.manager.get_security_dataframe(self.organization)
        table.clear(columns=True)
        table.add_columns("User", *df.columns.tolist())

        for idx, row in df.iterrows():
            table.add_row(idx, *row.tolist())


class ConfigLabel(Label):
    def __init__(self, label_text: str, value_text: str) -> None:
        super().__init__("")
        self.label_text = label_text
        self.value_text = value_text

    def on_mount(self):
        self.mount(Label(f"[bold]{self.label_text}:[/] {self.value_text}"))


class TUI(App):
    """Main TUI application class"""

    BINDINGS = [
        ("h", "help", "Help"),
        ("q", "quit", "Quit"),
        ("s", "switch_view", "Switch View"),
    ]
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    active_organization = reactive("")
    connection_status = reactive(False)  # start offline
    data_refreshed = reactive(False)  # Track refresh state

    def __init__(self) -> None:
        logger.info("Initializing TUI application")
        super().__init__()
        self.organization_view = ListView()
        host = "http://localhost:8080"
        self.manager = RUON(host=host)
        self.is_main_view = True
        self.status_indicator = ConnectionStatus(id="connection-indicator")

    def compose(self) -> ComposeResult:
        """Create children for layout"""
        logger.debug("Building UI layout")
        yield Header(
            icon="⏿",
            show_clock=True,
        )
        yield Horizontal(
            Vertical(
                ConfigLabel("host", self.manager.configuration.host),
                ConfigLabel("server_url", self.manager.config["server_url"]),
                ConfigLabel("client_id", self.manager.config["client_id"]),
                ConfigLabel("realm_name", self.manager.config["realm_name"]),
                id="config-parameters",
            ),
            self.status_indicator,
            id="config-info",
        )
        yield Footer()

        organizations = [
            ListItem(Label(item)) for item in self.manager.get_organization_list()
        ]
        self.organization_view = ListView(*organizations, id="organization-view")
        self.organization_view.border_title = "Organizations"
        self.tree_view = self.build_tree()
        self.tree_view.border_title = "Object tree"

        self.pretty_view = Pretty({}, id="pretty")
        self.security_view = Security(
            self.manager, self.active_organization, id="security_view"
        )
        # Main view components
        self.main_container = Container(
            Horizontal(
                Container(self.tree_view, id="tree-view"),
                Container(
                    self.organization_view,
                    VerticalScroll(self.pretty_view, id="detail-view"),
                ),
            ),
            id="main_view",
        )
        # Security view
        self.users_container = Container(
            Vertical(self.organization_view, self.security_view)
        )
        self.users_container.display = False
        yield self.main_container
        yield self.users_container
        logger.info("UI layout completed")

    def build_tree(self):
        tree = Tree("Objects", id="object_view")
        tree.root.expand()
        for organization in self.manager.organizations:
            org_node = tree.root.add(organization.id, expand=True)
            org_node.data = organization
            for workspace in self.manager.workspaces.get(organization.id, []):
                workspace_node = org_node.add(workspace.id)
                workspace_node.data = workspace
                for runner in self.manager.runners.get(
                    (organization.id, workspace.id), []
                ):
                    runner_node = workspace_node.add(runner.id)
                    runner_node.data = {
                        "organization": organization.id,
                        "workspace": workspace.id,
                    }
            for solution in self.manager.solutions.get(organization.id, []):
                solution_node = org_node.add(solution.id)
                solution_node.data = solution
        return tree

    def on_mount(self) -> None:
        """Handle mount event"""
        logger.info("TUI mounted")
        try:
            self.manager.connect()
            self.status_indicator.is_connected = True
            self.refresh_data()
        except Exception as e:
            logger.error(e)

    def refresh_data(self):
        """Refresh all data and views"""
        logger.info("Refreshing application data")
        try:
            self.manager.update_summary_data()
            self.data_refreshed = True  # Trigger watch handlers
            logger.debug("Data refresh completed")
        except Exception as e:
            logger.error(f"Data refresh failed: {e}")

    def watch_data_refreshed(self, value: bool) -> None:
        """React to data refresh"""
        if value:
            self.refresh_views()
            self.data_refreshed = False  # Reset for next refresh

    def refresh_views(self) -> None:
        """Update all view components"""
        logger.debug("Refreshing views")
        # Update organization list
        organizations = [
            ListItem(Label(item)) for item in self.manager.get_organization_list()
        ]
        self.organization_view.clear()
        self.organization_view.extend(organizations)

        # Update object tree
        new_tree = self.build_tree()
        self.tree_view.root = new_tree.root

        # Update security view if organization selected
        if self.active_organization:
            self.security_view.update_security(self.active_organization)

        # Clear detail view
        self.pretty_view.update({})
        logger.info("Views refreshed")

    @on(ListView.Highlighted, "#organizations_view")
    def organization_changed(self, message: ListView.Highlighted) -> None:
        organization = message.item.query_one(Label).renderable
        self.active_organization = message.item.name
        self.security_view.update_security(organization)

    @on(Tree.NodeSelected, "#object_view")
    def node_selected(self, message: Tree.NodeSelected) -> None:
        self.pretty_view.update(message.node.data)

    def action_help(self) -> None:
        print("Need some help!")

    async def action_quit(self) -> None:
        """Quit the application"""
        action_logger.info("User initiated quit")
        self.exit()

    async def action_switch_view(self) -> None:
        """Switch between views"""
        action_logger.info("User switched view")
        self.is_main_view = not self.is_main_view


if __name__ == "__main__":
    app = TUI()
    app.run()
