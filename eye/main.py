from dotenv import dotenv_values
from cosmotech_api.api.organization_api import OrganizationApi
from cosmotech_api.api.solution_api import SolutionApi
from cosmotech_api.api.workspace_api import WorkspaceApi
from cosmotech_api.api.runner_api import RunnerApi
from cosmotech_api.api.run_api import RunApi
from cosmotech_api import ApiClient, Configuration
from keycloak import KeycloakOpenID

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
      server_url=config['server_url'],
      client_id=config['client_id'],
      realm_name=config['realm_name'],
      client_secret_key=config['client_secret']
    )
    token = keycloak_openid.token(grant_type="client_credentials")
    self.configuration.access_token = token['access_token']

  def update_organizations(self):
    try:
      self.organizations = self.organization_api_instance.find_all_organizations()
    except Exception as e:
      print(f"error {e}")

  def update_solutions(self, organization_id):
    try:
      self.solutions[organization_id] = self.solution_api_instance.find_all_solutions(organization_id)
    except Exception as e:
      print(f"error {e}")

  def update_workspaces(self, organization_id):
    try:
      self.workspaces[organization_id] = self.workspace_api_instance.find_all_workspaces(organization_id)
    except Exception as e:
      print(f"error {e}")

  def update_runners(self, organization_id, workspace_id):
    try:
      self.runners[organization_id,workspace_id] = self.runner_api_instance.list_runners(organization_id, workspace_id)
    except Exception as e:
      print(f"error {e}")

  def update_runs(self, organization_id, workspace_id, runner_id):
    try:
      self.runs[organization_id,workspace_id,runner_id] = self.run_api_instance.find_all_runs(organization_id, workspace_id, runner_id)
    except Exception as e:
      print(f"error {e}")

def main():
    host = 'http://localhost:8080'
    manager = RUON(host=host)
    manager.update_organizations()
    for organization in manager.organizations:
      print(organization.id)
      manager.update_workspaces(organization.id)
      print(manager.workspaces[organization.id])
if __name__ == "__main__":
    main()