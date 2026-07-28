from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLineEdit,
    QStackedWidget, QMessageBox, QFileDialog, QListWidgetItem
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt, QTimer, QThread

import pathlib
from pathlib import Path

from models.results import RenameFileResult
from ui.pages.copy_rename_page import CopyRenamePage
from ui.pages.eva_page import EvaPage
from ui.pages.edit_files_page import EditFilesPage

from services.file_service import FileService
from workers.rename_worker import RenameWorker
from workers.replace_worker import ReplaceWorker

class Ui_MainWindow:
    def setup_ui(self, MainWindow):
        MainWindow.setWindowTitle("EVA Configurator")
        MainWindow.resize(950, 700)

        # === Центральный виджет ===
        self.central_widget = QWidget(MainWindow)
        MainWindow.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout(self.central_widget)

        # === Боковое меню ===
        self.side_menu = QVBoxLayout()
        self.side_menu.setAlignment(Qt.AlignTop)

        self.btn_eva = QPushButton("EVA")
        self.btn_other1 = QPushButton("Другая страница 1")
        self.btn_other2 = QPushButton("Другая страница 2")

        for btn in (self.btn_eva, self.btn_other1, self.btn_other2):
            btn.setMinimumHeight(40)
            self.side_menu.addWidget(btn)

        self.main_layout.addLayout(self.side_menu)

        # === Основная область с вкладками ===
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        # === Заглушки для других страниц ===
        self.page_other1 = QLabel("Страница 1 пока пустая")
        self.page_other1.setAlignment(Qt.AlignCenter)
        self.stacked_widget.addWidget(self.page_other1)

        self.page_other2 = QLabel("Страница 2 пока пустая")
        self.page_other2.setAlignment(Qt.AlignCenter)
        self.stacked_widget.addWidget(self.page_other2)

        self.setup_styles()


    def setup_styles(self):
        font = QFont()
        font.setPointSize(10)
        self.central_widget.setFont(font)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setup_ui(self)
        self.setup_connections()
        self.load_icons()
        self.eva_counter = 0
        # === Progress bar default value ===
        self.index = 0

        self.copy_page = CopyRenamePage()
        self.ui.stacked_widget.addWidget(self.copy_page)

        self.edit_page = EditFilesPage()
        self.ui.stacked_widget.addWidget(self.edit_page)

        self.eva_page = EvaPage()
        self.ui.stacked_widget.addWidget(self.eva_page)

        self.files_to_rename: list[Path] = []

        self.files_for_replace = []

        self.file_service = FileService()

        self.edit_page.loadFilesRequested.connect(
            self.on_load_files_requested
        )
        self.edit_page.renameFilesRequested.connect(
            self.start_rename
        )
        self.edit_page.replaceCharRequested.connect(
            self.start_replace
        )
        self.edit_page.filterRequested.connect(
            self.filter_files
        )
        self.edit_page.removeFilesRequested.connect(
            self.remove_files
        )

    def setup_connections(self):
        # === Меню слева ===
        self.ui.btn_eva.clicked.connect(lambda: self.ui.stacked_widget.setCurrentWidget(self.eva_page))
        self.ui.btn_other1.clicked.connect(lambda: self.ui.stacked_widget.setCurrentWidget(self.copy_page))
        self.ui.btn_other2.clicked.connect(lambda: self.ui.stacked_widget.setCurrentWidget(self.edit_page))

    def on_load_files_requested(self, current_path: str | None):
        start_dir = current_path if current_path else str(Path.home())

        directory = QFileDialog.getExistingDirectory(
            self,
            "Select source directory",
            start_dir
        )

        if not directory:
            return

        # сохраняем состояние
        self.edit_page.current_directory = directory

        # обновляем UI
        self.edit_page.source_dir_input.setText(directory)

        # вызываем сервис
        try:
            file_paths = self.file_service.load_files(directory)
            self.files_to_rename = file_paths
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
            return

        self.edit_page.files_to_rename_list.clear()
        self.edit_page.renamed_files_list.clear()
        self.edit_page.editFilesPbar.setValue(0)
        # рендерим
        self.render_files(file_paths)

    def load_icons(self):
        self.check_icon = QIcon("resources/icons/check.svg")

    def render_files(self, file_paths: list[Path]):

        for file_path in file_paths:
            file_name = file_path.name

            # Проверка на дубликат по имени
            items = self.edit_page.files_to_rename_list.findItems(
                file_name, Qt.MatchExactly
            )
            if items:
                continue

            item = QListWidgetItem(file_name)
            item.setData(Qt.UserRole, file_path)  # ПОЛНЫЙ ПУТЬ
            self.edit_page.files_to_rename_list.addItem(item)

    def set_processing_state(self, processing: bool):
        self.edit_page.load_files_btn.setEnabled(not processing)
        self.edit_page.rename_files_btn.setEnabled(not processing)
        self.edit_page.replace_btn.setEnabled(not processing)
        self.edit_page.remove_files_btn.setEnabled(not processing)

    def start_rename(self):
        self.set_processing_state(True)
        self.thread = QThread()
        self.worker = RenameWorker(self.files_to_rename, self.file_service)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.on_rename_progress)
        self.worker.finished.connect(self.on_rename_finished)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def move_renamed_file(self, file_result: RenameFileResult):
        left_list = self.edit_page.files_to_rename_list
        for row in range(left_list.count()):
            item = left_list.item(row)
            if item.data(Qt.UserRole) == file_result.old_path:
                moved_item = left_list.takeItem(row)
                moved_item.setText(file_result.new_path.name)
                moved_item.setData(Qt.UserRole, file_result.new_path)
                moved_item.setIcon(self.check_icon)
                self.edit_page.renamed_files_list.addItem(moved_item)
                self.edit_page.renamed_files_list.scrollToBottom()
                break

    def on_rename_progress(self, current, total, file_result):
        self.edit_page.editFilesPbar.setMaximum(total)
        self.edit_page.editFilesPbar.setValue(current)

        self.move_renamed_file(file_result)

    def on_rename_finished(self, result):
        summary = []

        if result.renamed_files:
            summary.append(f"{result.renamed_files} filenames renamed.")
        if result.renamed_layers:
            summary.append(f'{result.renamed_layers} "nadpis" layers updated.')

        QMessageBox.information(self, "Done", "\n".join(summary) or "No changes made.")
        self.files_to_rename.clear()
        self.set_processing_state(False)

    def filter_files(self, find_text: str):
        left_list = self.edit_page.files_to_rename_list
        for row in range(left_list.count()):
            item = left_list.item(row)
            if find_text not in item.text():
                left_list.setRowHidden(row, True)
            else:
                left_list.setRowHidden(row, False)


    def start_replace(self, find_text: str, replace_text: str):
        self.files_for_replace.clear()
        left_list = self.edit_page.files_to_rename_list
        for row in range(left_list.count()):
            if not left_list.isRowHidden(row):
                self.files_for_replace.append(left_list.item(row).data(Qt.UserRole))

        self.set_processing_state(True)
        self.thread = QThread()
        self.worker = ReplaceWorker(self.files_for_replace, find_text, replace_text, self.file_service)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.on_replace_progress)
        self.worker.finished.connect(self.on_replace_finished)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_replace_progress(self, current, total, file_result):
        self.edit_page.editFilesPbar.setMaximum(total)
        self.edit_page.editFilesPbar.setValue(current)

        self.move_renamed_file(file_result)

    def on_replace_finished(self, result):
        summary = []

        if result.renamed:
            summary.append(f"{result.renamed} files renamed.")
        if result.skipped:
            summary.append(f"Skipped {len(result.skipped)} files:\n" + "\n".join(result.skipped))
        if result.failed:
            summary.append(f"Failed {len(result.failed)} files:\n" + "\n".join(result.failed))
        summary = "\n\n".join(summary) if summary else "No changes made."
        QMessageBox.information(self, "Success", summary)

        self.set_processing_state(False)

    def remove_files(self):
        self.edit_page.files_to_rename_list.clear()
        self.edit_page.renamed_files_list.clear()
        self.files_to_rename.clear()
        self.files_for_replace.clear()
        self.edit_page.editFilesPbar.setValue(0)
        self.edit_page.find_input.clear()
        self.edit_page.replace_input.clear()






    def show_replaced_files(self, find_text: str, replace_text: str):
        if not find_text:
            QMessageBox.warning(self, "Error", "Find field can't be empty")
            return

        if find_text == replace_text:
            QMessageBox.warning(self, "Error", "Find and Replace are the same — nothing to do.")
            return



    #     self.ui.add_btn.clicked.connect(self.on_add)
    #     self.ui.clear_fields_btn.clicked.connect(self.on_clear_fields)
    #     self.ui.add_stopers_btn.clicked.connect(self.on_add_stopers)
    #
    #     # === Кнопки на странице EVA ===
    #     # Здесь можно будет добавить кнопки для EVA, если нужно
    #     # Например, логика create/save/clear и т.д.
    #     # self.ui.create_eva_btn.clicked.connect(self.on_create_eva)
    #     # ...
    # def on_add(self):
    #     name = self.ui.eva_fields["name"].text().strip()
    #     articles_text = self.ui.eva_fields["article_numbers"].text().strip()
    #
    #     if not name:
    #         print("Введите имя EVA")
    #         return
    #
    #     if not articles_text:
    #         print("Введите хотя бы один артикул")
    #         return
    #
    #     # Разделяем артикулы по запятой и удаляем лишние пробелы
    #     articles = [a.strip() for a in articles_text.split(",") if a.strip()]
    #
    #     # Увеличиваем счетчик EVA
    #     self.eva_counter += 1
    #
    #     # Формируем текст для QLabel
    #     label_text = f"{self.eva_counter}. {name}: " + ", ".join(articles)
    #
    #     # Создаём QLabel и добавляем в layout prepared_eva_layout
    #     label = QLabel(label_text)
    #     label.setWordWrap(True)  # если артикулы длинные
    #     row = self.ui.prepared_eva_layout.rowCount()  # следующая свободная строка
    #     self.ui.prepared_eva_layout.addWidget(label, row, 0)
    #
    #     # Очистка полей после добавления
    #     self.on_clear_fields()
    #
    # def on_clear_fields(self):
    #     for field in self.ui.eva_fields.values():
    #         field.clear()
    #
    # def on_add_stopers(self):
    #     self.dialog = EvaDialog(self)
    #     self.dialog.exec()
    #
    # def log(self, message: str):
    #     """Метод для логирования в одно место."""
    #     self.ui.log_output.appendPlainText(message)