#!/usr/bin/python
import sys, getopt

class do2en:
    def __init__(self):
        self.photoDir = ""
        self.entriesFile = ""
        self.lines = []
        return

    def main(self, argv):
        self.parseParam(argv)

        print "Entries File is "+ self.entriesFile
        print "Photo Dir is "+ self.photoDir

        self.readEntries()

        print self.lines[1]

    def parseParam(self, argv):
        try:
            opts, args = getopt.getopt(argv,"he:p:",["entries-file=","photos-dir="])
        except getopt.GetoptError:
            print sys.argv[0]+' -e <entries-file> -p <photos-dir>'
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print sys.argv[0]+' -e <entries-file> -p <photos-dir>'
                sys.exit()
            elif opt in ("-e", "--entries-file"):
                self.entriesFile = arg
            elif opt in ("-p", "--photos-dir"):
                self.photoDir = arg

    def readEntries(self):
        file = open( self.entriesFile )
        splitBy = "\tDate:\t"

        lines=file.read().split(splitBy)
        file.close()

        for l in lines:
            if(len(l) == 0):
                continue
            self.lines.append(splitBy + l)




if __name__ == "__main__":
    obj = do2en();
    obj.main(sys.argv[1:])