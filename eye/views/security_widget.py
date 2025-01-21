from textual.containers import Container
from textual.widgets import DataTable


class SecurityWidget(Container):
    """Security view component that displays user access permissions in a table"""

    def __init__(self, manager, organization, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager
        self.organization = organization

    def compose(self):
        self.table = DataTable(id="security-view")
        self.table.border_title = "Security"
        self.refresh()
        yield self.table

    def reload(self):
        print(self.organization)
        df = self.manager.get_security_dataframe(self.organization)
        self.table.clear(columns=True)
        self.table.add_columns("User", *df.columns.tolist())
        for idx, row in df.iterrows():
            self.table.add_row(idx, *row.tolist())
