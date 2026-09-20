from PySide6.QtGui import QDesktopServices, QIcon
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit, QListWidget,
    QProgressBar, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox
)
from PySide6.QtCore import Signal, QSize


class EditFilesPage(QWidget):

    loadFilesRequested = Signal(str)
    addFilesRequested = Signal(str)
    renameFilesRequested = Signal()
    removeFilesRequested = Signal()
    replaceRequested = Signal(str)
    stoppersRequested = Signal()
    filterRequested = Signal(str)
    returnProcessedRequested = Signal()

    copySourceRequested = Signal()
    deleteSourceRequested = Signal()
    moveToIdRequested = Signal()

    openExportFolderRequested = Signal()

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
        self.add_files_btn.clicked.connect(
            self.on_add_files_clicked
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
        self.stoppers_btn.clicked.connect(
            self.stoppersRequested.emit
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

        self.open_source_export_btn.clicked.connect(
            self.openExportFolderRequested.emit
        )

        self.open_processed_export_btn.clicked.connect(
            self.openExportFolderRequested.emit
        )

    def setup_ui(self):
        main_layout = QGridLayout(self)
        main_layout.setSpacing(10)

        # =====================================================
        # ROW 0 — Source directory
        # =====================================================
        source_group = QGroupBox("Исходная папка")
        source_layout = QHBoxLayout(source_group)

        self.source_dir_input = QLineEdit()
        self.load_files_btn = QPushButton("Перезагрузить файлы")
        self.add_files_btn = QPushButton("Добавить файлы")

        source_layout.addWidget(self.source_dir_input)
        source_layout.addWidget(self.load_files_btn)
        source_layout.addWidget(self.add_files_btn)

        main_layout.addWidget(
            source_group,
            0, 0, 1, 2
        )

        # =====================================================
        # ROW 1 — Files lists
        # =====================================================

        # --- Left: Source files ---
        left_group = QGroupBox("Файлы для переименования")
        left_layout = QVBoxLayout(left_group)

        self.files_to_rename_list = QListWidget()

        left_buttons_layout = QHBoxLayout()

        self.rename_files_btn = QPushButton("Переименовать")
        self.delete_source_btn = QPushButton("Удалить")
        self.move_to_id_btn = QPushButton("Переместить в ID")
        self.copy_source_btn = QPushButton("Экспорт")

        left_buttons_layout.addWidget(
            self.rename_files_btn
        )
        left_buttons_layout.addWidget(
            self.delete_source_btn
        )
        left_buttons_layout.addWidget(
            self.move_to_id_btn
        )
        left_buttons_layout.addWidget(
            self.copy_source_btn
        )

        self.open_source_export_btn = QPushButton(
            "Открыть папку экспорта"
        )

        left_layout.addWidget(
            self.files_to_rename_list
        )
        left_layout.addLayout(
            left_buttons_layout
        )
        left_layout.addWidget(
            self.open_source_export_btn
        )

        # --- Right: Processed files ---
        right_group = QGroupBox("Переименованные файлы")
        right_layout = QVBoxLayout(right_group)

        self.renamed_files_list = QListWidget()

        right_actions_layout = QHBoxLayout()

        self.return_processed_btn = QPushButton()

        self.return_processed_btn.setIcon(
            QIcon("resources/icons/arrow_left.svg")
        )
        self.return_processed_btn.setIconSize(
            QSize(20, 20)
        )
        self.return_processed_btn.setToolTip(
            "Вернуть в список файлов"
        )

        self.copy_processed_btn = QPushButton("Экспорт")

        self.open_processed_export_btn = QPushButton(
            "Открыть папку экспорта"
        )

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

        right_layout.addWidget(
            self.open_processed_export_btn
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

        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout(
            buttons_widget
        )

        buttons_layout.setContentsMargins(
            0, 10, 0, 0
        )

        self.remove_files_btn = QPushButton(
            "Очистить списки"
        )
        self.remove_files_btn.setMinimumHeight(
            36
        )

        buttons_layout.addWidget(
            self.remove_files_btn
        )
        buttons_layout.addStretch()

        # --- Right: File actions ---
        file_actions_group = QGroupBox(
            "Действия с файлами"
        )
        file_actions_layout = QVBoxLayout(
            file_actions_group
        )

        self.find_input = QLineEdit()
        self.replace_btn = QPushButton("Выполнить")
        self.stoppers_btn = QPushButton("Стоперы...")

        file_actions_layout.addWidget(
            QLabel("Найти текст")
        )

        replace_layout = QHBoxLayout()

        replace_layout.addWidget(
            self.find_input,
            1,
        )

        replace_layout.addWidget(
            self.replace_btn,
            0,
        )

        file_actions_layout.addLayout(
            replace_layout
        )

        file_actions_layout.addWidget(
            self.stoppers_btn
        )

        file_actions_layout.addStretch()

        main_layout.addWidget(
            buttons_widget,
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

    def on_add_files_clicked(self):
        self.addFilesRequested.emit(
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

