from os.path import dirname, abspath

class PiumPiumBot_Config:
    def __init__(self):
        #Version
        self.version = '1.0.6'
        self.type = 'PROD'
        self.host = PiumPiumBot_Host(url= 'https://control.bot-hosting.net/server/9f84f86d', id= '9f84f86d-7eab-40c5-94b2-7602d0d69208', node= 'fi3')
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
