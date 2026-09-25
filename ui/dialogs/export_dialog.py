from pathlib import Path
from PySide6.QtWidgets import (
    QLabel,
    QComboBox,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
)

from models.file_action_models import ExportLevel
from ui.dialogs.base_dialog import BaseDialog


class ExportDialog(BaseDialog):

    def __init__(
            self,
            default_path: Path | None = None,
            last_directory: str | None = None,
            parent=None,
    ):
        super().__init__(parent)

        self.setWindowTitle("Экспорт")
        self.setModal(True)

        self.default_path = default_path
        self.last_directory = last_directory

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self) -> None:

        main_layout = QVBoxLayout(self)

        main_layout.addWidget(
            QLabel("Уровень экспорта")
        )

        self.level_combo = QComboBox()

        self.level_combo.addItem(
            "Папки EVA",
            ExportLevel.EVA,
        )

        self.level_combo.addItem(
            "Папки ART",
            ExportLevel.ART,
        )

        self.level_combo.addItem(
            "Файлы",
            ExportLevel.FILE,
        )

        main_layout.addWidget(
            self.level_combo
        )

        main_layout.addWidget(
            QLabel("Папка назначения")
        )

        path_layout = QHBoxLayout()

        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)

        self.browse_btn = QPushButton(
            "Обзор"
        )

        path_layout.addWidget(
            self.path_input
        )

        path_layout.addWidget(
            self.browse_btn
        )

        main_layout.addLayout(
            path_layout
        )

        self.use_default_path_checkbox = QCheckBox(
            "Использовать путь экспорта по умолчанию"
        )

        if self.default_path is not None:
            self.use_default_path_checkbox.setChecked(
                True
            )

            self.path_input.setText(
                str(self.default_path)
            )

        main_layout.addWidget(
            self.use_default_path_checkbox
        )

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.cancel_btn = QPushButton(
            "Отмена"
        )

        self.execute_btn = QPushButton(
            "Выполнить"
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

        self.browse_btn.clicked.connect(
            self.on_browse_clicked
        )

        self.use_default_path_checkbox.toggled.connect(
            self.on_default_path_toggled
        )

    def on_browse_clicked(self) -> None:

        directory = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку назначения",
            self.last_directory or "",
        )

        if not directory:
            return

        self.path_input.setText(
            directory
        )

        self.use_default_path_checkbox.setChecked(
            False
        )

    def on_default_path_toggled(
            self,
            checked: bool,
    ) -> None:

        if not checked:
            return

        if self.default_path is None:
            self.use_default_path_checkbox.setChecked(
                False
            )
            return

        self.path_input.setText(
            str(self.default_path)
        )

    def get_level(self) -> ExportLevel:
        return self.level_combo.currentData()

    def get_destination_path(self) -> Path | None:

        path_text = (
            self.path_input.text().strip()
        )

        if not path_text:
            return None

        return Path(path_text)