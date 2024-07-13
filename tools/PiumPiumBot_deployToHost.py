import re
import os
import zipfile
import json
import sys
parentDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0,parentDir)
from PiumPiumBot_Config import PiumPiumBot_Config

bot = PiumPiumBot_Config()


#To Do: Implement function to delete #To Do comments from PROD
#To Do: Implement function to delete main from valorantFDS.py since it is only used for testing purposes
def update_version(versionToIncrease: str) -> str:
    """
        Increase the selected version (major|minor|patch) of the PiumPiumBot and set version type to PROD.

        Parameters:
            versionToIncrease   (str):  Version type to be increased (major|minor|patch)
        Returns:
            versionToZip        (str):  New updated version with the same format
        """
    #Read semver
    currentVersion = bot.version
    #Get major version, minor version and patch. Format - X.Y.z
    version = {'major': "",'minor': "",'patch': ""}
    majorMinorSepPos = currentVersion.find(".") #First '.' position in version string
    version['major'] = currentVersion[0:majorMinorSepPos]
    minorPatchSepPos = currentVersion.find(".",majorMinorSepPos + 1) #Last '.' position in version string
    version['minor'] = currentVersion[majorMinorSepPos+1:minorPatchSepPos]
    version['patch'] = currentVersion[minorPatchSepPos+1:]
    #Increase patch to deploy
    version[versionToIncrease] = str(int(version[versionToIncrease]) + 1)
    newVersion = "version = '" + version['major'] + "." + version['minor'] + "." + version['patch'] + "'"
    #Get python data to parse
    version_path = bot.WS_PATH + "/PiumPiumBot_Config.py"
    with open (version_path,"r") as f:
        data = f.read()
        newData = re.sub("version = *.*.*", newVersion, data)   #New version
        newData = re.sub("type = 'DEV'", "type = 'PROD'", newData)    #Change type from DEV to PROD
    #Overwrite new version
    with open (version_path,"w") as f:
        f.write(newData)
        f.truncate()

    versionToZip = re.sub("version = |'","",newVersion)
    return versionToZip

def create_zip(zipfile):
    excludeListFile = open(bot.WS_PATH + "/excludePROD.txt","r")
    excludeList = excludeListFile.read()

    #Check all the files and folders in the folder
    for file in os.listdir(bot.WS_PATH):
        #Get only files
        if(os.path.isfile(bot.WS_PATH + "/" + file) == True):
            #Get only files needed for PROD
            if(file not in excludeList):
                zipfile.write(bot.WS_PATH + "/" + file, file)

def update_host(host):
    """
        Modify the configuration file writing the host information for each zip file.

        Parameters:
            host   (str):  Information of the host
        """
    config_path = bot.WS_PATH + "/PiumPiumBot_Config.py"
    with open (config_path,"r") as f:
        data = f.read()
        for attrib in host:
            data = re.sub(f"(?<={attrib}= ')(.*?)(?=')", host[attrib], data)   #New version
    #Overwrite new version
    with open (config_path,"w") as f:
        f.write(data)
        f.truncate()


def main():
    old_version = bot.version
    new_version = update_version("patch")
    #Open host list
    with open(bot.PRIVATE_PATH + '/hostList.json') as json_file:
        hostList = json.load(json_file)

    for host in hostList['host']: 
        oldZipVersion = f"{bot.HOST_PATH}/PiumPiumBot_v{old_version}_{host['id']}.zip"
        update_host(host= host)
        with zipfile.ZipFile(f"{bot.HOST_PATH}/PiumPiumBot_v{new_version}_{host['id']}.zip",'w',zipfile.ZIP_DEFLATED) as zipf:
            create_zip(zipf)
        #Remove the old PROD version
        if(os.path.isfile(oldZipVersion)):
            os.remove(oldZipVersion)

if __name__ == "__main__":
    main()
