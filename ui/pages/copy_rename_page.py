from PySide6 import QtWidgets, QtCore, QtGui


class CopyRenamePage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QtWidgets.QGridLayout(self)

        # === Source directory (row 0, full width) ===
        src_frame = QtWidgets.QFrame(self)
        src_frame.setFrameShape(QtWidgets.QFrame.Box)
        src_frame.setFrameShadow(QtWidgets.QFrame.Sunken)

        src_layout = QtWidgets.QVBoxLayout(src_frame)

        label = QtWidgets.QLabel("Source directory")
        label.setFont(QtGui.QFont("", 10))
        src_layout.addWidget(label)

        src_path_layout = QtWidgets.QHBoxLayout()
        self.dirEdit_p2 = QtWidgets.QLineEdit()
        self.dirEdit_p2.setFont(QtGui.QFont("", 12))
        self.loadFilesButton_p2 = QtWidgets.QPushButton("Load files")
        self.loadFilesButton_p2.setFont(QtGui.QFont("", 10))

        src_path_layout.addWidget(self.dirEdit_p2)
        src_path_layout.addWidget(self.loadFilesButton_p2)
        src_layout.addLayout(src_path_layout)

        main_layout.addWidget(src_frame, 0, 0, 1, 2)

        # ==================================================
        # === Row 1: TWO COLUMNS ============================
        # ==================================================

        # ---------- LEFT COLUMN ----------
        left_column = QtWidgets.QVBoxLayout()

        all_articles_group = QtWidgets.QGroupBox("Choose article numbers")
        all_articles_layout = QtWidgets.QVBoxLayout(all_articles_group)

        self.artsTree = QtWidgets.QTreeWidget()
        self.artsTree.setHeaderHidden(True)

        all_articles_layout.addWidget(self.artsTree)
        left_column.addWidget(all_articles_group)

        main_layout.addLayout(left_column, 1, 0)

        # ---------- RIGHT COLUMN (FROM + TO) ----------
        right_column = QtWidgets.QVBoxLayout()

        # --- FROM ---
        from_group = QtWidgets.QGroupBox("Article numbers to copy from")
        from_layout = QtWidgets.QVBoxLayout(from_group)
        self.srcArtsList = QtWidgets.QListWidget()
        from_layout.addWidget(self.srcArtsList)

        # --- TO ---
        to_group = QtWidgets.QGroupBox("Article numbers to copy to")
        to_layout = QtWidgets.QVBoxLayout(to_group)
        self.dstArtsList = QtWidgets.QListWidget()
        to_layout.addWidget(self.dstArtsList)

        right_column.addWidget(from_group)
        right_column.addWidget(to_group)

        main_layout.addLayout(right_column, 1, 1)

        # ==================================================
        # === Progress bar (row 2, full width) ============
        # ==================================================
        self.copyAndRenamePbar = QtWidgets.QProgressBar()
        self.copyAndRenamePbar.setValue(0)
        main_layout.addWidget(self.copyAndRenamePbar, 2, 0, 1, 2)

        # ==================================================
        # === Buttons (row 3) ==============================
        # ==================================================
        self.removeArtNumbers = QtWidgets.QPushButton("Remove article numbers")
        self.copyAndRenameButton = QtWidgets.QPushButton("Copy and rename")

        main_layout.addWidget(self.removeArtNumbers, 3, 0)
        main_layout.addWidget(self.copyAndRenameButton, 3, 1)

        # ==================================================
        # === Stretch settings =============================
        # ==================================================
        main_layout.setColumnStretch(0, 1)  # левая шире
        main_layout.setColumnStretch(1, 1)
        main_layout.setRowStretch(1, 1)

        # ==================================================
        # === Widgets registry =============================
        # ==================================================
        self.widgets = {
            "dirEdit": self.dirEdit_p2,
            "loadFiles": self.loadFilesButton_p2,
            "artsTree": self.artsTree,
            "srcArts": self.srcArtsList,
            "dstArts": self.dstArtsList,
            "removeArts": self.removeArtNumbers,
            "copy": self.copyAndRenameButton,
            "progress": self.copyAndRenamePbar,
        }
