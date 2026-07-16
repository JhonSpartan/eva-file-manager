from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit, QListWidget,
    QProgressBar, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox
)
from PySide6.QtCore import Qt, Signal


class EditFilesPage(QWidget):

    loadFilesRequested = Signal(str)
    renameFilesRequested = Signal()
    replaceCharRequested = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_directory: str | None = None
        self.setup_ui()
        self.setup_connections()

    def setup_connections(self):
        self.load_files_btn.clicked.connect(self.on_load_files_clicked)
        self.rename_files_btn.clicked.connect(self.on_rename_files_clicked)
        self.replace_btn.clicked.connect(self.on_replace_char_clicked)

    def setup_ui(self):
        main_layout = QGridLayout(self)
        main_layout.setSpacing(10)

        # =====================================================
        # ROW 0 — Source directory (на всю ширину)
        # =====================================================
        source_group = QGroupBox("Source directory")
        source_layout = QHBoxLayout(source_group)

        self.source_dir_input = QLineEdit()
        self.load_files_btn = QPushButton("Load files")

        source_layout.addWidget(self.source_dir_input)
        source_layout.addWidget(self.load_files_btn)

        main_layout.addWidget(source_group, 0, 0, 1, 2)

        # =====================================================
        # ROW 1 — Files lists (2 колонки)
        # =====================================================

        # --- Left: Files to rename ---
        left_group = QGroupBox("Files to rename")
        left_layout = QVBoxLayout(left_group)

        self.files_to_rename_list = QListWidget()
        left_layout.addWidget(self.files_to_rename_list)

        # --- Right: Renamed files ---
        right_group = QGroupBox("Renamed files")
        right_layout = QVBoxLayout(right_group)

        self.renamed_files_list = QListWidget()
        right_layout.addWidget(self.renamed_files_list)

        main_layout.addWidget(left_group, 1, 0)
        main_layout.addWidget(right_group, 1, 1)

        # =====================================================
        # ROW 2 — Progress bar (на всю ширину)
        # =====================================================
        self.editFilesPbar = QProgressBar()
        self.editFilesPbar.setValue(0)

        main_layout.addWidget(self.editFilesPbar, 2, 0, 1, 2)

        # =====================================================
        # ROW 3 — Bottom controls (2 колонки)
        # =====================================================

        # --- Left: Rename / Remove buttons ---
        buttons_group = QGroupBox()
        buttons_layout = QVBoxLayout(buttons_group)

        self.rename_files_btn = QPushButton("Rename files")
        self.remove_files_btn = QPushButton("Remove files")

        self.rename_files_btn.setMinimumHeight(36)
        self.remove_files_btn.setMinimumHeight(36)

        buttons_layout.addWidget(self.rename_files_btn)
        buttons_layout.addWidget(self.remove_files_btn)
        buttons_layout.addStretch()

        # --- Right: Find / Replace ---
        replace_group = QGroupBox()
        replace_layout = QVBoxLayout(replace_group)

        self.find_input = QLineEdit()
        self.replace_input = QLineEdit()
        self.replace_btn = QPushButton("Replace")

        replace_layout.addWidget(QLabel("Find text"))
        replace_layout.addWidget(self.find_input)
        replace_layout.addWidget(QLabel("Replace with"))
        replace_layout.addWidget(self.replace_input)
        replace_layout.addWidget(self.replace_btn)
        replace_layout.addStretch()

        main_layout.addWidget(buttons_group, 3, 0)
        main_layout.addWidget(replace_group, 3, 1)

        # =====================================================
        # Stretch & proportions
        # =====================================================
        main_layout.setRowStretch(1, 1)   # списки растягиваются
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 1)

        # =====================================================
        # Словарь виджетов (как ты любишь 👍)
        # =====================================================
        self.widgets = {
            "source_dir": self.source_dir_input,
            "files_src": self.files_to_rename_list,
            "files_dst": self.renamed_files_list,
            "progress": self.editFilesPbar,
            "find": self.find_input,
            "replace": self.replace_input,
        }

    def on_load_files_clicked(self):
        self.loadFilesRequested.emit(self.current_directory)

    def on_rename_files_clicked(self):
        self.renameFilesRequested.emit()

    def on_replace_char_clicked(self):
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        self.replaceCharRequested.emit(find_text, replace_text)