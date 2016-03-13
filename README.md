# Day One to Evernote
![DayOne][dayOneLogo] ![Evernote][evernoteLogo]

To use this you have to have installed [Geeknote][geeknotewww] port from [GitHub][geeknoteGithub] or Official Ecernote Client

## usage with Geeknote
* instal and configure Geeknote
* export Entries from Day One by File > Export...
    * export as txt
* download this repozytory 
* use my script
    
    $ pythone script/do2en.py -e pathToExportedEntryFile.txt -p pathToExportedPhotosDirectory -n existingEvernoteNotebook
    
## usage with oficial Evernote client 

this metod is faster but requaiers oficial evernote client to import my output file

* download this repository
* use my script
    
    $ pythone script/do2en.py -t "tag which will by applaied to all notes" -d pathToJournal.dayone -o outputFile.enex
    
    * *pathToJournal.dayone* path to jurnal filder ex.: *~/Dropbox/Apps/Day\ One/Journal.dayone/*
    * *outputFile.enex* this file you shoud inport to your Evernote
    
* then inport output file to evernote by File > Inport Notes...
    

    
[evernoteLogo]: https://raw.githubusercontent.com/vonProteus/do2en/master/images/Evernote.tiff
[dayOneLogo]: https://raw.githubusercontent.com/vonProteus/do2en/master/images/DayOne-Mac.tiff
[geeknoteWWW]: http://www.geeknote.me
[geeknoteGithub]: https://github.com/jeffkowalski/geeknote
