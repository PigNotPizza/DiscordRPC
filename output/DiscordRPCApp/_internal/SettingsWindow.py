from PyQt5 import QtWidgets, QtGui

class SettingsWindow(QtWidgets.QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Settings")
        self.setGeometry(200, 200, 400, 300)
        self.setWindowIcon(QtGui.QIcon('SettingsIcon.png'))

        self.dark_theme_button = QtWidgets.QPushButton("Dark Theme")
        self.dark_theme_button.clicked.connect(self.parent.toggle_theme)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.dark_theme_button)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.update_theme()

    def toggle_theme(self):
        self.parent.dark_theme = not self.parent.dark_theme
        self.update_theme()

    def update_theme(self):
        if self.parent.dark_theme:
            self.setStyleSheet(
                "background-color: #222; color: #EEE;"
                "QPushButton { background-color: #444; color: #EEE; }"
            )
        else:
            self.setStyleSheet(
                "background-color: #FFF; color: #000;"
                "QPushButton { background-color: #CCC; color: #000; }"
            )
