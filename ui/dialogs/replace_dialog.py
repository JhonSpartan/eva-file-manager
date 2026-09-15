from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QVBoxLayout,
    QHBoxLayout,
)

from ui.dialogs.base_dialog import BaseDialog


class ReplaceDialog(BaseDialog):

    def __init__(
            self,
            find_text: str,
            parent=None,
    ):
        super().__init__(parent)

        self.setWindowTitle("Replace")
        self.setModal(True)

        self.setup_ui(find_text)
        self.setup_connections()

    def setup_ui(
            self,
            find_text: str,
    ) -> None:

        main_layout = QVBoxLayout(self)

        # Find text
        main_layout.addWidget(
            QLabel("Find text")
        )

        self.find_input = QLineEdit(find_text)
        self.find_input.setReadOnly(True)

        main_layout.addWidget(
            self.find_input
        )

        # Replace with
        main_layout.addWidget(
            QLabel("Replace with")
        )

        self.replace_input = QLineEdit()

        main_layout.addWidget(
            self.replace_input
        )

        # Mode
        self.create_new_files_checkbox = QCheckBox(
            "Create new files"
        )

        main_layout.addWidget(
            self.create_new_files_checkbox
        )

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.execute_btn = QPushButton("Execute")

        buttons_layout.addWidget(
            self.cancel_btn
        )
        buttons_layout.addWidget(
            self.execute_btn
        )

        main_layout.addLayout(
            buttons_layout
        )

    def setup_connections(self) -> None:
        self.cancel_btn.clicked.connect(
            self.reject
        )

        self.execute_btn.clicked.connect(
            self.accept
        )

    def get_replace_text(self) -> str:
        return self.replace_input.text()

    def create_new_files(self) -> bool:
        return self.create_new_files_checkbox.isChecked()