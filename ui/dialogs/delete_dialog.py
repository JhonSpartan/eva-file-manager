from PySide6.QtWidgets import (
    QLabel,
    QComboBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)

from models.file_action_models import (
    DeleteLevel,
)
from ui.dialogs.base_dialog import BaseDialog


class DeleteDialog(BaseDialog):

    def __init__(
            self,
            parent=None,
    ):
        super().__init__(parent)

        self.setWindowTitle("Удаление")
        self.setModal(True)

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self) -> None:

        main_layout = QVBoxLayout(self)

        main_layout.addWidget(
            QLabel("Уровень удаления")
        )

        self.level_combo = QComboBox()

        self.level_combo.addItem(
            "Файлы",
            DeleteLevel.FILE,
        )

        self.level_combo.addItem(
            "Папки ID",
            DeleteLevel.ID,
        )

        self.level_combo.addItem(
            "Папки ART",
            DeleteLevel.ART,
        )

        self.level_combo.addItem(
            "Папки EVA",
            DeleteLevel.EVA,
        )

        main_layout.addWidget(
            self.level_combo
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
            self.accept
        )

    def get_level(self) -> DeleteLevel:
        return self.level_combo.currentData()