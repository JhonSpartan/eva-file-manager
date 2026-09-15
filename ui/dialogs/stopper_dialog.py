# ui/dialogs/stopper_dialog.py

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
)

from ui.dialogs.base_dialog import BaseDialog


class StopperDialog(BaseDialog):

    def __init__(
            self,
            diameter: float | None = None,
            stopper_name: str = "",
            parent=None,
    ):
        super().__init__(parent)

        self.setWindowTitle(
            "Edit stopper"
            if diameter is not None
            else "Add stopper"
        )

        self.setup_ui()

        if diameter is not None:
            self.diameter_input.setText(
                str(diameter)
            )

        self.stopper_name_input.setText(
            stopper_name
        )

    def setup_ui(self):
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.diameter_input = QLineEdit()
        self.stopper_name_input = QLineEdit()

        form_layout.addRow(
            "Stopper diameter:",
            self.diameter_input,
        )

        form_layout.addRow(
            "Stopper name:",
            self.stopper_name_input,
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

    def _is_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def validate_and_accept(self):
        diameter = self.diameter_input.text().strip()
        stopper_name = (
            self.stopper_name_input.text().strip()
        )

        if not diameter:
            QMessageBox.warning(
                self,
                "Invalid data",
                "Diameter is required.",
            )
            return

        if not self._is_float(diameter):
            QMessageBox.warning(
                self,
                "Invalid data",
                "Diameter must be a number.",
            )
            return

        if not stopper_name:
            QMessageBox.warning(
                self,
                "Invalid data",
                "Stopper name is required.",
            )
            return

        self.accept()

    def get_data(self) -> tuple[float, str]:
        return (
            float(self.diameter_input.text()),
            self.stopper_name_input.text().strip(),
        )