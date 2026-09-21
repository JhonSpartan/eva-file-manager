from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
)

from models.catalog_models import StopperRecord
from ui.dialogs.base_dialog import BaseDialog


class StopperActionsDialog(BaseDialog):

    def __init__(
            self,
            stopper: StopperRecord,
            parent=None,
    ):
        super().__init__(parent)

        self.setWindowTitle("Стоперы")
        self.setModal(True)

        self.stopper = stopper

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self) -> None:

        main_layout = QVBoxLayout(self)

        main_layout.addWidget(
            QLabel(
                f"Стопер: {self.stopper.stopper_name}"
            )
        )

        main_layout.addWidget(
            QLabel(
                f"Текущий диаметр: "
                f"{self.stopper.diameter} мм"
            )
        )

        main_layout.addWidget(
            QLabel("Действие")
        )

        self.change_diameter_radio = QRadioButton(
            "Изменить диаметр"
        )

        self.delete_stoppers_radio = QRadioButton(
            "Удалить стоперы"
        )

        self.change_diameter_radio.setChecked(
            True
        )

        main_layout.addWidget(
            self.change_diameter_radio
        )

        main_layout.addWidget(
            self.delete_stoppers_radio
        )

        main_layout.addWidget(
            QLabel("Новый диаметр")
        )

        diameter_layout = QHBoxLayout()

        self.new_diameter_input = QLineEdit()

        diameter_layout.addWidget(
            self.new_diameter_input
        )

        diameter_layout.addWidget(
            QLabel("мм")
        )

        main_layout.addLayout(
            diameter_layout
        )

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.cancel_btn = QPushButton(
            "Отмена"
        )

        self.continue_btn = QPushButton(
            "Продолжить"
        )

        buttons_layout.addWidget(
            self.cancel_btn
        )

        buttons_layout.addWidget(
            self.continue_btn
        )

        main_layout.addLayout(
            buttons_layout
        )

    def setup_connections(self) -> None:

        self.cancel_btn.clicked.connect(
            self.reject
        )

        self.continue_btn.clicked.connect(
            self.on_continue_clicked
        )

        self.change_diameter_radio.toggled.connect(
            self.on_action_changed
        )

        self.delete_stoppers_radio.toggled.connect(
            self.on_action_changed
        )

    def on_action_changed(self) -> None:

        self.new_diameter_input.setEnabled(
            self.change_diameter_radio.isChecked()
        )

    def is_change_diameter(self) -> bool:
        return self.change_diameter_radio.isChecked()

    def is_delete_stoppers(self) -> bool:
        return self.delete_stoppers_radio.isChecked()

    def get_new_diameter(self) -> float | None:

        text = (
            self.new_diameter_input
            .text()
            .strip()
        )

        if not text:
            return None

        try:
            return float(
                text.replace(",", ".")
            )

        except ValueError:
            return None

    def on_continue_clicked(self) -> None:

        if self.is_delete_stoppers():
            self.accept()
            return

        text = (
            self.new_diameter_input
            .text()
            .strip()
        )

        if not text:
            QMessageBox.warning(
                self,
                "Стоперы",
                "Укажите новый диаметр.",
            )
            return

        try:
            diameter = float(
                text.replace(",", ".")
            )

        except ValueError:
            QMessageBox.warning(
                self,
                "Стоперы",
                "Некорректный диаметр.",
            )
            return

        if diameter <= 0:
            QMessageBox.warning(
                self,
                "Стоперы",
                "Диаметр должен быть больше нуля.",
            )
            return

        self.accept()