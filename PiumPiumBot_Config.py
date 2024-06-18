from os.path import dirname, abspath

class PiumPiumBot_Config:
    def __init__(self):
        self.version = '1.0.2'
        self.type = "PROD"

        ws_path = dirname(abspath(__file__))
        temp_path = ws_path + "/temp"
        self.TEMP_PATH = temp_path