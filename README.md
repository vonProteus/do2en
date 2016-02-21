# Day One to Evernote
![DayOne][dayOneLogo] ![Evernote][evernoteLogo]

To use this you have to have installed [Geeknote][geeknotewww] port from [GitHub][geeknoteGithub]

## usage
* instal and configure Geeknote
* export Entries from Day One by File > Export...
    * export as txt
* download this repozytory 
* use my script
    
    $ pythone script/do2en.py -e pathToExportedEntryFile.txt -p pathToExportedPhotosDirectory -n existingEvernoteNotebook
    
    

    
[evernoteLogo]: https://raw.githubusercontent.com/vonProteus/do2en/master/images/Evernote.tiff
[dayOneLogo]: https://raw.githubusercontent.com/vonProteus/do2en/master/images/DayOne-Mac.tiff
[geeknoteWWW]: http://www.geeknote.me
[geeknoteGithub]: https://github.com/jeffkowalski/geeknote
