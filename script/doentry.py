import plistlib

class DOEntry:
    def __init__(self,path):
        self.plist = []
        self.path = path
        return

    @staticmethod
    def fromFile(filePath):
        doe =  DOEntry(filePath)
        doe.plist = plistlib.readPlist(filePath)

        # print(doe.plist)

        return doe

    def getText(self):
        return self.plist["Entry Text"]

    def getCreateDate(self):
        return self.plist["Creation Date"]

    def getTags(self):
        if "Tags" not in self.plist:
            return []
        return self.plist["Tags"]

    def getLocation(self):
        locationDict = {}
        if "Location" not in self.plist:
            return locationDict
        locationDict["latitude"] = self.plist["Location"]["Latitude"]
        locationDict["longitude"] = self.plist["Location"]["Longitude"]
        return locationDict

    def getUUID(self):
        return self.plist["UUID"]

    def isStarred(self):
        return self.plist["Starred"]

    def getLocationName(self):
        locationName = ""
        if "Location" not in self.plist:
            return locationName

        if "Place Name" in self.plist["Location"] and self.plist["Location"]["Place Name"]  != "":
            locationName += self.plist["Location"]["Place Name"] + ", "

        if "Locality" in self.plist["Location"] and self.plist["Location"]["Locality"]  != "":
            locationName += self.plist["Location"]["Locality"] + ", "

        if "Administrative Area" in self.plist["Location"] and self.plist["Location"]["Administrative Area"]  != "":
            locationName += self.plist["Location"]["Administrative Area"] + ", "

        if "Country" in self.plist["Location"] and self.plist["Location"]["Country"]  != "":
            locationName += self.plist["Location"]["Country"]

        return locationName

    def getSource(self):
        try:
            return self.plist["Creator"]["Software Agent"]
        except KeyError, e:
            print 'I got a KeyError - for ["Creator"]["Software Agent"] in "%s"' % str(self.getFilePath())
            return ""

    def getFilePath(self):
        return self.path