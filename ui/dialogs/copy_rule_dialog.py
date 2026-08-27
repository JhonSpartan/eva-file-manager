from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
)


class CopyRuleDialog(QDialog):

    def __init__(
            self,
            mode: str = "",
            from_id: str = "",
            to_id: str = "",
            parent=None,
    ):
        super().__init__(parent)

        self.setWindowTitle(
            "Edit copy rule"
            if mode
            else "Add copy rule"
        )

        self.setup_ui()

        self.mode_input.setText(mode)
        self.from_id_input.setText(from_id)
        self.to_id_input.setText(to_id)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.mode_input = QLineEdit()
        self.from_id_input = QLineEdit()
        self.to_id_input = QLineEdit()

        form_layout.addRow(
            "Mode:",
            self.mode_input,
        )

        form_layout.addRow(
            "From ID:",
            self.from_id_input,
        )

        form_layout.addRow(
            "To ID:",
            self.to_id_input,
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
        mode = self.mode_input.text().strip()
        from_id = self.from_id_input.text().strip()
        to_id = self.to_id_input.text().strip()

        if not mode:
            QMessageBox.warning(
                self,
                "Invalid data",
                "Mode is required.",
            )
            return

        if not from_id:
            QMessageBox.warning(
                self,
                "Invalid data",
                "From ID is required.",
            )
            return

        if not to_id:
            QMessageBox.warning(
                self,
                "Invalid data",
                "To ID is required.",
            )
            return

        self.accept()

    def get_data(
            self,
    ) -> tuple[str, str, str]:
        return (
            self.mode_input.text().strip(),
            self.from_id_input.text().strip(),
            self.to_id_input.text().strip(),
        )