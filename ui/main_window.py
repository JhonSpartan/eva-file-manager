from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLineEdit,
    QStackedWidget, QMessageBox, QFileDialog, QListWidgetItem, QTreeWidgetItem, QAbstractItemView, QDialog
)
from PySide6.QtGui import QFont, QIcon, QDesktopServices
from PySide6.QtCore import Qt, QUrl, QThread

import pathlib
from pathlib import Path

from database.repositories.path_repository import PathRepository
from database.repositories.stopper_repository import StopperRepository
from database.repositories.template_repository import TemplateRepository
from models.results import RenameFileResult
from services.art_copy_planner import ArtCopyPlanner
from services.art_copy_service import ArtCopyService
from services.art_copy_validator import ArtCopyValidator
from services.eva_service import EvaService
from services.path_service import PathService
from services.stopper_service import StopperService
from services.template_service import TemplateService
from services.export_planner import ExportPlanner
from ui.dialogs.copy_rule_dialog import CopyRuleDialog
from ui.dialogs.custom_template_dialog import CustomTemplateDialog
from ui.dialogs.delete_dialog import DeleteDialog
from ui.dialogs.path_dialog import PathDialog
from ui.dialogs.stopper_selection_dialog import StopperSelectionDialog
from ui.dialogs.template_dialog import TemplateDialog
from ui.dialogs.stopper_dialog import StopperDialog
from ui.dialogs.replace_dialog import ReplaceDialog
from ui.dialogs.export_dialog import ExportDialog
from ui.dialogs.move_to_id_dialog import MoveToIdDialog
from ui.dialogs.stopper_actions_dialog import (StopperActionsDialog)
from ui.pages.copy_art_page import CopyArtsPage
from ui.pages.database_page import DatabasePage
from ui.pages.eva_page import EvaPage
from ui.pages.edit_files_page import EditFilesPage

from services.file_service import FileService
from services.art_service import ArtService
from workers.art_copy_worker import ArtCopyWorker
from workers.rename_worker import RenameWorker
from workers.replace_worker import ReplaceWorker
from workers.eva_generation_worker import EvaGenerationWorker
from workers.export_worker import ExportWorker
from workers.delete_worker import DeleteWorker
from workers.move_to_id_worker import MoveToIdWorker
from workers.stopper_worker import StopperWorker
from workers.sync_worker import SyncWorker


from database.database import Database
from database.cloud_database import CloudDatabase

from database.repositories.cloud_sync_repository import CloudSyncRepository
from services.sync_service import SyncService
from database.repositories.copy_rule_repository import CopyRuleRepository
from services.copy_rules import CopyRuleService
from models.eva_models import PreparedEva, PreviewTemplate
from models.file_action_models import ReplaceMode
from models.copy_models import ValidationIssueType
from services.eva_generation_planner import (EvaGenerationPlanner)
from services.replace_planner import ReplacePlanner
from services.delete_planner import DeletePlanner
from services.move_to_id_planner import MoveToIdPlanner
from services.stopper_detector import StopperDetector
from services.stopper_editor import StopperEditor
from services.stopper_validator import StopperValidator


