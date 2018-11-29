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
