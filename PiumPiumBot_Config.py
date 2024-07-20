from os.path import dirname, abspath
import os
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class PiumPiumBot_Config:
    def __init__(self):
        #Version
        self.version = '1.0.12'
        self.type = 'DEV'
        self.host = PiumPiumBot_Host(url= 'dev', id= 'dev', node= 'dev')
        if (self.type == 'DEV'):
            self.logLevel = logging.INFO
        else:
            self.logLevel = logging.ERROR
        # Paths
        self.WS_PATH = dirname(abspath(__file__))
        self.TEMP_PATH = self.WS_PATH + "/temp"
        self.PRIVATE_PATH = self.WS_PATH + "/private"
        self.HOST_PATH = self.WS_PATH + "/host"
        self.ICON_PATH = self.WS_PATH + "/icons"
        self.FLAKE8_PATH = self.WS_PATH + "/flake8"
        self.TOOLS_PATH = self.WS_PATH + "/tools"
        # Flake8 configuration
        self.FOLDERS_TO_ANALYZE = [self.WS_PATH, self.TOOLS_PATH]

    def clean_logs(self):
        today = datetime.now()
        for file in os.listdir(self.TEMP_PATH):
            # Get only files
            if (os.path.isfile(self.TEMP_PATH + "/" + file)):
                extension = re.findall(r"(?<=\.)[a-z]{3,4}", file)[0]
                # Get only logs files
                if (extension == "log"):
                    fileDate = re.findall(r"(?<=PiumPiumBot_).*(?=\.log)", file)[0]
                    fileTime = datetime.strptime(fileDate, "%d_%m_%Y")
                    fileDuration = today - fileTime
                    if (fileDuration.days > 7):   # Delete files older than a week
                        os.remove(self.TEMP_PATH + "/" + file)


class PiumPiumBot_Host:
    def __init__(self, url: str, id: str, node: str):
        self.url = url
        self.id = id
        self.node = node


class PiumPiumBot_Log:
    def __init__(self):
        self.startCommand = datetime.now()
        self.endCommand = datetime.now()

    def startLog(self):
        self.startCommand = datetime.now()

    def finishLog(self, command: str):
        self.endCommand = datetime.now()
        duration = self.endCommand - self.startCommand
        logger.info(f"!{command} - Duration: {duration.total_seconds()}s")
        self.startCommand = datetime.now()
