from PySide6.QtCore import Qt, Signal
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
            stretch_column: int | None = None,
            center_columns: set[int] | None = None,
            parent=None,
    ):
        super().__init__(parent)

        self.headers = headers
        self.stretch_column = stretch_column
        self.center_columns = center_columns or set()

        self.setup_ui()
        self.setup_connections()


    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QHBoxLayout()

        self.addButton = QPushButton("+ Добавить")
        self.editButton = QPushButton("Изменить")
        self.deleteButton = QPushButton("Удалить")

        toolbar.addWidget(self.addButton)
        toolbar.addWidget(self.editButton)
        toolbar.addWidget(self.deleteButton)
        toolbar.addStretch()

        layout.addLayout(toolbar)

        # Table
        self.table = QTableWidget()

        self.table.setAlternatingRowColors(True)

        self.header = CheckBoxHeader(
            Qt.Horizontal,
            self.table,
        )
        self.table.setHorizontalHeader(self.header)

        self.table.setColumnCount(len(self.headers) + 1)
        self.table.setHorizontalHeaderLabels(
            [""] + self.headers
        )

        header = self.table.horizontalHeader()

        for column in range(
                self.table.columnCount()
        ):
            if column == self.stretch_column:
                header.setSectionResizeMode(
                    column,
                    QHeaderView.Stretch,
                )
            else:
                header.setSectionResizeMode(
                    column,
                    QHeaderView.ResizeToContents,
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

        self.selectedLabel = QLabel("Выбрано: 0")
        self.recordsLabel = QLabel("Записей: 0")

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

        self.header.checkStateChanged.connect(
            self._set_all_checked
        )

    def render_records(self, records: list[dict]):
        self.table.blockSignals(True)

        self.table.setRowCount(0)

        for record in records:
            row = self.table.rowCount()
            self.table.insertRow(row)

            checkbox = QCheckBox()

            checkbox_container = QWidget()
            checkbox_container.setStyleSheet(
                "background-color: transparent;"
            )
            checkbox_layout = QHBoxLayout(
                checkbox_container
            )

            checkbox_layout.setContentsMargins(
                0, 0, 0, 0
            )

            checkbox_layout.setAlignment(
                Qt.AlignCenter
            )

            checkbox_layout.addWidget(
                checkbox
            )

            checkbox.setProperty(
                "record_id",
                record["id"],
            )

            checkbox.stateChanged.connect(
                self._update_status
            )

            self.table.setCellWidget(
                row,
                0,
                checkbox_container,
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

                if column in self.center_columns:
                    item.setTextAlignment(
                        Qt.AlignCenter
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
            container = self.table.cellWidget(
                row,
                0,
            )

            if container is None:
                continue

            checkbox = container.findChild(
                QCheckBox
            )

            if checkbox is None:
                continue

            if checkbox.isChecked():
                record_id = checkbox.property(
                    "record_id"
                )

                selected_ids.append(
                    record_id
                )

        return selected_ids

    def _set_all_checked(
            self,
            state: Qt.CheckState,
    ):
        for row in range(self.table.rowCount()):
            container = self.table.cellWidget(
                row,
                0,
            )

            if container is None:
                continue

            checkbox = container.findChild(
                QCheckBox
            )

            if checkbox is None:
                continue

            checkbox.blockSignals(True)

            checkbox.setChecked(
                state == Qt.Checked
            )

            checkbox.blockSignals(False)

        self._update_status()


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
            f"Выбрано: {selected_count}"
        )

        self.recordsLabel.setText(
            f"Записей: {total_count}"
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

class CheckBoxHeader(QHeaderView):

    checkStateChanged = Signal(Qt.CheckState)

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)

        self.checkbox = HeaderCheckBox(self)
        self.checkbox.setObjectName("headerCheckBox")
        self.checkbox.setTristate(True)
        self.checkbox.setFixedSize(14, 14)

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
            +  2
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