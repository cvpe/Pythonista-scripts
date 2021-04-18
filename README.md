# Pythonista-scripts
Pythonista scripts

**AddAfterAlarmToEvent.py**
 - display calendar events between two selected dates
 - select an event
 - display it's alarms thresholds (minus if before, plus if after begin of event) in minutes
 - add or update these thresholds
 - save th modified event

**AddButtonsToPythonistaKeyboard.py**      **iPAD ONLY**

Add your own keys in the standard Pythonista keyboard.

  - The script shows how we can add supplementar keys to the standard Pythonista keyboard. 
Unlike the new "keyboard" feature of the beta, this uses the standard keyboard, so in your own language and not the QWERTY keyboard of the new feature.

  - Check the (little) script to understand how you can add 'normal' keys that you use often but which are not displayed in the ABC initial keyboard, like >, #, " and \ in my example. You can also add keys for execute some particular process on your edited file, like 'next word', 'move cursor left', 'move cursor right' and 'delete at right of cursor' in my example.
To test it, you can edit and run it. Tapping anywhere in the file will show the keyboard, as usual, and you can try the new keys. Be careful, it will modify the script.

  - To use it in the real life, you will need to add it as a tool (wrench button) and execute it for each new editor's tab where you want to have your additional keys available. There is no known way, I think, to automatically run such a tool at each new edited tab.

  - For the fun, I've also put some moving emoji's on a road behind the keys.
Of course, you can very easily remove this code, but I just wanted to show how we can do a lot in this little ui.View (InputAccessoryView) above the keyboard.
23MAR2019: you can stop/restart the car by tapping it

**DownloadGithubRawFile.py**
  - use webview to navigate until a Github **RAW** file to download in Pythonista local files
    - of course, an url can be pasted in the url TextField
  - a **download** button will be enabled and has to be tapped
  - if File_Picker module present, asks user to select directory where to copy the downloaded Github file
    - else, file will be downloaded in the Documents root directory
  - 08MAR2019: bug "url pasted or entered in TextField gave a crash" corrected
  - 25MAR2019: support also of gist 
  
**find_in_files_via_help.py**
  - Little script to be executed once by Pythonista restart (fi in your pythonista_startup.py).
  - When you tap help in the popup menu of a selected text
  - After some seconds (function of your iDevice, the number and size of your scripts), you get  a list of scripts containing the selected text (case insensitive)
  - If you select a script, you'll get, like for Pythonista help, a small (webview) window displaying the script as an html with Python syntax highlighting, where occurrences of selected text are also highlighted (in yellow)
  - If you search has also results in Pythonista help, you'll see both results in the list
  - The script imports @jonB's [swizzle module](https://github.com/jsbain/objc_hacks/blob/master/swizzle.py)
  
**File_Picker.py**
 - file picker usable in a dialog textfield
 - displays thumbnails for images
 - 17FEB2019: add **only** parameter, True => only selectable (asked extension) files are showed