class Ui_MainWindow:
    def setup_ui(self, MainWindow):
        MainWindow.setWindowTitle("EVA Configurator")
        MainWindow.resize(950, 700)

        # === Центральный виджет ===
        self.central_widget = QWidget(MainWindow)
        MainWindow.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout(self.central_widget)

        # === Боковое меню ===
        self.side_menu_widget = QWidget()
        self.side_menu_widget.setObjectName(
            "sideMenu"
        )

        self.side_menu = QVBoxLayout(
            self.side_menu_widget
        )
        self.side_menu.setAlignment(
            Qt.AlignTop
        )

        self.side_menu.setContentsMargins(
            10, 12, 10, 12
        )

        self.side_menu.setSpacing(
            8
        )

        self.btn_eva = QPushButton("EVA")
        self.btn_other1 = QPushButton("Другая страница 1")
        self.btn_other2 = QPushButton("Другая страница 2")
        self.btn_other3 = QPushButton("Другая страница 3")

        for btn in (
                self.btn_eva,
                self.btn_other1,
                self.btn_other2,
                self.btn_other3,
        ):
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.setMinimumHeight(40)
            self.side_menu.addWidget(btn)

        self.side_menu.addStretch()

        self.btn_exit = QPushButton("Выход")
        self.btn_exit.setMinimumHeight(40)

        self.side_menu.addWidget(
            self.btn_exit
        )

        self.main_layout.addWidget(
            self.side_menu_widget
        )

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

        self.sync_thread: QThread | None = None
        self.sync_worker: SyncWorker | None = None

        self.last_export_path: Path | None = None
        self.pending_export_path: Path | None = None

        self.ui = Ui_MainWindow()
        self.ui.setup_ui(self)
        self.load_icons()
        self.eva_counter = 0
        # === Progress bar default value ===
        self.index = 0

        self.eva_page = EvaPage()
        self.ui.stacked_widget.addWidget(self.eva_page)

        self.copy_page = CopyArtsPage()
        self.ui.stacked_widget.addWidget(self.copy_page)

        self.edit_page = EditFilesPage()
        self.ui.stacked_widget.addWidget(self.edit_page)

        self.database_page = DatabasePage()
        self.ui.stacked_widget.addWidget(self.database_page)

        self.ui.stacked_widget.setCurrentWidget(
            self.eva_page
        )
        self.ui.btn_eva.setChecked(True)

        self.five_d_mode = False

        self.prepared_evas: list[PreparedEva] = []

        self.files_to_rename: list[Path] = []

        self.files_for_replace: list[Path] = []

        self.file_service = FileService()

        self.eva_service = EvaService()

        db_path = Path.home() / ".eva" / "eva.db"
        db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.database = Database(db_path)
        self.database.initialize()

        self.cloud_database = CloudDatabase()

        self.cloud_sync_repository: CloudSyncRepository | None = None
        self.sync_service: SyncService | None = None

        self.copy_rule_repository = CopyRuleRepository(self.database)
        self.copy_rule_service = CopyRuleService(self.copy_rule_repository)
        self.template_repository = TemplateRepository(self.database)
        self.template_service = TemplateService(self.template_repository)
        self.session_templates = (self.template_service.get_session_templates())
        self.stopper_repository = StopperRepository(self.database)
        self.stopper_service = StopperService(self.stopper_repository)
        self.path_repository = PathRepository(self.database)
        self.path_service = PathService(self.path_repository)
        self.eva_generation_planner = (EvaGenerationPlanner(self.copy_rule_service))
        self.replace_planner = ReplacePlanner()
        self.export_planner = ExportPlanner()
        self.delete_planner = DeletePlanner()
        self.move_to_id_planner = MoveToIdPlanner()
        self.stopper_detector = StopperDetector()
        self.stopper_validator = StopperValidator()
        self.stopper_editor = StopperEditor(
            detector=self.stopper_detector,
            validator=self.stopper_validator,
        )

        self.load_template_database_table()
        self.load_stopper_database_table()
        self.load_copy_rules_database_table()

        self.setup_connections()

        self.art_copy_validator = ArtCopyValidator(self.copy_rule_service)
        self.art_copy_planner = ArtCopyPlanner(self.copy_rule_service)

        self.art_service = ArtService()
        self.art_copy_service = ArtCopyService()

        self.load_templates_to_eva_page()

        self.refresh_eva_paths()
        self.refresh_files_paths()

        last_output_path = (self.path_service.get_eva_last_output_path())

        self.eva_page.open_last_output_btn.setEnabled(last_output_path is not None and last_output_path.exists())

        self.edit_page.loadFilesRequested.connect(
            self.on_load_files_requested
        )
        self.edit_page.renameFilesRequested.connect(
            self.start_rename
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
        self.eva_page.addStoppersRequested.connect(
            self.on_add_stoppers_requested
        )
        self.eva_page.customTemplateRequested.connect(
            self.on_custom_template_requested
        )
        self.eva_page.templateSelectionChanged.connect(
            self.on_template_selection_changed
        )
        self.eva_page.clearTemplateSelectionRequested.connect(
            self.on_clear_template_selection
        )
        self.eva_page.fiveDModeChanged.connect(
            self.on_five_d_mode_changed
        )
        self.eva_page.createStructureRequested.connect(
            self.on_create_structure_requested
        )
        self.database_page.editEvaDefaultPathRequested.connect(
            self.edit_eva_default_output_path
        )
        self.eva_page.openLastOutputRequested.connect(
            self.open_eva_last_output
        )
        self.database_page.editFilesDefaultPathRequested.connect(
            self.edit_files_default_output_path
        )
        self.edit_page.moveToIdRequested.connect(
            self.on_move_to_id_requested
        )

        self.database_page.openFilesLastOutputRequested.connect(
            self.open_files_last_output
        )
        self.database_page.openEvaLastOutputRequested.connect(
            self.open_eva_last_output
        )
        self.edit_page.replaceRequested.connect(
            self.on_replace_requested
        )
        self.edit_page.stoppersRequested.connect(
            self.on_stoppers_clicked
        )
        self.database_page.syncRequested.connect(
            self.start_cloud_sync
        )
        self.edit_page.returnProcessedRequested.connect(
            self.return_processed_files
        )
        self.edit_page.copySourceRequested.connect(
            self.on_export_source_requested
        )
        self.edit_page.copyProcessedRequested.connect(
            self.on_export_processed_requested
        )
        self.edit_page.deleteSourceRequested.connect(
            self.on_delete_source_requested
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

        self.start_cloud_sync()

    def show_page(
            self,
            page,
            button,
    ) -> None:
        self.ui.stacked_widget.setCurrentWidget(
            page
        )

        button.setChecked(
            True
        )

    def setup_connections(self):
        # === Меню слева ===
        self.ui.btn_eva.clicked.connect(
            lambda: self.show_page(
                self.eva_page,
                self.ui.btn_eva,
            )
        )

        self.ui.btn_other1.clicked.connect(
            lambda: self.show_page(
                self.copy_page,
                self.ui.btn_other1,
            )
        )

        self.ui.btn_other2.clicked.connect(
            lambda: self.show_page(
                self.edit_page,
                self.ui.btn_other2,
            )
        )

        self.ui.btn_other3.clicked.connect(
            lambda: self.show_page(
                self.database_page,
                self.ui.btn_other3,
            )
        )

        self.ui.btn_exit.clicked.connect(
            self.close
        )

        self.edit_page.openExportFolderRequested.connect(
            self.on_open_export_folder_requested
        )

        self.ui.btn_eva.setChecked(
            True
        )


    def load_icons(self):
        self.check_icon = QIcon("resources/icons/check.svg")

    def on_cloud_sync_thread_finished(self) -> None:
        self.sync_thread = None
        self.sync_worker = None

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
        self.filter_files(
            self.edit_page.find_input.text()
        )

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

        self.copy_page.copyAndRenamePbar.setValue(0)

        self.copy_page.artsTree.load_arts(art_paths)

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
        self.rename_worker  = RenameWorker(self.files_to_rename, self.file_service)

        self.rename_worker.moveToThread(self.thread)

        self.thread.started.connect(self.rename_worker.run)
        self.rename_worker.progress.connect(self.on_rename_progress)
        self.rename_worker.finished.connect(self.on_rename_finished)
        self.rename_worker.failed.connect(self.on_rename_failed)

        self.rename_worker.finished.connect(self.thread.quit)
        self.rename_worker.finished.connect(self.rename_worker.deleteLater)
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

    def on_rename_failed(
            self,
            error: str,
    ) -> None:
        QMessageBox.critical(
            self,
            "Rename failed",
            error,
        )

        self.files_to_rename.clear()
        self.set_processing_state(False)

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

    def on_replace_requested(
            self,
            find_text: str,
    ) -> None:

        dialog = ReplaceDialog(
            find_text=find_text,
            parent=self,
        )

        if dialog.exec() != QDialog.Accepted:
            return

        replace_text = dialog.get_replace_text()

        mode = (
            ReplaceMode.CREATE_COPY
            if dialog.create_new_files()
            else ReplaceMode.MODIFY_EXISTING
        )

        files = []

        left_list = (
            self.edit_page.files_to_rename_list
        )

        for row in range(left_list.count()):
            if left_list.isRowHidden(row):
                continue

            item = left_list.item(row)
            file_path = item.data(Qt.UserRole)

            files.append(file_path)

        plan = self.replace_planner.build_plan(
            files=files,
            find_text=find_text,
            replace_text=replace_text,
            mode=mode,
        )

        if plan.conflicts:
            conflict_names = "\n".join(
                path.name
                for path in plan.conflicts
            )

            QMessageBox.warning(
                self,
                "Replace conflict",
                (
                    "Некоторые целевые файлы уже существуют:\n\n"
                    f"{conflict_names}\n\n"
                    "Операция отменена."
                ),
            )
            return

        if plan.is_empty:
            QMessageBox.information(
                self,
                "Nothing to do",
                "Нет файлов для обработки.",
            )
            return

        self.current_replace_plan = plan

        self.set_processing_state(True)

        self.replace_thread = QThread()

        self.replace_worker = ReplaceWorker(
            plan
        )

        self.replace_worker.moveToThread(
            self.replace_thread
        )

        self.replace_thread.started.connect(
            self.replace_worker.run
        )

        self.replace_worker.progress.connect(
            self.on_replace_plan_progress
        )

        self.replace_worker.finished.connect(
            self.on_replace_plan_finished
        )

        self.replace_worker.errorOccurred.connect(
            self.on_replace_plan_error
        )

        self.replace_worker.finished.connect(
            self.replace_thread.quit
        )

        self.replace_worker.errorOccurred.connect(
            self.replace_thread.quit
        )

        self.replace_worker.finished.connect(
            self.replace_worker.deleteLater
        )

        self.replace_worker.errorOccurred.connect(
            self.replace_worker.deleteLater
        )

        self.replace_thread.finished.connect(
            self.replace_thread.deleteLater
        )

        self.replace_thread.start()

    def on_replace_plan_progress(
            self,
            current: int,
            total: int,
            operation,
    ) -> None:

        self.edit_page.editFilesPbar.setMaximum(
            total
        )

        self.edit_page.editFilesPbar.setValue(
            current
        )

        if self.current_replace_plan.mode == ReplaceMode.MODIFY_EXISTING:
            self.move_modified_replace_file(
                operation
            )

        elif self.current_replace_plan.mode == ReplaceMode.CREATE_COPY:
            self.add_created_replace_file(
                operation
            )

    def move_modified_replace_file(
            self,
            operation,
    ) -> None:

        left_list = (
            self.edit_page.files_to_rename_list
        )

        right_list = (
            self.edit_page.renamed_files_list
        )

        for row in range(left_list.count()):
            item = left_list.item(row)

            if (
                    item.data(Qt.UserRole)
                    != operation.source_file
            ):
                continue

            moved_item = left_list.takeItem(row)

            moved_item.setText(
                operation.destination_file.name
            )

            moved_item.setData(
                Qt.UserRole,
                operation.destination_file,
            )

            moved_item.setIcon(
                self.check_icon
            )

            right_list.addItem(
                moved_item
            )

            right_list.scrollToBottom()

            break

    def add_created_replace_file(
            self,
            operation,
    ) -> None:

        item = QListWidgetItem(
            operation.destination_file.name
        )

        item.setData(
            Qt.UserRole,
            operation.destination_file,
        )

        item.setIcon(
            self.check_icon
        )

        self.edit_page.renamed_files_list.addItem(
            item
        )

        self.edit_page.renamed_files_list.scrollToBottom()

    def on_replace_plan_finished(
            self,
            processed_count: int,
    ) -> None:

        self.sync_files_to_rename_from_ui()

        self.set_processing_state(False)

        QMessageBox.information(
            self,
            "Done",
            f"Обработано файлов: {processed_count}",
        )

    def on_replace_plan_error(
            self,
            message: str,
    ) -> None:

        self.set_processing_state(False)

        QMessageBox.critical(
            self,
            "Replace error",
            message,
        )


    def start_replace(self, find_text: str, replace_text: str):
        self.files_for_replace.clear()
        left_list = self.edit_page.files_to_rename_list
        for row in range(left_list.count()):
            if not left_list.isRowHidden(row):
                self.files_for_replace.append(left_list.item(row).data(Qt.UserRole))

        self.set_processing_state(True)
        self.thread = QThread()
        self.replace_worker = ReplaceWorker(self.files_for_replace, find_text, replace_text, self.file_service)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.replace_worker.progress.connect(self.on_replace_progress)
        self.replace_worker.finished.connect(self.on_replace_finished)

        self.replace_worker.finished.connect(self.thread.quit)
        self.replace_worker.finished.connect(self.worker.deleteLater)
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

    def sync_files_to_rename_from_ui(self) -> None:

        self.files_to_rename = []

        left_list = (
            self.edit_page.files_to_rename_list
        )

        for row in range(left_list.count()):
            item = left_list.item(row)

            self.files_to_rename.append(
                item.data(Qt.UserRole)
            )

    def on_stoppers_clicked(self) -> None:
        find_text = (
            self.edit_page
            .find_input
            .text()
            .strip()
        )

        # Проверяем Find text
        if not find_text:
            QMessageBox.warning(
                self,
                "Stoppers",
                "Find text is empty.",
            )
            return

        # Получаем имя стоппера из Find text:
        # "_av" -> "av"
        # "AV"  -> "av"
        stopper_name = find_text.lower()

        if stopper_name.startswith("_"):
            stopper_name = stopper_name[1:]

        if not stopper_name:
            QMessageBox.warning(
                self,
                "Stoppers",
                "Invalid stopper name.",
            )
            return

        # Проверяем, существует ли такой стоппер
        # в stopper_catalog
        stopper = self.stopper_repository.get_by_name(
            stopper_name
        )

        if stopper is None:
            QMessageBox.warning(
                self,
                "Stoppers",
                (
                    "Find text does not match "
                    "a stopper name from the catalog."
                ),
            )
            return

        # Открываем окно выбора действия
        dialog = StopperActionsDialog(
            stopper=stopper,
            parent=self,
        )

        result = dialog.exec()

        if result != QDialog.Accepted:
            return

        # Собираем только видимые файлы
        # из левого списка
        files = []

        left_list = (
            self.edit_page.files_to_rename_list
        )

        for row in range(left_list.count()):
            if left_list.isRowHidden(row):
                continue

            item = left_list.item(row)
            file_path = item.data(Qt.UserRole)

            files.append(file_path)

        if not files:
            QMessageBox.information(
                self,
                "Stoppers",
                "No files to process.",
            )
            return

        # Загружаем каталог шаблонов.
        #
        # Более длинные template_name проверяем первыми,
        # чтобы при похожих названиях выбрать
        # наиболее конкретное совпадение.
        templates = sorted(
            self.template_repository.get_all(),
            key=lambda item: len(
                item.template_name
            ),
            reverse=True,
        )

        files_with_stoppers = []
        files_without_stoppers = []
        unknown_files = []

        # Определяем шаблон каждого готового файла.
        #
        # Например:
        #
        # EVA5925_art-16143_2_driver_footrest_vlv.dxf
        #
        # содержит неизменную основу:
        #
        # driver_footrest
        for file_path in files:
            file_name = Path(
                file_path
            ).stem.lower()

            matched_template = None

            for template in templates:
                template_name = (
                    template.template_name.lower()
                )

                if template_name in file_name:
                    matched_template = template
                    break

            # Имя файла не удалось связать
            # ни с одним шаблоном из каталога
            if matched_template is None:
                unknown_files.append(
                    file_path
                )
                continue

            if matched_template.has_stoppers:
                files_with_stoppers.append(
                    file_path
                )
            else:
                files_without_stoppers.append(
                    file_path
                )

        # Неизвестные шаблоны считаем небезопасной
        # ситуацией и полностью отменяем операцию
        if unknown_files:
            QMessageBox.warning(
                self,
                "Stoppers",
                (
                    "Some templates were not found "
                    "in the template catalog.\n\n"
                    "The stopper operation was cancelled."
                ),
            )
            return

        # Среди выбранных файлов вообще нет
        # шаблонов со стопперами
        if not files_with_stoppers:
            QMessageBox.information(
                self,
                "Stoppers",
                (
                    "The selected templates "
                    "do not contain stoppers."
                ),
            )
            return

        # Если выбор смешанный, предупреждаем,
        # что файлы без стопперов будут пропущены
        if files_without_stoppers:
            answer = QMessageBox.warning(
                self,
                "Stoppers",
                (
                    f"{len(files_without_stoppers)} selected "
                    "file(s) use templates without stoppers.\n\n"
                    "These files will be skipped.\n\n"
                    "Continue?"
                ),
                QMessageBox.Yes
                | QMessageBox.No,
                QMessageBox.No,
            )

            if answer != QMessageBox.Yes:
                return

        # После preflight работаем ТОЛЬКО
        # с файлами шаблонов, у которых
        # has_stoppers=True
        files = files_with_stoppers
        file_count = len(files)

        # Change diameter
        if dialog.is_change_diameter():
            new_diameter = (
                dialog.get_new_diameter()
            )

            answer = QMessageBox.question(
                self,
                "Change stopper diameter",
                (
                    "Change stopper diameter to "
                    f"{new_diameter:g} mm?\n\n"
                    f"Files to modify: {file_count}"
                ),
                QMessageBox.Yes
                | QMessageBox.No,
                QMessageBox.No,
            )

            if answer != QMessageBox.Yes:
                return

            # Пока здесь будет подключён
            # StopperEditor для изменения диаметра

            self.start_stopper_worker(
                files=files,
                action="change",
                expected_diameter=stopper.diameter,
                new_diameter=new_diameter,
            )

        # Delete stoppers
        elif dialog.is_delete_stoppers():
            answer = QMessageBox.warning(
                self,
                "Delete stoppers",
                (
                    f"Delete stoppers from "
                    f"{file_count} files?\n\n"
                    "DXF files will be modified.\n"
                    "This operation cannot be undone."
                ),
                QMessageBox.Yes
                | QMessageBox.No,
                QMessageBox.No,
            )

            if answer != QMessageBox.Yes:
                return

            self.start_stopper_worker(
                files=files,
                action="delete",
                expected_diameter=stopper.diameter,
            )

    def remove_files(self):
        self.edit_page.files_to_rename_list.clear()
        self.edit_page.renamed_files_list.clear()
        self.files_to_rename.clear()
        self.files_for_replace.clear()
        self.edit_page.editFilesPbar.setValue(0)

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

            dialog = QMessageBox(self)
            dialog.setWindowTitle("Create missing IDs")
            dialog.setIcon(QMessageBox.Question)

            dialog.setText(
                f"{len(validation.create_id_issues)} missing ID(s) found."
            )

            dialog.setInformativeText(
                "Create missing IDs and continue?"
            )

            dialog.setDetailedText(message)

            dialog.setStandardButtons(
                QMessageBox.Yes | QMessageBox.No
            )
            dialog.setDefaultButton(QMessageBox.No)

            answer = dialog.exec()

            if answer != QMessageBox.Yes:
                return

        # 3. Копирование без замены
        # 3. Подтверждения перед копированием
        unselected_id_issues = [
            issue
            for issue in validation.confirmation_issues
            if (
                    issue.issue_type
                    == ValidationIssueType.DESTINATION_ID_NOT_SELECTED
            )
        ]

        add_without_replace_issues = [
            issue
            for issue in validation.confirmation_issues
            if (
                    issue.issue_type
                    == ValidationIssueType.ADD_FILES_WITHOUT_REPLACEMENT
            )
        ]

        if unselected_id_issues:
            message = "\n".join(
                issue.message
                for issue in unselected_id_issues
            )

            dialog = QMessageBox(self)
            dialog.setWindowTitle(
                "Unselected destination IDs"
            )
            dialog.setIcon(
                QMessageBox.Warning
            )

            dialog.setText(
                f"{len(unselected_id_issues)} destination ID(s) are not selected."
            )

            dialog.setInformativeText(
                "These IDs will be skipped during copying."
            )

            dialog.setDetailedText(
                message
            )

            skip_button = dialog.addButton(
                "Skip unselected IDs",
                QMessageBox.AcceptRole,
            )

            cancel_button = dialog.addButton(
                "Cancel",
                QMessageBox.RejectRole,
            )

            dialog.setDefaultButton(
                cancel_button
            )

            dialog.exec()

            if dialog.clickedButton() != skip_button:
                return

        if add_without_replace_issues:
            message = "\n".join(
                issue.message
                for issue in add_without_replace_issues
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

        self.art_copy_worker = ArtCopyWorker(
            plan,
            self.art_copy_service,
            self.file_service,
        )

        self.art_copy_worker.moveToThread(self.thread)

        self.thread.started.connect(
            self.art_copy_worker.run
        )

        self.art_copy_worker.progress.connect(
            self.on_copy_progress
        )

        self.art_copy_worker.finished.connect(
            self.on_copy_finished
        )

        self.art_copy_worker.finished.connect(
            self.thread.quit
        )

        self.art_copy_worker.finished.connect(
            self.art_copy_worker.deleteLater
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

    def is_cloud_available(self) -> bool:
        if (
                self.cloud_sync_repository is None
                or self.sync_service is None
        ):
            QMessageBox.warning(
                self,
                "Cloud unavailable",
                (
                    "Cloud database is unavailable.\n\n"
                    "Changes cannot be saved while offline."
                ),
            )
            return False

        return True

    def on_cloud_services_ready(
            self,
            cloud_sync_repository,
            sync_service,
    ) -> None:
        self.cloud_sync_repository = cloud_sync_repository
        self.sync_service = sync_service

    def start_cloud_sync(self) -> None:

        if (
                self.sync_thread is not None
                and self.sync_thread.isRunning()
        ):

            return

        self.database_page.set_cloud_syncing()

        self.sync_thread = QThread(self)

        self.sync_worker = SyncWorker(
            self.database,
            self.cloud_database,
            self.sync_service,
        )

        self.sync_worker.moveToThread(
            self.sync_thread
        )

        self.sync_thread.started.connect(
            self.sync_worker.run
        )

        self.sync_worker.services_ready.connect(
            self.on_cloud_services_ready
        )

        self.sync_worker.finished.connect(
            self.on_cloud_sync_finished
        )

        self.sync_worker.failed.connect(
            self.on_cloud_sync_failed
        )

        self.sync_worker.finished.connect(
            self.sync_thread.quit
        )

        self.sync_worker.failed.connect(
            self.sync_thread.quit
        )

        self.sync_thread.finished.connect(
            self.sync_worker.deleteLater
        )

        self.sync_thread.finished.connect(
            self.sync_thread.deleteLater
        )

        self.sync_thread.finished.connect(
            self.on_cloud_sync_thread_finished
        )

        self.sync_thread.start()

    def on_cloud_sync_finished(
            self,
            result: dict,
    ) -> None:
        print(
            "Cloud sync finished:",
            result,
        )

        self.database_page.set_cloud_online()

        self.load_template_database_table()
        self.load_stopper_database_table()
        self.load_copy_rules_database_table()

        self.load_templates_to_eva_page()

    def on_cloud_sync_failed(
            self,
            error: str,
    ) -> None:
        print(
            "Cloud sync failed:",
            error,
        )

        self.database_page.set_cloud_offline()

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
                        "has_stoppers": "Yes" if record.has_stoppers else "No"
                    },
                }
            )

        self.database_page.templatesTable.render_records(
            table_records
        )

    def on_add_template(self):
        if not self.is_cloud_available():
            return

        dialog = TemplateDialog(
            parent=self,
        )

        if dialog.exec() != QDialog.Accepted:
            return

        folder_id, template_name, has_stoppers = (
            dialog.get_data()
        )

        self.cloud_sync_repository.add_template(
            folder_id,
            template_name,
            has_stoppers,
        )

        self.sync_service.sync()

        self.load_template_database_table()
        self.load_templates_to_eva_page()

    def on_edit_template(self, record_id: int):
        if not self.is_cloud_available():
            return

        record = self.template_repository.get_by_id(
            record_id
        )

        if record is None:
            return

        template_uuid = self.template_repository.get_uuid_by_id(
            record_id
        )

        if template_uuid is None:
            return

        dialog = TemplateDialog(
            folder_id=record.folder_id,
            template_name=record.template_name,
            has_stoppers=record.has_stoppers,
            parent=self,
        )

        if dialog.exec() != QDialog.Accepted:
            return

        folder_id, template_name, has_stoppers = (
            dialog.get_data()
        )

        self.cloud_sync_repository.update_template(
            template_uuid=template_uuid,
            folder_id=folder_id,
            template_name=template_name,
            has_stoppers=has_stoppers,
        )

        self.sync_service.sync()

        self.load_template_database_table()
        self.load_templates_to_eva_page()
        
    def on_delete_templates(
            self,
            record_ids: list[int],
    ):
        if not self.is_cloud_available():
            return

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

        for record_id in record_ids:
            template_uuid = (
                self.template_repository.get_uuid_by_id(
                    record_id
                )
            )

            if template_uuid is None:
                continue

            self.cloud_sync_repository.delete_template(
                template_uuid=template_uuid
            )

        self.sync_service.sync()

        self.load_template_database_table()
        self.load_templates_to_eva_page()

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
        if not self.is_cloud_available():
            return

        dialog = StopperDialog(
            parent=self,
        )

        if dialog.exec() != QDialog.Accepted:
            return

        diameter, stopper_name = dialog.get_data()

        self.cloud_sync_repository.add_stopper(
            diameter=diameter,
            stopper_name=stopper_name,
        )

        self.sync_service.sync()

        self.load_stopper_database_table()

    def on_edit_stopper(self, record_id: int):
        if not self.is_cloud_available():
            return

        record = self.stopper_repository.get_by_id(
            record_id
        )

        if record is None:
            return

        stopper_uuid = self.stopper_repository.get_uuid_by_id(
            record_id
        )

        if stopper_uuid is None:
            return

        dialog = StopperDialog(
            diameter=record.diameter,
            stopper_name=record.stopper_name,
            parent=self,
        )

        if dialog.exec() != QDialog.Accepted:
            return

        diameter, stopper_name = dialog.get_data()

        self.cloud_sync_repository.update_stopper(
            stopper_uuid=stopper_uuid,
            stopper_name=stopper_name,
            diameter=diameter,
        )

        self.sync_service.sync()

        self.load_stopper_database_table()

    def on_delete_stoppers(
            self,
            record_ids: list[int],
    ):
        if not self.is_cloud_available():
            return

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

        for record_id in record_ids:
            stopper_uuid = (
                self.stopper_repository.get_uuid_by_id(
                    record_id
                )
            )

            if stopper_uuid is None:
                continue

            self.cloud_sync_repository.delete_stopper(
                stopper_uuid=stopper_uuid
            )

        self.sync_service.sync()

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
        if not self.is_cloud_available():
            return

        dialog = CopyRuleDialog(parent=self)

        if dialog.exec() != QDialog.Accepted:
            return

        mode, from_id, to_id = dialog.get_data()

        self.cloud_sync_repository.add_copy_rule(
            mode=mode,
            from_id=from_id,
            to_id=to_id,
        )

        self.sync_service.sync()

        self.load_copy_rules_database_table()

    def on_edit_copy_rule(
            self,
            record_id: int,
    ):
        if not self.is_cloud_available():
            return

        record = self.copy_rule_repository.get_by_id(
            record_id
        )

        if record is None:
            return

        rule_uuid = self.copy_rule_repository.get_uuid_by_id(
            record_id
        )

        if rule_uuid is None:
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

        self.cloud_sync_repository.update_copy_rule(
            rule_uuid=rule_uuid,
            mode=mode,
            from_id=from_id,
            to_id=to_id,
        )

        self.sync_service.sync()

        self.load_copy_rules_database_table()

    def on_delete_copy_rules(
            self,
            record_ids: list[int],
    ):
        if not self.is_cloud_available():
            return

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

        for record_id in record_ids:
            rule_uuid = (
                self.copy_rule_repository.get_uuid_by_id(
                    record_id
                )
            )

            if rule_uuid is None:
                continue

            self.cloud_sync_repository.delete_copy_rule(
                rule_uuid=rule_uuid
            )

        self.sync_service.sync()

        self.load_copy_rules_database_table()

    def load_templates_to_eva_page(self):
        self.session_templates = (
            self.template_service.get_session_templates()
        )

        self.eva_page.render_templates(
            self.session_templates
        )

    def add_prepared_eva(
            self,
            eva_name: str,
            articles: list[str],
    ):
        self.eva_service.add_prepared_eva(
            self.prepared_evas,
            eva_name,
            articles,
        )

        self.update_eva_preview()

    def clear_prepared_eva(self):
        self.prepared_evas.clear()

        self.update_eva_preview()

    def on_add_stoppers_requested(self):
        stoppers = self.stopper_repository.get_all()

        dialog = StopperSelectionDialog(
            stoppers=stoppers,
            parent=self,
        )

        if dialog.exec() != QDialog.Accepted:
            return

        combinations = dialog.get_combinations()

        self.session_templates = (
            self.template_service.add_stopper_templates(
                self.session_templates,
                combinations,
            )
        )

        self.eva_page.render_templates(
            self.session_templates
        )

    def on_custom_template_requested(
            self,
            folder_id: int,
    ):
        templates = [
            template
            for template in self.session_templates
            if template.folder_id == folder_id
        ]

        dialog = CustomTemplateDialog(
            templates,
            parent=self,
        )

        dialog.exec()

        created_templates = (
            dialog.get_created_templates()
        )

        self.session_templates = (
            self.template_service.add_custom_templates(
                self.session_templates,
                created_templates,
            )
        )

        self.eva_page.render_templates(
            self.session_templates
        )

    def on_template_selection_changed(
            self,
            folder_id: int,
            template_name: str,
            checked: bool,
    ):
        self.template_service.set_template_selected(
            self.session_templates,
            folder_id,
            template_name,
            checked,
            five_d_mode=self.five_d_mode,
        )

        self.eva_page.render_templates(
            self.session_templates
        )

        self.update_eva_preview()

    def on_clear_template_selection(self):
        for template in self.session_templates:
            template.selected = False

        self.eva_page.render_templates(
            self.session_templates
        )

    def on_five_d_mode_changed(
            self,
            enabled: bool,
    ):
        self.five_d_mode = enabled

        if enabled:
            for template in self.session_templates:
                if template.folder_id in {1, 5}:
                    template.selected = False

        self.eva_page.set_five_d_mode(
            enabled
        )

        self.eva_page.render_templates(
            self.session_templates
        )

        self.update_eva_preview()

    def build_preview_templates(
            self,
    ) -> list[PreviewTemplate]:

        preview_templates = []

        for template in self.session_templates:
            if not template.selected:
                continue

            destination_folder_id = (
                self.copy_rule_service
                .resolve_template_folder_id(
                    template.folder_id,
                    self.five_d_mode,
                )
            )

            preview_templates.append(
                PreviewTemplate(
                    destination_folder_id=int(
                        destination_folder_id
                    ),
                    template_name=template.template_name,
                )
            )

        return preview_templates

    def update_eva_preview(self):

        preview_templates = (
            self.build_preview_templates()
        )

        self.eva_page.render_preview(
            self.prepared_evas,
            preview_templates,
        )

    def on_create_structure_requested(self):
        use_default_path = (
            self.eva_page
            .use_default_path_checkbox
            .isChecked()
        )

        if use_default_path:
            destination_root = (
                self.path_service
                .get_eva_default_output_path()
            )

            if destination_root is None:
                QMessageBox.warning(
                    self,
                    "Путь не задан",
                    "Путь по умолчанию не настроен.",
                )
                return

        else:
            selected_path = (
                QFileDialog.getExistingDirectory(
                    self,
                    "Выберите папку для выгрузки",
                )
            )

            if not selected_path:
                return

            destination_root = Path(
                selected_path
            )

        generation_plan = (
            self.eva_generation_planner
            .build_plan(
                destination_root=destination_root,
                prepared_evas=self.prepared_evas,
                session_templates=self.session_templates,
                five_d_mode=self.five_d_mode,
            )
        )

        if generation_plan.is_empty:
            QMessageBox.warning(
                self,
                "Нет файлов",
                "Не выбраны шаблоны для создания.",
            )
            return

        self.current_generation_destination = (
            destination_root
        )

        self.eva_page.reset_creation_progress()

        self.generation_thread = QThread()

        self.generation_worker = (
            EvaGenerationWorker(
                generation_plan
            )
        )

        self.generation_worker.moveToThread(
            self.generation_thread
        )

        self.generation_thread.started.connect(
            self.generation_worker.run
        )

        self.generation_worker.progressChanged.connect(
            self.eva_page.set_creation_progress
        )

        self.generation_worker.finished.connect(
            self.on_generation_finished
        )

        self.generation_worker.errorOccurred.connect(
            self.on_generation_error
        )

        self.generation_worker.finished.connect(
            self.generation_thread.quit
        )

        self.generation_worker.errorOccurred.connect(
            self.generation_thread.quit
        )

        self.generation_worker.finished.connect(
            self.generation_worker.deleteLater
        )

        self.generation_worker.errorOccurred.connect(
            self.generation_worker.deleteLater
        )

        self.generation_thread.finished.connect(
            self.generation_thread.deleteLater
        )

        self.eva_page.create_structure_btn.setEnabled(
            False
        )

        self.generation_thread.start()

    def refresh_eva_paths(self):
        default_path = (
            self.path_service
            .get_eva_default_output_path()
        )

        last_path = (
            self.path_service
            .get_eva_last_output_path()
        )

        self.database_page.set_eva_paths(
            default_path,
            last_path,
        )

    def edit_eva_default_output_path(self):
        current_path = (
            self.path_service
            .get_eva_default_output_path()
        )

        dialog = PathDialog(
            current_path=current_path,
            parent=self,
        )

        if not dialog.exec():
            return

        selected_path = dialog.get_path()

        if selected_path is None:
            return

        self.path_service.set_eva_default_output_path(
            selected_path
        )

        self.refresh_eva_paths()

    def on_generation_finished(
            self,
            created_count: int,
            existing_count: int,
    ):
        self.eva_page.create_structure_btn.setEnabled(
            True
        )

        destination_root = (
            self.current_generation_destination
        )

        self.path_service.set_eva_last_output_path(
            destination_root
        )

        self.refresh_eva_paths()

        self.eva_page.open_last_output_btn.setEnabled(
            destination_root.exists()
        )

        QMessageBox.information(
            self,
            "Готово",
            (
                "Структура успешно создана.\n\n"
                f"Создано файлов: {created_count}\n"
                f"Уже существовало: {existing_count}"
            ),
        )

    def on_generation_error(
            self,
            message: str,
    ):
        self.eva_page.create_structure_btn.setEnabled(
            True
        )

        QMessageBox.critical(
            self,
            "Ошибка",
            message,
        )

    def open_eva_last_output(self):
        last_output_path = (
            self.path_service
            .get_eva_last_output_path()
        )

        if (
                last_output_path is None
                or not last_output_path.exists()
        ):
            QMessageBox.warning(
                self,
                "Папка не найдена",
                "Последняя выгрузка EVA не найдена.",
            )

            self.refresh_eva_paths()

            self.eva_page.open_last_output_btn.setEnabled(
                False
            )
            return

        QDesktopServices.openUrl(
            QUrl.fromLocalFile(
                str(last_output_path)
            )
        )

    def return_processed_files(self) -> None:

        processed_list = (
            self.edit_page.renamed_files_list
        )

        working_list = (
            self.edit_page.files_to_rename_list
        )

        while processed_list.count() > 0:
            item = processed_list.takeItem(0)

            item.setIcon(QIcon())

            working_list.addItem(item)

        self.sync_files_to_rename_from_ui()

        self.edit_page.editFilesPbar.setValue(0)

    def on_export_source_requested(self) -> None:

        files = self.get_visible_working_files()

        self.open_export_dialog(
            files
        )

    def get_visible_working_files(
            self,
    ) -> list[Path]:

        files = []

        file_list = (
            self.edit_page.files_to_rename_list
        )

        for row in range(file_list.count()):

            if file_list.isRowHidden(row):
                continue

            item = file_list.item(row)

            files.append(
                item.data(Qt.UserRole)
            )

        return files

    def on_export_processed_requested(self) -> None:

        files = self.get_processed_files()

        self.open_export_dialog(
            files
        )

    def get_processed_files(
            self,
    ) -> list[Path]:

        files = []

        file_list = (
            self.edit_page.renamed_files_list
        )

        for row in range(file_list.count()):
            item = file_list.item(row)

            files.append(
                item.data(Qt.UserRole)
            )

        return files

    def open_export_dialog(
            self,
            files: list[Path],
    ) -> None:

        if not files:
            QMessageBox.information(
                self,
                "Nothing to export",
                "Нет файлов для выгрузки.",
            )
            return

        default_path = (
            self.path_service
            .get_files_default_output_path()
        )

        dialog = ExportDialog(
            default_path=default_path,
            parent=self,
        )

        if dialog.exec() != QDialog.Accepted:
            return

        level = dialog.get_level()
        destination_path = (
            dialog.get_destination_path()
        )

        if destination_path is None:
            QMessageBox.warning(
                self,
                "Export",
                "Не выбран путь для выгрузки.",
            )
            return

        plan = self.export_planner.build_plan(
            files=files,
            level=level,
            destination_root=destination_path,
        )

        if plan.conflicts:
            conflict_names = "\n".join(
                str(path)
                for path in plan.conflicts
            )

            QMessageBox.warning(
                self,
                "Export conflict",
                (
                    "Некоторые объекты уже существуют "
                    "в папке выгрузки:\n\n"
                    f"{conflict_names}\n\n"
                    "Операция отменена."
                ),
            )

            return

        if plan.is_empty:
            QMessageBox.information(
                self,
                "Nothing to export",
                "Нет объектов для выгрузки.",
            )

            return

        self.current_export_plan = plan
        self.pending_export_path = Path(destination_path)

        self.edit_page.editFilesPbar.setValue(0)

        self.set_processing_state(True)

        self.export_thread = QThread()

        self.export_worker = ExportWorker(
            plan
        )

        self.export_worker.moveToThread(
            self.export_thread
        )

        self.export_thread.started.connect(
            self.export_worker.run
        )

        self.export_worker.progress.connect(
            self.on_export_progress
        )

        self.export_worker.finished.connect(
            self.on_export_finished
        )

        self.export_worker.errorOccurred.connect(
            self.on_export_error
        )

        self.export_worker.finished.connect(
            self.export_thread.quit
        )

        self.export_worker.errorOccurred.connect(
            self.export_thread.quit
        )

        self.export_worker.finished.connect(
            self.export_worker.deleteLater
        )

        self.export_worker.errorOccurred.connect(
            self.export_worker.deleteLater
        )

        self.export_thread.finished.connect(
            self.export_thread.deleteLater
        )

        self.export_thread.start()

    def on_export_progress(
            self,
            current: int,
            total: int,
            operation,
    ) -> None:

        self.edit_page.editFilesPbar.setMaximum(
            total
        )

        self.edit_page.editFilesPbar.setValue(
            current
        )

    def on_export_finished(
            self,
            processed_count: int,
    ) -> None:

        self.set_processing_state(False)

        destination_root = (
            self.current_export_plan.destination_root
        )

        self.path_service.set_files_last_output_path(
            destination_root
        )

        self.refresh_files_paths()

        self.last_export_path = (
            self.pending_export_path
        )

        if self.pending_export_path is not None:
            self.last_export_path = (
                self.pending_export_path
            )

        self.pending_export_path = None

        QMessageBox.information(
            self,
            "Export complete",
            (
                "Выгрузка завершена.\n\n"
                f"Обработано объектов: "
                f"{processed_count}"
            ),
        )

    def on_export_error(
            self,
            message: str,
    ) -> None:

        self.set_processing_state(False)
        self.pending_export_path = None

        QMessageBox.critical(
            self,
            "Export error",
            message,
        )

    def edit_files_default_output_path(self) -> None:

        current_path = (
            self.path_service
            .get_files_default_output_path()
        )

        dialog = PathDialog(
            current_path=current_path,
            parent=self,
        )

        if dialog.exec() != QDialog.Accepted:
            return

        path = dialog.get_path()

        if path is None:
            return

        self.path_service.set_files_default_output_path(
            path
        )

        self.refresh_files_paths()

    def refresh_files_paths(self) -> None:

        default_path = (
            self.path_service
            .get_files_default_output_path()
        )

        last_path = (
            self.path_service
            .get_files_last_output_path()
        )

        self.database_page.set_files_paths(
            default_path=default_path,
            last_path=last_path,
        )

    def open_files_last_output(self) -> None:

        last_output_path = (
            self.path_service
            .get_files_last_output_path()
        )

        if (
                last_output_path is None
                or not last_output_path.exists()
        ):
            QMessageBox.warning(
                self,
                "Папка не найдена",
                "Последняя выгрузка файлов не найдена.",
            )

            self.refresh_files_paths()
            return

        QDesktopServices.openUrl(
            QUrl.fromLocalFile(
                str(last_output_path)
            )
        )

    def on_delete_source_requested(
            self,
    ) -> None:

        files = self.get_visible_working_files()

        if not files:
            QMessageBox.information(
                self,
                "Nothing to delete",
                "Нет файлов для удаления.",
            )
            return

        dialog = DeleteDialog(
            parent=self
        )

        if dialog.exec() != QDialog.Accepted:
            return

        level = dialog.get_level()

        plan = self.delete_planner.build_plan(
            files=files,
            level=level,
        )

        if plan.is_empty:
            QMessageBox.information(
                self,
                "Nothing to delete",
                "Нет объектов для удаления.",
            )
            return

        targets_text = "\n".join(
            str(operation.target_path)
            for operation in plan.operations
        )

        reply = QMessageBox.warning(
            self,
            "Подтверждение удаления",
            (
                f"Будет удалено объектов: "
                f"{len(plan.operations)}\n\n"
                f"{targets_text}\n\n"
                "Это действие нельзя отменить.\n"
                "Продолжить?"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return

        self.current_delete_plan = plan

        self.edit_page.editFilesPbar.setValue(0)

        self.set_processing_state(True)

        self.delete_thread = QThread()

        self.delete_worker = DeleteWorker(
            plan
        )

        self.delete_worker.moveToThread(
            self.delete_thread
        )

        self.delete_thread.started.connect(
            self.delete_worker.run
        )

        self.delete_worker.progress.connect(
            self.on_delete_progress
        )

        self.delete_worker.finished.connect(
            self.on_delete_finished
        )

        self.delete_worker.errorOccurred.connect(
            self.on_delete_error
        )

        self.delete_worker.finished.connect(
            self.delete_thread.quit
        )

        self.delete_worker.errorOccurred.connect(
            self.delete_thread.quit
        )

        self.delete_worker.finished.connect(
            self.delete_worker.deleteLater
        )

        self.delete_worker.errorOccurred.connect(
            self.delete_worker.deleteLater
        )

        self.delete_thread.finished.connect(
            self.delete_thread.deleteLater
        )

        self.delete_thread.start()

    def on_delete_progress(
            self,
            current: int,
            total: int,
            operation,
    ) -> None:

        self.edit_page.editFilesPbar.setMaximum(
            total
        )

        self.edit_page.editFilesPbar.setValue(
            current
        )

    def on_delete_finished(
            self,
            processed_count: int,
    ) -> None:

        self.refresh_edit_files_after_delete()

        self.set_processing_state(False)

        QMessageBox.information(
            self,
            "Delete complete",
            (
                "Удаление завершено.\n\n"
                f"Удалено объектов: "
                f"{processed_count}"
            ),
        )

    def on_delete_error(
            self,
            message: str,
    ) -> None:

        self.set_processing_state(False)

        QMessageBox.critical(
            self,
            "Delete error",
            message,
        )

    def remove_missing_files_from_list(
            self,
            file_list,
    ) -> None:

        for row in range(
                file_list.count() - 1,
                -1,
                -1,
        ):
            item = file_list.item(row)

            file_path = item.data(
                Qt.UserRole
            )

            if file_path is None:
                continue

            if file_path.exists():
                continue

            file_list.takeItem(row)

    def refresh_edit_files_after_delete(
            self,
    ) -> None:

        self.remove_missing_files_from_list(
            self.edit_page.files_to_rename_list
        )

        self.remove_missing_files_from_list(
            self.edit_page.renamed_files_list
        )

        self.sync_files_to_rename_from_ui()

    def on_move_to_id_requested(
            self,
    ) -> None:

        files = self.get_visible_working_files()

        if not files:
            QMessageBox.information(
                self,
                "Nothing to move",
                "Нет файлов для перемещения.",
            )
            return

        dialog = MoveToIdDialog(
            parent=self
        )

        if dialog.exec() != QDialog.Accepted:
            return

        destination_id = (
            dialog.get_destination_id()
        )

        try:
            plan = (
                self.move_to_id_planner
                .build_plan(
                    files=files,
                    destination_id=destination_id,
                )
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "Move to ID",
                str(error),
            )
            return

        if plan.conflicts:
            conflict_names = "\n".join(
                str(path)
                for path in plan.conflicts
            )

            QMessageBox.warning(
                self,
                "Move conflict",
                (
                    "Некоторые целевые файлы "
                    "уже существуют:\n\n"
                    f"{conflict_names}\n\n"
                    "Операция отменена."
                ),
            )
            return

        if plan.is_empty:
            QMessageBox.information(
                self,
                "Nothing to move",
                (
                    "Нет файлов для перемещения.\n"
                    "Возможно, они уже находятся "
                    f"в ID {destination_id}."
                ),
            )
            return

        self.current_move_to_id_plan = plan

        self.current_move_to_id_plan = plan

        self.edit_page.editFilesPbar.setValue(0)

        self.set_processing_state(True)

        self.move_to_id_thread = QThread()

        self.move_to_id_worker = MoveToIdWorker(
            plan
        )

        self.move_to_id_worker.moveToThread(
            self.move_to_id_thread
        )

        self.move_to_id_thread.started.connect(
            self.move_to_id_worker.run
        )

        self.move_to_id_worker.progress.connect(
            self.on_move_to_id_progress
        )

        self.move_to_id_worker.finished.connect(
            self.on_move_to_id_finished
        )

        self.move_to_id_worker.errorOccurred.connect(
            self.on_move_to_id_error
        )

        self.move_to_id_worker.finished.connect(
            self.move_to_id_thread.quit
        )

        self.move_to_id_worker.errorOccurred.connect(
            self.move_to_id_thread.quit
        )

        self.move_to_id_worker.finished.connect(
            self.move_to_id_worker.deleteLater
        )

        self.move_to_id_worker.errorOccurred.connect(
            self.move_to_id_worker.deleteLater
        )

        self.move_to_id_thread.finished.connect(
            self.move_to_id_thread.deleteLater
        )

        self.move_to_id_thread.start()

    def on_move_to_id_progress(
            self,
            current: int,
            total: int,
            operation,
    ) -> None:

        self.edit_page.editFilesPbar.setMaximum(
            total
        )

        self.edit_page.editFilesPbar.setValue(
            current
        )

        self.update_moved_file_in_list(
            self.edit_page.files_to_rename_list,
            operation,
        )

        self.update_moved_file_in_list(
            self.edit_page.renamed_files_list,
            operation,
        )

    def on_move_to_id_error(
            self,
            message: str,
    ) -> None:

        self.set_processing_state(False)

        QMessageBox.critical(
            self,
            "Move error",
            message,
        )

    def update_moved_file_in_list(
            self,
            file_list,
            operation,
    ) -> None:

        for row in range(
                file_list.count()
        ):
            item = file_list.item(row)

            if (
                    item.data(Qt.UserRole)
                    != operation.source_file
            ):
                continue

            item.setText(
                operation.destination_file.name
            )

            item.setData(
                Qt.UserRole,
                operation.destination_file,
            )

            return

    def on_move_to_id_finished(
            self,
            processed_count: int,
    ) -> None:

        self.sync_files_to_rename_from_ui()

        self.set_processing_state(False)

        QMessageBox.information(
            self,
            "Move complete",
            (
                "Перемещение завершено.\n\n"
                f"Перемещено файлов: "
                f"{processed_count}"
            ),
        )

    def start_stopper_worker(
            self,
            files: list[str],
            action: str,
            expected_diameter: float,
            new_diameter: float | None = None,
    ) -> None:
        self.stopper_thread = QThread()

        self.stopper_worker = StopperWorker(
            editor=self.stopper_editor,
            files=files,
            action=action,
            expected_diameter=expected_diameter,
            new_diameter=new_diameter,
        )

        self.stopper_worker.moveToThread(
            self.stopper_thread
        )

        self.stopper_thread.started.connect(
            self.stopper_worker.run
        )

        self.stopper_worker.progress.connect(
            self.on_stopper_progress
        )

        self.stopper_worker.finished.connect(
            self.on_stopper_worker_finished
        )

        self.stopper_worker.failed.connect(
            self.on_stopper_worker_failed
        )

        self.stopper_worker.finished.connect(
            self.stopper_thread.quit
        )

        self.stopper_worker.failed.connect(
            self.stopper_thread.quit
        )

        self.stopper_thread.finished.connect(
            self.stopper_worker.deleteLater
        )

        self.stopper_thread.finished.connect(
            self.stopper_thread.deleteLater
        )

        self.stopper_thread.start()

    def on_stopper_worker_finished(
            self,
            result: dict,
    ) -> None:
        message = (
            "Stopper operation finished.\n\n"
            f"Files processed: "
            f"{result['processed_files']}\n"
            f"Files failed: "
            f"{result['failed_files']}"
        )

        if result["changed_total"]:
            message += (
                "\n"
                f"Stoppers changed: "
                f"{result['changed_total']} "
                f"in {result['changed_files']} files"
            )

        if result["deleted_total"]:
            message += (
                "\n"
                f"Stoppers deleted: "
                f"{result['deleted_total']} "
                f"in {result['deleted_files']} files"
            )

        QMessageBox.information(
            self,
            "Stoppers",
            message,
        )


    def on_stopper_worker_failed(
            self,
            error: str,
    ) -> None:
        QMessageBox.critical(
            self,
            "Stoppers",
            (
                "Stopper operation failed.\n\n"
                f"{error}"
            ),
        )

    def on_stopper_progress(
            self,
            current: int,
            total: int,
            file_path,
            modified: bool,
    ) -> None:

        self.edit_page.editFilesPbar.setMaximum(
            total
        )

        self.edit_page.editFilesPbar.setValue(
            current
        )

        if modified:
            self.move_stopper_file(
                Path(file_path)
            )

    def move_stopper_file(
            self,
            file_path: Path,
    ) -> None:

        left_list = (
            self.edit_page.files_to_rename_list
        )

        right_list = (
            self.edit_page.renamed_files_list
        )

        for row in range(left_list.count()):
            item = left_list.item(row)

            if item.data(Qt.UserRole) != file_path:
                continue

            moved_item = left_list.takeItem(
                row
            )

            moved_item.setIcon(
                self.check_icon
            )

            right_list.addItem(
                moved_item
            )

            right_list.scrollToBottom()

            break

    def on_open_export_folder_requested(
            self,
    ) -> None:

        if self.last_export_path is None:
            QMessageBox.information(
                self,
                "Export",
                "Выгрузка ещё не выполнялась.",
            )
            return

        if not self.last_export_path.exists():
            QMessageBox.warning(
                self,
                "Export",
                "Папка последней выгрузки больше не существует.",
            )
            return

        QDesktopServices.openUrl(
            QUrl.fromLocalFile(
                str(self.last_export_path)
            )
        )

