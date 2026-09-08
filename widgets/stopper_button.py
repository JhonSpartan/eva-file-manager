from PySide6.QtWidgets import QPushButton

from models.catalog_models import StopperRecord


class StopperButton(QPushButton):

    def __init__(
            self,
            stopper: StopperRecord,
            parent=None,
    ):
        super().__init__(
            stopper.stopper_name,
            parent,
        )

        self.stopper = stopper

        self.setCheckable(True)

        self.setFixedSize(
            60,
            60,
        )

        self.setStyleSheet("""
            QPushButton {
                border: 2px solid;
                border-radius: 30px;
            }

            QPushButton:checked {
                border: 4px solid;
            }
        """)