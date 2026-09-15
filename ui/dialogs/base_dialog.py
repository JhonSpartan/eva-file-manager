from PySide6.QtWidgets import QDialog


class BaseDialog(QDialog):

    DEFAULT_MIN_WIDTH = 420

    def __init__(
            self,
            parent=None,
    ):
        super().__init__(parent)

        self.setMinimumWidth(
            self.DEFAULT_MIN_WIDTH
        )