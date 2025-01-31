from dotenv import dotenv_values
from cosmotech_api.api.organization_api import OrganizationApi
from cosmotech_api.api.solution_api import SolutionApi
from cosmotech_api.api.workspace_api import WorkspaceApi
from cosmotech_api.api.runner_api import RunnerApi
from cosmotech_api.api.run_api import RunApi
from cosmotech_api import ApiClient, Configuration
from cosmotech_api.api.organization_api import OrganizationApi
from cosmotech_api.models.organization import Organization
from cosmotech_api.models.organization_security import OrganizationSecurity
from cosmotech_api.models.organization_access_control import OrganizationAccessControl

from keycloak import KeycloakOpenID
from rich.tree import Tree
from rich.console import Console
from rich.logging import RichHandler
import pandas as pd
import time
import logging

# Configure Rich logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)
logger = logging.getLogger("back")


class RUON:
    def __init__(self):
        logger.info(f"[bold blue]Initializing RUON[/]")
        start_time = time.time()

        try:
            self.config = dotenv_values(".env")
            self.configuration = Configuration(self.config["host"])

            # Initialize empty collections
            self.workspaces = {}
            self.organizations = {}
            self.solutions = {}
            self.runners = {}
            self.run = {}

            # Create API client and instances
            api_client = ApiClient(self.configuration)
            self.organization_api_instance = OrganizationApi(api_client)
            self.solution_api_instance = SolutionApi(api_client)
            self.workspace_api_instance = WorkspaceApi(api_client)
            self.runner_api_instance = RunnerApi(api_client)
            self.run_api_instance = RunApi(api_client)

            elapsed = time.time() - start_time
            logger.info(f"[green]✓[/] RUON initialized in {elapsed:.2f}s")

        except Exception as e:
            logger.error(f"[red]Failed to initialize RUON:[/] {str(e)}")
            raise

    def connect(self):
        logger.info("[yellow]Attempting connection...[/]")
        try:
            self.load_token()
            logger.info("[green]✓ Connected successfully[/]")
        except Exception as e:
            logger.error(f"[red]Connection failed:[/] {str(e)}")
            raise

    def refresh_token(self):
        try:
            token = self.keycloak_openid.token(grant_type="client_credentials")
            self.configuration.access_token = token["access_token"]
            self.token_expiry = time.time() + token["expires_in"]
        except Exception as e:
            raise RuntimeError(f"Failed to refresh token: {e}")

    def load_token(self):
        self.config = dotenv_values(".env")  # refresh
        self.config.setdefault("client_id", "cosmotech-api-client")
        self.keycloak_openid = KeycloakOpenID(
            server_url=self.config["server_url"],
            client_id=self.config.get("client_id"),
            realm_name=self.config["realm_name"],
            client_secret_key=self.config["client_secret"],
        )
        self.refresh_token()

    def update_organizations(self):
        try:
            self.organizations = self.organization_api_instance.list_organizations()
        except Exception as e:
            raise RuntimeError(f"Error getting organizations {e}")
            logger.error(f"error {e}")

    def get_organization_list(self):
        return [organization.id for organization in self.organizations]

    def get_solution_list(self, organization_id):
        return [solution.id for solution in self.solutions.get(organization_id, [])]

    def get_solutions(self, organization_id):
        return self.solutions.get(organization_id, [])

    def get_workspace_list(self, organization_id):
        return [workspace.id for workspace in self.workspaces.get(organization_id, [])]

    def get_runner_list(self, organization_id, workspace_id):
        return [
            (runner.id, runner.name)
            for runner in self.runners.get((organization_id, workspace_id), [])
        ]

    def update_solutions(self, organization_id):
        try:
            self.solutions[organization_id] = (
                self.solution_api_instance.find_all_solutions(organization_id)
            )
        except Exception as e:
            print(f"error {e}")

    def update_workspaces(self, organization_id):
        try:
            self.workspaces[organization_id] = (
                self.workspace_api_instance.find_all_workspaces(organization_id)
            )
        except Exception as e:
            print(f"error {e}")

    def update_runners(self, organization_id, workspace_id):
        try:
            self.runners[organization_id, workspace_id] = (
                self.runner_api_instance.list_runners(organization_id, workspace_id)
            )
        except Exception as e:
            print(f"error {e}")

    def update_runs(self, organization_id, workspace_id, runner_id):
        try:
            self.runs[organization_id, workspace_id, runner_id] = (
                self.run_api_instance.find_all_runs(
                    organization_id, workspace_id, runner_id
                )
            )
        except Exception as e:
            print(f"error {e}")

    def get_organization_security(self, org_id):
        data = {}
        try:
            org_security = self.organization_api_instance.get_organization_security(
                org_id
            )
            for acl in org_security.access_control_list:
                role = acl.role or org_security.default
                data[acl.id] = role
            return pd.Series(data)
        except Exception as e:
            raise RuntimeError(f"Error getting organization security for {org_id}: {e}")

    def get_workspace_security(self, org_id, workspace_id):
        data = {}
        try:
            ws_security = self.workspace_api_instance.get_workspace_security(
                org_id, workspace_id
            )
            for acl in ws_security.access_control_list:
                role = acl.role or ws_security.default
                data[acl.id] = role
            return pd.Series(data)
        except Exception as e:
            raise RuntimeError(
                f"Error getting workspace security for {workspace_id}: {e}"
            )

    def get_security_dataframe(self, organization_id):
        df = pd.DataFrame()
        organization_security = self.get_organization_security(organization_id)
        df["organization"] = organization_security
        for workspace_id in self.get_workspace_list(organization_id):
            workspace_security = self.get_workspace_security(
                organization_id, workspace_id
            )
            df[workspace_id] = workspace_security
        return df

    def update_summary_data(self):
        self.update_organizations()
        for organization in self.organizations:
            self.update_workspaces(organization.id)
            self.update_solutions(organization.id)
            for workspace in self.workspaces[organization.id]:
                self.update_runners(organization.id, workspace.id)

    def create_sample_organization(self):
        try:
            # Create the access control list
            access_control_list = [
                OrganizationAccessControl(
                    id="jane.doe@cosmotech.com",
                    role="editor"
                ),
                OrganizationAccessControl(
                    id="john.doe@cosmotech.com",
                    role="viewer"
                )
            ]

            # Create the security settings
            security = OrganizationSecurity(
                default="reader",
                access_control_list=access_control_list
            )

            # Create the organization object
            organization = Organization(
                name="Cosmo Tech",
                security=security
            )


            # Register the organization
            result = self.organization_api_instance.register_organization(organization)
            logger.info(f"[green]✓ Organization created successfully with ID: {result.id}[/]")
            return result

        except Exception as e:
            logger.error(f"[red]Failed to create organization:[/] {str(e)}")
            raise

def build_tree(manager):
    console = Console()
    tree = Tree("Organizations")
    for organization in manager.organizations:
        org_node = tree.add(f"{organization.id} {organization.name}")
        for workspace in manager.workspaces.get(organization.id, []):
            workspace_node = org_node.add(f"{workspace.id} {workspace.name}")
            for runner in manager.runners.get((organization.id, workspace.id), []):
                workspace_node.add(f"{runner.id} {runner.name}")
        for solution in manager.solutions.get(organization.id, []):
            org_node.add(f"{solution.id} {solution.name}")
    return console, tree


def main():
    manager = RUON()
    manager.connect()
    manager.update_organizations()
    for organization in manager.organizations:
        manager.update_workspaces(organization.id)
        manager.update_solutions(organization.id)
        for workspace in manager.workspaces[organization.id]:
            manager.update_runners(organization.id, workspace.id)
    console, tree = build_tree(manager)
    console.print(tree)
    manager.create_sample_organization()


if __name__ == "__main__":
    main()
