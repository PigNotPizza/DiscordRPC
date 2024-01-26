import sys
from pypresence import Presence
from PyQt5 import QtWidgets, QtGui, QtCore
import time
from settings_handler import SettingsHandler

class DiscordRPCApp(QtWidgets.QMainWindow):
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

    def __init__(self):
        super().__init__()

        self.settings_handler = SettingsHandler("settings_folder")  
        self.settings = self.settings_handler.load_settings()

        self.initUI()

        # Store references to child windows
        self.settings_window = None
        

    def initUI(self):
        self.setWindowTitle("Discord RPC")
        self.setGeometry(100, 100, 800, 600)

        self.dark_theme = False

        self.RPC = None

        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)

        layout = QtWidgets.QVBoxLayout(self.centralWidget)

        self.client_id_label = QtWidgets.QLabel("Client ID:")
        self.client_id_entry = QtWidgets.QLineEdit()

        self.frames_label = QtWidgets.QLabel("Number of Frames:")
        self.frames_entry = QtWidgets.QLineEdit()

        self.create_frames_button = QtWidgets.QPushButton("Create Frames")
        self.create_frames_button.clicked.connect(self.create_frame_entries)

        self.settings_action = QtWidgets.QAction(QtGui.QIcon('SettingsIcon.png'), 'Settings', self)
        self.settings_action.triggered.connect(self.open_settings)
        self.toolbar = self.addToolBar('Settings')
        self.toolbar.addAction(self.settings_action)

        self.load_button = QtWidgets.QPushButton()
        self.load_button.setIcon(QtGui.QIcon('LoadIcon.png'))
        self.load_button.setIconSize(QtCore.QSize(40, 40))
        self.load_button.setStyleSheet("border: none;")
        self.toolbar.addWidget(self.load_button)
        self.load_button.clicked.connect(self.load_settings)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.create_frames_button)
        button_layout.addStretch()

        self.frame_scroll = QtWidgets.QScrollArea()
        self.frame_scroll.setWidgetResizable(True)

        self.frame_entries_widget = QtWidgets.QWidget()
        self.frame_scroll.setWidget(self.frame_entries_widget)

        self.connect_button = QtWidgets.QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_rpc)

        self.disconnect_button = QtWidgets.QPushButton("Disconnect")
        self.disconnect_button.clicked.connect(self.disconnect_rpc)

        self.set_activity_button = QtWidgets.QPushButton("Set Activity")
        self.set_activity_button.clicked.connect(self.set_activity)

        self.save_action = QtWidgets.QAction(QtGui.QIcon('SaveIcon.png'), 'Save', self)
        self.save_action.triggered.connect(self.save_settings)
        self.toolbar.addAction(self.save_action)

        layout.addWidget(self.client_id_label)
        layout.addWidget(self.client_id_entry)
        layout.addWidget(self.frames_label)
        layout.addWidget(self.frames_entry)
        layout.addLayout(button_layout)

        layout.addWidget(self.frame_scroll)
        layout.addWidget(self.connect_button)
        layout.addWidget(self.disconnect_button)
        layout.addWidget(self.set_activity_button)
        self.toolbar.addAction(self.save_action)

        

        self.update_interval = 1000
        self.frame_entries = []
        self.defput_num = -1
        self.settings_window = None

    def set_activity(self):
        if self.RPC is not None:
            current_time = int(time.time())
            duration_text = self.frame_entries[self.defput_num]["duration"].text()
            end_time = current_time + int(duration_text) if duration_text.isdigit() else current_time

            activity = {
                "details": self.frame_entries[self.defput_num]["details"].text(),
                "state": f"Next update in {self.frame_entries[self.defput_num]['duration'].text()} milliseconds",
                "start": current_time,
                "end": end_time,
                "large_image": self.frame_entries[self.defput_num]["big_image"].text(),
                "large_text": "Large Image Text",
                "small_image": self.frame_entries[self.defput_num]["small_image"].text(),
                "small_text": "Small Image Text"
            }

            button1_label = self.frame_entries[self.defput_num]["button1_label"].text()
            button1_url = self.frame_entries[self.defput_num]["button1_url"].text()

            if button1_label and button1_url:
                activity["buttons"] = [{"label": button1_label, "url": button1_url}]
            else:
                activity["buttons"] = []

            button2_label = self.frame_entries[self.defput_num]["button2_label"].text()
            button2_url = self.frame_entries[self.defput_num]["button2_url"].text()

            if button2_label and button2_url:
                activity["buttons"].append({"label": button2_label, "url": button2_url})

            try:
                self.RPC.update(**activity)
                print("Rich Presence updated successfully")
            except Exception as e:
                print(f"Error updating Rich Presence: {e}")

            # Increment defput_num for the next update
            self.defput_num = (self.defput_num + 1) % len(self.frame_entries)


    def start_timer(self):
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.set_activity)
        self.timer.start(self.update_interval)



    def create_frame_entries(self):
        num_frames = self.frames_entry.text()
        if num_frames.isdigit():
            num_frames = int(num_frames)

            frame_layout = QtWidgets.QVBoxLayout(self.frame_entries_widget)

            for i in range(num_frames):
                frame_group_box = QtWidgets.QGroupBox(f"Frame {i+1}")
                frame_layout.addWidget(frame_group_box)

                frame_entry_layout = QtWidgets.QFormLayout(frame_group_box)

                # Remove this line
                # frame_entry = { ... }

                frame_entry = {
                    "duration": QtWidgets.QLineEdit(),
                    "big_image": QtWidgets.QLineEdit(),
                    "small_image": QtWidgets.QLineEdit(),
                    "details": QtWidgets.QLineEdit(),
                    "button1_label": QtWidgets.QLineEdit(),
                    "button1_url": QtWidgets.QLineEdit(),
                    "button2_label": QtWidgets.QLineEdit(),
                    "button2_url": QtWidgets.QLineEdit()
                }

                frame_entry_layout.addRow("Duration (milliseconds):", frame_entry["duration"])
                frame_entry_layout.addRow("Big Image URL:", frame_entry["big_image"])
                frame_entry_layout.addRow("Small Image URL:", frame_entry["small_image"])
                frame_entry_layout.addRow("Details:", frame_entry["details"])
                frame_entry_layout.addRow("Button Label:", frame_entry["button1_label"])
                frame_entry_layout.addRow("Button URL:", frame_entry["button1_url"])
                frame_entry_layout.addRow("Button2 Label:", frame_entry["button2_label"])
                frame_entry_layout.addRow("Button2 URL:", frame_entry["button2_url"])

                self.frame_entries.append(frame_entry)

                # Load existing frame texts if available
                settings = self.settings_handler.load_settings()
                frame_texts = settings.get("frame_texts", [])
                if i < len(frame_texts):
                    frame_text = frame_texts[i]
                    frame_entry["duration"].setText(frame_text.get("duration", ""))
                    frame_entry["big_image"].setText(frame_text.get("big_image", ""))
                    frame_entry["small_image"].setText(frame_text.get("small_image", ""))
                    frame_entry["details"].setText(frame_text.get("details", ""))
                    frame_entry["button1_label"].setText(frame_text.get("button1_label", ""))
                    frame_entry["button1_url"].setText(frame_text.get("button1_url", ""))
                    frame_entry["button2_label"].setText(frame_text.get("button2_label", ""))
                    frame_entry["button2_url"].setText(frame_text.get("button2_url", ""))



    def connect_rpc(self):
        client_id = self.client_id_entry.text()
        try:
            self.RPC = Presence(client_id)
            self.RPC.connect()
            print("Connected to Discord RPC")
            self.start_timer()  # Add this line
        except Exception as e:
            print(f"Error connecting to Discord RPC: {e}")



    def disconnect_rpc(self):
        if self.RPC:
            self.RPC.close()
            self.RPC = None

    def open_settings(self):
        if not self.settings_window or self.settings_window.isHidden():
            self.settings_window = self.SettingsWindow(self)
            self.settings_window.show()

    def toggle_theme(self):
        self.dark_theme = not self.dark_theme
        self.update_theme()

    def update_theme(self):
        if self.dark_theme:
            self.setStyleSheet(
                "background-color: #222; color: #EEE;"
                "QPushButton { background-color: #444; color: #EEE; }"
                "QLineEdit { background-color: #333; color: #EEE; border: 1px solid #555; }"
                "QLabel { color: #EEE; }"
                "QGroupBox { border: 1px solid #555; border-radius: 5px; margin-top: 10px; }"
            )
            self.settings_window.setStyleSheet(
                "background-color: #222; color: #EEE;"
                "QPushButton { background-color: #444; color: #EEE; }"
                "QLineEdit { background-color: #333; color: #EEE; border: 1px solid #555; }"
                "QLabel { color: #EEE; }"
                "QGroupBox { border: 1px solid #555; border-radius: 5px; margin-top: 10px; }"
            )

        else:
            self.setStyleSheet(
                "background-color: #FFF; color: #000;"
                "QPushButton { background-color: #CCC; color: #000; }"
                "QLineEdit { background-color: #FFF; color: #000; border: 1px solid #888; }"
                "QLabel { color: #000; }"
                "QGroupBox { border: 1px solid #888; border-radius: 5px; margin-top: 10px; }"
            )
            self.settings_window.setStyleSheet(
                "background-color: #FFF; color: #000;"
                "QPushButton { background-color: #CCC; color: #000; }"
                "QLineEdit { background-color: #FFF; color: #000; border: 1px solid #888; }"
                "QLabel { color: #000; }"
                "QGroupBox { border: 1px solid #888; border-radius: 5px; margin-top: 10px; }"
            )

        for widget in self.findChildren(QtWidgets.QWidget):
            if self.dark_theme:
                widget.setStyleSheet(
                    "background-color: #222; color: #EEE;"
                    "QPushButton { background-color: #444; color: #EEE; }"
                    "QLineEdit { background-color: #333; color: #EEE; border: 1px solid #555; }"
                    "QLabel { color: #EEE; }"
                )
            else:
                widget.setStyleSheet(
                    "background-color: #FFF; color: #000;"
                    "QPushButton { background-color: #CCC; color: #000; }"
                    "QLineEdit { background-color: #FFF; color: #000; border: 1px solid #888; }"
                    "QLabel { color: #000; }"
                )

    

    

    def save_settings(self):
        client_id = self.client_id_entry.text()
        frames = self.frames_entry.text()

        frame_texts = []
        for entry in self.frame_entries:
            frame_text = {
                "duration": entry["duration"].text(),
                "big_image": entry["big_image"].text(),
                "small_image": entry["small_image"].text(),
                "details": entry["details"].text(),
                "button1_label": entry["button1_label"].text(),
                "button1_url": entry["button1_url"].text(),
                "button2_label": entry["button2_label"].text(),
                "button2_url": entry["button2_url"].text(),
            }
            frame_texts.append(frame_text)

        settings = {
            "client_id": client_id,
            "frames": frames,
            "frame_texts": frame_texts
        }

        self.settings_handler.save_settings(settings)

    def load_settings(self):
        settings = self.settings_handler.load_settings()
        client_id = settings.get("client_id", "")
        frames = settings.get("frames", "")
        frame_texts = settings.get("frame_texts", [])

        self.client_id_entry.setText(client_id)
        self.frames_entry.setText(frames)

        for i, frame_text in enumerate(frame_texts):
            if i < len(self.frame_entries):
                entry = self.frame_entries[i]
                entry["duration"].setText(frame_text.get("duration", ""))
                entry["big_image"].setText(frame_text.get("big_image", ""))
                entry["small_image"].setText(frame_text.get("small_image", ""))
                entry["details"].setText(frame_text.get("details", ""))
                entry["button1_label"].setText(frame_text.get("button1_label", ""))
                entry["button1_url"].setText(frame_text.get("button1_url", ""))
                entry["button2_label"].setText(frame_text.get("button2_label", ""))
                entry["button2_url"].setText(frame_text.get("button2_url", ""))
            else:
                # If there are more frame_texts than frame_entries, create additional entries
                self.create_frame_entries()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = DiscordRPCApp()
    window.show()
    sys.exit(app.exec_())