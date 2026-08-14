from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView
from enum import Enum
from pathlib import Path
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag

ART_MIME_TYPE = "application/x-eva-art"

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

    def _create_item(self, text: str, path: Path, draggable: bool) -> QTreeWidgetItem:
        item = QTreeWidgetItem([text])
        item.setData(0, Qt.UserRole, path)

        flags = item.flags()

        if self.mode != ArtsTreeMode.AVAILABLE:
            flags |= Qt.ItemIsUserCheckable
            item.setCheckState(0, Qt.Checked)

        if draggable:
            flags |= Qt.ItemIsDragEnabled
        else:
            flags &= ~Qt.ItemIsDragEnabled

        item.setFlags(flags)

        return item

    def _id_sort_key(self, path: Path):
        try:
            return (0, int(path.name))
        except ValueError:
            return (1, path.name)

    def add_art(self, art_path: Path):
        root_item = self._create_item(art_path.name, art_path, draggable=True)

        self.addTopLevelItem(root_item)

        id_folders = sorted(
            (
                folder
                for folder in art_path.iterdir()
                if folder.is_dir()
            ),
            key=self._id_sort_key
        )

        for id_folder in id_folders:

            if not id_folder.is_dir():
                continue

            id_item = self._create_item(id_folder.name, id_folder, draggable=False)

            root_item.addChild(id_item)

            for file in id_folder.iterdir():

                if not file.is_file():
                    continue

                if file.suffix.lower() != ".dxf":
                    continue

                file_item = self._create_item(file.name, file, draggable=False)

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

    def dragEnterEvent(self, event):
        if self.mode == ArtsTreeMode.AVAILABLE:
            event.ignore()
            return

        if event.mimeData().hasFormat(ART_MIME_TYPE):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if self.mode == ArtsTreeMode.AVAILABLE:
            event.ignore()
            return

        if event.mimeData().hasFormat(ART_MIME_TYPE):
            event.acceptProposedAction()
        else:
            event.ignore()

    def _remove_art(self, path: Path):
        for index in range(self.topLevelItemCount()):
            item = self.topLevelItem(index)

            if item.data(0, Qt.UserRole) == path:
                self.takeTopLevelItem(index)
                return

    def startDrag(self, supportedActions):
        item = self.currentItem()

        if item is None:
            return

        path = item.data(0, Qt.UserRole)

        if not isinstance(path, Path):
            return

        mime_data = QMimeData()
        mime_data.setData(
            ART_MIME_TYPE,
            str(path).encode("utf-8")
        )

        drag = QDrag(self)
        drag.setMimeData(mime_data)

        result = drag.exec(Qt.MoveAction)

        if result == Qt.MoveAction:
            self._remove_art(path)

    def dropEvent(self, event):
        if not event.mimeData().hasFormat(ART_MIME_TYPE):
            event.ignore()
            return

        data = event.mimeData().data(ART_MIME_TYPE)
        path = Path(bytes(data).decode("utf-8"))

        if not path.is_dir():
            event.ignore()
            return

        self.add_art(path)

        event.acceptProposedAction()
        # self.set_item_checked()
        # self.set_single_art_mode(True)
        #
        # self.selected_art()
        #
        # self.dragEnterEvent()
        # self.dropEvent()
        # self.mimeData()