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


class RUON:
    def __init__(self, host="http://localhost:8080"):
        self.configuration = Configuration(host)
        self.load_token()
        self.workspaces = {}
        self.solutions = {}
        self.runners = {}
        self.run = {}
        api_client = ApiClient(self.configuration)
        self.organization_api_instance = OrganizationApi(api_client)
        self.solution_api_instance = SolutionApi(api_client)
        self.workspace_api_instance = WorkspaceApi(api_client)
        self.runner_api_instance = RunnerApi(api_client)
        self.run_api_instance = RunApi(api_client)

    def load_token(self):
        config = dotenv_values(".env")
        keycloak_openid = KeycloakOpenID(
            server_url=config["server_url"],
            client_id=config["client_id"],
            realm_name=config["realm_name"],
            client_secret_key=config["client_secret"],
        )
        token = keycloak_openid.token(grant_type="client_credentials")
        self.configuration.access_token = token["access_token"]

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
            f"{workspace.id}\n{workspace.name}"
            for workspace in self.workspaces.get(organization_id, [])
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
        """Extract security info for a single organization"""
        try:
            org_security = self.organization_api_instance.get_organization_security(
                org_id
            )
            return {
                acl.id: {"role": acl.role, "org_id": org_id}
                for acl in org_security.access_control_list
            }
        except Exception as e:
            print(f"Error getting organization security for {org_id}: {e}")
            return {}

    def get_workspace_security(self, org_id, workspace_id):
        """Extract security info for a single workspace"""
        try:
            ws_security = self.workspace_api_instance.get_workspace_security(
                org_id, workspace_id
            )
            return {
                acl.id: {
                    "role": acl.role,
                    "org_id": org_id,
                    "workspace_id": workspace_id,
                }
                for acl in ws_security.access_control_list
            }
        except Exception as e:
            print(f"Error getting workspace security for {workspace_id}: {e}")
            return {}

    def get_security_dataframe(self):
        """Return security info as pandas DataFrame"""
        data = []

        for org in self.organizations:
            # Get organization security
            org_security = self.get_organization_security(org.id)

            # Get workspace security
            workspaces = self.workspaces.get(org.id, [])
            for user, user_data in org_security.items():
                row = {"user": user, f"{org.id}_role": user_data["role"]}

                # Add workspace roles for this user
                for workspace in workspaces:
                    ws_security = self.get_workspace_security(org.id, workspace.id)
                    ws_role = ws_security.get(user, {}).get("role", "-")
                    row[f"{org.id}_{workspace.id}_role"] = ws_role

                data.append(row)

        # Create DataFrame and set user as index
        df = pd.DataFrame(data)
        if not df.empty:
            df.set_index("user", inplace=True)

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
    breakpoint()
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
    console, tree = build_tree(manager)
    console.print(tree)


if __name__ == "__main__":
    main()
