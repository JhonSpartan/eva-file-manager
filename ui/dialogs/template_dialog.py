from PySide6.QtWidgets import (
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
    QCheckBox
)

from ui.dialogs.base_dialog import BaseDialog


class TemplateDialog(BaseDialog):

    def __init__(
            self,
            folder_id: int | None = None,
            template_name: str = "",
            has_stoppers: bool = False,
            parent=None,
    ):
        super().__init__(parent)

        self.setWindowTitle(
            "Изменить шаблон"
            if folder_id is not None
            else "Добавить шаблон"
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

    def setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.folder_id_input = QLineEdit()
        self.template_name_input = QLineEdit()
        self.has_stoppers_checkbox = QCheckBox("Может иметь стоперы")

        form_layout.addRow(
            "ID папки:",
            self.folder_id_input,
        )

        form_layout.addRow(
            "Название шаблона:",
            self.template_name_input,
        )

        form_layout.addRow(
            "",
            self.has_stoppers_checkbox,
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

    def validate_and_accept(self) -> None:
        folder_id = self.folder_id_input.text().strip()
        template_name = (
            self.template_name_input.text().strip()
        )

        if not folder_id:
            QMessageBox.warning(
                self,
                "Некорректные данные",
                "Укажите ID папки.",
            )
            return

        if not folder_id.isdigit():
            QMessageBox.warning(
                self,
                "Некорректные данные",
                "ID папки должен быть числом.",
            )
            return

        if not template_name:
            QMessageBox.warning(
                self,
                "Некорректные данные",
                "Укажите название шаблона.",
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