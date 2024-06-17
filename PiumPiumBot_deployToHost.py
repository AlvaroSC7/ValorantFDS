from PiumPiumBot_Config import PiumPiumBot_Config
import re
from os.path import dirname, abspath
import os
import zipfile

bot = PiumPiumBot_Config()



def update_version(versionToIncrease: str, ws_path: str) -> str:
    """
        Increase the selected version (major|minor|patch) of the PiumPiumBot and set version type to PROD.

        Parameters:
            versionToIncrease   (str):  Version type to be increased (major|minor|patch)
            ws_path             (str):  Workspace path
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
    version_path = ws_path + "/PiumPiumBot_Config.py"
    with open (version_path,"r") as f:
        data = f.read()
        newData = re.sub("version = *.*.*", newVersion, data,)
    #Overwrite new version
    with open (version_path,"w") as f:
        f.write(newData)
        f.truncate()

    versionToZip = re.sub("version = |'","",newVersion)
    return versionToZip

def create_zip(zipfile, ws_path: str):
    excludeListFile = open(ws_path + "/excludePROD.txt","r")
    excludeList = excludeListFile.read()

    #Check all the files and folders in the folder
    for file in os.listdir(ws_path):
        #Get only files
        if(os.path.isfile(ws_path + "/" + file) == True):
            #Get only files needed for PROD
            if(file not in excludeList):
                zipfile.write(ws_path + "/" + file, file)


def main():
    ws_path = dirname(abspath(__file__))
    old_version = bot.version
    new_version = update_version("patch", ws_path)
    oldZipVersion = f"{ws_path}/host/PiumPiumBot_v{old_version}.zip"

    with zipfile.ZipFile(f"{ws_path}/host/PiumPiumBot_v{new_version}.zip",'w',zipfile.ZIP_DEFLATED) as zipf:
        create_zip(zipf, ws_path)
    #Remove the old PROD version
    if(os.path.isfile(oldZipVersion)):
        os.remove(oldZipVersion)
    #To Do: Implement function to delete #To Do comments from PROD

if __name__ == "__main__":
    main()
