# ui/pages/database_page.py

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
)

from widgets.database_table import (
    DatabaseTableWidget,
)


class DatabasePage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()

        self.templatesTable = DatabaseTableWidget(
            [
                "Folder ID",
                "Template",
            ]
        )

        self.stoppersTable = DatabaseTableWidget(
            [
                "Stopper",
                "Diameter",
            ]
        )

        self.copyRulesTable = DatabaseTableWidget(
            [
                "Mode",
                "From ID",
                "To ID",
            ]
        )

        self.tabs.addTab(
            self.templatesTable,
            "Templates",
        )

        self.tabs.addTab(
            self.stoppersTable,
            "Stoppers",
        )

        self.tabs.addTab(
            self.copyRulesTable,
            "Copy rules",
        )

        layout.addWidget(
            self.tabs
        )