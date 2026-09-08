# ui/pages/database_page.py

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QGroupBox, QGridLayout,
)

from widgets.database_table import (
    DatabaseTableWidget,
)

from PySide6.QtCore import Signal

from pathlib import Path


class DatabasePage(QWidget):

    editEvaDefaultPathRequested = Signal()
    openEvaLastOutputRequested = Signal()

    editFilesDefaultPathRequested = Signal()
    openFilesLastOutputRequested = Signal()

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
                "Stoppers"
            ]
        )

        self.stoppersTable = DatabaseTableWidget(
            [
                "Diameter",
                "Stopper",
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

        self.setup_paths_group()

        layout.addWidget(
            self.tabs
        )

        layout.addWidget(
            self.paths_group
        )

    def setup_paths_group(self):
        self.paths_group = QGroupBox(
            "Пути"
        )

        layout = QGridLayout(
            self.paths_group
        )

        # Default output

        default_label = QLabel(
            "Выгрузка EVA по умолчанию:"
        )

        self.eva_default_path_input = (
            QLineEdit()
        )
        self.eva_default_path_input.setReadOnly(
            True
        )

        self.edit_eva_default_path_btn = (
            QPushButton("Изменить")
        )

        # Last output

        last_label = QLabel(
            "Последняя выгрузка EVA:"
        )

        self.eva_last_path_input = (
            QLineEdit()
        )
        self.eva_last_path_input.setReadOnly(
            True
        )

        self.open_eva_last_path_btn = (
            QPushButton("Открыть")
        )

        layout.addWidget(
            default_label,
            0,
            0,
        )

        layout.addWidget(
            self.eva_default_path_input,
            0,
            1,
        )

        layout.addWidget(
            self.edit_eva_default_path_btn,
            0,
            2,
        )

        layout.addWidget(
            last_label,
            1,
            0,
        )

        layout.addWidget(
            self.eva_last_path_input,
            1,
            1,
        )

        layout.addWidget(
            self.open_eva_last_path_btn,
            1,
            2,
        )

        self.files_default_path_input = QLineEdit()
        self.files_default_path_input.setReadOnly(True)

        self.edit_files_default_path_btn = QPushButton(
            "Изменить"
        )

        layout.addWidget(
            QLabel("Выгрузка файлов по умолчанию:"),
            2,
            0,
        )

        layout.addWidget(
            self.files_default_path_input,
            2,
            1,
        )

        layout.addWidget(
            self.edit_files_default_path_btn,
            2,
            2,
        )

        self.files_last_path_input = QLineEdit()
        self.files_last_path_input.setReadOnly(True)

        self.open_files_last_path_btn = QPushButton(
            "Открыть"
        )

        layout.addWidget(
            QLabel("Последняя выгрузка файлов:"),
            3,
            0,
        )

        layout.addWidget(
            self.files_last_path_input,
            3,
            1,
        )

        layout.addWidget(
            self.open_files_last_path_btn,
            3,
            2,
        )

        self.edit_eva_default_path_btn.clicked.connect(
            self.editEvaDefaultPathRequested.emit
        )

        self.open_eva_last_path_btn.clicked.connect(
            self.openEvaLastOutputRequested.emit
        )

        self.edit_files_default_path_btn.clicked.connect(
            self.editFilesDefaultPathRequested.emit
        )

        self.open_files_last_path_btn.clicked.connect(
            self.openFilesLastOutputRequested.emit
        )

    def set_eva_paths(
            self,
            default_path: Path | None,
            last_path: Path | None,
    ):
        self.eva_default_path_input.setText(
            str(default_path)
            if default_path is not None
            else ""
        )

        self.eva_last_path_input.setText(
            str(last_path)
            if last_path is not None
            else ""
        )

        self.open_eva_last_path_btn.setEnabled(
            last_path is not None
            and last_path.exists()
        )

    def set_files_paths(
            self,
            default_path: Path | None,
            last_path: Path | None,
    ) -> None:
        self.files_default_path_input.setText(
            str(default_path)
            if default_path is not None
            else ""
        )

        self.files_last_path_input.setText(
            str(last_path)
            if last_path is not None
            else ""
        )

        self.open_files_last_path_btn.setEnabled(
            last_path is not None
            and last_path.exists()
        )