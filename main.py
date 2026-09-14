if __name__ == "__main__":
    import sys
    from pathlib import Path

    from PySide6.QtWidgets import QApplication
    from ui.main_window import MainWindow

    app = QApplication(sys.argv)

    style_path = (
        Path(__file__).parent
        / "ui"
        / "styles"
        / "dark.qss"
    )

    with style_path.open(
        "r",
        encoding="utf-8",
    ) as style_file:
        app.setStyleSheet(
            style_file.read()
        )

    window = MainWindow()
    window.show()

    sys.exit(app.exec())