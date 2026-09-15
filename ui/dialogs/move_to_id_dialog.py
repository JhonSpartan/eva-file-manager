from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QSpinBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)

from ui.dialogs.base_dialog import BaseDialog


class MoveToIdDialog(BaseDialog):

    def __init__(
            self,
            parent=None,
    ):
        super().__init__(parent)

        self.setWindowTitle("Move to ID")
        self.setModal(True)

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self) -> None:

        main_layout = QVBoxLayout(self)

        main_layout.addWidget(
            QLabel("Destination ID")
        )

        self.id_input = QSpinBox()
        self.id_input.setMinimum(1)
        self.id_input.setMaximum(999)

        main_layout.addWidget(
            self.id_input
        )

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.cancel_btn = QPushButton(
            "Cancel"
        )

        self.execute_btn = QPushButton(
            "Execute"
        )

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

    def get_destination_id(self) -> str:
        return str(
            self.id_input.value()
        )