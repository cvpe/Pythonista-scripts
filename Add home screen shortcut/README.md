Altough last version of Pythonista offers an easy way to add an home screen shortcut for an edited script, it still only allows as icon a standard icon.
This script will allow to create an home screen shortcut, either for any web page, either for any Pythonista script, but, mostly, will allow user to select any image as icon:
- a photo from camera roll
- a local Pythonista file
- an iCloud Drive file
- an internet file, both an image embedded in the web page that a file to download

1) the script sets the size of the shortcut icon in function of iDevice type, Retina or not, HD or not, Pro or not
It is not needed to support several icon sizes in the html file because an home screen shortcut can't be shared, thus only the icon size on the device where the shortcut will run is needed.
2) the script presents a dialog, with as fields:
   - the title of the shortcut 
   - either the shortcut url if used to launch a safari webpage 
     - if the user edits this field, a webbrowser is shown where the user can
       search his url, then "copy" it to the url textfield
   - either the Pythonista script to be launched
     - a switch iCloud or not will decide which files tree to show
     - a File Picker allows to select the script
   - the optional arguments in case of script to run
   - a SegmentedControl where user has to select the origin of the icon image
     - photo will show the photos picker
     - local will show a File Picker of local files
     - icloud will show a File Picker of iCloud Drive files
     - url will show a WebView where the user can search the image he wants to
       use as icon
       - then, he can drag and drop this image to a "receiving area"
     - once the image is defined, it is displayed at bottom of the dialog
3) the user tap ok when all needed fields are filled and the script will check 
   their coherence while staying in the dialog
   - top of tableview is an error message label
4) the user has still to a define square area for the icon by 
   - resizing the square by touching and moving a corner
   - moving the square by touching and moving inside the square
5) at ok, the script 
   - resizes the square area to the icon size 
     converts the image into a base74 string to be integrated in the html
   - opens Safari for the standard iser process of creating an home screen
   shortcut


The script needs some non-standard modules you should put in site-packages
  - [File_Picker.py](https://github.com/cvpe/Pythonista-scripts/blob/master/File_Picker.py), initially fom @omz, but modified to
    - be used in a TextField of a dialog
    - display thumbnails of images
    - show only selectable files (initially non selectable were grayed)
  - [MyPickDocument.py](https://github.com/cvpe/Pythonista-scripts/blob/master/MyPickDocument.py) to pick any file in iCloud Drive
