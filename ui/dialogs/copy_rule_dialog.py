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


class CopyRuleDialog(BaseDialog):

    def __init__(
            self,
            mode: str = "",
            from_id: str = "",
            to_id: str = "",
            parent=None,
    ):
        super().__init__(parent)

        self.setWindowTitle(
            "Изменить правило копирования"
            if mode
            else "Добавить правило копирования"
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
            "Режим:",
            self.mode_input,
        )

        form_layout.addRow(
            "Из ID:",
            self.from_id_input,
        )

        form_layout.addRow(
            "В ID:",
            self.to_id_input,
        )

        layout.addLayout(form_layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.cancel_button = QPushButton("Отмена")
        self.save_button = QPushButton("Сохранить")

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
                "Некорректные данные",
                "Укажите режим.",
            )
            return

        if not from_id:
            QMessageBox.warning(
                self,
                "Некорректные данные",
                "Укажите исходный ID.",
            )
            return

        if not to_id:
            QMessageBox.warning(
                self,
                "Некорректные данные",
                "Укажите целевой ID.",
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