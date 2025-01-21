from textual.widgets import OptionList
from textual.widgets.option_list import Option
from textual.message import Message
from textual import on
import logging

debug_logger = logging.getLogger("back.front.debug")

class OrganizationWidget(OptionList):
    """Organization view component that displays list of organizations"""
    
    class OrganizationHighlighted(Message):
        """Event emitted when an organization is selected"""
        def __init__(self, organization: str):
            self.organization = organization
            super().__init__()

    def __init__(self, manager, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager
        self.id = "organization-view"
        self.border_title = "Organizations"

    def _create_organization_items(self):
        returnlist = [Option(item, id = item) for item in self.manager.get_organization_list()]
        return returnlist

    def compose(self):
        """Compose the organization list"""
        for org in self._create_organization_items():
            yield org


    @on(OptionList.OptionHighlighted)
    def handle_selected(self, event: OptionList.OptionHighlighted) -> None:
        """Handle selection of an organization"""
        organization = event.option.prompt
        self.post_message(self.OrganizationHighlighted(organization))

    def reload(self):
        """Update the organization list"""
        self.clear_options()
        for org in self._create_organization_items():
            self.add_option(org)