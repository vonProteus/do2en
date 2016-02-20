#!/usr/bin/python
import sys, getopt, locale
from datetime import datetime
from subprocess import Popen, PIPE,call
from operator import  itemgetter
import time
import re


class do2en:
    def __init__(self):
        self.photoDir = ""
        self.entriesFile = ""
        self.notebook = ""
        self.entries = []
        self.locale='pl_PL'
        self.dataEntryFormat = "%Y %B %d %H:%M"
        self.titlePrefix = "Imported from Day One"
        self.dataInTitleFormat = "%Y-%m-%d %H:%M"


        return

    def main(self, argv):
        self.parseParam(argv)

        print "Entries File is "+ self.entriesFile
        print "Photo Dir is "+ self.photoDir
        print "Notebook is "+ self.notebook

        self.readEntries()

        self.sentToEvernotr()

    def parseParam(self, argv):
        try:
            opts, args = getopt.getopt(argv,"he:p:n:",["entries-file=","photos-dir=","evernote-notebook="])
        except getopt.GetoptError:
            print sys.argv[0]+' -e <entries-file> -p <photos-dir> -n <evernote-notebook>'
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print sys.argv[0]+' -e <entries-file> -p <photos-dir> -n <evernote-notebook>'
                sys.exit()
            elif opt in ("-e", "--entries-file"):
                self.entriesFile = arg
            elif opt in ("-p", "--photos-dir"):
                self.photoDir = arg
            elif opt in ("-n", "--evernote-notebook"):
                self.notebook = arg

        if (self.notebook == "" or self.entriesFile == ""):
            print sys.argv[0]+' -e <entries-file> -p <photos-dir> -n <evernote-notebook>'
            sys.exit(2)

    def readEntries(self):
        file = open( self.entriesFile )
        splitBy = "\tDate:\t"

        lines=file.read().split(splitBy)
        file.close()

        for line in lines:
            if(len(line) == 0):
                continue
            self.entries.append(self.parseEntry(splitBy + line))

    def parseEntry(self, entryString):
        lines=entryString.split("\n");
        ansDict = {"date":"",
                   "tags":"",
                   "location":"",
                   "weather":"",
                   "photo":"",
                   "text":"",
                   }
        locale.setlocale(locale.LC_ALL, self.locale)

        for line in lines:
            if(len(line) == 0):
                continue
            if(line.startswith("\tDate:\t")):
                line = line.replace("\tDate:\t","")
                ansDict['date'] = datetime.strptime(line, self.dataEntryFormat)
                continue
            if(line.startswith("\tLocation:\t")):
                line = line.replace("\tLocation:\t","")
                ansDict['location'] = line
                continue
            if(line.startswith("\tWeather:\t")):
                line = line.replace("\tWeather:\t","")
                ansDict['weather'] = line
                continue
            if(line.startswith("\tTags:\t")):
                line = line.replace("\tTags:\t","")
                ansDict['tags'] = line
                continue
            if(line.startswith("\tPhoto:\t")):
                line = line.replace("\tPhoto:\t","")
                ansDict['photo'] = line
                continue
            ansDict['text'] = ansDict['text'] + line + "\n"
        return ansDict

    def sentToEvernotr(self):
        sendetNotes = set()
        entries = sorted(self.entries,key=itemgetter('photo'),reverse= True)
        for entry in entries:
            self.createNoteFromEntry(entry,sendetNotes)

    def createNoteFromEntry(self,entry,sendetNotes):


        gnArgs = []
        gnArgs.append("geeknote")
        gnArgs.append("create")

        gnArgs.append("--notebook")
        gnArgs.append(self.notebook)

        title = self.titlePrefix
        if(entry['date'] != ""):
            title += " created on " + entry['date'].strftime(self.dataInTitleFormat)
        if(entry['location'] != ""):
            title += " created in " + entry['location']
        gnArgs.append("--title")
        gnArgs.append(title)

        if(entry['tags'] != ""):
            gnArgs.append("--tags")
            gnArgs.append(entry['tags'])
        if(entry['photo'] != ""):
            gnArgs.append("--resource")
            gnArgs.append(self.photoDir+"/"+entry['photo'])
        if(entry['text'] != ""):
            gnArgs.append("--content")
            gnArgs.append(entry['text'])

        print gnArgs
        if(entry['date'].strftime(self.dataInTitleFormat) + entry['text'] in sendetNotes):
            print "duplicate"
            return
        sendetNotes.add(entry['date'].strftime(self.dataInTitleFormat) + entry['text'])

        self.doCmd(gnArgs,0)


    def doCmd(self,cmd,wait):

        if(wait>60):
            print ("waiting %s minutes"%  str(wait / 60))
            time.sleep(60 + wait % 60)
            self.doCmd(cmd,wait - 60 - wait % 60);
            return
        if(wait>0):
            print "waiting " + wait + "s"
            time.sleep(1)
            self.doCmd(cmd,wait-1);
            return

        process = Popen(cmd, stdout=PIPE)
        out, err = process.communicate()
        if(out.startswith("\nRate Limit Hit: Please wait")):
            print(out)
            timeToWait = int(re.search(r'\d+', out).group())
            self.doCmd(cmd,timeToWait)
        else:
            print(out)
            sys.exit(1)


if __name__ == "__main__":
    obj = do2en();
    obj.main(sys.argv[1:])