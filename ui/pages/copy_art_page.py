from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit, QListWidget,
    QProgressBar, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QTreeWidget, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from widgets.arts_tree import ArtsTree, ArtsTreeMode

class TriStateControlCheckBox(QCheckBox):
    def nextCheckState(self) -> None:
        if self.checkState() == Qt.Checked:
            self.setCheckState(Qt.Unchecked)
        else:
            self.setCheckState(Qt.Checked)


class CopyArtsPage(QWidget):

    loadArtsRequested = Signal(str)
    copyAndRenameRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_directory: str | None = None
        self.dstIdCheckboxes: dict[str, QCheckBox] = {}

        self.setup_ui()
        self.setup_connections()

    def setup_connections(self):
        self.load_arts_btn.clicked.connect(self.on_load_arts_clicked)
        self.copyAndRenameButton.clicked.connect(self.on_copy_and_rename_clicked)
        self.clearSrcArtsButton.clicked.connect(self.srcArtsTree.clear_tree)
        self.removeDstArtsButton.clicked.connect(self.dstArtsTree.remove_selected_arts)
        self.clearDstArtsButton.clicked.connect(self.dstArtsTree.clear_tree)
        self.removeAvailableArtsButton.clicked.connect(self.artsTree.remove_selected_arts)
        self.clearAvailableArtsButton.clicked.connect(self.artsTree.clear_tree)
        self.srcMasterCheckbox.clicked.connect(self.on_src_master_clicked)
        self.srcArtsTree.checkStateChanged.connect(self.update_src_master_checkbox)
        self.dstMasterCheckbox.clicked.connect(self.on_dst_master_clicked)
        self.dstArtsTree.checkStateChanged.connect(self.update_dst_master_checkbox)
        self.dstArtsTree.checkStateChanged.connect(self.update_dst_id_checkboxes)
        self.dstArtsTree.artsChanged.connect(self.rebuild_dst_id_controls)

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

        # === Tree controls ===
        self.clearSrcArtsButton = QPushButton("Clear")

        self.srcMasterCheckbox = QCheckBox("Select all")
        self.srcMasterCheckbox.setTristate(True)

        self.removeDstArtsButton = QPushButton("Remove selected")
        self.clearDstArtsButton = QPushButton("Clear")

        self.dstMasterCheckbox = QCheckBox("Select all")
        self.dstMasterCheckbox.setTristate(True)


        src_buttons_layout = QHBoxLayout()

        src_buttons_layout.addWidget(
            self.clearSrcArtsButton,
        )

        src_buttons_layout.addStretch()

        src_buttons_layout.addWidget(
            self.srcMasterCheckbox
        )

        from_layout.addLayout(
            src_buttons_layout
        )

        dst_buttons_layout = QHBoxLayout()

        dst_buttons_layout.addWidget(
            self.removeDstArtsButton,
        )

        dst_buttons_layout.addWidget(
            self.clearDstArtsButton,
        )

        dst_buttons_layout.addStretch()

        dst_buttons_layout.addWidget(
            self.dstMasterCheckbox
        )

        to_layout.addLayout(
            dst_buttons_layout
        )

        self.dstIdControlsLayout = QHBoxLayout()

        self.dstIdControlsLayout.setContentsMargins(
            0, 0, 0, 0
        )

        self.dstIdControlsLayout.setSpacing(
            12
        )

        self.dstIdControlsLabel = QLabel(
            "IDs:"
        )

        self.dstIdControlsLayout.addWidget(
            self.dstIdControlsLabel
        )

        self.dstIdControlsLayout.addStretch()

        to_layout.addLayout(
            self.dstIdControlsLayout
        )

        self.clearSrcArtsButton.setMinimumWidth(100)
        self.clearDstArtsButton.setMinimumWidth(100)

        # ==================================================
        # === Progress bar (row 2, full width) ============
        # ==================================================
        self.copyAndRenamePbar = QProgressBar()
        self.copyAndRenamePbar.setValue(0)
        main_layout.addWidget(self.copyAndRenamePbar, 2, 0, 1, 2)

        # ==================================================
        # === Buttons (row 3) ==============================
        # ==================================================
        self.removeAvailableArtsButton = QPushButton("Remove selected")
        self.clearAvailableArtsButton = QPushButton("Clear")
        self.copyAndRenameButton = QPushButton("Copy and rename")
        self.fiveDModeCheckbox = QCheckBox("5D mode")

        bottom_layout = QHBoxLayout()

        bottom_layout.addWidget(
            self.removeAvailableArtsButton
        )

        bottom_layout.addWidget(
            self.clearAvailableArtsButton
        )

        bottom_layout.addStretch()

        bottom_layout.addWidget(
            self.fiveDModeCheckbox
        )

        bottom_layout.addStretch()

        bottom_layout.addWidget(
            self.copyAndRenameButton
        )

        main_layout.addLayout(
            bottom_layout,
            3, 0, 1, 2,
        )

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
            # "removeArts": self.removeArtNumbers,
            "copy": self.copyAndRenameButton,
            "clearSrc": self.clearSrcArtsButton,
            "removeDst": self.removeDstArtsButton,
            "clearDst": self.clearDstArtsButton,
            "progress": self.copyAndRenamePbar,
            "5DMode": self.fiveDModeCheckbox,
        }

    def on_src_master_clicked(
            self,
            checked: bool,
    ) -> None:
        state = (
            Qt.Checked
            if checked
            else Qt.Unchecked
        )

        self.srcArtsTree.set_all_check_state(
            state
        )

        self.update_src_master_checkbox()

    def update_src_master_checkbox(
            self,
    ) -> None:
        state = (
            self.srcArtsTree
            .get_overall_check_state()
        )

        self.srcMasterCheckbox.blockSignals(
            True
        )

        self.srcMasterCheckbox.setCheckState(
            state
        )

        self.srcMasterCheckbox.blockSignals(
            False
        )

    def on_dst_master_clicked(
            self,
            checked: bool,
    ) -> None:
        state = (
            Qt.Checked
            if checked
            else Qt.Unchecked
        )

        self.dstArtsTree.set_all_check_state(
            state
        )

        self.update_dst_master_checkbox()

    def update_dst_master_checkbox(
            self,
    ) -> None:
        state = (
            self.dstArtsTree
            .get_overall_check_state()
        )

        self.dstMasterCheckbox.blockSignals(
            True
        )

        self.dstMasterCheckbox.setCheckState(
            state
        )

        self.dstMasterCheckbox.blockSignals(
            False
        )

    def rebuild_dst_id_controls(
            self,
    ) -> None:

        # Удаляем старые динамические checkbox'ы
        for checkbox in self.dstIdCheckboxes.values():
            self.dstIdControlsLayout.removeWidget(
                checkbox
            )

            checkbox.deleteLater()

        self.dstIdCheckboxes.clear()

        # Получаем union всех ID из destination ART
        id_names = (
            self.dstArtsTree
            .get_available_id_names()
        )

        for id_name in id_names:
            checkbox = TriStateControlCheckBox(
                id_name
            )

            checkbox.setTristate(
                True
            )

            checkbox.stateChanged.connect(
                self.on_dst_id_checkbox_changed
            )

            checkbox.setCheckState(
                self.dstArtsTree.get_id_check_state(
                    id_name
                )
            )

            self.dstIdControlsLayout.insertWidget(
                self.dstIdControlsLayout.count() - 1,
                checkbox,
            )

            self.dstIdCheckboxes[
                id_name
            ] = checkbox

    def on_dst_id_checkbox_changed(
            self,
            state: int,
    ) -> None:

        checkbox = self.sender()

        if not isinstance(
                checkbox,
                QCheckBox,
        ):
            return

        id_name = checkbox.text()

        if state == Qt.Checked:
            checked = True

        elif state == Qt.Unchecked:
            checked = False

        else:
            return

        checkbox.blockSignals(True)

        try:

            self.dstArtsTree.set_id_checked(
                id_name,
                checked,
            )

        finally:
            checkbox.blockSignals(False)

    def update_dst_id_checkboxes(
            self,
    ) -> None:

        for id_name, checkbox in (
                self.dstIdCheckboxes.items()
        ):
            state = (
                self.dstArtsTree
                .get_id_check_state(id_name)
            )

            checkbox.blockSignals(True)

            try:
                checkbox.setCheckState(
                    state
                )

            finally:
                checkbox.blockSignals(False)


    def on_load_arts_clicked(self):
        self.loadArtsRequested.emit(self.current_directory)

    def on_copy_and_rename_clicked(self):
        self.copyAndRenameRequested.emit()


