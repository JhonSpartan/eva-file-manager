from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QGroupBox,
    QHBoxLayout,
    QScrollArea,
    QWidget, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QLabel,
)

from models.catalog_models import StopperRecord
from models.eva_models import StopperCombination
from widgets.stopper_button import StopperButton


class StopperSelectionDialog(QDialog):

    def __init__(
            self,
            stoppers: list[StopperRecord],
            parent=None,
    ):
        super().__init__(parent)

        self.stoppers = stoppers
        self.stopper_buttons: list[StopperButton] = []

        self.confirmed_combinations: list[
            StopperCombination
        ] = []

        self.setWindowTitle("Добавить стоперы")

        self.setup_ui()

    def group_stoppers(
            self,
    ) -> dict[float, list[StopperRecord]]:
        grouped: dict[
            float,
            list[StopperRecord]
        ] = {}

        for stopper in self.stoppers:
            grouped.setdefault(
                stopper.diameter,
                [],
            ).append(stopper)

        return grouped

    def setup_ui(self):
        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        self.groups_layout = QVBoxLayout(container)

        grouped_stoppers = self.group_stoppers()

        for diameter, stoppers in grouped_stoppers.items():
            group = QGroupBox(
                f"Ø {diameter:g} мм"
            )

            group_layout = QHBoxLayout(group)

            for stopper in stoppers:
                button = StopperButton(
                    stopper
                )

                button.toggled.connect(
                    self.update_current_combination
                )

                group_layout.addWidget(button)

                self.stopper_buttons.append(
                    button
                )

            group_layout.addStretch()

            self.groups_layout.addWidget(
                group
            )

        self.groups_layout.addStretch()

        scroll.setWidget(container)

        layout.addWidget(scroll)

        self.current_combination_group = QGroupBox(
            "Текущая комбинация"
        )

        combination_layout = QVBoxLayout(
            self.current_combination_group
        )

        self.current_combination_input = QLineEdit()
        self.current_combination_input.setReadOnly(True)

        self.confirm_combination_button = QPushButton(
            "Подтвердить комбинацию"
        )

        combination_layout.addWidget(
            self.current_combination_input
        )

        combination_layout.addWidget(
            self.confirm_combination_button
        )

        layout.addWidget(
            self.current_combination_group
        )

        self.confirmed_group = QGroupBox(
            "Подтверждённые комбинации"
        )

        confirmed_layout = QVBoxLayout(
            self.confirmed_group
        )

        self.confirmed_list = QListWidget()

        confirmed_layout.addWidget(
            self.confirmed_list
        )

        layout.addWidget(
            self.confirmed_group
        )

        self.add_stoppers_button = QPushButton(
            "Добавить стоперы"
        )

        layout.addWidget(
            self.add_stoppers_button
        )

        # Connections
        self.confirm_combination_button.clicked.connect(
            self.confirm_current_combination
        )

        self.add_stoppers_button.clicked.connect(
            self.on_add_stoppers_clicked
        )

    def update_current_combination(self):
        selected_buttons = [
            button
            for button in self.stopper_buttons
            if button.isChecked()
        ]

        if not selected_buttons:
            for button in self.stopper_buttons:
                button.setEnabled(True)

            self.current_combination_input.clear()
            return

        current_diameter = (
            selected_buttons[0].stopper.diameter
        )

        for button in self.stopper_buttons:
            button.setEnabled(
                button.stopper.diameter
                == current_diameter
            )

        combination = "_".join(
            button.stopper.stopper_name
            for button in selected_buttons
        )

        self.current_combination_input.setText(
            combination
        )

    def confirm_current_combination(self):
        selected_stoppers = [
            button.stopper
            for button in self.stopper_buttons
            if button.isChecked()
        ]

        if not selected_stoppers:
            return

        combination = StopperCombination(
            stoppers=selected_stoppers
        )

        if any(
                existing.name == combination.name
                for existing in self.confirmed_combinations
        ):
            return

        self.confirmed_combinations.append(
            combination
        )

        self.add_confirmed_combination_item(
            combination
        )

        self.clear_current_combination()

    def clear_current_combination(self):
        for button in self.stopper_buttons:
            button.setChecked(False)

        self.current_combination_input.clear()

        for button in self.stopper_buttons:
            button.setEnabled(True)

    def add_confirmed_combination_item(
            self,
            combination: StopperCombination,
    ):
        item = QListWidgetItem()

        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)

        row_layout.setContentsMargins(
            6,
            2,
            2,
            2,
        )

        combination_label = QLabel(
            combination.name
        )

        delete_button = QPushButton("×")
        delete_button.setFixedSize(
            28,
            28,
        )

        row_layout.addWidget(
            combination_label
        )
        row_layout.addStretch()
        row_layout.addWidget(
            delete_button
        )

        item.setSizeHint(
            row_widget.sizeHint()
        )

        self.confirmed_list.addItem(
            item
        )

        self.confirmed_list.setItemWidget(
            item,
            row_widget,
        )

        delete_button.clicked.connect(
            lambda: self.remove_confirmed_combination(
                item,
                combination,
            )
        )

    def remove_confirmed_combination(
            self,
            item: QListWidgetItem,
            combination: StopperCombination,
    ):
        if combination in self.confirmed_combinations:
            self.confirmed_combinations.remove(
                combination
            )

        row = self.confirmed_list.row(item)
        self.confirmed_list.takeItem(row)

    def on_add_stoppers_clicked(self):
        if not self.confirmed_combinations:
            return

        self.accept()

    def get_combinations(
            self,
    ) -> list[StopperCombination]:
        return self.confirmed_combinations.copy()