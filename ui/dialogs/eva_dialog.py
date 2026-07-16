from PySide6 import QtCore, QtGui, QtWidgets


class EvaDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("EvaDialog")
        self.resize(1000, 700)
        self.setMinimumSize(QtCore.QSize(0, 120))
        self.setMaximumSize(QtCore.QSize(16777215, 16777215))

        # --- Основная сетка ---
        self.gridLayout_2 = QtWidgets.QGridLayout(self)

        # === Заголовок ===
        self.label = QtWidgets.QLabel("Configurate new EVA", self)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 2)

        # === Левая часть формы ===
        self.evaForm = QtWidgets.QFrame(self)
        self.evaForm.setFrameShape(QtWidgets.QFrame.Box)
        self.evaForm.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.gridLayout = QtWidgets.QGridLayout(self.evaForm)

        font_label = QtGui.QFont()
        font_label.setPointSize(14)

        font_input = QtGui.QFont()
        font_input.setPointSize(12)

        font_btn = QtGui.QFont()
        font_btn.setPointSize(10)

        # EVA input
        self.label_4 = QtWidgets.QLabel("EVA", self.evaForm)
        self.label_4.setFont(font_label)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)

        self.evaInput = QtWidgets.QLineEdit(self.evaForm)
        self.evaInput.setFont(font_input)
        self.gridLayout.addWidget(self.evaInput, 0, 1, 1, 1)

        self.addEva = QtWidgets.QPushButton("Add", self.evaForm)
        self.addEva.setFont(font_btn)
        self.gridLayout.addWidget(self.addEva, 0, 2, 1, 1)

        # Art input
        self.label_3 = QtWidgets.QLabel("Art. number", self.evaForm)
        self.label_3.setFont(font_label)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)

        self.artIInput = QtWidgets.QLineEdit(self.evaForm)
        self.artIInput.setFont(font_input)
        self.gridLayout.addWidget(self.artIInput, 1, 1, 1, 1)

        self.addArt = QtWidgets.QPushButton("Add", self.evaForm)
        self.addArt.setFont(font_btn)
        self.gridLayout.addWidget(self.addArt, 1, 2, 1, 1)

        self.gridLayout_2.addWidget(self.evaForm, 1, 0, 1, 2)

        # === Основное содержимое (scroll) ===
        self.stoppersArea = QtWidgets.QScrollArea(self)
        self.stoppersArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.stoppersArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_2.addWidget(self.stoppersArea, 2, 0, 1, 2)

        # === Кнопки и списки ===
        self.clearSelectedStoppers = QtWidgets.QPushButton("Clear selected stoppers", self)
        self.clearSelectedStoppers.setFont(font_btn)
        self.gridLayout_2.addWidget(self.clearSelectedStoppers, 3, 0, 1, 2)

        self.suggestedStopperKomboList = QtWidgets.QListWidget(self)
        self.confirmedStopperKomboList = QtWidgets.QListWidget(self)
        self.gridLayout_2.addWidget(self.suggestedStopperKomboList, 4, 0, 1, 1)
        self.gridLayout_2.addWidget(self.confirmedStopperKomboList, 4, 1, 1, 1)

        self.addSelectedStoppers = QtWidgets.QPushButton("Add selected stoppers", self)
        self.addSelectedStoppers.setFont(font_btn)
        self.gridLayout_2.addWidget(self.addSelectedStoppers, 5, 0, 1, 2)

        # === Настройки сетки ===
        self.gridLayout_2.setRowMinimumHeight(2, 800)
        self.gridLayout_2.setRowMinimumHeight(4, 200)
        self.gridLayout_2.setColumnStretch(0, 500)
        self.gridLayout_2.setColumnStretch(1, 500)

        self.setWindowTitle("EVA Configurator")

        # --- Здесь можно привязать сигналы ---
        self.addEva.clicked.connect(self.add_eva_clicked)
        self.addArt.clicked.connect(self.add_art_clicked)
        self.clearSelectedStoppers.clicked.connect(self.clear_stoppers)
        self.addSelectedStoppers.clicked.connect(self.add_selected_stoppers)

    # === Примеры слотов ===
    def add_eva_clicked(self):
        name = self.evaInput.text().strip()
        if name:
            self.evaNameDialog.setText(f"EVA: {name}")

    def add_art_clicked(self):
        art = self.artIInput.text().strip()
        if art:
            self.artNamesDialog.setText(f"Art: {art}")

    def clear_stoppers(self):
        self.suggestedStopperKomboList.clear()
        self.confirmedStopperKomboList.clear()

    def add_selected_stoppers(self):
        # пример будущего функционала — динамическая вставка
        self.confirmedStopperKomboList.addItem("Example stopper")


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    dlg = EvaDialog()
    dlg.show()
    app.exec()
