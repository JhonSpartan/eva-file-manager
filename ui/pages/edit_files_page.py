from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit, QListWidget,
    QProgressBar, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox
)
from PySide6.QtCore import Signal


class EditFilesPage(QWidget):

    loadFilesRequested = Signal(str)
    renameFilesRequested = Signal()
    removeFilesRequested = Signal()
    replaceRequested = Signal(str)
    filterRequested = Signal(str)
    returnProcessedRequested = Signal()

    copySourceRequested = Signal()
    deleteSourceRequested = Signal()
    moveToIdRequested = Signal()

    copyProcessedRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_directory: str | None = None
        self.setup_ui()
        self.setup_connections()

    def setup_connections(self):
        self.load_files_btn.clicked.connect(
            self.on_load_files_clicked
        )
        self.rename_files_btn.clicked.connect(
            self.on_rename_files_clicked
        )
        self.find_input.textEdited.connect(
            self.on_char_input
        )
        self.replace_btn.clicked.connect(
            self.on_replace_clicked
        )
        self.copy_source_btn.clicked.connect(
            self.copySourceRequested.emit
        )
        self.delete_source_btn.clicked.connect(
            self.deleteSourceRequested.emit
        )
        self.move_to_id_btn.clicked.connect(
            self.moveToIdRequested.emit
        )
        self.copy_processed_btn.clicked.connect(
            self.copyProcessedRequested.emit
        )
        self.remove_files_btn.clicked.connect(
            self.on_remove_files_clicked
        )
        self.return_processed_btn.clicked.connect(
            self.returnProcessedRequested.emit
        )

    def setup_ui(self):
        main_layout = QGridLayout(self)
        main_layout.setSpacing(10)

        # =====================================================
        # ROW 0 — Source directory
        # =====================================================
        source_group = QGroupBox("Source directory")
        source_layout = QHBoxLayout(source_group)

        self.source_dir_input = QLineEdit()
        self.load_files_btn = QPushButton("Load files")

        source_layout.addWidget(self.source_dir_input)
        source_layout.addWidget(self.load_files_btn)

        main_layout.addWidget(
            source_group,
            0, 0, 1, 2
        )

        # =====================================================
        # ROW 1 — Files lists
        # =====================================================

        # --- Left: Source files ---
        left_group = QGroupBox("Files to rename")
        left_layout = QVBoxLayout(left_group)

        self.files_to_rename_list = QListWidget()

        left_buttons_layout = QHBoxLayout()

        self.copy_source_btn = QPushButton("Export")
        self.delete_source_btn = QPushButton("Delete")
        self.move_to_id_btn = QPushButton("Move to ID")

        left_buttons_layout.addWidget(
            self.copy_source_btn
        )
        left_buttons_layout.addWidget(
            self.delete_source_btn
        )
        left_buttons_layout.addWidget(
            self.move_to_id_btn
        )

        left_layout.addWidget(
            self.files_to_rename_list
        )
        left_layout.addLayout(
            left_buttons_layout
        )

        # --- Right: Processed files ---
        right_group = QGroupBox("Renamed files")
        right_layout = QVBoxLayout(right_group)

        self.renamed_files_list = QListWidget()
        right_actions_layout = QHBoxLayout()
        self.return_processed_btn = QPushButton("←")
        self.return_processed_btn.setFixedWidth(40)
        self.copy_processed_btn = QPushButton("Export")


        right_layout.addWidget(
            self.renamed_files_list
        )
        right_actions_layout.addWidget(
            self.return_processed_btn
        )
        right_actions_layout.addWidget(
            self.copy_processed_btn
        )



        right_layout.addLayout(
            right_actions_layout
        )

        main_layout.addWidget(
            left_group,
            1, 0
        )

        main_layout.addWidget(
            right_group,
            1, 1
        )

        # =====================================================
        # ROW 2 — Progress bar
        # =====================================================
        self.editFilesPbar = QProgressBar()
        self.editFilesPbar.setValue(0)

        main_layout.addWidget(
            self.editFilesPbar,
            2, 0, 1, 2
        )

        # =====================================================
        # ROW 3 — Bottom controls
        # =====================================================

        # --- Left: existing rename action ---
        buttons_group = QGroupBox()
        buttons_layout = QVBoxLayout(buttons_group)

        self.rename_files_btn = QPushButton("Rename files")
        self.remove_files_btn = QPushButton("Remove files")

        self.rename_files_btn.setMinimumHeight(36)
        self.remove_files_btn.setMinimumHeight(36)

        buttons_layout.addWidget(self.rename_files_btn)
        buttons_layout.addWidget(self.remove_files_btn)
        buttons_layout.addStretch()

        # --- Right: File actions ---
        file_actions_group = QGroupBox("File actions")
        file_actions_layout = QVBoxLayout(
            file_actions_group
        )

        self.find_input = QLineEdit()
        self.replace_btn = QPushButton("Execute")

        file_actions_layout.addWidget(
            QLabel("Find text")
        )
        file_actions_layout.addWidget(
            self.find_input
        )
        file_actions_layout.addWidget(
            self.replace_btn
        )
        file_actions_layout.addStretch()

        main_layout.addWidget(
            buttons_group,
            3, 0
        )

        main_layout.addWidget(
            file_actions_group,
            3, 1
        )

        # =====================================================
        # Stretch & proportions
        # =====================================================
        main_layout.setRowStretch(1, 1)
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 1)

        # =====================================================
        # Widgets dictionary
        # =====================================================
        self.widgets = {
            "source_dir": self.source_dir_input,
            "files_src": self.files_to_rename_list,
            "files_dst": self.renamed_files_list,
            "progress": self.editFilesPbar,
            "find": self.find_input,
        }

    def on_load_files_clicked(self):
        self.loadFilesRequested.emit(
            self.current_directory
        )

    def on_rename_files_clicked(self):
        self.renameFilesRequested.emit()

    def on_replace_clicked(self):
        find_text = self.find_input.text()
        self.replaceRequested.emit(
            find_text
        )

    def on_char_input(self):
        find_text = self.find_input.text()
        self.filterRequested.emit(
            find_text
        )

    def on_remove_files_clicked(self):
        self.removeFilesRequested.emit()