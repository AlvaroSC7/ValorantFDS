import re
import os
import subprocess
import sys
parentDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0,parentDir)
from PiumPiumBot_Config import PiumPiumBot_Config


def main():
    bot = PiumPiumBot_Config()
    excludeListFile = open(bot.WS_PATH + "/excludePROD.txt","r")
    excludeList = excludeListFile.read()

    #Check all the files and folders in the folder
    analysisFolders = [bot.WS_PATH, bot.TOOLS_PATH]
    for folder in analysisFolders:
        for file in os.listdir(folder):
            #Get only files
            if(os.path.isfile(folder + "/" + file) == True):
                #Get only files needed for PROD
                if(file not in excludeList):
                    isPythonFile = re.search("^.*.py",file)
                    if(isPythonFile != None):
                        flake8 = subprocess.run(["flake8", file, "--statistics"], stdout=subprocess.PIPE, shell=True)
                        fileName = re.sub(".py","",file)
                        flake8File = open(f"{bot.FLAKE8_PATH}/{fileName}_codeAnalysis.txt", "w")
                        flake8File.write(flake8.stdout.decode("utf-8"))


if __name__ == "__main__":
    main()
