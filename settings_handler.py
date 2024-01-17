import json
import os

class SettingsHandler:
    def __init__(self, folder_name):
        self.folder_name = folder_name
        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)
        self.settings_file = os.path.join(self.folder_name, "settings.json")

    def save_settings(self, settings):
        with open(self.settings_file, "w") as file:
            json.dump(settings, file)

    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as file:
                return json.load(file)
        return {}
