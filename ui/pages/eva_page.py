import re
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QHBoxLayout, QTreeWidget, QCheckBox, QTreeWidgetItem, QMessageBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QScrollArea, QProgressBar
from models.eva_models import (SessionTemplate, TemplateOrigin, PreviewTemplate, PreparedEva)


class EvaPage(QWidget):

    FIVE_D_DISABLED_FOLDER_IDS = {1, 5}

    """
    Страница EVA.
    Только UI + сигналы. Без логики.
    """

    addEvaRequested = Signal(str, list)
    addStoppersRequested = Signal()
    clearPreparedEvaRequested = Signal()
    customTemplateRequested = Signal(int)
    templateSelectionChanged = Signal( int, str, bool)
    clearTemplateSelectionRequested = Signal()
    fiveDModeChanged = Signal(bool)
    createStructureRequested = Signal()
    openLastOutputRequested = Signal()
    resetTemplatesRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.template_groups: dict[int, QGroupBox] = {}
        self.five_d_mode = False

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.layout = QGridLayout(self)

        self.setup_eva_group()
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

        stoppers_controls_layout = QHBoxLayout()

        stoppers_controls_layout.addWidget(
            self.add_stoppers_btn
        )

        stoppers_controls_layout.addWidget(
            self.clear_template_selection_btn
        )

        stoppers_controls_layout.addWidget(
            self.reset_templates_btn
        )

        stoppers_controls_layout.addStretch()

        stoppers_controls_layout.addWidget(
            self.use_default_path_checkbox,
            0,
            Qt.AlignVCenter,
        )

        stoppers_controls_layout.addWidget(
            self.five_d_mode_checkbox,
            0,
            Qt.AlignVCenter,
        )

        left_layout.addLayout(
            stoppers_controls_layout,
            0,
        )

        left_layout.addWidget(
            self.templates_group,
            4,
        )

        self.create_progress_bar = QProgressBar()
        self.create_progress_bar.setRange(0, 100)
        self.create_progress_bar.setValue(0)
        self.create_progress_bar.setTextVisible(True)

        self.create_structure_btn = QPushButton(
            "Создать структуру"
        )
        self.create_structure_btn.setMinimumHeight(40)

        self.open_last_output_btn = QPushButton(
            "Открыть выгрузку"
        )

        self.open_last_output_btn.setMinimumHeight(
            40
        )

        creation_buttons_layout = QHBoxLayout()

        creation_buttons_layout.addWidget(
            self.create_structure_btn,
            2,
        )

        creation_buttons_layout.addWidget(
            self.open_last_output_btn,
            1,
        )

        left_layout.addWidget(
            self.create_progress_bar
        )

        left_layout.addLayout(
            creation_buttons_layout
        )

        self.layout.addLayout(
            left_layout,
            1, 0,
        )

        # Правая колонка
        right_layout = QVBoxLayout()

        right_controls_layout = QHBoxLayout()
        right_controls_layout.addStretch()

        right_controls_layout.addWidget(
            self.clear_prepared_eva_btn
        )

        right_layout.addLayout(
            right_controls_layout
        )

        right_layout.addWidget(
            self.preview_group
        )

        self.layout.addLayout(
            right_layout,
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
        self.clear_inputs_btn = QPushButton("Очистить поля")

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.clear_inputs_btn)

        self.eva_layout.addLayout(button_layout, 2, 0, 1, 2)

        self.eva_fields = {
            "name": self.eva_name_input,
            "article_numbers": self.article_numbers_input,
        }

    # ---------- Stoppers ----------

    def setup_stoppers_button(self):
        self.add_stoppers_btn = QPushButton("Добавить стоперы")
        self.add_stoppers_btn.setMinimumHeight(35)
        self.clear_template_selection_btn = QPushButton("Снять все галочки")
        self.clear_template_selection_btn.setMinimumHeight(35)
        self.five_d_mode_checkbox = QCheckBox("Режим 5D")
        self.use_default_path_checkbox = QCheckBox("Путь по умолчанию")
        self.use_default_path_checkbox.setChecked(True)
        self.reset_templates_btn = QPushButton("Сбросить шаблоны")
        self.reset_templates_btn.setMinimumHeight(35)
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
        self.add_stoppers_btn.clicked.connect(self.addStoppersRequested.emit)
        self.add_btn.clicked.connect(self.on_add_clicked)
        self.clear_prepared_eva_btn.clicked.connect(self.clearPreparedEvaRequested.emit)
        self.clear_template_selection_btn.clicked.connect(self.clearTemplateSelectionRequested.emit)
        self.five_d_mode_checkbox.toggled.connect(self.fiveDModeChanged.emit)
        self.clear_inputs_btn.clicked.connect(self.clear_inputs)
        self.create_structure_btn.clicked.connect(self.createStructureRequested.emit)
        self.open_last_output_btn.clicked.connect(self.openLastOutputRequested.emit)
        self.reset_templates_btn.clicked.connect(self.resetTemplatesRequested.emit)

    def render_templates(
            self,
            templates: list[SessionTemplate],
    ):
        self.clear_templates()

        self.template_groups.clear()

        grouped: dict[int, list[SessionTemplate]] = {}

        for template in templates:
            grouped.setdefault(
                template.folder_id,
                [],
            ).append(template)

        for index, (folder_id, folder_templates) in enumerate(
                grouped.items()
        ):
            row = index // 2
            column = index % 2

            group = QGroupBox(
                f"ID {folder_id}"
            )

            self.template_groups[folder_id] = group

            if (
                    self.five_d_mode
                    and folder_id in self.FIVE_D_DISABLED_FOLDER_IDS
            ):
                group.setEnabled(False)

            group_layout = QHBoxLayout(group)

            templates_layout = QVBoxLayout()
            templates_layout.setAlignment(Qt.AlignTop)

            button_layout = QVBoxLayout()
            button_layout.setAlignment(Qt.AlignTop)

            add_custom_button = QPushButton()

            add_custom_button.setFixedSize(24,24)

            add_custom_button.setIcon(
                QIcon("resources/icons/add.svg")
            )
            add_custom_button.setStyleSheet("""
                QPushButton {
                    padding: 0px;
                    text-align: center;
                }
            """)
            add_custom_button.setToolTip(
                "Добавить пользовательский шаблон"
            )

            button_layout.addWidget(
                add_custom_button
            )

            group_layout.addLayout(
                templates_layout,
                1,
            )

            group_layout.addLayout(
                button_layout,
                0,
            )

            add_custom_button.clicked.connect(
                lambda checked=False, current_folder_id=folder_id:
                self.customTemplateRequested.emit(
                    current_folder_id
                )
            )

            for template in folder_templates:
                template_layout = QHBoxLayout()

                checkbox = QCheckBox(
                    template.template_name
                )

                checkbox.setChecked(
                    template.selected
                )

                checkbox.toggled.connect(
                    lambda checked,
                           folder_id=template.folder_id,
                           template_name=template.template_name:
                    self.templateSelectionChanged.emit(
                        folder_id,
                        template_name,
                        checked,
                    )
                )

                template_layout.addWidget(
                    checkbox
                )

                if template.origin == TemplateOrigin.CUSTOM:
                    badge = self.create_template_badge(
                        "C",
                        "Пользовательский",
                    )

                    template_layout.addWidget(
                        badge
                    )

                if template.stopper_combination is not None:
                    badge = self.create_template_badge(
                        "S",
                        "Стопер",
                    )

                    template_layout.addWidget(
                        badge
                    )

                template_layout.addStretch()

                templates_layout.addLayout(
                    template_layout
                )

            self.templates_layout.addWidget(
                group,
                row,
                column,
            )


    def create_template_badge(
            self,
            text: str,
            tooltip: str,
    ) -> QLabel:
        badge = QLabel(text)

        badge.setToolTip(tooltip)
        badge.setAlignment(Qt.AlignCenter)

        badge.setFixedSize(
            20,
            20,
        )

        badge.setStyleSheet("""
            QLabel {
                border: 1px solid;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
            }
        """)

        return badge

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

        controls_layout = QHBoxLayout()
        controls_layout.addStretch()

        self.clear_prepared_eva_btn = QPushButton(
            "Очистить структуру EVA"
        )
        self.clear_prepared_eva_btn.setMinimumHeight(35)

        controls_layout.addWidget(
            self.clear_prepared_eva_btn
        )

        preview_layout.addLayout(
            controls_layout
        )

        self.preview_tree = QTreeWidget()
        self.preview_tree.setHeaderHidden(True)

        preview_layout.addWidget(
            self.preview_tree
        )

    def parse_articles(self, text: str) -> list[str]:
        return [
            article.lower()
            for article in re.findall(
                r"art-\d+",
                text,
                flags=re.IGNORECASE,
            )
        ]

    def on_add_clicked(self):
        eva_name = self.eva_name_input.text().strip()

        articles = self.parse_articles(
            self.article_numbers_input.text()
        )

        if not eva_name:
            QMessageBox.warning(
                self,
                "Не заполнено поле",
                "Введите имя EVA.",
            )
            return

        if not articles:
            QMessageBox.warning(
                self,
                "Не заполнено поле",
                "Введите хотя бы один артикул.",
            )
            return

        self.addEvaRequested.emit(
            eva_name,
            articles,
        )

    def set_template_group_enabled(
            self,
            folder_id: int,
            enabled: bool,
    ):
        group = self.template_groups.get(
            folder_id
        )

        if group is not None:
            group.setEnabled(enabled)

    def set_five_d_mode(
            self,
            enabled: bool,
    ):
        self.five_d_mode = enabled

        for folder_id, group in self.template_groups.items():
            group.setEnabled(
                not (
                        enabled
                        and folder_id in self.FIVE_D_DISABLED_FOLDER_IDS
                )
            )

    def render_preview(
            self,
            prepared_evas: list[PreparedEva],
            preview_templates: list[PreviewTemplate],
    ):
        self.preview_tree.clear()

        grouped_templates = {}

        for template in preview_templates:
            grouped_templates.setdefault(
                template.destination_folder_id,
                [],
            ).append(template)

        for prepared_eva in prepared_evas:
            eva_item = QTreeWidgetItem(
                [prepared_eva.name]
            )

            self.preview_tree.addTopLevelItem(
                eva_item
            )

            for article in prepared_eva.articles:
                article_item = QTreeWidgetItem(
                    [article]
                )

                eva_item.addChild(
                    article_item
                )

                for folder_id in sorted(
                        grouped_templates
                ):
                    id_item = QTreeWidgetItem(
                        [f"ID {folder_id}"]
                    )

                    article_item.addChild(
                        id_item
                    )

                    for template in grouped_templates[
                        folder_id
                    ]:
                        template_item = QTreeWidgetItem(
                            [
                                f"{template.template_name}.dxf"
                            ]
                        )

                        id_item.addChild(
                            template_item
                        )

        self.preview_tree.expandAll()

    def clear_inputs(self):
        self.eva_name_input.clear()
        self.article_numbers_input.clear()

        self.eva_name_input.setFocus()

    def set_creation_progress(
            self,
            value: int,
    ):
        self.create_progress_bar.setValue(
            value
        )

    def reset_creation_progress(self):
        self.create_progress_bar.setValue(0)