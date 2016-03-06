import plistlib

class DOEntry:
    def __init__(self):
        self.plist = []
        return
    @staticmethod
    def fromFile(filePath):
        doe =  DOEntry();
        doe.plist = plistlib.readPlist(filePath)

        # print(doe.plist)

        return doe

    def getText(self):
        return self.plist["Entry Text"]

    def getCreateDate(self):
        return self.plist["Creation Date"]

    def getTags(self):
        return  self.plist["Tags"]

    def getLocation(self):
        locationDict = []
        if "Location" not in  self.plist:
            return locationDict



        return locationDict
