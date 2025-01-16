from dotenv import dotenv_values
from cosmotech_api.api.organization_api import OrganizationApi
from cosmotech_api.api.solution_api import SolutionApi
from cosmotech_api.api.workspace_api import WorkspaceApi
from cosmotech_api.api.runner_api import RunnerApi
from cosmotech_api.api.run_api import RunApi
from cosmotech_api import ApiClient, Configuration
from keycloak import KeycloakOpenID
from rich.tree import Tree
from rich.console import Console
import pandas as pd
from rich.pretty import pprint
import time
class RUON:
    def __init__(self, host="http://localhost:8080"):
        self.configuration = Configuration(host)
        self.load_token()
        self.workspaces = {}
        self.organizations = {}
        self.solutions = {}
        self.runners = {}
        self.run = {}
        api_client = ApiClient(self.configuration)
        self.organization_api_instance = OrganizationApi(api_client)
        self.solution_api_instance = SolutionApi(api_client)
        self.workspace_api_instance = WorkspaceApi(api_client)
        self.runner_api_instance = RunnerApi(api_client)
        self.run_api_instance = RunApi(api_client)

    def refresh_token(self):
        try:
            token = self.keycloak_openid.token(grant_type="client_credentials")
            self.configuration.access_token = token["access_token"]
            self.token_expiry = time.time() + token["expires_in"]
        except Exception as e:
            raise RuntimeError(f"Failed to refresh token: {e}")

    def load_token(self):
        self.config = dotenv_values(".env")
        self.keycloak_openid = KeycloakOpenID(
            server_url=self.config["server_url"],
            client_id=self.config["client_id"],
            realm_name=self.config["realm_name"],
            client_secret_key=self.config["client_secret"],
        )
        self.refresh_token()

    def update_organizations(self):
        try:
            self.organizations = self.organization_api_instance.find_all_organizations()
        except Exception as e:
            print(f"error {e}")

    def get_organization_list(self):
        return [organization.id for organization in self.organizations]

    def get_solution_list(self, organization_id):
        return [
            f"{solution.id}\n{solution.name}"
            for solution in self.solutions.get(organization_id, [])
        ]

    def get_workspace_list(self, organization_id):
        return [
            workspace.id for workspace in self.workspaces.get(organization_id, [])
        ]

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
            print(f"Error getting organization security for {org_id}: {e}")

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
            print(f"Error getting workspace security for {workspace_id}: {e}")

    def get_security_dataframe(self, organization_id):
        # o-3wwx046jdwqe6 w-314qryelkyop5
        df = pd.DataFrame()
        organization_security = self.get_organization_security(organization_id)
        df['organization'] = organization_security
        for workspace_id in self.get_workspace_list(organization_id):
          workspace_security = self.get_workspace_security(organization_id, workspace_id)
          df[workspace_id] = workspace_security
        return df


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
    host = "http://localhost:8080"
    manager = RUON(host=host)
    manager.update_organizations()
    for organization in manager.organizations:
        manager.update_workspaces(organization.id)
        manager.update_solutions(organization.id)
        for workspace in manager.workspaces[organization.id]:
            manager.update_runners(organization.id, workspace.id)
    manager.get_security_dataframe(manager.organizations[1].id)
    console, tree = build_tree(manager)
    console.print(tree)


if __name__ == "__main__":
    main()
