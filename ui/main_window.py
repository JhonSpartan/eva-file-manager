from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLineEdit,
    QStackedWidget, QMessageBox, QFileDialog, QListWidgetItem, QTreeWidgetItem, QAbstractItemView, QDialog
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt, QTimer, QThread

import pathlib
from pathlib import Path

from database.repositories.stopper_repository import StopperRepository
from database.repositories.template_repository import TemplateRepository
from models.results import RenameFileResult
from services.art_copy_planner import ArtCopyPlanner
from services.art_copy_service import ArtCopyService
from services.art_copy_validator import ArtCopyValidator
from services.stopper_service import StopperService
from services.template_service import TemplateService
from ui.dialogs.copy_rule_dialog import CopyRuleDialog
from ui.dialogs.template_dialog import TemplateDialog
from ui.dialogs.stopper_dialog import StopperDialog
from ui.pages.copy_art_page import CopyArtsPage
from ui.pages.database_page import DatabasePage
from ui.pages.eva_page import EvaPage
from ui.pages.edit_files_page import EditFilesPage

from services.file_service import FileService
from services.art_service import ArtService
from workers.art_copy_worker import ArtCopyWorker
from workers.rename_worker import RenameWorker
from workers.replace_worker import ReplaceWorker

from database.database import Database
from database.repositories.copy_rule_repository import CopyRuleRepository
from services.copy_rules import CopyRuleService

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
        self.btn_other3 = QPushButton("Другая страница 3")

        for btn in (self.btn_eva, self.btn_other1, self.btn_other2, self.btn_other3):
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

        self.copy_page = CopyArtsPage()
        self.ui.stacked_widget.addWidget(self.copy_page)

        self.edit_page = EditFilesPage()
        self.ui.stacked_widget.addWidget(self.edit_page)

        self.eva_page = EvaPage()
        self.ui.stacked_widget.addWidget(self.eva_page)

        self.files_to_rename: list[Path] = []

        self.files_for_replace: list[Path] = []

        self.file_service = FileService()

        db_path = Path.home() / ".eva" / "eva.db"
        db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.database = Database(db_path)
        self.database.initialize()

        self.copy_rule_repository = CopyRuleRepository(self.database)
        self.copy_rule_service = CopyRuleService(self.copy_rule_repository)
        self.template_repository = TemplateRepository(self.database)
        self.template_service = TemplateService(self.template_repository)
        self.stopper_repository = StopperRepository(self.database)
        self.stopper_service = StopperService(self.stopper_repository)

        self.database_page = DatabasePage()
        self.ui.stacked_widget.addWidget(self.database_page)
        self.load_template_database_table()
        self.load_stopper_database_table()
        self.load_copy_rules_database_table()

        self.art_copy_validator = ArtCopyValidator(self.copy_rule_service)
        self.art_copy_planner = ArtCopyPlanner(self.copy_rule_service)

        self.art_service = ArtService()
        self.art_copy_service = ArtCopyService()

        self.load_templates_to_eva_page()


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
        self.copy_page.loadArtsRequested.connect(
            self.on_load_arts_requested
        )
        self.copy_page.copyAndRenameRequested.connect(
            self.start_copy_art
        )
        self.eva_page.addEvaRequested.connect(
            self.add_prepared_eva
        )
        self.eva_page.clearPreparedEvaRequested.connect(
            self.clear_prepared_eva
        )
        self.database_page.templatesTable.addRequested.connect(
            self.on_add_template
        )
        self.database_page.templatesTable.editRequested.connect(
            self.on_edit_template
        )
        self.database_page.templatesTable.deleteRequested.connect(
            self.on_delete_templates
        )
        self.database_page.stoppersTable.addRequested.connect(
            self.on_add_stopper
        )
        self.database_page.stoppersTable.editRequested.connect(
            self.on_edit_stopper
        )
        self.database_page.stoppersTable.deleteRequested.connect(
            self.on_delete_stoppers
        )
        self.database_page.copyRulesTable.addRequested.connect(
            self.on_add_copy_rule
        )
        self.database_page.copyRulesTable.editRequested.connect(
            self.on_edit_copy_rule
        )
        self.database_page.copyRulesTable.deleteRequested.connect(
            self.on_delete_copy_rules
        )



    def setup_connections(self):
        # === Меню слева ===
        self.ui.btn_eva.clicked.connect(lambda: self.ui.stacked_widget.setCurrentWidget(self.eva_page))
        self.ui.btn_other1.clicked.connect(lambda: self.ui.stacked_widget.setCurrentWidget(self.copy_page))
        self.ui.btn_other2.clicked.connect(lambda: self.ui.stacked_widget.setCurrentWidget(self.edit_page))
        self.ui.btn_other3.clicked.connect(lambda: self.ui.stacked_widget.setCurrentWidget(self.database_page))


    def load_icons(self):
        self.check_icon = QIcon("resources/icons/check.svg")

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

    def render_files(self, file_paths: list[Path]):

        for file_path in file_paths:
            file_name = file_path.name

            item = QListWidgetItem(file_name)
            item.setData(Qt.UserRole, file_path)  # ПОЛНЫЙ ПУТЬ
            self.edit_page.files_to_rename_list.addItem(item)

    def on_load_arts_requested(self, current_path: str | None):
        start_dir = current_path if current_path else str(Path.home())

        directory = QFileDialog.getExistingDirectory(
            self,
            "Select source directory",
            start_dir
        )

        if not directory:
            return

        # сохраняем состояние
        self.copy_page.current_directory = directory

        # обновляем UI
        self.copy_page.source_dir_input.setText(directory)

        # вызываем сервис
        try:
            art_paths = self.art_service.load_arts(directory)
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
            return

        # self.copy_page.srcArtsTree.clear_tree()
        # self.copy_page.dstArtsTree.clear_tree()
        self.copy_page.copyAndRenamePbar.setValue(0)

        self.copy_page.artsTree.load_arts(art_paths)

        # self.copy_page.artsTree.clear()

        # рендерим
        # self.render_arts(art_paths)

    # def render_arts(self, art_paths: list[Path]):
    #     self.copy_page.artsTree.clear_tree()
    #
    #     for art_path in art_paths:
    #         self.copy_page.artsTree.add_art(art_path)
    #         art_name = art_path.name
    #
    #         root_item = QTreeWidgetItem([art_name])
    #         root_item.setData(0, Qt.UserRole, art_path)  # ПОЛНЫЙ ПУТЬ
    #         self.copy_page.artsTree.addTopLevelItem(root_item)

    def set_processing_state(self, processing: bool):
        self.edit_page.load_files_btn.setEnabled(not processing)
        self.edit_page.rename_files_btn.setEnabled(not processing)
        self.edit_page.replace_btn.setEnabled(not processing)
        self.edit_page.remove_files_btn.setEnabled(not processing)

    def set_copy_processing_state(self, processing: bool):

        self.copy_page.load_arts_btn.setEnabled(
            not processing
        )

        self.copy_page.copyAndRenameButton.setEnabled(
            not processing
        )

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
            path = item.data(Qt.UserRole)
            if find_text not in path.stem:
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

    def start_copy_art(self):
        five_d_mode = self.copy_page.fiveDModeCheckbox.isChecked()

        source_selections = (
            self.copy_page.srcArtsTree.get_art_selections()
        )

        destination_selections = (
            self.copy_page.dstArtsTree.get_art_selections()
        )

        source = (
            source_selections[0]
            if source_selections
            else None
        )

        validation = self.art_copy_validator.validate(
            source,
            destination_selections,
            five_d_mode=five_d_mode,
        )

        # 1. Блокирующие ошибки
        if validation.blocking_issues:
            message = "\n".join(
                issue.message
                for issue in validation.blocking_issues
            )

            QMessageBox.warning(
                self,
                "Copy validation",
                message,
            )
            return

        # После blocking validation source уже гарантированно существует
        if source is None:
            return

        # 2. Отсутствующие ID
        if validation.create_id_issues:
            message = "\n".join(
                issue.message
                for issue in validation.create_id_issues
            )

            answer = QMessageBox.question(
                self,
                "Create missing IDs",
                message + "\n\nCreate missing IDs and continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if answer != QMessageBox.Yes:
                return

        # 3. Копирование без замены
        if validation.confirmation_issues:
            message = "\n".join(
                issue.message
                for issue in validation.confirmation_issues
            )

            answer = QMessageBox.question(
                self,
                "Confirm copy",
                message + "\n\nContinue without replacing existing files?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if answer != QMessageBox.Yes:
                return

        # 4. Строим готовый план
        plan = self.art_copy_planner.build(
            source,
            destination_selections,
            five_d_mode=five_d_mode,
        )

        if plan.is_empty:
            QMessageBox.information(
                self,
                "Nothing to do",
                "No operations selected."
            )
            return

        self.current_copy_plan = plan

        # 5. Дальше остаётся твоя существующая QThread-обвязка
        self.set_copy_processing_state(True)

        self.thread = QThread()

        self.worker = ArtCopyWorker(
            plan,
            self.art_copy_service,
            self.file_service,
        )

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(
            self.worker.run
        )

        self.worker.progress.connect(
            self.on_copy_progress
        )

        self.worker.finished.connect(
            self.on_copy_finished
        )

        self.worker.finished.connect(
            self.thread.quit
        )

        self.worker.finished.connect(
            self.worker.deleteLater
        )

        self.thread.finished.connect(
            self.thread.deleteLater
        )

        self.thread.start()

    def on_copy_progress(self, current, total):
        self.copy_page.copyAndRenamePbar.setMaximum(total)
        self.copy_page.copyAndRenamePbar.setValue(current)

    def on_copy_finished(self, result):
        self.set_copy_processing_state(False)

        if isinstance(result, Exception):
            QMessageBox.critical(
                self,
                "Copy error",
                str(result),
            )
            self.current_copy_plan = None
            return

        if self.current_copy_plan is not None:
            for destination_plan in self.current_copy_plan.destinations:
                self.copy_page.dstArtsTree.refresh_art(
                    destination_plan.destination_art
                )

        self.current_copy_plan = None

        summary = []

        if result.created_ids:
            summary.append(
                f"{result.created_ids} IDs created."
            )

        if result.deleted_files:
            summary.append(
                f"{result.deleted_files} files deleted."
            )

        if result.copied_files:
            summary.append(
                f"{result.copied_files} files copied."
            )

        if result.renamed_files:
            summary.append(
                f"{result.renamed_files} filenames renamed."
            )

        if result.renamed_layers:
            summary.append(
                f'{result.renamed_layers} "nadpis" layers updated.'
            )

        if result.errors:
            summary.append(
                f"{len(result.errors)} errors."
            )

        QMessageBox.information(
            self,
            "Done",
            "\n".join(summary) or "No changes made.",
        )

    def load_template_database_table(self):
        records = (
            self.template_repository.get_all()
        )

        table_records = []

        for record in records:
            table_records.append(
                {
                    "id": record.id,
                    "values": {
                        "folder_id": record.folder_id,
                        "template_name": record.template_name,
                    },
                }
            )

        self.database_page.templatesTable.render_records(
            table_records
        )

    def on_add_template(self):
        dialog = TemplateDialog(parent=self)

        if dialog.exec() != QDialog.Accepted:
            return

        folder_id, template_name = dialog.get_data()

        self.template_repository.add(
            folder_id,
            template_name,
        )

        self.load_template_database_table()

    def on_edit_template(self, record_id: int):
        record = self.template_repository.get_by_id(
            record_id
        )

        if record is None:
            return

        dialog = TemplateDialog(
            folder_id=record.folder_id,
            template_name=record.template_name,
            parent=self,
        )

        if dialog.exec() != QDialog.Accepted:
            return

        folder_id, template_name = dialog.get_data()

        self.template_repository.update(
            record_id,
            folder_id,
            template_name,
        )

        self.load_template_database_table()

    def on_delete_templates(
            self,
            record_ids: list[int],
    ):
        if not record_ids:
            return

        answer = QMessageBox.question(
            self,
            "Delete templates",
            f"Delete {len(record_ids)} selected records?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if answer != QMessageBox.Yes:
            return

        self.template_repository.delete_by_ids(
            record_ids
        )

        self.load_template_database_table()


    def load_stopper_database_table(self):
        records = (
            self.stopper_repository.get_all()
        )

        table_records = []

        for record in records:
            table_records.append(
                {
                    "id": record.id,
                    "values": {
                        "diameter": record.diameter,
                        "stopper_name": record.stopper_name,
                    },
                }
            )

        self.database_page.stoppersTable.render_records(
            table_records
        )

    def on_add_stopper(self):
        dialog = StopperDialog(parent=self)

        if dialog.exec() != QDialog.Accepted:
            return

        diameter, stopper_name = dialog.get_data()

        self.stopper_repository.add(
            diameter,
            stopper_name,
        )

        self.load_stopper_database_table()

    def on_edit_stopper(self, record_id: int):
        record = self.stopper_repository.get_by_id(
            record_id
        )

        if record is None:
            return

        dialog = StopperDialog(
            diameter=record.diameter,
            stopper_name=record.stopper_name,
            parent=self,
        )

        if dialog.exec() != QDialog.Accepted:
            return

        diameter, stopper_name = dialog.get_data()

        self.stopper_repository.update(
            record_id,
            diameter,
            stopper_name,
        )

        self.load_stopper_database_table()

    def on_delete_stoppers(
            self,
            record_ids: list[int],
    ):
        if not record_ids:
            return

        answer = QMessageBox.question(
            self,
            "Delete stoppers",
            f"Delete {len(record_ids)} selected records?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if answer != QMessageBox.Yes:
            return

        self.stopper_repository.delete_by_ids(
            record_ids
        )

        self.load_stopper_database_table()

    def load_copy_rules_database_table(self):
        records = (
            self.copy_rule_repository.get_all()
        )

        table_records = []

        for record in records:
            table_records.append(
                {
                    "id": record.id,
                    "values": {
                        "mode": record.mode,
                        "from_id": record.from_id,
                        "to_id": record.to_id,
                    },
                }
            )

        self.database_page.copyRulesTable.render_records(
            table_records
        )

    def on_add_copy_rule(self):
        dialog = CopyRuleDialog(parent=self)

        if dialog.exec() != QDialog.Accepted:
            return

        mode, from_id, to_id = dialog.get_data()

        self.copy_rule_repository.add(
            mode,
            from_id,
            to_id,
        )

        self.load_copy_rules_database_table()

    def on_edit_copy_rule(
            self,
            record_id: int,
    ):
        record = self.copy_rule_repository.get_by_id(
            record_id
        )

        if record is None:
            return

        dialog = CopyRuleDialog(
            mode=record.mode,
            from_id=record.from_id,
            to_id=record.to_id,
            parent=self,
        )

        if dialog.exec() != QDialog.Accepted:
            return

        mode, from_id, to_id = dialog.get_data()

        self.copy_rule_repository.update(
            record_id,
            mode,
            from_id,
            to_id,
        )

        self.load_copy_rules_database_table()

    def on_delete_copy_rules(
            self,
            record_ids: list[int],
    ):
        if not record_ids:
            return

        answer = QMessageBox.question(
            self,
            "Delete copy rules",
            f"Delete {len(record_ids)} selected records?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if answer != QMessageBox.Yes:
            return

        self.copy_rule_repository.delete_by_ids(
            record_ids
        )

        self.load_copy_rules_database_table()

    def load_templates_to_eva_page(self):
        templates = (
            self.template_service.get_grouped_templates()
        )

        self.eva_page.render_templates(
            templates
        )

    def add_prepared_eva(
            self,
            eva_name: str,
            articles: list[str],
    ):
        articles_text = ", ".join(articles)

        label = QLabel(
            f"{eva_name} ({articles_text})"
        )

        self.eva_page.prepared_eva_layout.insertWidget(
            self.eva_page.prepared_eva_layout.count() - 1,
            label,
        )

    def clear_prepared_eva(self):
        while self.eva_page.prepared_eva_layout.count() > 1:
            item = self.eva_page.prepared_eva_layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()