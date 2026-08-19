from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView
from enum import Enum
from pathlib import Path
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag
import json
from models.copy_models import ArtSelection, SelectionState

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
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
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
        self.blockSignals(True)

        try:
            self.update_children(item)
            self.update_parent(item)

        finally:
            self.blockSignals(False)

    def update_children(
            self,
            item: QTreeWidgetItem,
    ):
        if item.childCount() == 0:
            return

        state = item.checkState(0)

        if state == Qt.PartiallyChecked:
            return

        self.set_children_state(
            item,
            state,
        )

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
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(ART_MIME_TYPE):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat(ART_MIME_TYPE):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

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
        selected_items = self.selectedItems()

        if not selected_items:
            return

        paths = []

        for item in selected_items:

            # Только ART верхнего уровня
            if item.parent() is not None:
                continue

            path = item.data(0, Qt.UserRole)

            if not isinstance(path, Path):
                continue

            if not path.is_dir():
                continue

            paths.append(str(path))

        if not paths:
            return

        mime_data = QMimeData()
        mime_data.setData(
            ART_MIME_TYPE,
            json.dumps(paths).encode("utf-8")
        )

        drag = QDrag(self)
        drag.setMimeData(mime_data)

        result = drag.exec(Qt.MoveAction)

        if result == Qt.MoveAction:
            for path in paths:
                self._remove_art(Path(path))

    def dropEvent(self, event):
        if not event.mimeData().hasFormat(ART_MIME_TYPE):
            event.ignore()
            return

        # Не разрешаем бросать ART обратно в то же самое дерево
        if event.source() is self:
            event.ignore()
            return

        data = event.mimeData().data(ART_MIME_TYPE)

        try:
            paths = json.loads(
                bytes(data).decode("utf-8")
            )
        except (json.JSONDecodeError, UnicodeDecodeError):
            event.ignore()
            return

        if not isinstance(paths, list):
            event.ignore()
            return

        arts = []

        for raw_path in paths:
            path = Path(raw_path)

            if path.is_dir():
                arts.append(path)

        if not arts:
            event.ignore()
            return

        # SOURCE — максимум один ART
        if self.mode == ArtsTreeMode.SOURCE:
            if self.topLevelItemCount() + len(arts) > 1:
                event.ignore()
                return

        for art_path in arts:
            self.add_art(art_path)

        event.setDropAction(Qt.MoveAction)
        event.accept()

    def get_art_selections(self) -> list[ArtSelection]:
        selections = []

        for art_index in range(self.topLevelItemCount()):
            art_item = self.topLevelItem(art_index)
            art_path = art_item.data(0, Qt.UserRole)

            if not isinstance(art_path, Path):
                continue

            id_states = {}
            files_by_id = {}

            for id_index in range(art_item.childCount()):
                id_item = art_item.child(id_index)
                id_path = id_item.data(0, Qt.UserRole)

                if not isinstance(id_path, Path):
                    continue

                state = self.get_id_selection_state(id_item)
                id_states[id_path] = state

                checked_files = []

                for file_index in range(id_item.childCount()):
                    file_item = id_item.child(file_index)

                    if file_item.checkState(0) != Qt.Checked:
                        continue

                    file_path = file_item.data(0, Qt.UserRole)

                    if isinstance(file_path, Path):
                        checked_files.append(file_path)

                files_by_id[id_path] = checked_files

            selections.append(
                ArtSelection(
                    art_path=art_path,
                    id_states=id_states,
                    files_by_id=files_by_id,
                )
            )

        return selections

    def get_id_selection_state(
            self,
            id_item: QTreeWidgetItem,
    ) -> SelectionState:

        if id_item.childCount() == 0:
            return SelectionState.NONE

        checked_count = 0

        for index in range(id_item.childCount()):
            file_item = id_item.child(index)

            if file_item.checkState(0) == Qt.Checked:
                checked_count += 1

        if checked_count == 0:
            return SelectionState.NONE

        if checked_count == id_item.childCount():
            return SelectionState.FULL

        return SelectionState.PARTIAL

    def update_parent(
            self,
            item: QTreeWidgetItem,
    ):
        parent = item.parent()

        if parent is None:
            return

        states = [
            parent.child(index).checkState(0)
            for index in range(parent.childCount())
        ]

        if all(
                state == Qt.Checked
                for state in states
        ):
            parent_state = Qt.Checked

        elif all(
                state == Qt.Unchecked
                for state in states
        ):
            parent_state = Qt.Unchecked

        else:
            parent_state = Qt.PartiallyChecked

        parent.setCheckState(
            0,
            parent_state,
        )

        self.update_parent(parent)

    def remove_selected_arts(self):
        selected_items = self.selectedItems()

        for item in selected_items:
            # удаляем только ART верхнего уровня
            if item.parent() is not None:
                continue

            index = self.indexOfTopLevelItem(item)

            if index != -1:
                self.takeTopLevelItem(index)

    def refresh_art(self, art_path: Path):
        self._remove_art(art_path)
        self.add_art(art_path)