from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QWidget
)

from models.eva_models import SessionTemplate, TemplateOrigin


class CustomTemplateDialog(QDialog):

    def __init__(
            self,
            templates: list[SessionTemplate],
            parent=None,
    ):
        super().__init__(parent)

        self.templates = templates
        self.created_templates: list[SessionTemplate] = []

        self.setWindowTitle(
            "Custom templates"
        )

        layout = QVBoxLayout(self)

        for template in self.templates:
            row_layout = QHBoxLayout()

            name_input = QLineEdit(
                template.template_name
            )

            add_button = QPushButton(
                "Добавить вариант"
            )

            row_layout.addWidget(
                name_input
            )

            row_layout.addWidget(
                add_button
            )

            layout.addLayout(
                row_layout
            )

            add_button.clicked.connect(
                lambda checked=False,
                       source_template=template,
                       current_input=name_input:
                    self.add_template_to_preview(
                        source_template,
                        current_input,
                    )
            )

        preview_label = QLabel(
            "Добавляемые шаблоны"
        )

        layout.addWidget(
            preview_label
        )

        self.preview_list = QListWidget()

        layout.addWidget(
            self.preview_list
        )

        self.confirm_button = QPushButton(
            "Добавить custom-шаблоны"
        )

        layout.addWidget(
            self.confirm_button
        )

        self.confirm_button.clicked.connect(
            self.on_confirm_clicked
        )

    def add_template_to_preview(
            self,
            source_template: SessionTemplate,
            name_input: QLineEdit,
    ):
        new_name = name_input.text().strip()

        if not new_name:
            return

        custom_template = SessionTemplate(
            folder_id=source_template.folder_id,
            template_name=new_name,
            origin=TemplateOrigin.CUSTOM,
            selected=True,
            stopper_combination=(
                source_template.stopper_combination
            ),
        )

        self.created_templates.append(
            custom_template
        )

        self.add_preview_item(
            custom_template
        )

    def add_preview_item(
            self,
            template: SessionTemplate,
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

        name_label = QLabel(
            template.template_name
        )

        delete_button = QPushButton("×")
        delete_button.setFixedSize(
            28,
            28,
        )

        row_layout.addWidget(
            name_label
        )

        row_layout.addStretch()

        if template.stopper_combination is not None:
            stopper_badge = QLabel("S")
            stopper_badge.setFixedSize(
                20,
                20,
            )
            row_layout.addWidget(
                stopper_badge
            )

        custom_badge = QLabel("C")
        custom_badge.setFixedSize(
            20,
            20,
        )

        row_layout.addWidget(
            custom_badge
        )

        row_layout.addWidget(
            delete_button
        )

        item.setSizeHint(
            row_widget.sizeHint()
        )

        self.preview_list.addItem(
            item
        )

        self.preview_list.setItemWidget(
            item,
            row_widget,
        )

        delete_button.clicked.connect(
            lambda:
            self.remove_preview_item(
                item,
                template,
            )
        )

    def remove_preview_item(
            self,
            item: QListWidgetItem,
            template: SessionTemplate,
    ):
        if template in self.created_templates:
            self.created_templates.remove(
                template
            )

        row = self.preview_list.row(
            item
        )

        self.preview_list.takeItem(
            row
        )

    def on_confirm_clicked(self):
        if not self.created_templates:
            return

        self.accept()

    def get_created_templates(
            self,
    ) -> list[SessionTemplate]:
        return self.created_templates.copy()