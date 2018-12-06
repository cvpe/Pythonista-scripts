# Pythonista-scripts
Pythonista scripts

AddAfterAlarmToEvent.py
 - display calendar events between two selected dates
 - select an event
 - display it's alarms thresholds (minus if before, plus if after begin of event) in minutes
 - add or update these thresholds
 - save th modified event

IdentifyAlbumOfPhotos.py
 - scan all photos with photos module
 - store their file name in a dictionary "name->index"
 - scan all photos with Photos Objc Framework
 - get their album name and update dictionary as "name->index,album"

contacts on map.py
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

geocodeAddressString
 - convert address into GPS location latitude,longitude via APPLE CLGeocoder
 
SMB_client.py
 - SMB basic client
 - based   on   https://github.com/humberry/smb-example/blob/master/smb-test.py
 - needs smb+nmb from https://github.com/miketeo/pysmb/tree/master/python3
 - needs pyasn1  from https://github.com/etingof/pyasn1
 - upload/download optional buffering and callback
 - upload/download optional full local path 
 - instance creation, optinal parameter to print or store eventual error
 
SetTextFieldPad.py
 - real numeric pad on iPAD
 - see https://forum.omz-software.com/topic/4951/real-numeric-pad-on-ipad
 
test speech via objc.py

you can set 
- the text, even with combined emoji like flags or 'woman artist' 👩 + 🎨 = 👩‍🎨
- the language/voice among the 52 available
  - you need to tap the voice and the TableView will expand with all voices
- the rate of speaking
- speak or spell, and in this case, the delay between two letters
- bug: speak does not work, corrected 06 dec 2018

threads_indicator_in_status_bar.py

Display the number of active threads in the status bar
- little script to start a thread to display permanently the number of active threads in the status bar of Pythonista
- I wrote this script because some of my scripts, using multi-threads, sometimes let a thread still active even when the script is ended, with its UI closed, and I didn't remark it...
- the script can be run or launched via the tools or in the Pythonista_startup
- tapping on the number displays a little popover window with the names of the threads
- in this popover, you can close this window (x-button) or end the thread it-self (end-button)
