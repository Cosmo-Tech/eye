from textual.widgets import ListView, ListItem, Label

class OrganizationView(ListView):
    """Organization view component that displays list of organizations"""
    
    def __init__(self, manager, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager
        self.border_title = "Organizations"

    def _create_organization_items(self):
        """Helper method to create organization list items"""
        return [
            ListItem(Label(item)) 
            for item in self.manager.get_organization_list()
        ]

    def compose(self):
        """Compose the organization list"""
        for org in self._create_organization_items():
            yield org

    def update_organizations(self):
        """Update the organization list"""
        self.clear()
        for org in self._create_organization_items():
            self.append(org)