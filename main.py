if __name__ == "__main__":
    import sys
    from pathlib import Path
    from PySide6.QtGui import QIcon

    from PySide6.QtWidgets import QApplication
    from ui.main_window import MainWindow


    from utils.resource_path import resource_path

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    app.setWindowIcon(
        QIcon(
            str(
                resource_path(
                    "icons",
                    "fileforge.ico",
                )
            )
        )
    )

    app_dir = Path(__file__).parent

    style_path = (
        app_dir
        / "ui"
        / "styles"
        / "dark.qss"
    )

    with style_path.open(
            "r",
            encoding="utf-8",
    ) as style_file:
        stylesheet = style_file.read()

    for icon_name in (
            "spin-up.svg",
            "spin-down.svg",
            "checkbox-partial.svg",
    ):
        stylesheet = stylesheet.replace(
            f"resources/icons/{icon_name}",
            resource_path(
                "icons",
                icon_name,
            ).as_posix(),
        )

    app.setStyleSheet(stylesheet)


    app.setStyleSheet(stylesheet)

    window = MainWindow()
    window.showMaximized()

    sys.exit(app.exec())