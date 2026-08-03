from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView
from enum import Enum
from pathlib import Path
from PySide6.QtCore import Qt

class ArtsTreeMode(Enum):
    AVAILABLE = 1
    SOURCE = 2
    DESTINATION = 3

class ArtsTree(QTreeWidget):
    """Tree widget used for displaying EVA articles."""

    def __init__(
            self,
            mode: ArtsTreeMode,
            parent=None,
    ):
        super().__init__(parent)

        self.mode = mode

        self.setup_ui()

    def setup_ui(self):
        self.setHeaderHidden(True)
        self.setAnimated(True)
        self.setIndentation(18)
        self.setUniformRowHeights(True)
        self.setExpandsOnDoubleClick(True)
        self.setup_drag_drop()

        self.itemChanged.connect(self.on_item_changed)

    def clear_tree(self):
        self.clear()

    def _create_item(self, text: str, path: Path) -> QTreeWidgetItem:
        item = QTreeWidgetItem([text])
        item.setData(0, Qt.UserRole, path)

        if self.mode != ArtsTreeMode.DESTINATION:
            item.setFlags(
                item.flags() | Qt.ItemIsUserCheckable
            )
            item.setCheckState(0, Qt.Checked)

        return item

    def add_art(self, art_path: Path):
        root_item = self._create_item(art_path.name, art_path)

        self.addTopLevelItem(root_item)

        for id_folder in art_path.iterdir():

            if not id_folder.is_dir():
                continue

            id_item = self._create_item(id_folder.name, id_folder)

            root_item.addChild(id_item)

            for file in id_folder.iterdir():

                if not file.is_file():
                    continue

                if file.suffix.lower() != ".dxf":
                    continue

                file_item = self._create_item(file.name, file)

                id_item.addChild(file_item)

    def load_arts(self, art_paths: list[Path]):
        self.clear_tree()

        for art_path in art_paths:
            self.add_art(art_path)

    def on_item_changed(
            self,
            item: QTreeWidgetItem,
            column: int,
    ):
        self.update_children(item)

    def update_children(
            self,
            item: QTreeWidgetItem,
    ):
        if item.childCount() == 0:
            return

        state = item.checkState(0)

        self.blockSignals(True)

        self.set_children_state(item, state)

        self.blockSignals(False)

    def set_children_state(
            self,
            item: QTreeWidgetItem,
            state: Qt.CheckState,
    ):
        for i in range(item.childCount()):
            child = item.child(i)

            child.setCheckState(0, state)
            self.set_children_state(child, state)

    def setup_drag_drop(self):

        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)

        if self.mode == ArtsTreeMode.AVAILABLE:
            self.setAcceptDrops(False)
        else:
            self.setAcceptDrops(True)

        self.setDragDropMode(QAbstractItemView.DragDrop)


        # self.set_item_checked()
        # self.set_single_art_mode(True)
        #
        # self.selected_art()
        #
        # self.dragEnterEvent()
        # self.dropEvent()
        # self.mimeData()