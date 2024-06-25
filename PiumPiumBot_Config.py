from os.path import dirname, abspath

class PiumPiumBot_Config:
    def __init__(self):
        #Version
        self.version = '1.0.5'
        self.type = 'DEV'
        self.host = PiumPiumBot_Host(url= 'dev', id= 'dev', node= 'dev')
        #Paths
        self.WS_PATH = dirname(abspath(__file__))
        self.TEMP_PATH = self.WS_PATH + "/temp"
        self.PRIVATE_PATH = self.WS_PATH + "/private"
        self.HOST_PATH = self.WS_PATH + "/host"

class PiumPiumBot_Host:
    def __init__(self, url: str, id: str, node: str):
        self.url = url
        self.id = id
        self.node = node
