from os.path import dirname, abspath

class PiumPiumBot_Config:
    def __init__(self):
        #Version
        self.version = '1.0.4'
        self.type = 'DEV'
        #Paths
        self.WS_PATH = dirname(abspath(__file__))
        self.TEMP_PATH = self.WS_PATH + "/temp"
        self.PRIVATE_PATH = self.WS_PATH + "/private"
