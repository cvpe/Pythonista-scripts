# Pythonista-scripts
Pythonista scripts

**AddAfterAlarmToEvent.py**
 - display calendar events between two selected dates
 - select an event
 - display it's alarms thresholds (minus if before, plus if after begin of event) in minutes
 - add or update these thresholds
 - save th modified event
 
**File_Picker.py**
 - file picker usable in a dialog textfield
 - displays thumbnails for images
 - 17FEB2019: add **only** parameter, True => only selectable (asked extension) files are showed

**Folder_Picker**
  - based on OMZ Script at https://gist.github.com/omz/e3433ebba20c92b63111
  
**DownloadGithubRawFile.py**
  - use webview to navigate until a Github **RAW** file to download in Pythonista local files
    - of course, an url can be pasted in the url TextField
  - a **download** button will be enabled and has to be tapped
  - if File_Picker module present, asks user to select directory where to copy the downloaded Github file
    - else, file will be downloaded in the Documents root directory
  edit: 08MAY2019: bug "url pasted or entered in TextField gave a crash" corrected
  
**IdentifyAlbumOfPhotos.py**
 - scan all photos with photos module
 - store their file name in a dictionary "name->index"
 - scan all photos with Photos Objc Framework
 - get their album name and update dictionary as "name->index,album"

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
		 
**File_Explorer.py**
  - base of a file explorer, really not perfect

**geocodeAddressString**
 - convert address into GPS location latitude,longitude via APPLE CLGeocoder
 
**My_Apps_Button_in_TitleBar.py**
  - menu of Pythonista scripts displayed by a user button in the TitleBar
  
**MyPickDocument.py**
  - use of UIDocumentPickerViewController to open or import an iCloud file
  
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
 - custom textfield_did_change not called, I added an optional parameter textfield_did_change=function to call 13/01/2019
 
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
