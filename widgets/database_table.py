# widgets/database_table.py

from PySide6.QtCore import Qt, Signal, QRect
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QAbstractItemView,
    QHeaderView, QCheckBox
)



class DatabaseTableWidget(QWidget):

    addRequested = Signal()
    editRequested = Signal(int)
    deleteRequested = Signal(list)

    def __init__(
            self,
            headers: list[str],
            parent=None,
    ):
        super().__init__(parent)

        self.headers = headers

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QHBoxLayout()

        self.addButton = QPushButton("+ Add")
        self.editButton = QPushButton("Edit")
        self.deleteButton = QPushButton("Delete")

        toolbar.addWidget(self.addButton)
        toolbar.addWidget(self.editButton)
        toolbar.addWidget(self.deleteButton)
        toolbar.addStretch()

        layout.addLayout(toolbar)

        # Table
        self.table = QTableWidget()

        self.header = CheckBoxHeader(
            Qt.Horizontal,
            self.table,
        )
        self.table.setHorizontalHeader(self.header)

        self.table.setColumnCount(len(self.headers) + 1)
        self.table.setHorizontalHeaderLabels(
            [""] + self.headers
        )

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        layout.addWidget(self.table)

        # Status
        status_layout = QHBoxLayout()

        self.selectedLabel = QLabel("0 selected")
        self.recordsLabel = QLabel("0 records")

        status_layout.addWidget(self.selectedLabel)
        status_layout.addStretch()
        status_layout.addWidget(self.recordsLabel)

        layout.addLayout(status_layout)

    def setup_connections(self):
        self.addButton.clicked.connect(
            self.addRequested.emit
        )

        self.editButton.clicked.connect(
            self._on_edit_clicked
        )

        self.deleteButton.clicked.connect(
            self._on_delete_clicked
        )

        self.table.itemChanged.connect(
            self._update_status
        )

        self.header.checkStateChanged.connect(
            self._set_all_checked
        )

    def render_records(self, records: list[dict]):
        self.table.blockSignals(True)

        self.table.setRowCount(0)

        for record in records:
            row = self.table.rowCount()
            self.table.insertRow(row)

            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(
                checkbox_item.flags()
                | Qt.ItemIsUserCheckable
            )
            checkbox_item.setCheckState(
                Qt.Unchecked
            )

            checkbox_item.setData(
                Qt.UserRole,
                record["id"],
            )

            self.table.setItem(
                row,
                0,
                checkbox_item,
            )

            for column, key in enumerate(
                    record["values"],
                    start=1,
            ):
                item = QTableWidgetItem(
                    str(record["values"][key])
                )

                item.setFlags(
                    item.flags()
                    & ~Qt.ItemIsEditable
                )

                self.table.setItem(
                    row,
                    column,
                    item,
                )

        self.table.blockSignals(False)

        self._update_status()

    def _selected_record_ids(self) -> list[int]:
        selected_ids = []

        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)

            if (
                item is not None
                and item.checkState() == Qt.Checked
            ):
                record_id = item.data(
                    Qt.UserRole
                )

                selected_ids.append(
                    record_id
                )

        return selected_ids

    def _on_edit_clicked(self):
        record_ids = self._selected_record_ids()

        if len(record_ids) != 1:
            return

        self.editRequested.emit(
            record_ids[0]
        )

    def _on_delete_clicked(self):
        record_ids = (
            self._selected_record_ids()
        )

        if not record_ids:
            return

        self.deleteRequested.emit(
            record_ids
        )

    def _update_status(self):
        selected_count = len(
            self._selected_record_ids()
        )

        self.editButton.setEnabled(
            selected_count == 1
        )

        total_count = self.table.rowCount()

        self.selectedLabel.setText(
            f"{selected_count} selected"
        )

        self.recordsLabel.setText(
            f"{total_count} records"
        )

        if total_count == 0:
            state = Qt.Unchecked

        elif selected_count == 0:
            state = Qt.Unchecked

        elif selected_count == total_count:
            state = Qt.Checked

        else:
            state = Qt.PartiallyChecked

        self.header.set_check_state(
            state
        )

    def _set_all_checked(
            self,
            state: Qt.CheckState,
    ):
        self.table.blockSignals(True)

        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)

            if item is not None:
                item.setCheckState(state)

        self.table.blockSignals(False)

        self._update_status()

class CheckBoxHeader(QHeaderView):

    checkStateChanged = Signal(Qt.CheckState)

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)

        self.checkbox = HeaderCheckBox(self)
        self.checkbox.setTristate(True)

        self.checkbox.stateChanged.connect(
            self._on_state_changed
        )

        self.sectionResized.connect(
            self._update_checkbox_position
        )

        self.sectionMoved.connect(
            self._update_checkbox_position
        )

    def _on_state_changed(self, state):
        self.checkStateChanged.emit(
            Qt.CheckState(state)
        )

    def set_check_state(
            self,
            state: Qt.CheckState,
    ):
        self.checkbox.blockSignals(True)

        self.checkbox.setCheckState(
            state
        )

        self.checkbox.blockSignals(False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_checkbox_position()

    def _update_checkbox_position(self):
        section_x = self.sectionViewportPosition(0)
        section_width = self.sectionSize(0)

        checkbox_size = self.checkbox.sizeHint()

        x = (
            section_x
            + (section_width - checkbox_size.width()) // 2
        )

        y = (
            (self.height() - checkbox_size.height()) // 2
        )

        self.checkbox.move(
            x,
            y,
        )

class HeaderCheckBox(QCheckBox):

    def nextCheckState(self):
        if self.checkState() == Qt.Checked:
            self.setCheckState(Qt.Unchecked)
        else:
            self.setCheckState(Qt.Checked)