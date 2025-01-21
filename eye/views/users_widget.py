from textual.containers import Horizontal
from textual.widget import Widget
from textual import on

from eye.views.organization_widget import OrganizationWidget
from eye.views.security_widget import SecurityWidget

class UsersWidget(Widget):
    def __init__(self, manager, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager
        self.organization_view = OrganizationWidget(self.manager)
        self.security_view = SecurityWidget(self.manager, organization=None)
        
    def compose(self):
        """Layout the widgets horizontally"""
        with Horizontal():
            yield self.organization_view
            yield self.security_view
            
    @on(OrganizationWidget.OrganizationHighlighted)
    def handle_organization_selected(self, event):
        """Update security view when an organization is selected"""
        self.security_view.organization = event.organization
        self.security_view.reload()

    def reload(self):
        """Reload both widgets"""
        self.organization_view.reload()
        self.security_view.reload()