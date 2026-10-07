from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QListWidget


class FileDropListWidget(QListWidget):

    pathsDropped = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            return

        event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            return

        event.ignore()

    def dropEvent(self, event):
        if not event.mimeData().hasUrls():
            event.ignore()
            return

        paths = [
            Path(url.toLocalFile())
            for url in event.mimeData().urls()
            if url.isLocalFile()
        ]

        if not paths:
            event.ignore()
            return

        self.pathsDropped.emit(
            paths
        )

        event.acceptProposedAction()