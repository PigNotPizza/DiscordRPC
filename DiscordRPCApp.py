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
            self.dark_theme = not self.dark_theme
            self.update_theme()

            # Check if the settings window is open and update its theme
            if self.settings_window and not self.settings_window.isHidden():
                self.settings_window.update_theme()




        def update_theme(self):
            theme_color, text_color, border_color = ("#222", "#EEE", "#555") if self.parent.dark_theme else ("#FFF", "#000", "#888")
            style_sheet = (
                f"background-color: {theme_color}; color: {text_color};"
                "QPushButton { background-color: #444; color: #EEE; }"
                "QLineEdit { background-color: #333; color: #EEE; border: 1px solid #555; }"
                "QLabel { color: #EEE; }"
                "QGroupBox { border: 1px solid %s; border-radius: 5px; margin-top: 10px; }" % border_color
            )
            self.setStyleSheet(style_sheet)

            
    def apply_theme(self):
        theme_color, text_color, border_color = ("#222", "#EEE", "#555") if self.dark_theme else ("#FFF", "#000", "#888")
        style_sheet = (
            f"background-color: {theme_color}; color: {text_color};"
            "QPushButton { background-color: #444; color: #EEE; }"
            "QLineEdit { background-color: #333; color: #EEE; border: 1px solid #555; }"
            "QLabel { color: #EEE; }"
            "QGroupBox { border: 1px solid %s; border-radius: 5px; margin-top: 10px; }" % border_color
        )
        self.setStyleSheet(style_sheet)
    
        # Check if the settings window is open and update its theme
        if self.settings_window and not self.settings_window.isHidden():
            self.settings_window.apply_theme()



    def __init__(self):
        super().__init__()

        self.settings_handler = SettingsHandler("settings_folder")  
        self.settings = self.settings_handler.load_settings()

        self.init_ui()

        self.settings_window = None
        self.search_window = None

    def init_ui(self):
        self.setWindowTitle("Discord RPC")
        self.setGeometry(100, 100, 800, 600)

        self.dark_theme = False
        self.RPC = None

        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)

        layout = QtWidgets.QVBoxLayout(self.central_widget)

        self.client_id_label = self.create_label("Client ID:")
        self.client_id_entry = self.create_line_edit()

        self.frames_label = self.create_label("Number of Frames:")
        self.frames_entry = self.create_line_edit()

        self.create_frames_button = self.create_button("Create Frames", self.create_frame_entries)

        self.setup_toolbar()

        self.load_button = self.create_load_button()
        layout.addWidget(self.client_id_label)
        layout.addWidget(self.client_id_entry)
        layout.addWidget(self.frames_label)
        layout.addWidget(self.frames_entry)
        layout.addWidget(self.create_frames_button)

        self.frame_scroll = self.create_scroll_area()

        self.frame_entries_widget = QtWidgets.QWidget()
        self.frame_scroll.setWidget(self.frame_entries_widget)

        self.connect_button = self.create_button("Connect", self.connect_rpc)
        self.disconnect_button = self.create_button("Disconnect", self.disconnect_rpc)
        self.set_activity_button = self.create_button("Set Activity", self.set_activity)
        self.save_action = self.create_action(QtGui.QIcon('SaveIcon.png'), 'Save', self.save_settings)

        layout.addWidget(self.frame_scroll)
        layout.addWidget(self.connect_button)
        layout.addWidget(self.disconnect_button)
        layout.addWidget(self.set_activity_button)

        self.toolbar.addAction(self.save_action)

        

        self.update_interval = 1000
        self.frame_entries = []
        self.default_num = -1
        self.settings_window = None

    def create_label(self, text):
        label = QtWidgets.QLabel(text)
        return label

    def create_line_edit(self):
        line_edit = QtWidgets.QLineEdit()
        return line_edit

    def create_button(self, text, func):
        button = QtWidgets.QPushButton(text)
        button.clicked.connect(func)
        return button

    def create_load_button(self):
        load_button = self.create_button("", self.load_settings)
        load_button.setIcon(QtGui.QIcon('LoadIcon.png'))
        load_button.setIconSize(QtCore.QSize(40, 40))
        load_button.setStyleSheet("border: none;")
        self.toolbar.addWidget(load_button)
        load_button.clicked.connect(self.load_settings)
        return load_button

    def create_scroll_area(self):
        frame_scroll = QtWidgets.QScrollArea()
        frame_scroll.setWidgetResizable(True)
        return frame_scroll

    def setup_toolbar(self):
        self.settings_action = self.create_action(QtGui.QIcon('SettingsIcon.png'), 'Settings', self.open_settings)
        self.toolbar = self.addToolBar('Settings')
        self.toolbar.addAction(self.settings_action)

    def create_action(self, icon, text, func):
        action = QtWidgets.QAction(icon, text, self)
        action.triggered.connect(func)
        return action

    def set_activity(self):
        if self.RPC is not None:
            current_time = int(time.time())
            duration_text = self.frame_entries[self.default_num]["duration"].text()
            end_time = current_time + int(duration_text) if duration_text.isdigit() else current_time

            activity = {
                "details": self.frame_entries[self.default_num]["details"].text(),
                "state": f"Next update in {self.frame_entries[self.default_num]['duration'].text()} milliseconds",
                "start": current_time,
                "end": end_time,
                "large_image": self.frame_entries[self.default_num]["big_image"].text(),
                "large_text": "Large Image Text",
                "small_image": self.frame_entries[self.default_num]["small_image"].text(),
                "small_text": "Small Image Text"
            }

            self.update_buttons(activity)

            try:
                self.RPC.update(**activity)
                print("Rich Presence updated successfully")
            except Exception as e:
                print(f"Error updating Rich Presence: {e}")

            self.default_num = (self.default_num + 1) % len(self.frame_entries)

    def update_buttons(self, activity):
        for i in range(1, 3):
            button_label = self.frame_entries[self.default_num][f"button{i}_label"].text()
            button_url = self.frame_entries[self.default_num][f"button{i}_url"].text()

            if button_label and button_url:
                activity["buttons"] = [{"label": button_label, "url": button_url}]
            else:
                activity["buttons"] = []

    def start_timer(self):
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.set_activity)
        self.timer.start(self.update_interval)

    def create_frame_entries(self):
        num_frames = self.frames_entry.text()
        if num_frames.isdigit():
            num_frames = int(num_frames)

            # Ensure the layout is set for self.frame_entries_widget
            if self.frame_entries_widget.layout() is None:
                self.frame_entries_widget.setLayout(QtWidgets.QVBoxLayout())

            # Clear existing widgets inside frame_entries_widget
            for widget in reversed(range(self.frame_entries_widget.layout().count())):
                self.frame_entries_widget.layout().itemAt(widget).widget().setParent(None)

            frame_layout = self.frame_entries_widget.layout()

            for i in range(num_frames):
                frame_widget = QtWidgets.QWidget()
                frame_group_box = self.create_group_box(f"Frame {i+1}")
                frame_widget.setLayout(QtWidgets.QVBoxLayout())
                frame_widget.layout().addWidget(frame_group_box)

                frame_entry_layout = QtWidgets.QFormLayout(frame_group_box)

                frame_entry = self.create_frame_entry()
                frame_entry_layout.addRow("Duration (milliseconds):", frame_entry["duration"])
                frame_entry_layout.addRow("Big Image URL:", frame_entry["big_image"])
                frame_entry_layout.addRow("Small Image URL:", frame_entry["small_image"])
                frame_entry_layout.addRow("Details:", frame_entry["details"])

                for j in range(1, 3):
                    frame_entry_layout.addRow(f"Button{j} Label:", frame_entry[f"button{j}_label"])
                    frame_entry_layout.addRow(f"Button{j} URL:", frame_entry[f"button{j}_url"])

                self.frame_entries.append(frame_entry)
                self.load_existing_frame_texts(i, frame_entry)

                frame_layout.addWidget(frame_widget)






    def create_frame_entry(self):
        return {
            "duration": self.create_line_edit(),
            "big_image": self.create_line_edit(),
            "small_image": self.create_line_edit(),
            "details": self.create_line_edit(),
            "button1_label": self.create_line_edit(),
            "button1_url": self.create_line_edit(),
            "button2_label": self.create_line_edit(),
            "button2_url": self.create_line_edit()
        }

    def create_group_box(self, title):
        frame_group_box = QtWidgets.QGroupBox(title)
        return frame_group_box

    def load_existing_frame_texts(self, i, frame_entry):
        settings = self.settings_handler.load_settings()
        frame_texts = settings.get("frame_texts", [])

        if i < len(frame_texts):
            frame_text = frame_texts[i]
            for key in frame_entry.keys():
                frame_entry[key].setText(frame_text.get(key, ""))

    def connect_rpc(self):
        client_id = self.client_id_entry.text()
        try:
            self.RPC = Presence(client_id)
            self.RPC.connect()
            print("Connected to Discord RPC")
            self.start_timer()
        except Exception as e:
            print(f"Error connecting to Discord RPC: {e}")

    def disconnect_rpc(self):
        if self.RPC:
            self.RPC.close()
            self.RPC = None

    def open_settings(self):
        if not self.settings_window or self.settings_window.isHidden():
            self.settings_window = self.SettingsWindow(self)  # Pass only the 'parent' argument
            self.settings_window.show()



    def toggle_theme(self):
        self.dark_theme = not self.dark_theme
        self.update_theme()

        # Check if the settings window is open and update its theme
        if self.settings_window and not self.settings_window.isHidden():
            self.settings_window.update_theme()


    def update_theme(self):
        theme_color, text_color, border_color = ("#222", "#EEE", "#555") if self.dark_theme else ("#FFF", "#000", "#888")
        style_sheet = (
            f"background-color: {theme_color}; color: {text_color};"
            "QPushButton { background-color: #444; color: #EEE; }"
            "QLineEdit { background-color: #333; color: #EEE; border: 1px solid #555; }"
            "QLabel { color: #EEE; }"
            "QGroupBox { border: 1px solid %s; border-radius: 5px; margin-top: 10px; }" % border_color
        )
        self.setStyleSheet(style_sheet)

        # Check if the settings window is open and update its theme
        if self.settings_window and not self.settings_window.isHidden():
            self.settings_window.setStyleSheet(style_sheet)


    

    def closeEvent(self, event):
        if hasattr(self, 'search_window') and self.search_window:
            self.search_window.close()

        super().closeEvent(event)

    def save_settings(self):
        client_id = self.client_id_entry.text()
        frames = self.frames_entry.text()

        frame_texts = []
        for entry in self.frame_entries:
            frame_text = {key: entry[key].text() for key in entry.keys()}
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
                for key in entry.keys():
                    entry[key].setText(frame_text.get(key, ""))
            else:
                self.create_frame_entries()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = DiscordRPCApp()
    window.show()
    sys.exit(app.exec_())
