#!/usr/bin/python
import sys, getopt, locale
from datetime import datetime
from subprocess import Popen, PIPE
from operator import  itemgetter
import time
import re
from os import walk
import os.path
import codecs
import hashlib
import base64
import magic
import exifread

from lxml import etree
import urllib2

from StringIO import StringIO


from doentry import DOEntry

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
        self.evernoteFormat = "%Y%m%dT%H%M%SZ"
        self.dayOneDir = ""
        self.tag = ""
        self.oudputFile = ""
        self.photoTag = "DOPhoto"

        self.doentrys = [];


        return

    def main(self, argv):
        self.parseParam(argv)

        print "Entries File is "+ self.entriesFile
        print "Photo Dir is "+ self.photoDir
        print "Notebook is "+ self.notebook

        print "Oudput File is "+ self.oudputFile
        print "Day One Dir is "+ self.dayOneDir
        print "Tag is "+ self.tag

        if(self.entriesFile != "" ):
            self.readEntries()
            self.sentToEvernotr()
        elif(self.dayOneDir != ""):
            self.readDayOneDir()
            self.saveOutFile()


    def parseParam(self, argv):
        try:
            opts, args = getopt.getopt(argv,"he:p:n:t:d:o:",["entries-file=","photos-dir=","evernote-notebook=","tag=","day-one-dir=","oudput="])
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
            elif opt in ("-t", "--tag"):
                self.tag = arg
            elif opt in ("-d", "--day-one-dir"):
                self.dayOneDir = arg
            elif opt in ("-o", "--oudput"):
                self.oudputFile = arg

        if (self.notebook == ""):
            print sys.argv[0]+' -e <entries-file> -p <photos-dir> -n <evernote-notebook>'
            sys.exit(2)
        elif (self.dayOneDir == "" and self.entriesFile == ""):
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
            print("%s/%s"%(str(entries.index(entry)),str(len(entries))))
            self.createNoteFromEntry(entry,sendetNotes)

    def createNoteFromEntry(self,entry,sendetNotes):
        gnArgs = []
        gnArgs.append("geeknote")
        gnArgs.append("create")

        gnArgs.append("--notebook")
        gnArgs.append(self.notebook)

        title = self.titlePrefix
        if(entry['date'] != ""):
            # title += " created on " + entry['date'].strftime(self.dataInTitleFormat)
            gnArgs.append("--created")
            gnArgs.append(entry['date'].strftime(self.dataInTitleFormat))
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
        elif(entry['photo'] == ""):
            print "empty"
            return
        else:
            gnArgs.append("--content")
            gnArgs.append("photo only")

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
            print ("waiting %ss"%  str(wait))
            time.sleep(1)
            self.doCmd(cmd,wait-1);
            return

        process = Popen(cmd, stdout=PIPE)
        out, err = process.communicate()
        print("out:"+str(out))
        print("err:"+str(err))
        if(out.startswith("\nRate Limit Hit: Please wait")):
            timeToWait = int(re.search(r'\d+', out).group())
            self.doCmd(cmd,timeToWait)

    def readDayOneDir(self):
        for (dirpath, dirnames, filenames) in walk(self.dayOneDir+"/entries/"):
            for filename  in filenames:
                doe = DOEntry.fromFile(str(dirpath+filename))
                self.doentrys.append(doe)

                # print str(doe.getCreateDate()) +" => " + str(doe.getTags())
            break
        return

    def saveOutFile(self):
        out = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n" \
            "<!DOCTYPE en-export SYSTEM \"http://xml.evernote.com/pub/evernote-export3.dtd\">\n" \
            "<en-export export-date=\""+datetime.now().strftime(self.evernoteFormat)+"\" application=\"do2en\" version=\"do2en 0.1\">\n"

        for doe in self.doentrys:
            note = self.makeNote(doe)
            out += note

        out += "</en-export>"
        # print out



        target = codecs.open(self.oudputFile, 'w', 'utf-8')
        target.truncate()
        target.write(out)
        target.close()
        return


    def makeNote(self,doe):
        note = "\t<note>\n"
        note += "\t\t" + self.makeTitle(doe) + "\n"
        note += self.makeTags(doe)

        note += "\t\t<note-attributes>\n"
        note += self.makeAttributes(doe)
        note += "\t\t</note-attributes>\n"

        note += self.makeContent(doe)

        note += self.makeTime(doe)

        photo = self.photoFrom(doe)

        if photo != "":
            note += self.makeResource(photo)

        note += self.makeResource(doe.getFilePath())

        note += "\t</note>\n"
        return note

    def makeTitle(self,doe):
        title ="<title>"
        title += self.titlePrefix
        if doe.getLocationName() != "":
            title += " created in " +  doe.getLocationName()
        title +="</title>"
        return title

    def makeTags(self,doe):
        tags = self.makeTag(self.tag)
        for tag in doe.getTags():
            tags+= self.makeTag(tag)

        if self.photoFrom(doe) != "":
            tags+= self.makeTag(self.photoTag)

        return tags

    def makeTag(self,tag):
        if tag == "":
            return ""
        tagout = "\t\t<tag>"+tag+"</tag>\n"
        return tagout

    def photoFrom(self,doe):
        photo = self.dayOneDir + "/photos/"+doe.getUUID()+".jpg"

        if os.path.isfile(photo):
            return photo
        else:
            return ""


    def makeAttributes(self,doe):
        attributes = "\t\t\t<source>"+doe.getSource()+"</source>\n"
        attributes += "\t\t\t<reminder-order>0</reminder-order>\n"
        if doe.getLocation() != {}:
             attributes += "\t\t\t<latitude>"+str(doe.getLocation()["latitude"]) +"</latitude>\n"
             attributes += "\t\t\t<longitude>"+str(doe.getLocation()["longitude"]) +"</longitude>\n"
        return attributes

    def makeContent(self,doe):
        content = "\t\t<content><![CDATA[<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n" \
            "<!DOCTYPE en-note SYSTEM \"http://xml.evernote.com/pub/enml2.dtd\">\n" \
            "<en-note>\n"

        lines = doe.getText().split("\n")

        for line in lines:
            content += "<div>"+line+"</div>\n"

        photo = self.photoFrom(doe)

        if photo != "":
            photoHash = self.md5File(photo)
            photoMime = self.mimeFrom(photo)
            content += "<en-media type=\""+photoMime+"\" hash=\""+photoHash+"\" />\n"

        hash = self.md5File(doe.getFilePath())
        mime = self.mimeFrom(doe.getFilePath())
        content += "<en-media type=\""+mime+"\" hash=\""+hash+"\" />\n"

        content += "</en-note>]]></content>\n"
        return content

    def makeTime(self,doe):
        timeCU = ""

        time = doe.getCreateDate().strftime(self.evernoteFormat)

        timeCU +="\t\t<created>"+time+"</created>\n"
        timeCU +="\t\t<updated>"+time+"</updated>\n"

        return timeCU

    def md5File(self,path):
        return hashlib.md5(open(path, 'rb').read()).hexdigest()

    def makeResource(self,path):
        if not os.path.isfile(path):
            return ""
        resource = "\t\t<resource>\n"

        rfile = file(path,'rb')

        mime = self.mimeFrom(path)
        resource += "\t\t\t<mime>"+mime+"</mime>\n"
        resource += self.makeResourceAttributes(rfile)

        with open(path, "rb") as ffile:
            data = base64.b64encode(ffile.read())
        # data = "sdfsdfsdfsdfsdfsdfsdf"
        resource += "\t\t\t<data encoding=\"base64\">"+data+"</data>\n"
        resource += "\t\t</resource>\n"

        return resource;

    def mimeFrom(self,path):
        mime = magic.Magic(mime=True)
        return mime.from_file(path)

    def makeResourceAttributes(self,rfile):
        resourceAttributes =""


        tags = exifread.process_file(rfile)

        if "EXIF ExifImageWidth" in tags:
            resourceAttributes += "\t\t\t<width>"+str(tags["EXIF ExifImageWidth"])+"</width>\n"

        if "EXIF ExifImageLength" in tags:
            resourceAttributes += "\t\t\t<height>"+str(tags["EXIF ExifImageLength"])+"</height>\n"
        resourceAttributes += "\t\t\t<duration>0</duration>\n"

        resourceAttributes += "\t\t\t<resource-attributes>\n"

        # print tags
        timestamp = ""
        if "EXIF DateTimeOriginal" in tags:
            timestamp = datetime.strptime(tags["EXIF DateTimeOriginal"].values,"%Y:%m:%d %H:%M:%S").strftime(self.evernoteFormat)
        elif "GPS GPSTimeStamp" in tags:
            timestamp = datetime.strptime(tags["GPS GPSTimeStamp"].values,"%Y:%m:%d %H:%M:%S").strftime(self.evernoteFormat)

        if timestamp != "":
            resourceAttributes += "\t\t\t\t<timestamp>"+timestamp+"</timestamp>\n"

        if "GPS GPSLatitude" in tags and "GPS GPSLongitude" in tags:
            latitude = self.convertToDegress(tags["GPS GPSLatitude"])
            longitude = self.convertToDegress(tags["GPS GPSLongitude"])

            if tags["GPS GPSLatitudeRef"].values != "N":
                latitude = 0-latitude

            if tags["GPS GPSLongitudeRef"].values != "E":
                longitude = 0-longitude

            latitude = str(latitude)
            longitude = str(longitude)

            resourceAttributes += "\t\t\t\t<latitude>"+latitude+"</latitude>\n"
            resourceAttributes += "\t\t\t\t<longitude>"+longitude+"</longitude>\n"

        if "Image Model" in tags :
            cameraMake= tags["Image Model"].values
            resourceAttributes+="\t\t\t\t<camera-make>"+cameraMake+"</camera-make>\n"

        resourceAttributes += "\t\t\t</resource-attributes>\n"
        return resourceAttributes

    def convertToDegress(self,gps):
        d0 = gps.values[0].num
        d1 = gps.values[0].den
        d = float(d0) / float(d1)

        m0 = gps.values[1].num
        m1 = gps.values[1].den
        m = float(m0) / float(m1)

        s0 = gps.values[2].num
        s1 = gps.values[2].den
        s = float(s0) / float(s1)

        return d + (m / 60.0) + (s / 3600.0)


if __name__ == "__main__":
    obj = do2en();
    obj.main(sys.argv[1:])