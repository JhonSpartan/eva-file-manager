from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit, QListWidget,
    QProgressBar, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QTreeWidget
)
from PySide6.QtCore import Qt, Signal
from widgets.arts_tree import ArtsTree, ArtsTreeMode


class CopyArtsPage(QWidget):

    loadArtsRequested = Signal(str)
    copyAndRenameRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_directory: str | None = None
        self.setup_ui()
        self.setup_connections()

    def setup_connections(self):
        self.load_arts_btn.clicked.connect(self.on_load_arts_clicked)

    def setup_ui(self):
        main_layout = QGridLayout(self)

        # === Source directory (row 0, full width) ===
        source_group = QGroupBox("Source directory")
        source_layout = QHBoxLayout(source_group)

        self.source_dir_input = QLineEdit()
        self.load_arts_btn = QPushButton("Load files")

        source_layout.addWidget(self.source_dir_input)
        source_layout.addWidget(self.load_arts_btn)

        main_layout.addWidget(source_group, 0, 0, 1, 2)

        # ==================================================
        # === Row 1: TWO COLUMNS ============================
        # ==================================================

        # ---------- LEFT COLUMN ----------
        left_column = QVBoxLayout()

        all_articles_group = QGroupBox("Choose article numbers")
        all_articles_layout = QVBoxLayout(all_articles_group)

        self.artsTree = ArtsTree(ArtsTreeMode.AVAILABLE)

        all_articles_layout.addWidget(self.artsTree)
        left_column.addWidget(all_articles_group)

        main_layout.addLayout(left_column, 1, 0)

        # ---------- RIGHT COLUMN (FROM + TO) ----------
        right_column = QVBoxLayout()

        # --- FROM ---
        from_group = QGroupBox("Article numbers to copy from")
        from_layout = QVBoxLayout(from_group)

        self.srcArtsTree = ArtsTree(ArtsTreeMode.SOURCE)

        from_layout.addWidget(self.srcArtsTree)

        # --- TO ---
        to_group = QGroupBox("Article numbers to copy to")
        to_layout = QVBoxLayout(to_group)

        self.dstArtsTree = ArtsTree(ArtsTreeMode.DESTINATION)

        to_layout.addWidget(self.dstArtsTree)

        right_column.addWidget(from_group)
        right_column.addWidget(to_group)

        main_layout.addLayout(right_column, 1, 1)

        # ==================================================
        # === Progress bar (row 2, full width) ============
        # ==================================================
        self.copyAndRenamePbar = QProgressBar()
        self.copyAndRenamePbar.setValue(0)
        main_layout.addWidget(self.copyAndRenamePbar, 2, 0, 1, 2)

        # ==================================================
        # === Buttons (row 3) ==============================
        # ==================================================
        self.removeArtNumbers = QPushButton("Remove article numbers")
        self.copyAndRenameButton = QPushButton("Copy and rename")

        main_layout.addWidget(self.removeArtNumbers, 3, 0)
        main_layout.addWidget(self.copyAndRenameButton, 3, 1)

        # ==================================================
        # === Stretch settings =============================
        # ==================================================
        main_layout.setColumnStretch(0, 1)  # левая шире
        main_layout.setColumnStretch(1, 1)
        main_layout.setRowStretch(1, 1)

        # ==================================================
        # === Widgets registry =============================
        # ==================================================
        self.widgets = {
            "source_dir": self.source_dir_input,
            "artsTree": self.artsTree,
            "srcArts": self.srcArtsTree,
            "dstArts": self.dstArtsTree,
            "removeArts": self.removeArtNumbers,
            "copy": self.copyAndRenameButton,
            "progress": self.copyAndRenamePbar,
        }

    def on_load_arts_clicked(self):
        self.loadArtsRequested.emit(self.current_directory)

    def on_copy_and_rename_clicked(self):
        self.copyAndRenameRequested.emit()
