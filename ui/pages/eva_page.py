from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Signal

from ui.dialogs.eva_dialog import EvaDialog


class EvaPage(QWidget):
    """
    Страница EVA.
    Только UI + сигналы. Без логики.
    """

    addEvaRequested = Signal(str, list)
    addStoppersRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        self.setup_eva_group()
        self.setup_prepared_eva_group()
        self.setup_stoppers_button()
        self.setup_templates_group()

        self.layout.addStretch()

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

        self.layout.addWidget(self.eva_group)

        self.eva_fields = {
            "name": self.eva_name_input,
            "article_numbers": self.article_numbers_input,
        }

    # ---------- Prepared EVA ----------

    def setup_prepared_eva_group(self):
        self.prepared_eva_group = QGroupBox("Добавленные EVA")
        self.prepared_eva_layout = QGridLayout(self.prepared_eva_group)
        self.layout.addWidget(self.prepared_eva_group)

    # ---------- Stoppers ----------

    def setup_stoppers_button(self):
        self.add_stoppers_btn = QPushButton("Добавить стоперы")
        self.add_stoppers_btn.setMinimumHeight(35)
        self.layout.addWidget(self.add_stoppers_btn)

    # ---------- Logs / Templates ----------

    def setup_templates_group(self):
        self.templates_group = QGroupBox("Типы шаблонов")
        self.templates_layout = QVBoxLayout(
            self.templates_group
        )

        self.layout.addWidget(
            self.templates_group
        )

    # ---------- Connections ----------

    def setup_connections(self):
        self.add_btn.clicked.connect(self.on_add_clicked)
        self.add_stoppers_btn.clicked.connect(
            lambda: self.addStoppersRequested.emit()
        )

    def on_add_clicked(self):
        name = self.eva_name_input.text().strip()
        articles_text = self.article_numbers_input.text().strip()
        articles = [a.strip() for a in articles_text.split(",") if a.strip()]

        self.addEvaRequested.emit(name, articles)

    def render_templates(
            self,
            templates: dict[int, list[str]],
    ):
        self.clear_templates()

        for folder_id, template_names in templates.items():
            group = QGroupBox(f"ID {folder_id}")
            group_layout = QVBoxLayout(group)

            for template_name in template_names:
                label = QLabel(template_name)
                group_layout.addWidget(label)

            self.templates_layout.addWidget(group)

    def clear_templates(self):
        while self.templates_layout.count():
            item = self.templates_layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()