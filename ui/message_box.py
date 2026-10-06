from PySide6.QtWidgets import QMessageBox, QLabel


def show_message(
        parent,
        icon: QMessageBox.Icon,
        title: str,
        text: str,
        min_width: int = 300,
) -> None:

    dialog = QMessageBox(parent)
    dialog.setIcon(icon)
    dialog.setWindowTitle(title)
    dialog.setText(text)

    dialog.setStandardButtons(
        QMessageBox.StandardButton.Ok
    )

    label = dialog.findChild(
        QLabel,
        "qt_msgbox_label",
    )

    if label:
        label.setMinimumWidth(min_width)

    dialog.exec()