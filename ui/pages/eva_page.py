from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QHBoxLayout, QTreeWidget, QCheckBox
)
from PySide6.QtCore import Signal

from ui.dialogs.eva_dialog import EvaDialog

from PySide6.QtWidgets import QScrollArea


class EvaPage(QWidget):
    """
    Страница EVA.
    Только UI + сигналы. Без логики.
    """

    addEvaRequested = Signal(str, list)
    addStoppersRequested = Signal()
    clearPreparedEvaRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.layout = QGridLayout(self)

        self.setup_eva_group()
        self.setup_prepared_eva_group()
        self.setup_stoppers_button()
        self.setup_templates_group()
        self.setup_preview_group()

        self.layout.addWidget(
            self.eva_group,
            0, 0,
            1, 2,
        )

        # Левая колонка
        left_layout = QVBoxLayout()

        left_layout.addWidget(
            self.prepared_eva_group,
            1,
        )

        left_layout.addWidget(
            self.add_stoppers_btn,
        )

        left_layout.addWidget(
            self.templates_group,
            4,
        )

        self.layout.addLayout(
            left_layout,
            1, 0,
        )

        # Правая колонка
        self.layout.addWidget(
            self.preview_group,
            1, 1,
        )

        self.layout.setColumnStretch(0, 7)
        self.layout.setColumnStretch(1, 3)

        self.layout.setRowStretch(1, 1)

    # ---------- EVA input group ----------

    def setup_eva_group(self):
        self.eva_group = QGroupBox("Параметры EVA")
        self.eva_layout = QGridLayout(self.eva_group)

        self.eva_name_input = QLineEdit()
        self.article_numbers_input = QLineEdit()

        self.eva_layout.addWidget(QLabel("Имя EVA:"), 0, 0)
        self.eva_layout.addWidget(self.eva_name_input, 0, 1)
        self.eva_layout.addWidget(QLabel("Номера артикулов:"), 1, 0)
        self.eva_layout.addWidget(self.article_numbers_input, 1, 1)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.add_btn = QPushButton("Добавить")
        self.clear_fields_btn = QPushButton("Очистить поля")

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.clear_fields_btn)

        self.eva_layout.addLayout(button_layout, 2, 0, 1, 2)

        self.eva_fields = {
            "name": self.eva_name_input,
            "article_numbers": self.article_numbers_input,
        }


    # ---------- Prepared EVA ----------

    def setup_prepared_eva_group(self):
        self.prepared_eva_group = QGroupBox(
            "Добавленные EVA"
        )

        group_layout = QVBoxLayout(
            self.prepared_eva_group
        )

        controls_layout = QHBoxLayout()
        controls_layout.addStretch()

        self.clear_prepared_eva_btn = QPushButton(
            "Очистить"
        )

        controls_layout.addWidget(
            self.clear_prepared_eva_btn
        )

        group_layout.addLayout(
            controls_layout
        )

        self.prepared_scroll = QScrollArea()
        self.prepared_scroll.setWidgetResizable(True)

        self.prepared_container = QWidget()

        self.prepared_eva_layout = QVBoxLayout(
            self.prepared_container
        )

        self.prepared_eva_layout.addStretch()

        self.prepared_scroll.setWidget(
            self.prepared_container
        )

        group_layout.addWidget(
            self.prepared_scroll
        )

    # ---------- Stoppers ----------

    def setup_stoppers_button(self):
        self.add_stoppers_btn = QPushButton("Добавить стоперы")
        self.add_stoppers_btn.setMinimumHeight(35)

    # ---------- Logs / Templates ----------

    def setup_templates_group(self):
        self.templates_group = QGroupBox(
            "Типы шаблонов"
        )

        group_layout = QVBoxLayout(
            self.templates_group
        )

        self.templates_scroll = QScrollArea()
        self.templates_scroll.setWidgetResizable(True)

        self.templates_container = QWidget()

        self.templates_layout = QGridLayout(
            self.templates_container
        )

        self.templates_layout.setColumnStretch(0, 1)
        self.templates_layout.setColumnStretch(1, 1)

        self.templates_scroll.setWidget(
            self.templates_container
        )

        group_layout.addWidget(
            self.templates_scroll
        )

    # ---------- Connections ----------

    def setup_connections(self):
        self.add_stoppers_btn.clicked.connect(lambda: self.addStoppersRequested.emit())
        self.add_btn.clicked.connect(self.on_add_clicked)
        self.clear_prepared_eva_btn.clicked.connect(self.clearPreparedEvaRequested.emit)

    def render_templates(
            self,
            templates: dict[int, list[str]],
    ):
        self.clear_templates()

        for index, (folder_id, template_names) in enumerate(
                templates.items()
        ):
            row = index // 2
            column = index % 2

            group = QGroupBox(
                f"ID {folder_id}"
            )

            group_layout = QVBoxLayout(group)

            for template_name in template_names:
                checkbox = QCheckBox(
                    template_name
                )

                group_layout.addWidget(
                    checkbox
                )

            self.templates_layout.addWidget(
                group,
                row,
                column,
            )

    def clear_templates(self):
        while self.templates_layout.count():
            item = self.templates_layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()


    def setup_preview_group(self):
        self.preview_group = QGroupBox(
            "Структура EVA"
        )

        preview_layout = QVBoxLayout(
            self.preview_group
        )

        self.preview_tree = QTreeWidget()
        self.preview_tree.setHeaderHidden(True)

        preview_layout.addWidget(
            self.preview_tree
        )

    def on_add_clicked(self):
        name = self.eva_name_input.text().strip()
        articles_text = self.article_numbers_input.text().strip()
        articles = [a.strip() for a in articles_text.split(",") if a.strip()]

        self.addEvaRequested.emit(name, articles)