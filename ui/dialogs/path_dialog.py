from pathlib import Path

from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QDialogButtonBox,
)

from ui.dialogs.base_dialog import BaseDialog


class PathDialog(BaseDialog):
    def __init__(
            self,
            current_path: Path | None = None,
            parent=None,
    ):
        super().__init__(parent)

        self.setWindowTitle(
            "Путь выгрузки EVA"
        )

        self.setup_ui(current_path)

    def setup_ui(
            self,
            current_path: Path | None,
    ):
        layout = QVBoxLayout(self)

        layout.addWidget(
            QLabel(
                "Путь выгрузки EVA "
                "по умолчанию:"
            )
        )

        path_layout = QHBoxLayout()

        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)

        if current_path is not None:
            self.path_input.setText(
                str(current_path)
            )

        self.browse_btn = QPushButton(
            "Обзор"
        )

        path_layout.addWidget(
            self.path_input
        )
        path_layout.addWidget(
            self.browse_btn
        )

        layout.addLayout(path_layout)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok
            | QDialogButtonBox.Cancel
        )

        self.buttons.button(
            QDialogButtonBox.Ok
        ).setText(
            "ОК"
        )

        self.buttons.button(
            QDialogButtonBox.Cancel
        ).setText(
            "Отмена"
        )

        layout.addWidget(self.buttons)

        self.browse_btn.clicked.connect(
            self.select_directory
        )

        self.buttons.accepted.connect(
            self.accept
        )

        self.buttons.rejected.connect(
            self.reject
        )

    def select_directory(self):
        directory = (
            QFileDialog.getExistingDirectory(
                self,
                "Выберите папку выгрузки",
                self.path_input.text(),
            )
        )

        if not directory:
            return

        self.path_input.setText(directory)

    def get_path(self) -> Path | None:
        path_text = (
            self.path_input.text().strip()
        )

        if not path_text:
            return None

        return Path(path_text)