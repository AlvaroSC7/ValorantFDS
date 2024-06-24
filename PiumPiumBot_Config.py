from os.path import dirname, abspath

class PiumPiumBot_Config:
    def __init__(self):
        self.version = '1.0.4'
        self.type = 'DEV'

        ws_path = dirname(abspath(__file__))
        temp_path = ws_path + "/temp"
        self.TEMP_PATH = temp_path