**Folder_Picker**
  - based on OMZ Script at https://gist.github.com/omz/e3433ebba20c92b63111
  - [see](https://forum.omz-software

**GoogleDriveBrowser**
script to edit Google Drive files like if they were local Pythonista files.

It assumes that you have installed [pydrive](https://github.com/googleworkspace/PyDrive/tree/master/pydrive) module and that you have defined a Google Drive API authorized user, read carefully [this topic](https://forum.omz-software.com/topic/5076/google-drive-support).

Be sure that the script can be improved about Python's way, functionalities and quality (surely not bug free), but it is "à prendre ou à laisser" (as is).

You could define this script as Pythonista tool but it is not mandatory and it can be run as usual.

The script is based on @omz's [File Picker](https://gist.github.com/omz/e3433ebba20c92b63111).

Script is here [GoogleDriveBrowser](https://github.com/cvpe/Pythonista-scripts/blob/master/GoogleDriveBrowser.py)

When you have installed this script on your iDevice, you have to modify the line
```
	google_drive_auth_path = os.path.expanduser('~/Documents/MesTools/settings.yaml')
```
pointing to your Google Drive authorization file.

Of course, you can also modify the title and the size of your view.
```
		self.table_view.frame = (0, 0, 700,800)
		.
		.
		.
		self.view.name = 'My Google Drive'
```
And you can also modify the icon displayed in function of the file type.
Also, actually, the program only allows to edit .py files but it is possible that it could also work with other ones (txt?, html?), but up to you to test them.

What the program offers?
- first, it presents a view of your Google Drive root folders and files.
- you can 
  - expand a folder by tapping its right arrow icon
    nb: this process may be very slow if you have a lot of files
    --- example, some seconds for 200 files on my iPad 2020
  - collapse an expanded folder by tapping its down arrow icon
  - edit a not grayed file name (actually .py only),
    in this case, the program 
    - downloads the Google Drive file in the same folder as the script,
      with a name of "x...x (on GoogleDrive).eee", where
      - x...x is the original file name
      - eee is its extension
    - loads this local file in the same tab as the program (if you run it) or in 
      an existing tab if you launch it as a tool (not tested)
  - save the local file on Google Drive by checking file modification each second 
    (up to you to modify it if too slow) and when the tab is closed.

    
**IdentifyAlbumOfPhotos.py**
 - scan all photos with photos module
 - store their file name in a dictionary "name->index"
 - scan all photos with Photos Objc Framework
 - get their album name and update dictionary as "name->index,album"
 
**Japanese Braille Input.py**
 - [see](https://forum.omz-software.com/topic/5584/braille-application)
 
**Juxtaposition de Photos.py**
 - pictures jointer
 - still in development, do not ask support, do not put issues please
 - crashes very often

**contacts on map.py**
 - the script uses a function, geocodeAddressString, for converting an
  	address string into a localization (latitude,longitude).
		If you want to use it in different scripts, you could store it in
		site-packages folder
 - a button (satellite) allows to switch between the standard, satellite and 
		hybrid views of the map
 - you can zoom and move the map by pinching and swiping
 - a button (pin) allows to switch between a pin or a photo for contact
		if a contact does not have a photo, a pin is always shown
 - tapping a pin or a photo shows a view with the name(s) of the contact(s)
		at this location, and the address
 - if several contacts have the same address, the script cumulates them
 	on an unique pin, by horizontally juxtaposing their photos into a wide one
		the script also tries to cumulate the contacts full names by identifying
		the identic last words as a family name. Not sure it's always ok
		ex: Fred Astaire and Mary Astaire give a title of Fred, Mary Astaire
		Normally a long title is shorten by ...
 	The script shows a small view under the title with one line per group
		of persons with different last names.
 -	a button (address) allows to type a manual address. At enter, the script
		will try to get its location. If successful, a green pin is displayed 
		and the map is automatically centered and zoomed on it.
		If unsuccessful, the address is set in red and no pin is shown
 - there is a simulation mode (main(simulation=True)) where a namedtuple
		simulates contacts. Photo can be any internal or external image
		and their names need to be given in the 'simul = namedtuple...' line
 - sometimes, geocodeAddressString returns None. Either the address string
		is invalid, but somerimes, a retry gives a correct gps localization.
		Perhaps due to a big number of calls in a short time.
		In this case, the script display a button 'nn not (yet) localized' and 
		starts a thread which will retry (maximum 100 times) all not yet localized
		contacts. The delay between two retries increase at each retry.
		The button title is green if the thread runs and red if not.
		Tapping this button gives the list of these contacts with their retries
		number
 - The close button forces the thread to be stopped. 
 - the script has been tested with 250 contacts and sometimes, after   several 
 		runs, it crashs, perhaps due to memory problems. In this case, remove
		 the app from memory and restart.
		
**Export script to pdf.py**
 - is based on an @omz [sample](https://forum.omz-software.com/topic/1950/syntax-highlight-python-code-on-screen-while-running)
 - needs that you install **xhtml2pdf** via stash, then pip install xhtml2pdf
 - can be added as a tool via wrench menu
 - when executed on an edited script, creates a file **script_name.pdf** with highlighted code
		 
**File_Explorer.py**
  - base of a file explorer, really not perfect

**geocodeAddressString**
 - convert address into GPS location latitude,longitude via APPLE CLGeocoder
 
**My_Apps_Button_in_TitleBar.py**
  - menu of Pythonista scripts displayed by a user button in the TitleBar
  
**PhotosPickerView.py**
  - see your Photos in an UIPickerView
  
**MyPickDocument.py**
  - use of UIDocumentPickerViewController to open or import an iCloud file
  - 24MAY2019: add optional parameter to allow multiple selection
  
**SaveInFiles.py**

Function to open a sheet or popover view with the "save in Files app" without passing via the "Open In menu"
It uses the ObjectiveC UIDocumentPickerViewController, called Picker necise you pick the folder where to save
Checking source code shows that you could use an UIDocumentPickerMode=3
instead of 2, but implying a (dangerous) move instead copy.
Parameters are:
 - positional: local file to save
 - positional: width and height of view 
 - optional title= displayed between the two standard buttons: cancel and add
 - optional callback= function called when the PickerViewController is
   - canceled (returns 'cancel')
   - ended (returns the url where the file has been saved)
 - optional mode= presentation mode,either
   - 'sheet' (default)
   - 'popover' 
 - optional popover_location= (x,y) tuple where to present the popover view
 
**SMB_client.py**
 - SMB basic client
 - based   on   https://github.com/humberry/smb-example/blob/master/smb-test.py
 - needs smb+nmb from https://github.com/miketeo/pysmb/tree/master/python3
 - needs pyasn1  from https://github.com/etingof/pyasn1
 - upload/download optional buffering and callback
 - upload/download optional full local path 
 - instance creation, optinal parameter to print or store eventual error
 
**SetTextFieldPad.py**
 - real numeric pad on iPAD
 - see https://forum.omz-software.com/topic/4951/real-numeric-pad-on-ipad
 - 13JAN2019: custom textfield_did_change not called, I added an optional parameter textfield_did_change=function to call 
 - 17APR2019: added optional parameter to rotate, at random between -10° and +10°, each key
 
 ![](https://i.imgur.com/KO1AxYw.jpg)
 
  - 12OCT2020: added support of SFsymbols as icon on keyboard keys
 
 ![](https://i.imgur.com/qVaklcR.jpg)
 
**test speech via objc.py**

-  you can set 
  - the text, even with combined emoji like flags or 'woman artist' 👩 + 🎨 = 👩‍🎨
  - the language/voice among the 52 available
    - you need to tap the voice and the TableView will expand with all voices
  - the rate of speaking
  - speak or spell, and in this case, the delay between two letters
  - bug: speak does not work, corrected 06 dec 2018

**threads_indicator_in_status_bar.py**

Display the number of active threads in the status bar
- little script to start a thread to display permanently the number of active threads in the status bar of Pythonista
- I wrote this script because some of my scripts, using multi-threads, sometimes let a thread still active even when the script is ended, with its UI closed, and I didn't remark it...
- the script can be run or launched via the tools or in the Pythonista_startup
- tapping on the number displays a little popover window with the names of the threads
- in this popover, you can close this window (x-button) or end the thread it-self (end-button)

**VersionInStatusBar.py**

I program my scripts on my ipad, in local Pythonista folders.
But some scripts are written for my wife, then I copy these scripts on Pythonista iCloud folder, and they are executed by tapping an home screen icon pointing to pythonista3://script_name?action=run&root=icloud.
But, sometimes, I forget to copy my modified script from local to iCloud.
Thus, I've decided to display in the status bar (at top) of the iDevice, a label showing the version of the running script, so I can check if the script executed by my wife is the last version.
For that:
- a module VersionInStatusBar.py is installed in site-packages folder
- these lines are added at top of my scripts
   * from  VersionInStatusBar import VersionInStatusBar
   * version = 'nn.n'
   * VersionInStatusBar(version=version)
- this line is added in the will_close def, to remove the label from status bar
   * VersionInStatusBar(version=False)
	 
![](https://i.imgur.com/LXMPBlU.jpg)
