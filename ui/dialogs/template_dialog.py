# ui/dialogs/template_dialog.py

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
)
from PySide6.QtWidgets import QCheckBox

class TemplateDialog(QDialog):

    def __init__(
            self,
            folder_id: int | None = None,
            template_name: str = "",
            has_stoppers: bool = False,
            parent=None,
    ):
        super().__init__(parent)

        self.setWindowTitle(
            "Edit template"
            if folder_id is not None
            else "Add template"
        )

        self.setup_ui()

        if folder_id is not None:
            self.folder_id_input.setText(
                str(folder_id)
            )

        self.template_name_input.setText(
            template_name
        )

        self.has_stoppers_checkbox.setChecked(
            has_stoppers
        )

    def setup_ui(self):
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.folder_id_input = QLineEdit()
        self.template_name_input = QLineEdit()
        self.has_stoppers_checkbox = QCheckBox("Может иметь стоперы")

        form_layout.addRow(
            "Folder ID:",
            self.folder_id_input,
        )

        form_layout.addRow(
            "Template name:",
            self.template_name_input,
        )

        form_layout.addRow(
            "",
            self.has_stoppers_checkbox,
        )

        layout.addLayout(form_layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.save_button = QPushButton("Save")

        buttons_layout.addWidget(
            self.cancel_button
        )

        buttons_layout.addWidget(
            self.save_button
        )

        layout.addLayout(buttons_layout)

        self.cancel_button.clicked.connect(
            self.reject
        )

        self.save_button.clicked.connect(
            self.validate_and_accept
        )

    def validate_and_accept(self):
        folder_id = self.folder_id_input.text().strip()
        template_name = (
            self.template_name_input.text().strip()
        )

        if not folder_id:
            QMessageBox.warning(
                self,
                "Invalid data",
                "Folder ID is required.",
            )
            return

        if not folder_id.isdigit():
            QMessageBox.warning(
                self,
                "Invalid data",
                "Folder ID must be a number.",
            )
            return

        if not template_name:
            QMessageBox.warning(
                self,
                "Invalid data",
                "Template name is required.",
            )
            return

        self.accept()

    def get_data(
            self,
    ) -> tuple[int, str, bool]:
        return (
            int(self.folder_id_input.text()),
            self.template_name_input.text().strip(),
            self.has_stoppers_checkbox.isChecked(),
        )