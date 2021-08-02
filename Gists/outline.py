'''
todo 
====
- .. bug: 0️⃣ pick folder to save and asking name does not appear if Files app (loop)
							- save does not work
							- prms['path'] and 'file' not written
							- use when save => above bug workaround
							- open last does not work, not saved in prm?
- .. bug: 1️⃣ tab => bad undo successifs
- .. bug: 🔟 choice local/filesapp blinks once on iPhone
- .. bug: 🔟 if image, typing multiple soft lines do not resize textview immediately
- .. bug: 🔟 if we create a file xxx, check the .content does not exist
- .. bug: 🔟 However, I went into portrait mode and I got a TypeError 
					'builtin_function_or_method' object is not iterable. I'm not exactly sure what I did when I got it but I believe I was trying to paste a new line and then delete it. It also seems to occur when I hit return to create a new item.
					**** not reproductible ****
- .. bug: 🔟 popup with keyboard displayed at middle of The screen
					If I scroll the outline I can see it and if I then bring up the pop-up menu, it comes up but in the middle of the outline (i.e., not at the item that is being edited). If instead, I hide the keyboard and then select the popup menu, it points to the correct item.
					
					not vital, workaround: do not ask popup while keyboard is active
					
					this occurs only for row having had an autoscroll for the keyboard,
					after, there is a scroll to put 1st row above with cursor and keyboard.
					why
					
					def scrollview_did_scroll(self, scrollview):
						if popup on screen, check new position row, change location popover?
						could be easy for iphone as there is a visible view, not presented
						
					do not allow popup if row edited?
					
					best: prohibit automatic scroll back but how?					
- .. bug: 🔟 add new line at end, new line hidden by keyboard for @ihf, not for me
					If i open outline now and do text insertion on last item, hit return, a new item is created that is hidden by the keyboard.
					
					not vital, workaround: manual scroll
					
					ipad, landscape, line 10 fontsize 24
					
- .. new: Keep a creation + change + due + complete (set when checked) date/time 
					for each outline item and the ability to sort Alphabetically, on change , creation , or due or complete date.
					
						popup: 4 dates creation/change/due/complete 3rd = textfield
										complete set when checked, None else
										'dates':(c,u,due,complete)
									 horizontal => 2nd line?
					
					the app I have stores four dates: creation, change, due, completion. Only one date can be selected at a time for viewing and it is shown to the left of the items ((i.e., the outline is moved to the right to make room for the date when it is viewed.)
					
					https://imgur.com/a/Gb7mdu9
					
						eye menu: show segments creation/change/due/complete date		
											name of date
											sort ? up down
											format yy/mm/dd	or use f'' strings			
											tableview right moved, protected by a transparent shield

- .. new: add image (not prioritary)
					- print text+images in program btn=printer or submenu files, option print

- .. new: 2nd arg file = directory (in progress)

					question: when the program shows all the files, other extensions are grayed, do you want to hide them?
						
- .. bug: files aa.txt .content outline length incorrect thus part of text
					seen as outline 4.0 Fi Re ... should be abc every line
					https://forum.omz-software.com/topic/7110/outliner-with-drag-drop-reordering/336

- .. new: support level 0 = [] > no outline
					- doubletap on checkbox to get popup menu
- .. new: accelerate program 
					- redisp visible rows instead of reload_data 
						- except if del/add/move? if add at end, stupid 
						- show/hide
						- check/uncheck
						- ...
					- ...
- .. new: drag with copy
			- start how? popupmenu: move line with its children
			- display moving box
			- touch state = 1 = take it
			-               2 = move it
			-               3 = drop it copy without delete and remove box
			- how to cancel it without drop: drop outside
														
- .. main menu: style => modif font,font_size, color for each level
- ..	- memo not per line but per file in .content general, like format type
- .. functionnality to build/modify user format?
- ..	- memo infos in .prm if detail modifiable
- .. 	- formats=tableview {item:type,accessorytype:detail} ou swipe avec user 
- ..	- explication: I->roman A->alpha 1.->n i-> a-> level+1
'''
import appex
import ast
import collections
import console
from   datetime import datetime
import dialogs
import File_Picker		# https://github.com/cvpe/Pythonista-scripts/blob/master/File_Picker.py
from   functools import partial
from   gestures  import *
import inspect
from   math      import isinf
from   objc_util import *
import os
import re
from   SetTextFieldPad import SetTextFieldPad # https://github.com/cvpe/Pythonista-scripts/blob/master/SetTextFieldPad.py
if not appex.is_running_extension():
	import swizzle
import sys
import time
import ui
import unicodedata
import urllib.parse

Version = 'V00.61'
Versions = '''
Version V00.61
  - correction of bug "save did not work"
Version V00.60
  - correction of bug "hidden child shows its image"
  - correction of bug "in popup menu, actions in two lines were not executed"
  - correction of bug "tap 🖼 in horizontal popup menu gives error 'view in use'"
  - correction of bug "intercept error of image from unaccessible file"
    and draw an 'open error' image
  - support UIDocumentPickerViewController for set current path
  - support UIDocumentPickerViewController for log file to play
  - support UIDocumentPickerViewController for open
  - support UIDocumentPickerViewController for image
  - new parameter "current path" used for accessing files
  - in settings dialog, display current path as header of settings
  - new "set current path" option in files menu
    - not used for images, so you can pick an image anywhere
    - used for play log, on local or Files app folder
    - used for open file, on local or Files app folder
  - new options in eye menu
    - hide checked
    - show checked only
    nb: if one of these modes is active and we change the status checked/unchecked
        of one displayed line, this line will be automatically hidden
Version V00.59
  - support images in rows
    - use UIDocumentPickerViewController allowing to pick even not yet downloaded 
      iCloud files
Version V00.58
  - correction of bug "some typing, like left delete, give error 'IndexError: string
    index out of range' when saving for undo"
  - remove option 'show all' of eye button, same process as 'expand all'
Version V00.57
  - correction of bug "selecting option in eye submenu gives error
    'TypeError: string indices must be integers'"
Version V00.56
  - eye button now shows a submenu with
    - show all to unhide all rows
    - collapse all to hide all rows with level > 1 (children)
    - expand all to unhide all rows with level > 1 (children)
    nb: expand all and show all do exactly the same process
  - to be tested modification for the problem of enter on row just above keyboard, 
    which implies a new row but hidden by keyboard
Version V00.55
  - the "triangle" symbol to the left of the outline item should
    - point down when the children are visible 
    - point to the right when they are hidden
    - be a filled circle if no children
Version V00.54
  - correction of bug "crash at start with error
    AttributeError: 'Outliner' object has no attribute 'cursor'"
Version V00.53
  - when editing a row that would be hidden by the appearing keyboard, 
    automatically scrolls so the row is above the keyboard
Version V00.52
  - protection against crash when open a file. 
    Offer only "on my iDevice" and "iCloud Drive" if their path exists,
    that will say "open once as external folder"
Version V00.51
  - protection against crash on iPhone when open a file. 
    On iPhone, iCloud Drive folder is not seen as a folder by os.path.isdir().
    => Support only Pythonista local and iCloud files
Version V00.50
  - support automatic soft line-feed when typing reachs right side with recomputing
    of height of TextView in TableView row
Version V00.49
  - correction of bug "scrolling not allowed when keyboard hides row to be edited"
    by setting tableview content inset bottom = keyboard height
Version V00.48
  - modified File_Picker to support in the browser 
      - Pythonista local
      - Pythonista iCloud
      - On my iDevice
      - iCloud Drive
    - no more setting "folder choice"
    - no more import Folder_Picker
Version V00.47
  - add a "dismiss keyboard" key to iPhone kyboard to see all rows for editing
  - follow @ccc advice about "for i, item in enumerate(items):"
  - correction of bug "info button of format types did not react"
Version V00.46
  - support device rotation while running
  - support split view even while running (buttons locations recomputed)
  - height of TableView rows recomputed in function of number of soft linefeeds
    generated by long texts 
Version V00.45
  - correction of bug "on iPhone, script hangs when trying to open a file"
Version V00.44
  - correction of bug "if outline.py on iCloud, local is not accessible"
  - correction of bug "on iPhone, no way to close Versions window"
  - correction of bug "on iPhone, portrait, filter dialog segments not full 
    visible, font size recomputed"
  - correction of bug "on iPhone, portrait, settings dialog segments not full 
    visible, font size recomputed"
Version V00.43
  - popup menu
    - options about checkbox only shown if checkboxes setting is yes
    - new option "hidden" if checkbox has to be hidden for a specific row
      nb: checkbox can be reshown if option checked or unchecked is tapped
Version V00.42
  - open a xxx.content file is not allowed
  - name a new file as xxx.content is not allowed
Version V00.41
  - correction of bug "crash when closing settings option"
  - support of extension passed as 1st argument
    nb: - example: .txt will show all files grayed except .txt ones
Version V00.40
  - support of file passed as 1st argument 
    nb: - only file in script folder is actually supported
        - script checks file and its.content both exit
        - ex url: pythonista3://MyFolder/outline?action=run&argv=a.txt
Version V00.39
  - correction of bug "keyboard hides data entry of text in rows"
Version V00.38
  - correction of bug "drop into the moving lines was allowed"
Version V00.37
  - correction of bug "filter was reset to zero"
  - support on iPhone kind of popover presentation via half transparent shield for:
  	- files menu tableview
  	- format types menu tableview
  	- search textfield
  	- font size textfield
  	- popup menu
  - not needed for dialogs like settings and filter and for big views like versions
  - force vertical popup menu on iPhone
Version V00.36
  - support iPhone by using ui.Buttons instead of ui.ButtonItems for menu buttons
Version V00.35
  - new options in popup menu to check or uncheck the tapped row and its children
Version V00.34
  - new functionnality: filter
    - new button in main menu
    - allows to filter lines to show (other are hidden)
       < level
       = level
       > level
Version V00.33
  - correction of bug "local variable 'cell' reference before assign"
  - correction of bug "move before first row does not work"
  - correction of bug "move after last row does not work"
  - correction of bug "cursor leaves search field and goes to a row at each char"
  - long options of horizontal popup menu in two lines 
    nb: popup black menu has same height as before, the minimum allowed (40 pixels)
Version V00.32
  - support "autocapitalization type (see ui.TextView doc)"
    - new general setting
    - use this setting when entering text (none, words, sentence, all)
Version V00.31
  - correction of bug "undo did not work"
  - correction of bug "move before first line did not work"
Version V00.30
  - use a TableView instead of a TextView (full review)
  - support delete row and its children option in popup menu
  - support enter between words in text, stay in same outline
  - modif infos stored in .log file easier reading
  - for new file, do not ask folder and name before first save or at end 
    - without folder/file, no auto save is possible and title is ?
  - an outline with multiple lines is saved with a blnk outline from the second
    line so the text is visible and printable as is.
  - On my iPad/iPhone now accessible if, and only if, you share ONCE a file 
    from this Files app folder to this program. 
    The path will be stored in .prm file.
  - support "delete in red" 
    - new general setting
    - display or not red background for "delete with children" option in popup menu
  - support "single or double tap for popup menu"
    - new general "setting"
    - single or double tap on outline needed for popup menu
  - support of redo after undo (same button, icon changes automatically)
Version V00.29
  - support top folder also for folder_picker when creating a new file
  - bad scrolling at typing normal characters solved in some cases, 
    but not all, bug still not identified...
Version V00.28
  - support "Files"
    - new general setting local, iCloud, on my iDevice, iCloud Drive
      - if not accessible, segment will be disabled
    - file picker on selected folder
Version V00.27
  - correction of bug "auto-save parameter incorrect in .prm file"
  - temporary workaround to scrolling problem: when typing in a line, automatic 
    scroll so this line is at top of screen and you don't have this annoying
    scroll at each typed character. But this does not work each time. Weird
Version V00.26
  - support "auto-save"
    - new general setting no, each character typed, each line by CR, tab, back tab
      nb: time of last save (in hh:mm:ss.ssss) is shown in settings screen
    - save in function of setting and typing 
    - save will now
      - delete .old files if they exist
      - rename files into .old 
      - save files
Version V00.25
  - correction of bug "predictive text may generate crash or doubled end characters"
  - no more error message when you drop a box on its original area, used to cancel
  - new file will use default font Menlo and default font size 18
  - support clickable (short press) and underlined weblink
    on all words (ending with a blank) beginning by http:// or https://
    nb: be careful, url is case sensitive
  - new option in Files popup menu: rename
    - check actual file and its .content exist (not the case if new in progress)
    - ask new name
    - check renamed file and its .content do not already exist
    - rename file and its content
Version V00.24
  - default font size will be now 18
  - no more alert if last open file, stored in .prm, does no exist anymore
  - font and font_size saved in .content, so when file is open, they are known
  - backtab on an outline of first level not allowed
Version V00.23
  - correction of bug "paste text containing CR did lock the script"
  - correction of bug "popup menu location incorrect if long text"
  - outline showed in yellow in horizontal popup menu, to be sure
    the menu is relative to the tapped outline
  - new functionnality: undo
    - new button in main menu
    - shows name of action undoable in red on the button
    - operational for undoing move (drag/drop)
    - operational for undoing CR (linefeed)
    - operational for undoing tab (demote)
    - operational for undoing back (promote)
    - disable if typed or deleted characters 
Version V00.22
  - correction of bug "if text bigger than one screen, any typing
    automatically scrolls until end of file".
    workaround found is to locate text row at edited line
  - correction of bug "checkbox was not saved correctly in .content"
  - correction of bug "checkboxes are being reset as soon as new item is typed"
Version V00.21
  - correction of BIG (sorry) bug "hide/show icons were not synchronized with lines
    when scrolling more than one screen"
  - correction of bug "tap outside search field while it was not empty" does not 
    reshow all lines""
  - support move left/right dragged box on its initial line to promote/demote
  - support "show lines separator" 
    - new general setting
    - display or not a line after each (not hidden) text line
   - support "checkboxes" 
    - new general setting
    - display or not a checkbox in front of (not hidden) line
    - store checkbox per line in the .content file
Version V00.20
  - review all renumbering (one more time)
Version V00.19
  - correction of bug "log may not be activated after an 'open file'"
  - correction of bug "move last line shows a too high pink area"
  - correction of bug "bad renumbering after move"
  - support new setting "font size of hidden outlines, may be set to 0"
  - support longpress and double tap popup menu only on outline
  - support standard gesture select/copy/paste only on text it-self
  - differentiate if we would drop under the outline or under the text
    by start the red line at left of outline or left of the text
  - support drop under outline and under text
Version V00.18
  - bugs
    - correction of bug "bad renumbering after drop"
    - correction of bug "crash 'tuple index out of range' if change outline type"
    - correction of bug "crash if drop after a line without outline"
Version V00.17
  - support "hide/show children via buttons at left of outline"
Version V00.16
  - support "log" 
    - new general setting
    - log each typed key
    - play log typed keys
    - log each move
    - play log move
Version V00.15
  - bugs
    - correction of bug "long press on last lines shows full text as pink area"
Version V00.14
  - bugs
    - correction of bug "backtab on a line did not also backtab its children"
    - correction of bug "drop after last line didn't do anything"
    - full review for renumbering for 
      - "backtab" 
Version V00.13
  - bugs
    - correction of bug "new file was saved as first use, even if not asked"
    - correction of bug "enter in font size did not close the textfield"
    - correction of bug "error 'list index out of range' at end of file"
    - correction of bug "error 'list index out of range' in renumbering"
      if last line has a CR"
    - full review for renumbering for 
      - tab" 
      - "lf " 
      - "backtab" still in progress
      - "dropped lines" 
      - "removed lines of dropped original" 
  - text in moving box will have same font and font size as TextView text
  - support "show original area" 
    - new general setting
    - display or no a coloured rectangle on the original dragged area
Version V00.12
  - bugs
    - full review of tab process and checks
    - full review of backtab process and checks
    - correction of bug "typing a tab or backtab before an outline was now allowed"
Version V00.11
  - bugs
    - correction of bug "characters insertion before an outline was allowed"
    - correction of bug "CR before an outline was allowed"
    - correction of bug "CR before a line without outline crashed"
    - correction of bug "CR at begin of file before an outline was incorrect" 
  - support CR in the middle of a line, with renumbering of following lines
Version V00.10
  - bugs
    - correction of bug "tab crashes on replaceObjectsInRange out of bounds"
    - correction of bug "incorrect renumbering lines after CR"
Version V00.09
  - bugs
    - correction of bug of crash when "drop before first line"
      nb: new renumbering bug has appeared, not yet solved
    - correction of bug of crash with "'Outliner' object has no attribute 'target'"
    - correction of bug of hidden but identic (invisible) outlines do not have
      the font size of hidden
    - correction of bug of tapping outside textfield (font size, searched text) 
      closes the entire app
    - correction of bug of same outlines (gray) do not have same font_size 
      as normal ones
  - moving box
    - will now contain coloured outlines
    - the moving box was displayed above the finger position to allow to always
      see where it would be inserted, but, at the top of the text, the box was
      outside the screen, thus invisible. Now, this box will be drawn at right
      of the finger.
  - search in lines
    - new main button for searching
    - display an ui.TextField to enter the searched text
    - display only lines containing the search text (case,accents non sensitive)
      nb: displayed lines vary in real time
    - press enter to close the TextField and come back to full display
  - review .content file for future improvements like outline hidden, style etc...
Version V00.08
  - no more blue dot at top/left of moving box
  - new settings button in main menu
  - support "popup menu orientation" 
    - new general setting
    - support both vertical and horizontal orientations of popup menu
  - bugs
    - correction of bug of two successive tabs on same line
  - support of drop
    - check no drop of a box of text into it-self
    - support of drop for move operation only 
      nb: draft process, several renumbering bugs subsist, be patient
  - support of "force a new line with same outline"
    - new general setting
    - new option in popup menu
      - with special icon if horizontal popup menu
    - generates an outline, same as previous line
    - no renumbering of next lines will occur
    nb: long lines automatically (by ui.TextView) break and should generate a same outline on next line, but this is not yet supported. 
    Force same outline functionality may be a workaround
  - support "same outline invisibility" 
    - new general setting
    - support both invisible or light gray (tests) same outline
  - begin of future (eventual) development for details of outline format types
    - better parametrization of format types
    - accessory info button in format types popup menu gives more details
Version V00.07
  - popup menu was shown by tapping a line but this does no more allow to set
    the cursor, thus replace tap by a double tap
  - tap popup menu y-centered on the tapped line
  - popup menu now horizontal in more standard aspect
  - locally built icon for font size button
  - locally built icon for font button
  - correction of bug of cursor always set at end of text
  - support outline bullets format
  - height of outline format types menu computed in function of types number
  - font size introduction via integer keyboard in popover TextField
Version V00.06
  - moving box for dragging limited to text it contains
  - during dragging, a red line indicates where the moving text would be inserted
  - font button for font selection
  - font size button for font size selection
  - promote/demote by gestures:
    - either by a long press on one line and moving the dragging box left or right 
      on the same line
    - either by a left or right swipe on one line 
Version V00.05
  - remove the "move" option from the popup menu when tapping an outline
  - to start a drag operation, long press anywhere on a line
    - hold your finger on the screen
    - pressed line and its children lines are set in a little mobile label
    - this label is above your finger so it stays visible why moving your finger
    - move the mobile label so its top/left blue point falls on a line
    - drop process is still to be developped, wait and see
      nb: actual drop process drops the entire text (outlines included) 
          at specified location
Version V00.04
  - correction of bug of automatic renumbering after line feed
  - correction of bug of automatic renumbering after tab
  - correction of bug of automatic renumbering after back tab
  - if outline is exactly the same as previous line, display it in gray
    nb: - actually, this should not be authorized but automatic renumbering
          sometimes generates such invalid cases
        - if this functionnality is allowed, the outline would become invisible
  - hide/show children supported (also saved for next run)
    nb: actually, for testing, not really hidden but small characters to check
        which lines would be hidden
Version V00.03
  - at program end, outline.prm written with path and name of last edited file
  - automatic open last edited file at program start
  - automatic generation of first outline when new file
Version V00.02
  - File Picker
  - Folder Picker
  - file open
  - file save
  - file new
  - save levels and outline type in xxx.content
  - when tab, check maximum level reached
  - when change outline format, check maximum level reached
Version V00.01
  - add row above keyboard with up/down outline level' keys
  - differentiate up/down level keys of tab and left delete
  - add Files button and its submenu, without any process
  - checks: delete/cut selected mix of outline not allowed (message)
  - allows "up level" key anywhere in the line
Version V00.00
  - checks: editing outline is not allowed (message)
  - checks: delete/cut selected mix of outline and normal characters 
            not allowed (message)
  - checks: delete line feed followed by a line with an outline
            not allowed (message)
  - support normal characters
  - support tab at begin of line with automatic outline
  - support tab in text, simulate line feed keeping same (invisible) outline
  - support line feed with automatic outline, only at end of text
  - support delete/cut of normal characters, even lf (see checks)
  - support coloured outline
  - support outline color picker, even during editing
  - support outline format change, even during editing
  - support outline decimal format (not yet alignment and big numbers)
  - support outline alphanumeric format (not yet alignment and big numbers)
  - support outline traditional format (not yet alignment and big numbers)   
  - support versions button (ok, you have tested it, nice isn't it? 😀)
  - support button on each outline for future actions (move?...)
'''

#===================== delegate of UIDocumentPickerViewController: begin
def documentPickerWasCancelled_(_self, _cmd, _controller):
	#print('documentPickerWasCancelled_')
	UIDocumentPickerViewController = ObjCInstance(_controller)
	UIDocumentPickerViewController.uiview.close()
	if UIDocumentPickerViewController.callback:
		UIDocumentPickerViewController.callback('canceled')
	UIDocumentPickerViewController.picked = 'canceled'
	UIDocumentPickerViewController.done = True

def documentPicker_didPickDocumentsAtURLs_(_self, _cmd, _controller, _urls):
	#print('documentPicker_didPickDocumentsAtURLs_')
	UIDocumentPickerViewController = ObjCInstance(_controller)
	UIDocumentPickerViewController.uiview.close()
	urls = ObjCInstance(_urls)
	if len(urls) == 1:
		url = urllib.parse.unquote(str(urls[0]))
	else:
		url = []
		for i in range(0,len(urls)):
			url.append(urllib.parse.unquote(str(urls[i])))
	if UIDocumentPickerViewController.callback:
		UIDocumentPickerViewController.callback(url)
	UIDocumentPickerViewController.picked = url
	UIDocumentPickerViewController.done = True

methods = [documentPicker_didPickDocumentsAtURLs_,documentPickerWasCancelled_]
protocols = ['UIDocumentPickerDelegate']
try:
		MyUIDocumentPickerViewControllerDelegate = ObjCClass('MyUIDocumentPickerViewControllerDelegate')
except Exception as e:
	MyUIDocumentPickerViewControllerDelegate = create_objc_class('MyUIDocumentPickerViewControllerDelegate', methods=methods, protocols=protocols)
#===================== delegate of UIDocumentPickerViewController: end

NSMutableAttributedString = ObjCClass('NSMutableAttributedString')
NSForegroundColorAttributeName = ns('NSColor')
UIColor = ObjCClass('UIColor')

UIFont = ObjCClass('UIFont')
NSFontAttributeName = ns('NSFont')
NSLinkAttributeName = ns('NSLink')
NSUnderlineStyleAttributeName = ns('NSUnderline')
font = UIFont.fontWithName_size_('Menlo', 18)
font_hidden = UIFont.fontWithName_size_('Menlo', 6)

SUIViewController = ObjCClass('SUIViewController')
UIFontPickerViewController = ObjCClass('UIFontPickerViewController')
UIFontPickerViewControllerConfiguration = ObjCClass('UIFontPickerViewControllerConfiguration')

pad_integer = [{'key':'1'},{'key':'2'},{'key':'3'},
	{'key':'back space','icon':'typb:Delete'},
	{'key':'new row'},
	{'key':'4'},{'key':'5'},{'key':'6'},
	#{'key':'delete','icon':'emj:Multiplication_X'},
	{'key':'new row'},
	{'key':'7'},{'key':'8'},{'key':'9'},
	{'key':'new row'},
	{'key':'nul'},{'key':'0'},{'key':'nul'},{'key':'⏎','SFicon':'return'}]

bs = '\b'
lf ='\n'
tab = '\t'

PY3 = sys.version_info[0] >= 3
if PY3:
	basestring = str
	
def my_form_dialog(title='', fields=None, sections=None, done_button_title='Done', wd=500, hd=500):
	global mv
	wd = min(wd,mv.get_screen_size()[0])
	# copy of dialogs.form_dialog
	if not sections and not fields:
		raise ValueError('sections or fields are required')
	if not sections:
		sections = [('', fields)]
	if not isinstance(title, basestring):
		raise TypeError('title must be a string')
	for section in sections:
		if not isinstance(section, collections.Sequence):
			raise TypeError('Sections must be sequences (title, fields)')
		if len(section) < 2:
			raise TypeError('Sections must have 2 or 3 items (title, fields[, footer]')
		if not isinstance(section[0], basestring):
			raise TypeError('Section titles must be strings')
		if not isinstance(section[1], collections.Sequence):
			raise TypeError('Expected a sequence of field dicts')
		for field in section[1]:
			if not isinstance(field, dict):
				raise TypeError('fields must be dicts')
				
	header0 = sections[0][0]
	if header0 != '':
		sections[0] = (' ',sections[0][1])
		#sections = [('',sections[0][1])] + [sections[1:]]

	cc = dialogs._FormDialogController(title, sections, done_button_title=done_button_title)
	cc.container_view.frame = (0, 0, wd, hd)
	cc.view.frame = (0, 0, wd, hd)

	# assure that path in he<der title is not shown in capitals
	if header0 != '':
		tblo = ObjCInstance(cc.view)
		hh = 60
		tblo.sectionHeaderHeight = hh
		header = ui.Label()
		header.number_of_lines = 0
		header.text = header0
		dx = 15
		header.frame = (dx,0,wd-dx,hh)
		header.font = ('Menlo',12)
		header.text_color = 'blue'
		# uncomment next line of you want to see room of label
		#header.border_width = 1 # only for tests
		cc.view.add_subview(header)


	#==================== dialogs.form_dialog modification 1: begin	
	w_for_segments = 240
	w_for_label = wd - w_for_segments - 10 - 10
	# first loop to compute max width of labels
	nc = 0
	for i in range(0,len(cc.cells[0])):			# loop on rows of section 0
		cell = cc.cells[0][i]									# ui.TableViewCell of row i
		if len(cell.content_view.subviews) > 0:
			nc = max(nc, len(cell.text_label.text))
	ft = ('Menlo',14)
	wt = ui.measure_string(' '*nc, font=ft)[0] + 10
	font_size = min(14, int(14*w_for_label/wt))
	ft = ('Menlo',font_size)
	
	for i in range(0,len(cc.cells[0])):			# loop on rows of section 0
		cell = cc.cells[0][i]									# ui.TableViewCell of row i
		# some fields types are subviews of the cell:
		#   text,number,url,email,password,switch
		#  but check, date and time are not set as subviews of cell.content_view
		if len(cell.content_view.subviews) > 0:
			tf = cell.content_view.subviews[0] 		# ui.TextField of value in row
			cell.text_label.font = ft
			# attention: tf.name not set for date fields
			item = cc.sections[0][1][i]	# section 0, 1=items, row i
			if 'segmented' in tf.name:
				segmented = ui.SegmentedControl()
				segmented.name = cell.text_label.text
				segmented.frame = tf.frame
				segmented.width = w_for_segments
				segmented.x = cc.view.width - segmented.width-10 # cc.view is tableview
				segmented.segments = item['segments']
				value = item.get('value', '')
				segmented.selected_index = item['segments'].index(value)
				cell.content_view.remove_subview(tf)
				del cc.values[tf.name]
				del tf
				cell.content_view.add_subview(segmented)
				# multiline segments
				for sv in ObjCInstance(segmented).subviews():
					if sv._get_objc_classname().startswith(b'UISegmentedControl'):
						if 'accessible' in item:
							accessible = item['accessible']
							for i,access in enumerate(accessible):
								#print(item['segments'][i],access)
								if not access:
									sv.setEnabled_forSegmentAtIndex_(False,i)
						for ssv in sv.subviews():
							if ssv._get_objc_classname().startswith(b'UISegment'):
								ssv.label().numberOfLines = 0	
								ssv.label().adjustsFontSizeToFitWidth = True # auto resize font to fit
			elif isinstance(tf, ui.TextField):
				#print(tf.name)
				#tf.item = item	# if needed during checks
				tf.alignment=ui.ALIGN_RIGHT
				tf.bordered = True
				tf.font = ('Menlo',16)
				tf.flex = ''
				enabled = item.get('enabled', True)
				tf.enabled = enabled
				h = cell.content_view.height
				if 'pad' in item:
					SetTextFieldPad(tf, pad=item['pad'], textfield_did_change=cc.textfield_did_change)
					w = 80
				else:
					tf.font = ('Menlo',12)
					w = 500				
				tf.frame = (cc.view.width-w-10,(h-20)/2,w,20)
		
	#==================== dialogs.form_dialog modification 1: end
	
	cc.container_view.present('sheet')
	cc.container_view.wait_modal()
	# Get rid of the view to avoid a retain cycle:
	cc.container_view = None
	if cc.was_canceled:
		return None
	
#==================== dialogs.form_dialog modification 2: begin	
	for i in range(0,len(cc.cells[0])):			# loop on rows of section 0
		cell = cc.cells[0][i]									# ui.TableViewCell of row i
		# some fields types are subviews of the cell:
		#   text,number,url,email,password,switch
		#  but check, date and time are not set as subviews of cell.content_view
		for tf in cell.content_view.subviews:
			if 'SegmentedControl' in str(type(tf)):
				item = cc.sections[0][1][i]	# section 0, 1=items, row i
				if tf.selected_index >= 0:
					cc.values[tf.name] = item['segments'][tf.selected_index]
#==================== dialogs.form_dialog modification 2: end

	return cc.values
#==================== copied from dialogs: end

def fontPickerViewControllerDidPickFont_(_self, _cmd, _controller):
	global mv
	controller = ObjCInstance(_controller)
	font = str(controller.selectedFontDescriptor().objectForKey_('NSFontFamilyAttribute'))
	mv.set_font(font_type=font)

PickerDelegate = create_objc_class(
    'PickerDelegate',
    methods=[fontPickerViewControllerDidPickFont_],
    protocols=['UIFontPickerViewControllerDelegate']
)

class MyInputAccessoryView(ui.View):
	def __init__(self, row, *args, **kwargs):
		global mv
		#super().__init__(self, *args, **kwargs)	
		self.row = row
		self.width = mv.get_screen_size()[0]			# width of keyboard = screen
		self.background_color = 'lightgray'#(0,1,0,0.2)
		d = 4
		hb = 44
		self.height = 2*d + hb
		self.pad = [
		{'key':'tab','data':'\x01', 'sf':'text.chevron.right', 'x':10},
		{'key':'shift-tab','data':'\x02', 'sf':'text.chevron.left', 'x':self.width-10-hb}
		]
		if mv.device_model == 'iPhone':
			self.pad.append({'key':'tab','data':'\x00', 'sf':'keyboard.chevron.compact.down', 'x':self.width/2})
		
		# build buttons
		for pad_elem in self.pad:
			button = ui.Button()									# Button for user functionnality
			button.frame = (int(pad_elem['x']),d,hb,hb)
			button.name = pad_elem['key']
			button.background_color = 'white'			# or any other color
			button.tint_color = 'black'
			button.corner_radius = 5		
			button.title = ''
			db = hb
			o = ObjCClass('UIImage').systemImageNamed_(pad_elem['sf'])
			with ui.ImageContext(db,db) as ctx:
				#o.drawAtPoint_(CGPoint(0,0))
				o.drawInRect_(CGRect(CGPoint(0, 0), CGSize(db,db)))
				button.image = ctx.get_image()				
			button.data = pad_elem['data']
			button.action = self.key_pressed
			retain_global(button) # see https://forum.omz-software.com/topic/4653/button-action-not-called-when-view-is-added-to-native-view
			self.add_subview(button)	
		
	def key_pressed(self, sender):
		global mv
		#import ui
		#from objc_util import ObjCClass
		tv = sender.objc_instance.firstResponder()	# associated TextView		
		if sender.data == '\x00':
			tv.endEditing_(None)
			return
		row = self.row
		mv.textview_should_change(None, [row,row], sender.data)
		#tv.insertText_(sender.data)	
		
def OMColorPickerViewController(title=None, rgb=None):
	v = ui.View()
	if title:
		v.name = title
	v.rgb = None
	vc = ObjCInstance(v)
	colorpicker = ObjCClass('OMColorPickerViewController').new().autorelease()
	clview = colorpicker.view()
	v.frame = (0,0,512,960)
	vc.addSubview_(clview)
	done_button = ui.ButtonItem(title='ok')
	def tapped(sender):
		cl = colorpicker.color()
		v.rgb = (cl.red(),cl.green(),cl.blue())
		v.close()
	done_button.action = tapped
	v.right_button_items = [done_button]
	if rgb:
		color = ObjCClass('UIColor').colorWithRed_green_blue_alpha_(rgb[0], rgb[1], rgb[2], 1.0)
		colorpicker.setColor_(color)
	v.rgb = rgb
	v.present('sheet')
	v.wait_modal()
	return v.rgb 	
	
@on_main_thread
def tableView_heightForRowAtIndexPath_(_self,_sel,tv,path):
	try:
		import sys, objc_util, ctypes
		# For some reason, tv returns a NSNumber.  But, our tableview is in _self
		tv_o=objc_util.ObjCInstance(_self)
		# get row and section from the path
		indexPath=objc_util.ObjCInstance(path)
		row=indexPath.row()
		section=indexPath.section()
		# get the pyObject.  get as an opaque pointer, then cast to py_object and deref 
		pyo=tv_o.pyObject(restype=ctypes.c_void_p,argtypes=[])
		tv_py=ctypes.cast(pyo.value,ctypes.py_object).value
		# if the delegate has the right method, call it
		if tv_py.delegate and hasattr(tv_py.delegate,'tableview_height_for_section_row'):
			return tv_py.delegate.tableview_height_for_section_row(tv_py,section,row)
		else:
			return tv_py.row_height
	except Exception as e:
		import traceback
		traceback.print_exc()
		return 44
		
# set up the swizzle.. only needs to be done once
def setup_tableview_swizzle(override=False):
	t=ui.TableView()
	t_o=ObjCInstance(t)

	encoding=ObjCInstanceMethod(t_o,'rowHeight').encoding[0:1]+b'@:@@'
	if hasattr(t_o,'tableView_heightForRowAtIndexPath_') and not override:
		return
	swizzle.swizzle(ObjCClass(t_o._get_objc_classname()),
								('tableView:heightForRowAtIndexPath:'),
								tableView_heightForRowAtIndexPath_,encoding)

if not appex.is_running_extension():								
	#upon import, swizzle the textview class. this only ever needs to be done once 
	setup_tableview_swizzle(1)	

class Outliner(ui.View):
	def __init__(self, *args, **kwargs):
		ui.View.__init__(self, *args, **kwargs)
		ws,hs = self.get_screen_size()
		self.width, self.height = ws,hs
		#self.frame = (0,0,375,667)						# iPhone SE
		self.name = 'Outliner'
		self.background_color = 'white'

		nb = 12
		w = self.get_screen_size()[0]
		dd = 4
		wb = (w - (nb+1)*dd)/nb
		if wb > 32:
			wb = 32
			dd = (w - wb*nb)/(nb+1)
		d = int(w/nb)
		y = 10 + wb
		
		x = dd
		b_close	= ui.Button(name='b_close')
		b_close.frame = (x,y,wb,wb)
		b_close.image = ui.Image.named('iob:close_round_32')
		b_close.action = self.close_action
		self.add_subview(b_close)

		x = x + wb + dd		
		b_version = ui.Button(name='b_version')
		b_version.frame = (x,y,wb,wb)
		w12 = ui.measure_string(Version+'_',font=('Menlo',12))[0]
		fs = 12 * wb/w12
		b_version.font = ('Menlo',fs)
		b_version.title = Version
		b_version.tint_color = 'green'
		b_version.action = self.button_version_action	
		self.add_subview(b_version)

		x = x + wb + dd				
		b_files = ui.Button(name='b_files')
		b_files.frame = (x,y,wb,wb)
		b_files.image = ui.Image.named('iob:ios7_folder_outline_32')
		b_files.tint_color = 'blue'
		b_files.action = self.button_files_action	
		self.add_subview(b_files)

		x = x + wb + dd				
		b_settings = ui.Button(name='b_settings')
		b_settings.frame = (x,y,wb,wb)
		b_settings.image = ui.Image.named('iob:ios7_gear_outline_32')
		b_settings.action = self.button_settings_action			
		self.add_subview(b_settings)

		x = self.width - wb - dd			
		b_format = ui.Button(name='b_format')
		b_format.frame = (x,y,wb,wb)
		o = ObjCClass('UIImage').systemImageNamed_('list.number')
		with ui.ImageContext(32,32) as ctx:
			o.drawAtPoint_(CGPoint(4,4))
			b_format.image = ctx.get_image()					
		b_format.action = self.button_format_action
		self.add_subview(b_format)
		self.outline_format = 'decimal'

		x = x - wb - dd				
		b_color = ui.Button(name='b_color')
		b_color.frame = (x,y,wb,wb)
		b_color.image = ui.Image.named('emj:Artist_Palette').with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		b_color.action = self.button_color_action
		self.add_subview(b_color)
		self.outline_rgb = (1,0,0)
		self.outline_color = UIColor.colorWithRed_green_blue_alpha_(self.outline_rgb[0], self.outline_rgb[1], self.outline_rgb[2], 1)

		x = x - wb - dd				
		b_font = ui.Button(name='b_font')
		b_font.frame = (x,y,wb,wb)
		with ui.ImageContext(32,32) as ctx:
			ui.draw_string('A', rect=(16,9,16,16), font=('Academy Engraved LET',24))
			b_font.image = ctx.get_image()
		b_font.action = self.button_font_action
		self.add_subview(b_font)

		x = x - wb - dd				
		b_fsize = ui.Button(name='b_fsize')
		b_fsize.frame = (x,y,wb,wb)
		#b_fsize.title = 'font_size'
		with ui.ImageContext(32,32) as ctx:
			ui.draw_string('A', rect=(8,12,12,12), font=('Menlo',12))
			ui.draw_string('A', rect=(16,9,16,16), font=('Menlo',16))
			b_fsize.image = ctx.get_image()
		b_fsize.action = self.button_fsize_action
		self.add_subview(b_fsize)		

		x = x - wb - dd		
		b_search = ui.Button(name='b_search')
		b_search.frame = (x,y,wb,wb)
		b_search.image = ui.Image.named('iob:ios7_search_32')
		b_search.action = self.button_search_action
		self.add_subview(b_search)

		x = x - wb - dd				
		b_undo = ui.Button(name='undo_button')
		b_undo.frame = (x,y,wb,wb)
		b_undo.action = self.button_undo_action
		b_undo.image = ui.Image.named('iob:ios7_undo_outline_32')
		b_undo.enabled = False
		self.add_subview(b_undo)
		
		b_redo = ui.Button(name='redo_button')
		b_redo.frame = (x,10,wb,wb)
		b_redo.action = self.button_redo_action
		b_redo.image = ui.Image.named('iob:ios7_redo_outline_32')
		b_redo.enabled = False
		self.add_subview(b_redo)
		
		title = ui.Label(name='title')
		title.frame = (0,10,b_redo.x - 10,wb)
		title.font = ('Menlo',16)
		title.text_color = 'green'
		title.alignment = ui.ALIGN_CENTER
		self.add_subview(title)

		x = x - wb - dd				
		b_show = ui.Button(name='b_show')
		b_show.frame = (x,y,wb,wb)
		b_show.action = self.button_show_action
		b_show.image = ui.Image.named('iob:ios7_eye_outline_32')
		self.add_subview(b_show)

		x = x - wb - dd				
		b_filter = ui.Button(name='b_filter')
		b_filter.frame = (x,y,wb,wb)
		b_filter.action = self.button_filter_action
		b_filter.image = ui.Image.named('iob:levels_32')
		self.add_subview(b_filter)
		
		sep = ui.Label(name='sep')
		sep.frame = (0,y+wb,self.width,1)
		sep.background_color = 'lightgray'
		self.add_subview(sep)
		
		self.button_undo_enable(False,'')
		self.button_redo_enable(False,'')
		
		self.tv = ui.TableView(name='outliner')
		#self.tv.border_width = 2
		#self.tv.border_color = 'red'
		self.tv.allows_selection = False
		self.tv.data_source = ui.ListDataSource(items=[])
		self.tv.data_source.delete_enabled = False
		self.tv.separator_color=(1,0,0,0)
		self.tv.delegate = self
		self.tv.data_source.tableview_cell_for_row = self.tableview_cell_for_row
		self.tv.data_source.tableview_number_of_rows = self.tableview_number_of_rows
		self.tv.data_source.tableview_height_for_section_row = self.tableview_height_for_section_row
		self.tv.background_color = (1,1,1)
		#self.tv.border_width = 1
		#d = 20*2
		self.ht = 10 + wb*2
		self.keyboard_y = 0
		
		self.tv.frame = (0,self.ht,ws-2,hs-self.ht)
		self.tv.delegate = self
		
		#======== to be moved for textfikd in cell for row
		#self.tv.font = ('Menlo',14)
		self.tvo = ObjCInstance(self.tv)
		#print(dir(self.tvo))
		self.tv.row_height = -1
		self.tvo.estimatedRowHeight = 44
		
		self.add_subview(self.tv)
		self.content = []
				
		self.font = 'Menlo'
		self.font_size = 18
		self.font_hidden = 6
		font = UIFont.fontWithName_size_('Menlo', self.font_size)
		font_hidden = UIFont.fontWithName_size_('Menlo', self.font_hidden)
		
		self.text_color = UIColor.colorWithRed_green_blue_alpha_(0, 0, 1, 1)
		self.text_attributes = {NSForegroundColorAttributeName:self.text_color, NSFontAttributeName:font}
		self.text_attributes_hidden = {NSForegroundColorAttributeName:self.text_color, NSFontAttributeName:font_hidden}
		self.outline_attributes = {NSForegroundColorAttributeName:self.outline_color, NSFontAttributeName:font}
		self.outline_attributes_hidden = {NSForegroundColorAttributeName:self.outline_color, NSFontAttributeName:font_hidden}
		self.link_color = UIColor.colorWithRed_green_blue_alpha_(0, 1, 1, 1)
				
		self.modif = False 
		self.file = None
		self.log = 'no'
		self.filter = ('>',0)
		self.device_model = str(ObjCClass('UIDevice').currentDevice().model())		
		#self.device_model = 'iPhone'	# force for tests
		self.cursor = (0,0)
		
		path = sys.argv[0]
		i = path.rfind('.')
		self.prm_file = path[:i] + '.prm'
		if os.path.exists(self.prm_file):
			with open(self.prm_file, mode='rt') as fil:
				x = fil.read()
				self.prms = ast.literal_eval(x)
		else:
			self.prms = {}
			self.prms['font'] = self.font
			self.prms['font_hidden'] = self.font_hidden
			
		self.log_file = path[:i] + '.log'
		
		if 'current path' not in self.prms:
			self.prms['current path'] = path # default = script path
		self.current_path = self.prms['current path']
			
		if 'popup menu orientation' not in self.prms:
			self.prms['popup menu orientation'] = 'horizontal'
		self.popup_menu_orientation = self.prms['popup menu orientation']
		if self.device_model != 'iPad':
			self.popup_menu_orientation = 'vertical'
		if 'show original area' not in self.prms:
			self.prms['show original area'] = 'no'
		self.show_original_area = self.prms['show original area']
		if 'show lines separator' not in self.prms:
			self.prms['show lines separator'] = 'yes'
		self.show_lines_separator = self.prms['show lines separator']
		if 'checkboxes' not in self.prms:
			self.prms['checkboxes'] = 'yes'
		self.checkboxes = self.prms['checkboxes']
		if 'delete option in red' not in self.prms:
			self.prms['delete option in red'] = 'yes'
		self.red_delete = self.prms['delete option in red']
		if 'tap for popup' not in self.prms:
			self.prms['tap for popup'] = 'single'
		self.tap_for_popup = self.prms['tap for popup']
		if 'autocapitalize type' not in self.prms:
			self.prms['autocapitalize type'] = 'none'
		self.autocapitalize_type = self.prms['autocapitalize type']
		# temporary protection vs invalid data in .prm
		if 'delete in red' in self.prms:
			del self.prms['delete in red']
		if 'auto_save' in self.prms:
			del self.prms['auto_save']
		if 'auto-save' not in self.prms:
			self.prms['auto-save'] = 'no'
		else:
			# temporary protection vs invalid data in .prm
			if 'auto-save' in self.prms['auto-save']:
				self.prms['auto-save'] = 'no'
		self.auto_save = self.prms['auto-save']
		
		if 'folder' in self.prms:
			del self.prms['folder']

		local_path = sys.argv[0]
		#print(local_path)
		path = os.path.expanduser('~/Documents/')
		# /private/var/mobile/Containers/Shared/AppGroup/1B829014-77B3-4446-9B65-034BDDC46F49/Pythonista3/Documents/
		i = len('/private/var/mobile/Containers/Shared/AppGroup/')
		j = path.find('/',i)
		# on my ipad does not have same device_id as local Pythonista....
		device_id_local = path[i:j]
		#print(local_path,device_id_local)
		if 'on_my_path' in self.prms:
			path_on_my = self.prms['on_my_path']
		else:
			path_on_my = '?'
		
		self.path_to_name = {}
		
		self.path_to_name['/private/var/mobile/Containers/Shared/AppGroup/'+device_id_local+'/Pythonista3/Documents/'] = 'Pythonista local'
		
		self.path_to_name['/private/var/mobile/Library/Mobile Documents/iCloud~com~omz-software~Pythonista3/Documents/'] = 'Pythonista iCloud'

		if 'on_my_path' in self.prms:		
			if os.path.exists(path_on_my):
				self.path_to_name[path_on_my] = 'On my ' + self.device_model
		
		path_icloud_drive = '/private/var/mobile/Library/Mobile Documents/com~apple~CloudDocs/'
		if os.path.exists(path_icloud_drive):
			self.path_to_name[path_icloud_drive] = 'iCloud Drive'
		
		self.outline_formats = {
			'decimal':(['v.0','v.v','v.v.v','v.v.v.v','v.v.v.v.v','v.v.v.v.v.v', 'v.v.v.v.v.v.v', 'v.v.v.v.v.v.v.v'],2),
			'alphanumeric':(['I.', 'A.', 'i.', 'a.', '(1).', '(a).'],3),
			'traditional':(['1.', 'A.', 'i.', 'a.', '(1).', '(a).', '((1)).',   '((a)).'],3),
			'bullets':(['•', '‣', '◦', '⦿', '⁃', '⦾', '◘'],3)
			}
			
		self.checkmark_ui_image  = ui.Image.named('emj:Checkmark_3').with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		
		self.save_duration = None
		self.orig_area = None
		self.cells = {}
		
		# must be last process of init	
		local_path = sys.argv[0]
		if len(sys.argv) > 1:
			# 1st argument passed
			if len(sys.argv) > 2:
				# 2nd argument passed 
				parm = sys.argv[2].lower()
				if parm.startswith('local/'):
					l = 6
					folder = 'Pythonista local'
				elif parm.startswith('icloud/'):
					l = 7
					folder = 'Pythonista iCloud'
				elif parm.startswith('onmy'+self.device_model+'/'):
					l = len('onmy'+self.device_model+'/')
					folder = 'On my ' + self.device_model
				elif parm.startswith('iclouddrive'):			
					l = 12
					folder = 'iCloud Drive'
				else:
					console.alert('❌ incorrect base folder','','ok', hide_cancel_button=True)
					return
				for p in self.path_to_name.keys():
					if self.path_to_name[p] == folder:
						path = p
						break
				path = path[l:]				
				path = os.path.expanduser(path)   
			else:
				path = local_path
				i = path.rfind('/')
				path = path[:i+1]
			parm = sys.argv[1]
			if parm.startswith('.'):
				# extension passed
				ext = parm
				#f = self.pick_file('from where to find the file', self['b_files'],ext=ext)
				f = File_Picker.file_picker_dialog('Pick a text file', root_dir=self.path_to_name, file_pattern=r'^.*\{}$'.format(ext))
				if not f:
					console.alert('❌ No file has been picked','','ok', hide_cancel_button=True)
					return
				print(f)
				i = f.rfind('/')
				path = f[:i+1]
				file = f[i+1:]
				self.prms['path'] = path
				self.prms['file'] = file		
			else:
				# file passed
				file = parm
				if not os.path.exists(path+file):
					console.alert('❌ '+file+' passed as argument',"does not exits",'ok', hide_cancel_button=True)
				else:
					i = file.rfind('.')
					if i < 0:
						i = len(file)
					file_content = file[:i] + '.content'
					if not os.path.exists(path+file_content):
						console.alert('❌ '+file_content+' passed as argument',"does not exits",'ok', hide_cancel_button=True)
					else:
						self.prms['path'] = path
						self.prms['file'] = file										
		if 'file' in self.prms:	
			# simulate files button and open last file	
			if not os.path.exists(self.prms['path']+self.prms['file']):
				#console.hud_alert(self.prms['file']+' in .prm does not exist\nprm will be cleaned','error',1)
				del self.prms['path']
				del self.prms['file']
			else:
				self.button_files_action('Open')

	def get_screen_size(self):				
		app = UIApplication.sharedApplication().keyWindow() 
		for window in UIApplication.sharedApplication().windows():
			ws = window.bounds().size.width
			hs = window.bounds().size.height
			break
		return ws,hs
				
	def layout(self):
		ws,hs = self.get_screen_size()
		#print('layout:',ws,hs)
		self.width, self.height = ws,hs
		self.tv.frame = (0,self.ht,ws-2,hs-self.ht)
		nb = 12
		dd = 4
		wb = (ws - (nb+1)*dd)/nb
		if wb > 32:
			wb = 32
			dd = (ws - wb*nb)/(nb+1)
		d = int(ws/nb)
		y = 30 + (self.ht - 30 - wb)/2
		
		x = dd
		self['b_close'].frame = (x,y,wb,wb)
		x = x + wb + dd		
		self['b_version'].frame = (x,y,wb,wb)
		x = x + wb + dd				
		self['b_files'].frame = (x,y,wb,wb)
		x = x + wb + dd				
		self['b_settings'].frame = (x,y,wb,wb)
		x = self.width - wb - dd			
		self['b_format'].frame = (x,y,wb,wb)
		x = x - wb - dd				
		self['b_color'].frame = (x,y,wb,wb)
		x = x - wb - dd				
		self['b_font'].frame = (x,y,wb,wb)
		x = x - wb - dd				
		self['b_fsize'].frame = (x,y,wb,wb)
		x = x - wb - dd		
		self['b_search'].frame = (x,y,wb,wb)
		x = x - wb - dd				
		self['undo_button'].frame = (x,y,wb,wb)
		self['redo_button'].frame = (x,10,wb,wb)
		self['title'].frame = (0,10,x-10,wb)
		x = x - wb - dd				
		self['b_show'].frame = (x,y,wb,wb)
		x = x - wb - dd				
		self['b_filter'].frame = (x,y,wb,wb)
		self['sep'].frame = (0,y+wb,self.width,1)
		self.tv.reload_data()

	def tableview_height_for_section_row(self,tv,section,row):
		#print('tableview_height_for_section_row')
		if tv.name != 'outliner':
			return tv.row_height
		vals,n,opts = tv.data_source.items[row]['content']
		ft = (self.font, self.font_size)
		hidden = False
		if 'hidden' in opts:
			if opts['hidden']:
				hidden = True
				ft = (self.font,self.font_hidden)

		x = self.font_size * 2 + ui.measure_string(tv.data_source.items[row]['outline'], font=ft)[0]
		
		if not hidden and 'image' in opts:
			himg = opts['image'][1]*self.font_size  # (image file name, h_in_rows)
			try:
				image = ui.Image.named(opts['image'][0]).with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			except:
				image = ui.Image.named('emj:Question_Mark_1').with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			wi,hi = image.size
			del image
			wimg = wi * himg/hi
		else:
			himg =  0
			wimg = 0
			
		l = ui.TextView()
		self.set_content_inset(l)
		l.font = ft
		l.text = tv.data_source.items[row]['title']
		l.number_of_lines = 0
		if himg == 0:
			l.frame = (0,0,self.width - x - 4,ft[1])
			l.size_to_fit()
			ho = l.height
		else:
			pos = opts['image'][2]
			if pos == 'left':
				l.frame = (wimg,0,self.width - x - 4 - wimg,ft[1])				
				l.size_to_fit()
				ho = max(himg,l.height)
			elif pos == 'right':
				l.frame = (0,0,self.width - x - 4 - wimg,ft[1])				
				l.size_to_fit()
				ho = max(himg,l.height)
			elif pos == 'top':
				l.frame = (0,0,self.width - x - 4,ft[1])				
				l.size_to_fit()
				ho = himg + l.height
			elif pos == 'bottom':
				l.frame = (0,0,self.width - x - 4,ft[1])				
				l.size_to_fit()
				ho = himg + l.height
		del l

		#print('tableview_height_for_section_row', self.width,ho)
		return ho
		'''
		undo = tv before action
		action
		
		undo:
			redo = tv after action
			tv = undo
		redo:
			tv = redo
		'''	
	def button_undo_action(self,sender):
		#console.alert('Multiple undo/redo still in development')
		#return
		if self.undo_multiples_index > 0:
			items = []
			self.undo_multiples_index -= 1
			for item in self.undo_multiples[self.undo_multiples_index][1]:
				items.append(item.copy())
			self.tv.data_source.items = items
			if self.undo_multiples_index > 0:
				self.button_undo_enable(True, self.undo_multiples[self.undo_multiples_index][0])
			else:
				self.button_undo_enable(False, '')
		else:
			self.button_undo_enable(False, '')
		self.tv.reload_data()
		if self.undo_multiples_index < (len(self.undo_multiples)-1):
			self.button_redo_enable(True,self.undo_multiples[self.undo_multiples_index+1][0])
				
	def button_redo_action(self,sender):
		#console.alert('Multiple undo/redo still in development')
		#return
		if self.undo_multiples_index < (len(self.undo_multiples)-1):
			items = []
			self.undo_multiples_index += 1
			for item in self.undo_multiples[self.undo_multiples_index][1]:
				items.append(item.copy())
			self.tv.data_source.items = items
			if self.undo_multiples_index < (len(self.undo_multiples)-1):
				self.button_redo_enable(True, self.undo_multiples[self.undo_multiples_index][0])
			else:
				self.button_redo_enable(False, '')
		else:
			self.button_redo_enable(False, '')
		self.tv.reload_data()	
		if self.undo_multiples_index > 0:
			self.button_undo_enable(True,self.undo_multiples[self.undo_multiples_index][0])	
		
	def undo_save(self,action):
		#print('undo_save:',action)
		# new action forces delete of all saved undo after index
		if self.undo_multiples_index < (len(self.undo_multiples)-1):
			del self.undo_multiples[self.undo_multiples_index+1:]
		items = []
		for item in self.tv.data_source.items:
			items.append(item.copy())
		self.undo_multiples.append((action,items))
		#print(self.undo_multiples)
		self.undo_multiples_index += 1
		#print('undo_save: size of self.undo_multiples =', sys.getsizeof(self.undo_multiples), 'len=',len(self.undo_multiples))
		self.button_undo_enable(self.undo_multiples_index>0,action)
		
	def button_undo_enable(self,enabled,text):
		#print('button_undo_enable', enabled, text)
		b = self['undo_button']
		b.image = ui.Image.named('iob:ios7_undo_outline_32')
		b.enabled = enabled
		if enabled:
			with ui.ImageContext(b.width,b.height) as ctx:
				b.image.draw(0,0)
				#print('text=|'+text+'|')
				ui.draw_string(text, rect=(0,b.height-16,b.width,14), font=('<system>', 12), color='red')
				b.image = ctx.get_image().with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)			
			
	def button_redo_enable(self,enabled,text):
		#print('button_redo_enable', enabled, text)
		b = self['redo_button']
		b.image = ui.Image.named('iob:ios7_redo_outline_32')
		b.enabled = enabled
		if enabled:
			with ui.ImageContext(b.width,b.height) as ctx:
				b.image.draw(0,0)
				#print('text=|'+text+'|')
				ui.draw_string(text, rect=(0,b.height-16,b.width,14), font=('<system>', 12), color='red')
				b.image = ctx.get_image().with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)			
			
	def button_search_action(self,sender):
		x = sender.x +sender.width/2
		y = 58
		tf = ui.TextField(name='search')
		tf.font = ('Menlo',18)
		tf.frame = (x,y,400,20)
		tf.placeholder = 'type text to be searched'
		tf.delegate = self
		tf.text = ''
		self.present_popover(tf, 'popover',popover_location=(x,y),hide_title_bar=True)
		#tf.present('popover', popover_location=(x,y),hide_title_bar=True)
		#tf.begin_editing()
		#tf.wait_modal()	
		if self.device_model == 'iPad':
			# reset no search
			tf.text = ''
			self.textfield_did_change(tf)
			self.tv.reload_data()

	def textfield_did_change(self, textfield):
		#print('textfield_did_change:', textfield.name, textfield.text)
		if textfield.name == 'search':
			txt = textfield.text
			txt = unicodedata.normalize('NFKD', txt).encode('ASCII', 'ignore')
			txt = str(txt,'utf-8').upper()
			#........... not yet for invisible and hidden	
			row = 0
			for item in self.tv.data_source.items:
				title = self.tv.data_source.items[row]['title']
				t = unicodedata.normalize('NFKD', title).encode('ASCII', 'ignore')
				t = str(t,'utf-8').upper()			
				vals,n,opts = self.tv.data_source.items[row]['content']
				opts['hidden'] = (t.find(txt) < 0)
				self.tv.data_source.items[row]['content'] = (vals,n,opts)
				row += 1
			self.tv.reload_data()
			ui.delay(textfield.begin_editing,0.1)
								
	def button_settings_action(self,sender):
		sections = []
		fields = []
		accessible = [True] + [self.device_model=='iPad']
		fields.append({'title':'popup menu orientation', 'type':'text', 'value':self.popup_menu_orientation, 'key':'segmented1', 'segments':['vertical', 'horizontal'], 'accessible':accessible})
		fields.append({'title':'show original area', 'type':'text', 'value':self.show_original_area, 'key':'segmented4', 'segments':['yes', 'no']})
		fields.append({'title':'log active', 'type':'text', 'value':self.log, 'key':'segmented5', 'segments':['yes', 'no']})
		fields.append({'title':'font size of hidden outlines', 'type':'number', 'pad':pad_integer, 'value':str(self.font_hidden)})
		fields.append({'title':'show lines separator', 'type':'text', 'value':self.show_lines_separator, 'key':'segmented6', 'segments':['yes', 'no']})
		fields.append({'title':'checkboxes', 'type':'text', 'value':self.checkboxes, 'key':'segmented7', 'segments':['yes', 'no']})
		auto_save = 'auto-save'
		if self.file:
			accessible = [True]*3
		else:
			accessible = [True,False,False]
		if self.save_duration:
			auto_save += ' [' + self.save_duration + ']'
		fields.append({'title':auto_save, 'type':'text', 'value':self.auto_save, 'key':'segmented8', 'segments':['no','each char','each line'], 'accessible':accessible})
		
		fields.append({'title':'delete option in red', 'type':'text', 'value':self.red_delete, 'key':'segmented10', 'segments':['yes', 'no']})
		
		fields.append({'title':'tap for popup', 'type':'text', 'value':self.tap_for_popup, 'key':'segmented11', 'segments':['single', 'double']})
		
		fields.append({'title':'autocapitalize type', 'type':'text', 'value':self.autocapitalize_type, 'key':'segmented12', 'segments':['none', 'words', 'sentences', 'all']})

		sections.append((self.current_path,fields))	
		f = my_form_dialog('settings', sections=sections, hd=600)			
		#f = my_form_dialog('settings', fields=fields, hd=600)		
		#print(f)
		if not f:
			# canceled
			return
			
		self.popup_menu_orientation = f['popup menu orientation']
		self.prms['popup menu orientation'] = self.popup_menu_orientation
		
		self.show_original_area = f['show original area']
		self.prms['show original area'] = self.show_original_area
		
		self.log = f['log active']
		self.prms['log active'] = self.log
		
		n = int('0'+f['font size of hidden outlines'])
		self.prms['font_hidden'] = n
		self.set_font(font_hidden_size=n)
		
		self.show_lines_separator = f['show lines separator']
		self.prms['show lines separator'] = self.show_lines_separator
		
		self.checkboxes = f['checkboxes']
		self.prms['checkboxes'] = self.checkboxes
		
		self.auto_save = f[auto_save]
		self.prms['auto-save'] = self.auto_save
				
		self.red_delete = f['delete option in red']
		self.prms['delete option in red'] = self.red_delete
		
		self.tap_for_popup = f['tap for popup']
		self.prms['tap for popup'] = self.tap_for_popup
		
		self.autocapitalize_type = f['autocapitalize type']
		self.prms['autocapitalize type'] = self.autocapitalize_type
		
		self.tv.reload_data()
		
	def button_filter_action(self,sender):
		fields = []
		fields.append({'title':'filter type', 'type':'text', 'value':self.filter[0], 'key':'segmented1', 'segments':['<', '=', '>']})
		fields.append({'title':'filter level', 'type':'number', 'pad':pad_integer, 'value':str(self.filter[1])})
		
		f = my_form_dialog('show only if level', fields=fields, hd=600)		
		#print(f)
		if not f:
			# canceled
			return			
		self.filter = (f['filter type'], int(f['filter level']))
		self.tv.reload_data()		
						
	def button_font_action(self,sender):
		root = self

		conf = UIFontPickerViewControllerConfiguration.alloc().init()
		picker = UIFontPickerViewController.alloc().initWithConfiguration_(conf)

		delegate = PickerDelegate.alloc().init()
		picker.setDelegate_(delegate)
		
		vc = SUIViewController.viewControllerForView_(root.objc_instance)
		vc.presentModalViewController_animated_(picker, True)
		
	def button_fsize_action(self,sender):
		x = sender.x +sender.width/2
		y = 58
		tf = ui.TextField(name='font_size')
		tf.frame = (x,y,200,24)
		tf.placeholder = 'type font size in pixels'
		tf.delegate = self
		SetTextFieldPad(tf, pad_integer)
		tf.text = str(self.font_size)
		self.present_popover(tf, 'popover',popover_location=(x,y),hide_title_bar=True)
		#tf.present('popover', popover_location=(x,y),hide_title_bar=True)
		#tf.begin_editing()
		#tf.wait_modal()	
		if self.device_model == 'iPad':
			n = int(tf.text)
			self.set_font(font_size=n)
		
	def set_font(self,font_type=None,font_size=None,font_hidden_size=None, set=True):
		global font, font_hidden
		if font_type:
			self.font = font_type
		if font_hidden_size != None:
			self.font_hidden = font_hidden_size
		if font_size != None:
			self.font_size = font_size
		font = UIFont.fontWithName_size_(self.font, self.font_size)
		if self.font_hidden > 0:
			font_hidden = UIFont.fontWithName_size_(self.font, self.font_hidden)
		else:
			font_hidden = UIFont.fontWithName_size_(self.font, 0.01)
		self.text_attributes = {NSForegroundColorAttributeName:self.text_color, NSFontAttributeName:font}
		self.text_attributes_hidden = {NSForegroundColorAttributeName:self.text_color, NSFontAttributeName:font_hidden}		
		self.outline_attributes = {NSForegroundColorAttributeName:self.outline_color, NSFontAttributeName:font}
		self.outline_attributes_hidden = {NSForegroundColorAttributeName:self.outline_color, NSFontAttributeName:font_hidden}
		
		self.tv.font = (self.font, self.font_size)
		
		if not set:
			return
			
		self.tv.reload_data()
		
	def present_popover(self, view, mode, popover_location=None, hide_title_bar=False,  color=False):
		if self.device_model == 'iPad':
			time.sleep(0.5) # let time to previous view to close
			view.present(mode, popover_location=popover_location,hide_title_bar=hide_title_bar)
			if isinstance(view, ui.TextField):
				view.begin_editing()
			view.wait_modal()
		else:
			try:
				self.shield.hidden = False
			except:
				self.shield = ui.Button()
				self.shield.frame = (0,0,self.width, self.height)
				if view.name == 'search':
					self.shield.background_color = (1,1,1, 0.3)
				else:
					self.shield.background_color = (0.8, 0.8, 0.8, 0.8)
				self.shield.hidden = False
				self.shield.action = self.shield_tapped
				self.add_subview(self.shield)
			self.shield.view = view
			view.x, view.y = popover_location
			view.x = min(view.x, self.width - view.width - 2)
			view.y = min(view.y, self.height - view.height - 2)
			view.border_width = 1
			view.border_color = 'blue'
			view.corner_radius = 5
			self.add_subview(view)
			self.shield.bring_to_front()
			view.bring_to_front()
			
			if isinstance(view, ui.TextField):
				view.begin_editing()			
			
	def shield_tapped(self, sender):
		# tap outside the popover view
		sender.hidden = True
		try:
			self.remove_subview(sender.view)
			del sender.view
		except:
			pass
		self.selected_row = None

	@ui.in_background		
	def tableview_did_select(self, tableview, section, row):
		#print('tableview_did_select', tableview.name)
		self.selected_row = (section,row)
		if tableview.name != 'outliner':
			# any of the popover tableviews
			if self.device_model == 'iPad':
				# real popover with wait modal
				tableview.close()
			else:
				# simulated popover with shield
				if tableview.name == 'files':
					act = tableview.data_source.items[self.selected_row[1]]
					self.remove_subview(tableview)
					del tableview
					self.shield.hidden = True
					self.files_action(None, act) # no need to pass waited sender
				elif tableview.name == 'formats':					
					loc_format = tableview.data_source.items[self.selected_row[1]]['title']
					self.remove_subview(tableview)
					del tableview
					self.shield.hidden = True
					self.format_action(loc_format)		
				elif tableview.name.startswith('for outline'):										
					row = tableview.outline_row
					act = tableview.data_source.items[self.selected_row[1]]
					self.remove_subview(tableview)
					del tableview
					self.shield.hidden = True
					self.popup_menu_action(act, row=row)
				elif tableview.name == 'show':					
					act = tableview.data_source.items[self.selected_row[1]]
					self.remove_subview(tableview)
					del tableview
					self.shield.hidden = True
					self.show_action(act)		

	def textfield_should_return(self, textfield):
		#print('textfield_should_return:', textfield.name)
		textfield.end_editing()
		if self.device_model == 'iPad':
			textfield.close()  
		else: 
			if textfield.name == 'search':
				textfield.text = ''
				self.textfield_did_change(textfield)
				self.tv.reload_data()
			elif textfield.name == 'font_size':						
				n = int(textfield.text)
				self.set_font(font_size=n)
			elif textfield.name == 'image_size':						
				n = int(textfield.text)				
				pos = textfield['position'].segments[textfield['position'].selected_index]
				self.set_image_size(textfield.row, n, pos)
			self.remove_subview(textfield)
			del textfield
			self.shield.hidden = True
		
	def textfield_did_end_editing(self,textfield):
		#print('textfield_did_end_editing:', textfield.name)
		if textfield.name in ['font_size', 'search', 'image_size']:
			if sys._getframe(1).f_code.co_name == 'key_pressed':
				# return key pressed in SetTextFieldPad
				if self.device_model == 'iPad':
					textfield.close()
				else: 
					if textfield.name == 'search':
						textfield.text = ''
						self.textfield_did_change(textfield)
						self.tv.reload_data()
					elif textfield.name == 'font_size':						
						n = int(textfield.text)
						self.set_font(font_size=n)
					elif textfield.name == 'image_size':						
						n = int(textfield.text)				
						self.set_image_size(textfield.row, n)

					self.remove_subview(textfield)
					del textfield
					self.shield.hidden = True
			else:
				# tap outside popover
				if self.device_model == 'iPad':
					pass
				else: 
					self.shield_tapped(self.shield)

	def button_files_action(self,sender):	
		if not isinstance(sender, ui.Button):
			act = sender
			self.files_action(sender, act)
		else:
			x = sender.x + sender.width/2
			y = sender.y + sender.height
			sub_menu = ['Set current path', 'New', 'Open','Save', 'Rename']
			if self.log == 'yes':
				sub_menu.append('Play log')
			tv = ui.TableView(name='files')
			tv.row_height = 30
			h = tv.row_height*len(sub_menu)
			tv.frame = (0,0,180,h)
			tv.data_source = ui.ListDataSource(items=sub_menu)
			tv.allows_multiple_selection = False
			tv.delegate = self
			self.selected_row = None
			self.present_popover(tv, 'popover',popover_location=(x,y),hide_title_bar=True)
			#tv.present('popover',popover_location=(x,y),hide_title_bar=True)
			#tv.wait_modal()
			if self.device_model == 'iPad':
				if not self.selected_row:
					return
				act = sub_menu[self.selected_row[1]]
				self.files_action(sender, act)

	def files_action(self, sender, act):
		if act in ['New', 'Open']:
			if self.file:
				# current file loaded
				if self.modif:
					# current file modified
					b = console.alert('⚠️ File has been modified', 'save before loading another?', 'yes', 'no', hide_cancel_button=True)
					if b == 1:
						self.file_save()
		if act == 'New':
			self['title'].text = '?'
			self.tv.text = ''
			self.content =[]
			self.outline_format = 'decimal'
			self.set_font(font_type='Menlo', set=False)		
			self.set_font(font_size=18, set=False)	
			# simulate tab pressed
			self.open_log()
			vals = [0]
			outline = self.OutlineFromLevelValue(vals)
			n = len(outline)
			opts = {}
			item = {'title':'','outline':outline, 'content':(vals,n,opts)}
			self.tv.data_source.items = [item]
			self.tv.reload_data
			self.modif = True
			self.cursor = (0,0)
			self.auto_save = 'no'
			self.file = None
			self.undo_multiples = []
			self.undo_multiples_index = -1
			self.undo_save('')
			self.show_mode = 'Expand all'
		elif act == 'Open':
			if sender == 'Open':
				self.path = self.prms['path']
				self.file = self.prms['file']
				if 'font' in self.prms:
					self.set_font(font_type=self.prms['font'])		
				if 'font_size' in self.prms:
					self.set_font(font_size=self.prms['font_size'])	
				if 'font_hidden' in self.prms:
					self.set_font(font_hidden_size=self.prms['font_hidden'])	
				self.pick_open_callback(None)		
			else:
				f = self.pick_file('from where to open the file', uti=['public.item'], callback=self.pick_open_callback, ask=False, init=self.current_path)
				if not f:
					console.alert('❌ No log has been picked','','ok', hide_cancel_button=True)
					return
				if f == 'delayed':
					# Files app via UIDocumentPickerViewController needs delay
					return
				# immediate return for Files_Picker use for local Pythonista files
				simul = 'file://' + f
				self.pick_open_callback(simul)		
		elif act == 'Save':
			self.path = self.current_path
			if not self.file:				
				while True:
					f = console.input_alert('Name of new file', hide_cancel_button=True)
					if not f:
						b = console.alert('❌ No file name has been entered','','retry','cancel',hide_cancel_button=True)
						if b == 2:
							return
						else:
							continue
					if os.path.exists(self.path+f):
						b = console.alert('❌ '+f+' file already exists','in selected folder','retry', 'cancel', hide_cancel_button=True)
						if b == 2:
							return
						else:
							continue
					i = f.rfind('.')
					if i < 0:
						i = len(f)
					file_content = f[:i] + '.content'
					if os.path.exists(self.path+file_content):
						b = console.alert('❌ '+file_content+' file already exists','in selected folder','retry', 'cancel', hide_cancel_button=True)
						if b == 2:
							return
						else:
							continue
					break
				j = f.rfind('.')
				ext = f[j:].lower()
				if ext == '.content':
					console.alert('❌ Name new file as .content','not allowed','ok', hide_cancel_button=True)
					return
				self.file = f
				self.file_content = file_content
			self['title'].text = self.file
			self.file_save()
				
		elif act == 'Rename':
			# check if open/new files exist
			if not os.path.exists(self.path+self.file):
				console.alert('❌ '+self.file+' does not exist', 'rename not allowed','ok', hide_cancel_button=True)
				return
			if not os.path.exists(self.path+self.file_content):
				console.alert('❌ '+self.file_content+' does not exist', 'rename not allowed','ok', hide_cancel_button=True)
				return
			# ask new name
			f = console.input_alert('Name of new file', hide_cancel_button=True)
			if not f:
				console.alert('❌ No file name has been entered','','ok', hide_cancel_button=True)
				return
			# check if new name files do not exist
			i = f.rfind('.')
			if i < 0:
				i = len(f)
			file_content = f[:i] + '.content'
			if os.path.exists(self.path+f):
				console.alert('❌ '+f+' already exists', 'rename not allowed','ok', hide_cancel_button=True)
				return
			if os.path.exists(self.path+file_content):
				console.alert('❌ '+file_content+' already exists', 'rename not allowed','ok', hide_cancel_button=True)
				return
			# rename
			os.rename(self.path+self.file, self.path+f)
			os.rename(self.path+self.file_content, self.path+file_content)
			# activate new file
			self.file = f
			self.file_content = file_content
			self.name = f
		elif act == 'Play log':
			if not self.file:
				console.alert('❌ No file is active','','ok', hide_cancel_button=True)
				return
				
			f = self.pick_file('from where to open the log', uti=['public.item'], callback=self.pick_log_callback, ask=False, init=self.current_path)
			if not f:
				console.alert('❌ No log has been picked','','ok', hide_cancel_button=True)
				return
			if f == 'delayed':
				# Files app via UIDocumentPickerViewController needs delay
				return
			# immediate return for Files_Picker use for local Pythonista files
			simul = 'file://' + f
			self.pick_log_callback(simul)		
		elif act == 'Set current path':
			f = self.pick_file('from where to save', uti=['public.folder'], callback=self.pick_folder_callback)
			if not f:
				console.alert('❌ No folder has been picked','','ok', hide_cancel_button=True)
				return
			if f == 'delayed':
				# Files app via UIDocumentPickerViewController needs delay
				return
			# immediate return for Files_Picker use for local Pythonista files
			simul = 'file://' + f
			self.pick_folder_callback(simul)				
			
	def pick_open_callback(self,param):
		#print('pick_open_callback:',param)
		if param == 'canceled':
			return
		if param:
			# param = None if open at stat without passing by open files option
			f = str(param)[7:]  # remove file://
			i = f.rfind('/')
			j = f.rfind('.',i)
			ext = f[j:].lower()
			if ext == '.content':
				console.alert('❌ Open .content file','not allowed','ok', hide_cancel_button=True)
				return
			self.path = f[:i+1]
			self.file = f[i+1:]
		else:
			# self.path and .file already known
			pass
		i = self.file.rfind('.')
		if i < 0:
			i = len(self.file)
		self.file_content = self.file[:i] + '.content'
		if not os.path.exists(self.path+self.file_content):
			console.alert('❌ '+self.file_content,'does not exist','ok', hide_cancel_button=True)
			return
		self['title'].text = self.file
		i = self.file.rfind('.')
		if i < 0:
			i = len(self.file)
			
		filt = open(self.path+self.file,mode='rt')
		t = filt.read()
		filt.close()
		lines = t.split(lf)
		del t
		filc = open(self.path+self.file_content,mode='rt')
		c = filc.read()
		filc.close()
		c_prms = c.split(lf)
		c = c_prms[0]
		prms = c_prms[1]
		cs = ast.literal_eval(c)
		del c
		del c_prms
		
		row = -1
		i = 0
		pre_c = ()
		items = []
		#print(cs)
		#print(lines)
		for c in cs:
			t = lines[i]
			#print(c,t)
			# c is (vals,n,{opts})
			vals,n,opts = c
			if c != pre_c:
				# new outline
				row += 1
				pre_c = c
				item = {}
				item['title'] = t[n:]
				item['content'] = (vals,n,opts)
				item['outline'] = t[:n]
				items.append(item)
			else:
				# same outline
				items[row]['title'] += lf + t[n:]
			i += 1
			
		self.tv.data_source.items = items
		del cs
		del lines
		
		self.tv.data_source.items = items
		del items
		self.content = []
	
		if prms.startswith('{'):
			prms = ast.literal_eval(prms)
			self.outline_format = prms['format']
			self.set_font(font_type=prms['font'], set=False)		
			self.set_font(font_size=prms['font_size'], set=False)	
		else:
			self.outline_format = prms
						
		#self.set_outline_attributes()
		self.prms_save()
		self.open_log()
		self.cursor = (0,0)
		self.edited_row = None
		self.undo_multiples = []
		self.undo_multiples_index = -1
		self.undo_save('')
		self.show_mode = 'Expand all'


	def pick_folder_callback(self,param):
		#print('pick_folder_callback:',param)
		if param == 'canceled':
			return
		fil = str(param)[7:]  # remove file://				
		if fil[-1] != '/':
			fil += '/'
		self.current_path = fil
		self.prms['current path'] = self.current_path
				
	def pick_log_callback(self,param):
		#print('pick_log_callback:',param)
		if param == 'canceled':
			return
		f = str(param)[7:]  # remove file://
		self.tv.text = ''
		self.content = []
		i = f.rfind('/')
		path = f[:i+1]
		log  = f[i+1:]
		with open(path+log, mode='rt') as fil:
			recs = fil.read().split(lf)
			for rec in recs[:-1]:
				fs = rec.split(',')
				if fs[0] == 'drop':
					found,fm,tm = (int(fs[1]), int(fs[2]), int(fs[3]))
					if len(fs) > 4:
						tgx = int(fs[4])
					else:
						tgx = 0
					self.drop(found, fm, tm, tgx, play=True)
				else:
					row = int(fs[0])
					rge = (int(fs[1]), int(fs[2]))
					rep = fs[3]
					replacement = rep.replace('lf',lf).replace('backtab','\x02').replace('tab','\x01')
					self.textview_should_change(row, rge, replacement, play=True)

	def pick_file(self, title, ext=None, uti=['public.item'], callback=None, ask=True, init=None):
		path = os.path.expanduser('~/')
		if ask:
			# ask user from where
			b = console.alert(title,'','Local Pythonista', 'Files app', hide_cancel_button=True)
		else:
			# use current_path to know from where
			if path in self.current_path:
				b = 1
			else:
				b = 2
			path = self.current_path
		if b == 1:
			if ext:
				fil = File_Picker.file_picker_dialog('Pick a text file', root_dir=path, file_pattern=r'^.*\{}$'.format(ext))	
			elif uti == ['public.folder']:
				fil = File_Picker.file_picker_dialog('Select a folder where to create the new', root_dir=path, select_dirs=True, only=True)
			else:			
				fil = File_Picker.file_picker_dialog(title, root_dir=path)

			#print(fil)
			return fil
		else:	
			time.sleep(0.2)	# to be sure previous uiview closed
			self.picked_file = None
			#ui.delay(partial(self.pick,uti), 0.0)
			UIDocumentPickerViewController = self.MyPickDocument(600,500, callback=callback, UTIarray=uti, init=init)
			return 'delayed'
								
	@on_main_thread	
	def MyPickDocument(self, w, h, callback=None, UTIarray=['public.item'], PickerMode=1, init=None):
		
		# view needed for picker
		uiview = ui.View()
		uiview.frame = (0,0,w,h)
		uiview.present('sheet',hide_title_bar=True)
		
		UIDocumentPickerMode = PickerMode
															# 1 = UIDocumentPickerMode.open
															#   this mode allows a search field
															#   and url in delegate is the original one
															# 0 = UIDocumentPickerMode.import
															#   url is url of a copy
															# 2 = UIDocumentPickerModeExportToService (copy)
															# 3 = UIDocumentPickerModeMoveToService   (move)⚠️
		UIDocumentPickerViewController = ObjCClass('UIDocumentPickerViewController').alloc().initWithDocumentTypes_inMode_(UTIarray,UIDocumentPickerMode)
		#print(dir(UIDocumentPickerViewController))
	
		objc_uiview = ObjCInstance(uiview)
		SUIViewController = ObjCClass('SUIViewController')
		vc = SUIViewController.viewControllerForView_(objc_uiview)	
				
		UIDocumentPickerViewController.setModalPresentationStyle_(3) #currentContext
		
		# Use new delegate class:
		delegate = MyUIDocumentPickerViewControllerDelegate.alloc().init()
		UIDocumentPickerViewController.delegate = delegate	
		UIDocumentPickerViewController.callback = callback	# used by delegate
		UIDocumentPickerViewController.uiview   = uiview  		# used by delegate
		UIDocumentPickerViewController.done = False
		UIDocumentPickerViewController.allowsMultipleSelection = False
		if init:
			UIDocumentPickerViewController.setDirectoryURL_(nsurl(init))
		vc.presentViewController_animated_completion_(UIDocumentPickerViewController, True, None)#handler_block)
		
		return UIDocumentPickerViewController
			
	def open_log(self):			
		if self.log == 'yes':
			try:
				self.log_fil.close()
			except:
				pass
			self.log_fil = open(self.log_file, mode='wt')
					
	def button_version_action(self,sender):
		x = sender.x + sender.width/2
		y = sender.y + sender.height
		tv = ui.TextView(name='versions')
		tv.editable = False
		w,h = self.get_screen_size()
		w -= 100
		h -= 200
		tv.frame = (0,0,w-10,h-10)
		tv.font = ('Menlo',14)
		tv.text = Versions
		tv.name = 'Versions'
		tv.present('popover',popover_location=(x,y),hide_title_bar=False)
		
		# Coloring versions numbers in TextView
		tvo = ObjCInstance(tv)
		tvo.setAllowsEditingTextAttributes_(True)
		txto = ObjCClass('NSMutableAttributedString').alloc().initWithString_(tv.text)
		color = ObjCClass('UIColor').redColor()
		attribs = {NSForegroundColorAttributeName:color, NSFontAttributeName:font}
		vers = re.finditer('Version V', tv.text)
		for ver in vers:
			st,end = ver.span()
			txto.setAttributes_range_(attribs, NSRange(st,end-st+5)) # + 5 due to Vnn.nn
		@on_main_thread
		def th():
			tvo.setAttributedText_(txto)
		th()
		
		#tv.wait_modal()
		
	def button_format_action(self,sender):
		x = sender.x +sender.width/2
		y = 58
		sub_menu = []
		for format in self.outline_formats.keys():
			menu = {'title':format, 'accessory_type':'detail_button'}
			sub_menu.append(menu)
		tv = ui.TableView(name='formats')
		tv.row_height = 30
		h = tv.row_height*len(sub_menu)
		tv.frame = (0,0,180,h)
		lds = ui.ListDataSource(items=sub_menu)
		lds.tableview = tv 	# my own attribute needed in action
		lds.delete_enabled = False
		tv.data_source = lds
		tv.allows_multiple_selection = False
		#i = sub_menu.index(self.outline_format)
		#tv.selected_row = (0,i)
		tv.delegate = self
		lds.accessory_action = self.accessory_action
		lds.action = self.action
		tv.delegate = lds
		self.selected_row = None
		self.present_popover(tv, 'popover',popover_location=(x,y),hide_title_bar=True)
		#tv.present('popover',popover_location=(x,y),hide_title_bar=True)
		#tv.wait_modal()
		if self.device_model == 'iPad':
			if not self.selected_row:
				return
			loc_format = sub_menu[self.selected_row[1]]['title']
			self.format_action(loc_format)		
		
	def format_action(self, loc_format):
		if loc_format != self.outline_format:
			save_format = self.outline_format	# save in case of error
			self.outline_format = loc_format
			# 1) check if format accepts high levels
			for item in self.tv.data_source.items:
				vals,n,opts = item['content']
				t_out = self.OutlineFromLevelValue(vals)
				if not t_out:
					# too high level
					console.alert('❌ too high outline level','for this outline format','ok', hide_cancel_button=True)
					self.outline_format = save_format	# reset
					return
			# 2) repplace outlines
			row = 0
			for item in self.tv.data_source.items:
				vals,n,opts = item['content']
				t_out = self.OutlineFromLevelValue(vals)
				n = len(t_out)
				self.tv.data_source.items[row]['content'] =(vals,n,opts)
				self.tv.data_source.items[row]['outline'] = t_out
				row += 1
			self.modif = True
			self.tv.reload_data()
			
	def action(self, sender):
		#print('action',sender.selected_row)
		self.selected_row = (0,sender.selected_row)
		sender.tableview.close()
			
	def accessory_action(self,sender):
		#print('accessory_action',sender.tapped_accessory_row)
		#sender.tableview.close()
		ft = sender.items[sender.tapped_accessory_row]['title']
		outline_types = self.outline_formats[ft][0]
		blanks = self.outline_formats[ft][1]
		a = []
		for l,outline_type in enumerate(outline_types):
			a.append(' '*blanks*l + outline_type)
		tv = ui.TableView(name='accessory')
		tv.allows_selection = False
		lds = ui.ListDataSource(items=a)
		lds.delete_enabled = False
		tv.data_source = lds
		tv.row_height = 30
		h = tv.row_height*len(outline_types)
		tv.frame = (0,0,180,h)
		tv.name = ft
		x = sender.tableview.width/4
		y = (1+sender.tapped_accessory_row) * sender.tableview.row_height
		self.present_popover(tv, 'popover',popover_location=(x,y),hide_title_bar=True)
		#tv.present('popover',popover_location=(x,y),hide_title_bar=True)
		tv.wait_modal()		
					
	def button_color_action(self,sender):				
		rgb = OMColorPickerViewController(title='choose outline color', rgb=self.outline_rgb)
		self.outline_rgb = rgb
		self.outline_color = UIColor.colorWithRed_green_blue_alpha_(self.outline_rgb[0], self.outline_rgb[1], self.outline_rgb[2], 1)
		self.outline_attributes = {NSForegroundColorAttributeName:self.outline_color, NSFontAttributeName:font}
		
		self.tv.reload_data()
		
	def tableview_number_of_rows(self, tableview, section):
		# Return the number of rows in the section
		return len(tableview.data_source.items)
			
	@on_main_thread
	def set_content_inset(self,bb):
		# Standard TextView has a top positive inset by default
		ObjCInstance(bb).textContainerInset = UIEdgeInsets(0,0,0,0)
		
	#=================== until here ok ==================================p			

	def tableview_cell_for_row(self, tableview, section, row):
		#print('tableview_cell_for_row',row)
		# Create and return a cell for the given section/row
		cell = ui.TableViewCell()
		hrow = self.tableview_height_for_section_row(tableview,section,row)
		self.cells[row] = cell
		item = tableview.data_source.items[row]
		# build cell from left to right
		vals,n,opts = item['content']
		outline = item['outline']
		bg_color = None
		if self.show_original_area == 'yes':		
			# show original area in TextView
			if self.orig_area:
				fr,to =self.orig_area
				if fr <= row <= to:
					bg_color = 'pink'
		hidden = False		
		ft = (self.font, self.font_size)	
		#cell.text_label.text = item['title']
		#cell.text_label.font = ft
		cell.text_label.number_of_lines = 0	# multi-lines
		#cell.text_label.hidden = True
		h = self.font_size
		if 'hidden' in opts:
			if opts['hidden']:
				hidden = True
		img = opts.get('image', None)
		if self.filter:
			if self.filter[0] == '<':
				if len(vals) >= self.filter[1]:
					hidden = True
			elif self.filter[0] == '=':
				if len(vals) != self.filter[1]:
					hidden = True
			elif self.filter[0] == '>':
				if len(vals) <= self.filter[1]:
					hidden = True
		if hidden:
			ft = (self.font, self.font_hidden)
			h = self.font_hidden
			x = self.font_size
		if not hidden:
			if self.checkboxes == 'yes':	
				# 1) checkbox				
				chk = ui.Button(name='checkbox')
				d = 2
				chk.frame = (d,d,h-2*d,h-2*d)
				chk.border_width = 1
				chk.border_color = 'black'
				chk.corner_radius = 4
				chk.font = ('<System>',10)#h-2*d)
				chk.action = self.checkbox_button_action
				chk.row = row
				chk.checkmark = False
				if 'checkmark' in opts:
					chk.checkmark = True
					if opts['checkmark'] == 'yes':
						chk.checkmark = True
						chk.image = self.checkmark_ui_image
						chk.border_width = 0
					elif opts['checkmark'] == 'hidden':
						chk.hidden = True
				cell.content_view.add_subview(chk)			
				if bg_color:
					chk.background_color =  bg_color
					
		# 1) outline it-self
		x = 2 * self.font_size	# after checkbox, let a place for hide/show button
		bb = ui.Label(name='outline')
		bb.row = row
		bb.text = outline
		bb.text_color = self.outline_rgb
		bb.font = ft
		wo,ho = ui.measure_string(outline, font=ft)
		bb.frame = (x,0,wo,ho)
		#bb.border_width = 1
		if self.tap_for_popup == 'single':
			tap(bb,self.single_or_double_tap_handler)
		else:
			doubletap(bb,self.single_or_double_tap_handler)
		long_press(bb,self.long_press_handler)
		cell.content_view.add_subview(bb)
		if bg_color:
			bb.background_color = bg_color
		xaftout = x + wo
			
		if not hidden:
			
			# 2) hide/show button
			j = len(outline) - len(outline.lstrip())	# length of front blanks
			wo,ho = ui.measure_string(' '*j, font=ft)
			x = x - self.font_size + wo
			b = ui.Button(name='hide_show_'+str(row))
			# check of children hidden
			vals = self.tv.data_source.items[row]['content'][0]
			row1 = row + 1
			b.image = ui.Image.named('iob:ios7_circle_filled_32')
			hide = False
			if row1 < len(self.tv.data_source.items):
				# row has nexts
				nvals = self.tv.data_source.items[row1]['content'][0]
				if len(nvals) > len(vals):
					# next is child
					opts = self.tv.data_source.items[row1]['content'][2]
					b.image = ui.Image.named('iob:arrow_down_b_32')
					if 'hidden' in opts:
						if opts['hidden']:
							b.image = ui.Image.named('iob:arrow_right_b_32')
							hide = True
			b.frame = (x,0,h,h)
			b.action = self.hide_children_via_button
			b.data = (row,len(vals)-1,hide)
			cell.content_view.add_subview(b)
			if bg_color:
				b.background_color = bg_color

		x = xaftout
		bb = ui.TextView(name='text')				
		#bb.border_width = 1
		if img and not hidden:	
			# image
			himg = img[1]*self.font_size
			iv = ui.Button()
			iv.row = row
			iv.frame = (x,0,self.width-x-4,hrow)
			iv.content_mode = ui.CONTENT_SCALE_ASPECT_FIT
			try:
				iv.image = ui.Image.named(img[0]).with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			except:
				with ui.ImageContext(32,32) as ctx:
					path = ui.Path.rect(0,0,32,32)
					ui.set_color('yellow')
					path.fill()
					ui.draw_string('open\nerror',rect=(0,0,32,32),color='red')
					iv.image= ctx.get_image().with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			iv.action = self.image_size_action
			wi,hi = iv.image.size
			wimg = wi * himg/hi
			iv.width = wimg
			cell.content_view.add_subview(iv)
			
			pos = img[2]
			if pos == 'left':
				iv.frame = (x,0,wimg,himg)				
				bb.frame = (x+wimg+4,0,self.width - x - 4 - wimg, hrow)
				htxt = hrow
			elif pos == 'right':
				iv.frame = (self.width-wimg,0,wimg,himg)				
				bb.frame = (x,0,self.width - x - 4 - wimg, hrow)			
				htxt = hrow	
			elif pos == 'top':
				htxt = hrow - himg	
				bb.frame = (x,himg,self.width-x-4,htxt)
				iv.frame = (x,0,wimg,himg)
			elif pos == 'bottom':
				htxt = hrow - himg	
				bb.frame = (x,0,self.width-x-4,htxt)			
				iv.frame = (x,htxt,wimg,himg)			
		else:
			himg = 0
			wimg = 0	
			htxt = hrow
			bb.frame = (x,0,self.width - x - 4, hrow)					
			
		# text it-self
		txt = item['title']
		if self.autocapitalize_type == 'none':
			bb.autocapitalization_type = ui.AUTOCAPITALIZE_NONE
		elif self.autocapitalize_type == 'words':
			bb.autocapitalization_type = ui.AUTOCAPITALIZE_WORDS
		elif self.autocapitalize_type == 'sentences':
			bb.autocapitalization_type = ui.AUTOCAPITALIZE_SENTENCES
		elif self.autocapitalize_type == 'all':
			bb.autocapitalization_type = ui.AUTOCAPITALIZE_ALL
		bb.delegate = self
		self.set_content_inset(bb)
		bb.row = row
		bb.text = txt
		bb.text_color = 'blue'
		#bb.border_width = 1
		bb.font = ft
		bb.number_of_lines = 0
		#bb.frame = (x,0,self.width-x-4,ft[1])
		w = bb.width
		bb.size_to_fit()
		ho = bb.height
		bb.frame = (bb.x,bb.y,w,ho)
		#print('bb:',self.font_size,ho)
		swipe(bb, self.swipe_left_handler,direction=LEFT)
		swipe(bb, self.swipe_right_handler,direction=RIGHT)
		#bb.border_width = 1
		cell.content_view.add_subview(bb)
				
		if not hidden:	
			# separation line
			if self.show_lines_separator == 'yes':					
				sep = ui.Label()
				sep.frame = (0,hrow-1,self.tv.width,1)
				sep.border_width = 1
				sep.border_color = 'lightgray'
				cell.content_view.add_subview(sep)	
			# weblinks
			t = txt.lower()
			# set attributes for general text
			attrText = NSMutableAttributedString.alloc().initWithString_(txt)
			attrText.setAttributes_range_(self.text_attributes, NSRange(0,len(txt)))	
			li = 0
			while li < len(t):	
				lk = t.find('http://',li)
				if lk < 0:
					lk = t.find('https://',li)
				if lk < 0:
					break
				lj = t.find(' ',lk)
				if lj < 0:
					lj = len(t)
				link = txt[lk:j+lj]
				self.link_attributes = {NSForegroundColorAttributeName:self.link_color, NSFontAttributeName:font, NSLinkAttributeName:link, NSUnderlineStyleAttributeName:1}
				attrText.setAttributes_range_(self.link_attributes, NSRange(lk,lj-lk))	
				li = lj
			self.set_attributed_text(ObjCInstance(bb), attrText)	
		
		if row == self.cursor[0]:
			bb.begin_editing()
			ui.delay(partial(self.textview_did_begin_editing,bb),0.1)
			c = self.cursor[1]
			if c >= len(bb.text):
				c = max(0,len(bb.text) - 1)
			bb.selected_range = (c,c)
		
		if bg_color:
			bb.background_color = bg_color

		if not hidden:			
			# create ui.View for InputAccessoryView above keyboard
			v = MyInputAccessoryView(row)
			vo = ObjCInstance(v)									# get ObjectiveC object of v
			retain_global(v) # see https://forum.omz-software.com/topic/4653/button-action-not-called-when-view-is-added-to-native-view
			bbo = ObjCInstance(bb)
			bbo.inputAccessoryView = vo	# attach accessory to textview
			#  remove undo/redo/paste BarButtons above standard keyboard
			#bbo.inputAssistantItem().setLeadingBarButtonGroups(None)
			#bbo.inputAssistantItem().setTrailingBarButtonGroups(None)

		return cell
		
	def keyboard_frame_did_change(self, frame):
		# Called when the on-screen keyboard appears/disappears
		# Note: The frame is in screen coordinates.
		#print('keyboard_frame_did_change', frame)
		self.keyboard_y = max(frame[1],self.keyboard_y)
		self.tv.content_inset = (0,0,frame[3],0) # bottom
		
	def textview_did_begin_editing(self, textview):
		#print('textview_did_begin_editing', textview.row)
		#print('before',self.tv.content_offset[1])
		h = textview.height
		# yp = y bottom of row in screen coordinates		
		NSIndexPath = ObjCClass("NSIndexPath")
		nsindex = NSIndexPath.indexPathForRow_inSection_(textview.row,0)
		rect = self.tvo.rectForRowAtIndexPath_(nsindex)
		yp = rect.origin.y + rect.size.height - self.tv.content_offset[1] + self.tv.y + 1
		#print(yp,self.keyboard_y,'content_offset y=',self.tv.content_offset[1])
		if yp > self.keyboard_y:
			#print('row hidden:', textview.row, yp, self.keyboard_y)
			# scroll so bottom of edited line is just above keyboard
			y = self.tv.content_offset[1] + (yp - self.keyboard_y) + 1
			self.tv.content_offset = (0,y)
			
	#def scrollview_did_scroll(self, scrollview):
	#	print('scrollview_did_scroll', scrollview.content_offset[1])
		
	#def textview_did_end_editing(self, textview):
		# if did_end_editing active,
		#    - dismissing keyboard or editing other row, shows new weblink
		#    - crash at lf at end of a row
		#print('textview_did_end_editing', textview.row)
	#	self.tableview_reload_one_row(textview.row)
	#	return True
				
	def textview_should_change(self, textview, range_c, replacement, play=False):
		#print('textview_should_change', range_c,'|'+replacement+'|')
		# problem occurs when replacement is a predictive (non typed) text
		# textview_should_change is called by itself, what forces either crash,
		# either unwanted additional characters

		if len(inspect.stack()) > 1:
			if inspect.stack()[1][3] == 'textview_should_change':
				return False
		# may be called by
		#   swipe left/right on text
		#   tab/backtab in double tap  popup menu
		#   swipe in long n outline
		#   tab/backtab keys
		#   simulated tab in new file
		#   simulated drop by playlog
		if textview == None:
			# for actions outside the textview of the row: popup menu, swipes, ...
			# range_c = (row,row)
			row = range_c[0]
		elif isinstance(textview, int):
			# from play log
			row = textview
			if replacement in [lf, '\x01', '\x02']:
				rep = {lf:'lf', '\x01':'tab', '\x02':'backtab'}[replacement]
			else:
				rep = replacement
			try:
				l = str(len(self.tv.data_source.items[row]['title']))
			except:
				l = 'len of row, row outside limits'
			#print(rep, row, range_c, l)
		else:
			# real textview of the row for text or special keys
			row = textview.row
		#print('before:',textview.text)
			
		# eventual log
		if self.log == 'yes' and not play:
			rec = f"{row},{range_c[0]},{range_c[0]},"
			rep = replacement.replace(lf,'lf').replace('\x02','backtab').replace('\x01','tab')
			rec += rep
			rec += lf
			try:
				self.log_fil.write(rec)
			except:
				console.alert('❌ You did activate the log on an open file, do that only on a new file','automatically desactivated','ok', hide_cancel_button=True)
				self.log = 'no'
		processed = False
		vals_before = None
		if replacement == '\x01':
			# next level outline
			# ==================
			vals,n,opts = self.tv.data_source.items[row]['content']
			if vals == [0]:
				console.alert('❌ increase first level ','not allowed','ok', hide_cancel_button=True)
				return False	# not allowed		
			vals_before = vals.copy()				
			# previous line exists because vals not = [0]
			pvals = self.tv.data_source.items[row-1]['content'][0]

			# check if not increase level of more than 1: begin ====
			if len(pvals) > len(vals):
				a = pvals[len(vals)] + 1
			else:
				a = 0
			nvals = pvals[:len(vals)] + [a] # add one level
			if len(nvals) > (len(pvals)+1):
				console.alert('❌ increase level two consecutive times','not allowed','ok', hide_cancel_button=True)
				return False	# not allowed	
			if nvals == vals:
				console.alert('❌ no change','','ok', hide_cancel_button=True)
				return False	# not allowed	
			# check if not increase level of more than 1: end ========
			outline = self.OutlineFromLevelValue(nvals)
			if not outline:
				# too high level
				console.alert('❌ too high outline level','','ok', hide_cancel_button=True)
				return False	# not allowed		
			# remove old outline

			self.undo_save('tab')	

			n = len(outline)
			self.tv.data_source.items[row]['content']	= (nvals,n,opts)
			self.tv.data_source.items[row]['outline']	= outline

			if len(nvals) > 1:			
				# automatic outlines renumbering of next lines 		
				self.renumbering('tab', row, vals_before, nvals)		
				self.renumbering('all',None,None, None)		

			self.tv.reload_data()
			self.setCursor(row,0)	
			self.modif = True
			return False	# no replacement to process				
		#elif replacement == lf and range_c[0] == len(textview.text):
		elif replacement == lf and range_c[0] == len(self.tv.data_source.items[row]['title']):
			# line feed at end of line
			# ========================
			self.undo_save('CR')		
			# we will add a new row after row, with sale level, value + 1
			self.add_row_after(row)
			return False	# no replacement to process				
		elif replacement == '\x02':
			# back level outline
			# ==================
			vals,n,opts = self.tv.data_source.items[row]['content']
			if len(vals) == 1:
				console.alert('❌ no outline level to decrease','','ok', hide_cancel_button=True)
				return False	# not allowed		
			vals_before = vals.copy()
			# replace old outline by a new one with one level less					
			# remove old outline
			self.undo_save('back')			
			nvals = vals[:-1]
			if len(nvals) > 0:
				nvals = nvals[:-1] + [nvals[-1]+1]
			outline = self.OutlineFromLevelValue(nvals)
			n = len(outline)
			self.tv.data_source.items[row]['content']	= (nvals,n,opts)
			self.tv.data_source.items[row]['outline']	= outline			
			if len(nvals) >= 1:			
				# automatic outlines renumbering of next lines 		
				self.renumbering('backtab', row, vals_before, nvals)		
				self.renumbering('all',None,None, None)		
				
			self.tv.reload_data()
			self.setCursor(row,0)	
			self.modif = True
			return False	# no replacement to process				
			
		elif replacement == '\x03':	
			# delete row and its children
			# ===========================	
			self.undo_save('del')		
			self.delete_row_and_children(row)			
			self.modif = True
			return False	# no replacement to process				
			
		else:
			# normal character, tab, del, cut to remove, lf in text
			# =====================================================
			self.button_undo_enable(False,'')
			t = self.tv.data_source.items[row]['title']
			if lf in t[range_c[0]:range_c[1]]:
				# delete lf, textview will be less high but if return is True,
				# let some time before reload this row
				ui.delay(partial(self.tableview_reload_one_row, row), 0.1)
			t = t[:range_c[0]] + replacement + t[range_c[1]:]
			self.tv.data_source.items[row]['title'] = t

			if replacement == '':
				self.undo_save("...")		
			else:		
				self.undo_save("'" + replacement[0] + "'")		
			
			# if we reach the right side of the cell, a soft lf will be generated
			# and the TextView would need to be resized
			ft = (self.font, self.font_size)
			x = self.font_size * 2 + ui.measure_string(self.tv.data_source.items[row]['outline'], font=ft)[0]
			# before
			l = ui.TextView()
			l.font = ft
			l.number_of_lines = 0
			l.frame = (0,0,self.width - x - 4, ft[1])
			l.text = textview.text
			l.size_to_fit()
			ho_before = l.height
			#print(ho_before,l.text)
			del l
			# after
			l = ui.TextView()
			l.font = ft
			l.number_of_lines = 0
			l.frame = (0,0,self.width - x - 4, ft[1])
			l.text = t
			l.size_to_fit()
			ho_after = l.height
			#print(ho_after,l.text)
			del l
									
			self.modif = True
			self.cursor = (row,range_c[0]) # not needed else if reload done
			#if lf in replacement:
			if ho_after != ho_before:
				# lf not at end, textview will be higher but if return is True,
				# let some time before reload this row
				ui.delay(partial(self.tableview_reload_one_row, row), 0.1)
			return True # no replacement to process				
			
	#def textview_did_change(self, textview):
	# print('textview_did_change')
	#	pass

	def tableview_reload_one_row(self, row):
		self.cursor = (row,0) # not needed else if reload done
		#print('tableview_reload_one_row',row)
		NSIndexPath = ObjCClass("NSIndexPath")
		nsindex = NSIndexPath.indexPathForRow_inSection_(row,0)
		UITableViewRowAnimationNone = 5
		#self.tvo.beginUpdates()
		self.tvo.reloadRowsAtIndexPaths_withRowAnimation_([nsindex], UITableViewRowAnimationNone)
		#self.tvo.endUpdates()

		cell = self.cells[row]
		tv = cell.content_view['text']
		tvo = ObjCInstance(tv)
		i = len(self.tv.data_source.items[row]['title'])
		p1 = tvo.positionFromPosition_offset_(tvo.beginningOfDocument(), i)
		p2 = p1
		tvo.selectedTextRange = tvo.textRangeFromPosition_toPosition_(p1, p2)
			
	def renumbering(self, typ, fr, vals_before, vals_after):		
		if typ == 'all':
			# automatic renumbering of all (no parameters needed)
			row = 0
			pre_vals = []
			while row < len(self.tv.data_source.items):
				vals,n,opts = self.tv.data_source.items[row]['content']
				if len(vals) > len(pre_vals):
					nvals = pre_vals + vals[len(pre_vals):len(vals)-1] + [0]
				elif len(vals) == len(pre_vals):
					nvals = pre_vals[:-1] + [pre_vals[-1]+1]
				else:
					nvals = pre_vals[:len(vals)-1] + [pre_vals[len(vals)-1]+1]
				outline = self.OutlineFromLevelValue(nvals)
				n = len(outline)
				self.tv.data_source.items[row]['outline'] = outline
				self.tv.data_source.items[row]['content'] = (nvals,n,opts)
				row += 1
				pre_vals = nvals
			return
		# automatic outlines renumbering of next lines 
		row = fr + 1
		while row < len(self.tv.data_source.items):
			vals,n,opts = self.tv.data_source.items[row]['content']
			nvals = None
			if typ == 'lf':
				# not called with this parameter, old code
				if len(vals) >= len(vals_after):			
					fr_level = len(vals_after) - 1
					nvals = vals[:fr_level] + [vals[fr_level]+1] + vals[fr_level+1:]
			elif typ == 'tab':
				# tapped outline level already increased
				if vals[:len(vals_before)] == vals_before:
					# child of tabbed outline
					nvals = vals_after + vals[len(vals_before):]
				elif len(vals) >= len(vals_before):					
					fr_level = len(vals_before) - 1
					nvals = vals[:fr_level] + [vals[fr_level]-1] + vals[fr_level+1:]
			elif typ == 'backtab':
				# tapped outline level already decreased
				if vals[:len(vals_before)] == vals_before:
					# child of tabbed outline
					nvals = vals_after + vals[len(vals_before):]
				elif len(vals) >= len(vals_after):					
					fr_level = len(vals_after) - 1
					nvals = vals[:fr_level] + [vals[fr_level]+1] + vals[fr_level+1:]
			elif typ == 'del':
				# not called with this parameter, old code, not tested
				if len(vals) >= len(vals_before):			
					fr_level = len(vals_before) - 1
					nvals = vals[:fr_level] + [vals[fr_level]-1] + vals[fr_level+1:]
			
			if nvals:
				outline = self.OutlineFromLevelValue(nvals)
				n = len(outline)
				self.tv.data_source.items[row]['outline'] = outline
				self.tv.data_source.items[row]['content'] = (nvals,n,opts)
			row += 1
												
	def long_press_handler(self,data):
		global line1,xp1,found
		xp,yp = data.location
		v = data.view
		xp,yp = ui.convert_point(point=(xp,yp), from_view=v, to_view=self.tv)
		#print('long_press_handler',xp,yp,'state=',data.state)
		# get outline
		if data.state == 1:
			# start long_press
			row = v.row
			xp = v.width/2
			yp = v.height/2
			xp,yp = ui.convert_point(point=(xp,yp), from_view=v, to_view=self.tv)
			self.tvm = None
			self.target = None
			line1 = row
			xp1 = xp
			self.drag_children(row,xp,yp)
		elif data.state == 2:
			# move
			if self.tvm:
				self.tvm.x = xp+100
				self.tvm.y = yp
				#--------- show a red line where moving text would be inserted: begin ----
				if yp >= 0:
					indexpath = self.tvo.indexPathForRowAtPoint_(CGPoint(xp,yp))
					#print(indexpath)
					if not indexpath:
						found = len(self.tv.data_source.items) - 1
					else:
						found = indexpath.row()
					#print('found=',found)
					#print('state 2: found=',self.found_redline)					
					cell = self.cells[found]
					v = cell.content_view['text']
					y = v.height
					x,y = ui.convert_point(point=(0,y), from_view=v, to_view=self.tv)
					try:
						self.target.y = y		
					except:
						self.target = ui.Label()
						self.target.frame = (0,y,self.tv.width-4,1)
						self.target.background_color = 'red'
						self.tv.add_subview(self.target)
					# under outline or under text?
					w = v.x
					if (xp-100) > w:
						self.target.x = w
					else:
						self.target.x = 0
				else:
					# before first row
					found = -1
					y = 0
					self.target.x = 0					
					self.target.y = y		
				self.found_redline = found

				# tried but locks					
				#self.auto_scroll(found, even=True)
				#--------- show a red line where moving text would be inserted: end ------
		elif data.state == 3:
			# end
			#print('state 3: found=',self.found_redline)					
			if self.tvm:
				tgx = 0
				self.tv.remove_subview(self.tvm)
				del self.tvm
				if self.target:
					tgx = self.target.x
					self.tv.remove_subview(self.target)
					del self.target

				if self.orig_area:
					# blank original area in TextView
					fr,k1 = self.orig_area
					# search visible rows
					visible_rows ={}
					for indexpath in self.tvo.indexPathsForVisibleRows():
						visible_rows[indexpath.row()] = indexpath
		
					for row in range(fr,k1+1):			
						# if we reload, the long press is cancelled (state 4)
						# thus we need to change the background by another way			
						if row in visible_rows:
							# row is visible	
							cell = self.cells[row]
							for sv in cell.content_view.subviews:
								sv.background_color = 'white'
					self.orig_area = None

				found = self.found_redline
				fm,tm = self.drag_range
				if found >= 0:
					if found == line1:
						cell = self.cells[found]
						tv = cell.content_view['text']
						if xp > xp1:
							# move left to right => simulate tab
							self.textview_should_change(tv,[found,found],'\x01')					
						else:
							# move right to left => simulate back tab
							self.textview_should_change(tv,[found,found],'\x02')				
						return
					if fm <= found <= tm:
						console.alert('❌ Drop into the moving lines', 'not allowed', 'ok', hide_cancel_button=True)	
						return
					# drop
				self.drop(self.found_redline,fm,tm,tgx)
							
	def drag_children(self,fr,xp,yp):
		# prepare text to drag
		bvals = self.tv.data_source.items[fr]['content'][0]
		k1 = fr
		row = fr + 1
		while row < len(self.tv.data_source.items):
			vals = self.tv.data_source.items[row]['content'][0]
			if (len(vals)-1) > (len(bvals)-1):						
				# level higher that from level, set as selected
				k1 = row
			else:
				# level too high, end of select
				break
			row += 1
		#print(fr,k1)
		
		self.drag_range = (fr,k1)
		try:
			self.remove_subview(self['tvm'])
		except:
			pass
		tvm = ui.View(name='tvm')
		# text in moving box: begin
		y = 0
		wmax = 0
		for row in range(fr,k1+1):
			# 1) outline
			x = 0
			ft = (self.font, self.font_size)	
			bg_color = (0.9,0.9,0.9,0.5)
			o = ui.Label()
			txt = self.tv.data_source.items[row]['outline']
			o.text = txt
			o.text_color = self.outline_rgb
			o.background_color = bg_color
			o.font = ft
			wo,ho = ui.measure_string(txt, font=ft)
			o.frame = (x,y,wo,ho)
			tvm.add_subview(o)
			x += wo
			# 2) text it-self
			t = ui.TextView()
			txt = self.tv.data_source.items[row]['title']
			t.text = txt
			self.set_content_inset(t)
			t.text_color = 'black'
			t.background_color = bg_color
			t.font = ft
			wo,ho = ui.measure_string(txt, font=ft)
			wo += 20
			t.frame = (x,y,wo,ho)
			y += ho
			tvm.add_subview(t)
			wmax = max(wmax, x+wo)
		# text in moving box: end
		h = y
		xdrag = xp + 100 # only to not hide the moving box by the finger
		ydrag = yp 
		tvm.frame = (xdrag,ydrag,wmax,h)
		tvm.border_width = 1
		r = 10
		tvm.corner_radius = r/2
		tvm.background_color = (0.9,0.9,0.9,0.5)
		self.tvm = tvm
		self.tv.add_subview(tvm)

		if self.show_original_area == 'yes':		
			# show original area in TextView
			self.orig_area = (fr,k1)
			# search visible rows
			visible_rows ={}
			for indexpath in self.tvo.indexPathsForVisibleRows():
				visible_rows[indexpath.row()] = indexpath

			for row in range(fr,k1+1):			
				# if we reload, the long press is cancelled (state 4)
				# thus we need to change the background by another way			
				if row in visible_rows:
					# row is visible	
					cell = self.cells[row]
					for sv in cell.content_view.subviews:
						sv.background_color = 'pink'
		
	def drop(self,found, fm, tm, tgx, play=False):
		#print('drop:', found, fm,tm, len(self.tv.data_source.items))
		self.undo_save('move')
		
		# eventual log
		if self.log == 'yes' and not play:
			rec = f"drop,{found},{fm},{tm},{tgx}"
			rec += lf
			self.log_fil.write(rec)
		
		under_outline = (tgx == 0)

		if found >= 0:
			pre_vals = self.tv.data_source.items[found]['content'][0]	# vals of prev row
		else:
			pre_vals = [-1]
		# process dropped lines
		first = True
		row = fm
		moved_items = []
		while row <= tm:
			vals,n,opts = self.tv.data_source.items[row]['content']
			if first:
				vals1 = vals.copy()
				if under_outline:
					# drop under outline
					# same level as previous
					nvals = pre_vals[:-1] + [pre_vals[-1]+1]
				else:
					# drop under text
					# next level vs previous
					nvals = pre_vals + [0]
				nvals1 = nvals.copy()
				first = False
			else:
				ndiff = len(vals) - len(vals1) 
				nvals = nvals1 + vals[-ndiff:]  
			outline = self.OutlineFromLevelValue(nvals)
			n = len(outline)
			item ={}
			item['title'] = self.tv.data_source.items[row]['title']
			item['outline'] = outline
			item['content'] = (nvals,n,opts)
			moved_items.append(item)
			row += 1
		self.tv.data_source.items = self.tv.data_source.items[:found+1] + moved_items + self.tv.data_source.items[found+1:]
		
		# remove original
		nbr_added_rows = tm - fm + 1
		if tm > found:
			# deleted part after insertion, thus increase indexes
			fm += nbr_added_rows
			tm += nbr_added_rows
		# if copy instead of move, comment this line: begin ========
		self.tv.data_source.items = self.tv.data_source.items[:fm] + self.tv.data_source.items[tm+1:]
		# if copy instead of move, comment this line: end  ==========
		
		# renumbering after old removed
		self.renumbering('all',None,None, None)		
		
		self.tv.reload_data()
		c = found + 1
		if tm < found:
			c -= nbr_added_rows
		self.setCursor(c,0)	
		self.modif = True
		
		return
			
	@on_main_thread
	def set_attributed_text(self,tvo,t):
		tvo.setAttributedText_(t)

	def setCursor(self,row,index):
		#print('setCursor')
		rowc = row
		indexc = index
		while rowc < len(self.tv.data_source.items):
			opts = self.tv.data_source.items[rowc]['content'][2]
			hidden = False
			if 'hidden' in opts:
				if opts['hidden']:
					hidden = True
			if not hidden:
				self.cursor = (rowc,indexc)
				self.auto_scroll(rowc)
				return
			rowc += 1
			indexc = 0
		rowc = min(row,len(self.tv.data_source.items)-1)
		while rowc >= 0:
			#print(rowc)
			opts = self.tv.data_source.items[rowc]['content'][2]
			hidden = False
			if 'hidden' in opts:
				if opts['hidden']:
					hidden = True
			if not hidden:
				self.cursor = (rowc,indexc)
				self.auto_scroll(rowc)
				return
			rowc += -1
			indexc = 0
			
	def auto_scroll(self,row, even=False, UITableViewScrollPosition=1):
		#print('auto_scroll', row, 'even=',even)
		# search which rows are visible
		if not even:
			for indexpath in self.tvo.indexPathsForVisibleRows():
				if indexpath.row() == row:
					# row is visible, no scroll needed
					return
		# automatic scroll to row
		#print('scroll')
		NSIndexPath = ObjCClass("NSIndexPath")
		nsindex = NSIndexPath.indexPathForRow_inSection_(row,0	)
		# UITableViewScrollPosition = 0 None
		#															1 Top
		#															2 Middle
		#															3 Bottom
		self.tvo.scrollToRowAtIndexPath_atScrollPosition_animated_(nsindex, UITableViewScrollPosition, True)
			
	def checkbox_button_action(self,sender):
		reshow_all = False
		row = sender.row
		vals,n,opts = self.tv.data_source.items[row]['content']
		if sender.checkmark:
			opts['checkmark'] = 'no'
			sender.image = None			
			sender.border_width = 1
			if self.show_mode == 'Show checked only':
				opts['hidden'] = True
				reshow_all = True
		else:
			opts['checkmark'] = 'yes'
			sender.image = self.checkmark_ui_image
			sender.border_width = 0
			if self.show_mode == 'Hide checked':
				opts['hidden'] = True
				reshow_all = True
		sender.checkmark = not sender.checkmark
		self.tv.data_source.items[row]['content'] = (vals,n,opts)
		self.modif = True
		if reshow_all:
			self.tv.reload_data()
		
	def popup_menu_action(self,actin, row=None):
		#print('popup_menu_action',row,actin)
		act = actin.replace('\n',' ')
		vals,n,opts = self.tv.data_source.items[row]['content']
		if act == 'hide children':
			self.hide_children(row,len(vals)-1,hide=True)
		elif act == 'show children':
			self.hide_children(row,len(vals)-1,hide=False)
		elif act == '⏭':			
			self.textview_should_change(None,[row,row],'\x01')				
		elif act == '⏮':			
			self.textview_should_change(None,[row,row],'\x02')			
		elif act == '✅':	
			self.check_children(row,len(vals)-1,check='yes')	
		elif act == '⬜️':		
			self.check_children(row,len(vals)-1,check='no')			
		elif act == 'no box':	
			vals,n,opts = self.tv.data_source.items[row]['content']
			opts['checkmark'] = 'hidden'
			self.tv.data_source.items[row]['content'] = vals,n,opts
			self.modif = True	
			#self.tableview_reload_one_row(row)
			self.tv.reload_data()
		elif act == 'delete with children':
			self.textview_should_change(None,[row,row],'\x03')			
		elif act == '🖼':	
			self.image_row = row
			f = self.pick_file('from where to open the image', uti=['public.image'], callback=self.pick_image_callback)
			if not f:
				console.alert('❌ No image has been picked','','ok', hide_cancel_button=True)
				return
			if f == 'delayed':
				# Files app via UIDocumentPickerViewController needs delay
				return
			# immediate return for Files_Picker use for local Pythonista files
			simul = 'file://' + f
			self.pick_image_callback(simul)

	def pick_image_callback(self,param):
		#print('pick_image_callback:',param)
		if param == 'canceled':
			return
		f = str(param)[7:]  # remove file://
		row = self.image_row
		vals,n,opts = self.tv.data_source.items[row]['content']
		opts['image'] = (f,2,'left')
		self.tv.data_source.items[row]['content'] = vals,n,opts
		self.modif = True	
		self.tv.reload_data()				
		
	def image_size_action(self,sender):
		row = sender.row
		vals,n,opts = self.tv.data_source.items[row]['content']
		pos = opts['image'][2] # ex: 'left'
		x = sender.width/2
		y = sender.height/2
		x,y = ui.convert_point(point=(x,y), from_view=sender, to_view=None)
		tf = ui.TextField(name='image_size')
		tf.frame = (0,0,300,50)
		tf.delegate = self
		SetTextFieldPad(tf, pad_integer)
		tf.text = str(opts['image'][1])
		tf.row = sender.row
		tf.text_color = 'green'
		ph = ui.Label()
		ph.frame = (50,0,tf.width-50,20)
		ph.text = 'height in number of lines'
		ph.text_color = 'gray'
		tf.add_subview(ph)
		sg = ui.SegmentedControl(name='position')
		sg.segments = ['left','right','top','bottom']
		sg.selected_index = sg.segments.index(pos)
		sg.frame = (50,25,tf.width-50,20)
		tf.add_subview(sg)
		self.present_popover(tf, 'popover',popover_location=(x,y),hide_title_bar=True)
		if self.device_model == 'iPad':
			n = int(tf.text)
			pos = tf['position'].segments[tf['position'].selected_index]
			self.set_image_size(tf.row, n, pos)
			
	def set_image_size(self,row, ns, pos):
		vals,n,opts = self.tv.data_source.items[row]['content']
		f,s,posn = opts['image']
		opts['image'] = (f,ns,pos)
		self.tv.data_source.items[row]['content'] = (vals,n,opts)
		self.modif = True
		self.tv.reload_data()
			
	def add_row_after(self,row):
			self.undo_save('CR')
			vals = self.tv.data_source.items[row]['content'][0]
			nvals = vals[:-1] + [vals[-1]+1]
			outline = self.OutlineFromLevelValue(nvals)
			dt = datetime.now()
			creation_date = f'{dt:%Y-%m-%d %H:%M:%S}'
			opts = {}
			opts['dates'] = (creation_date,None,None,None)
			n = len(outline)
			item = {}
			item['title'] = ''
			item['outline'] = outline
			item['content'] = (nvals,n,opts)
			#self.tv.data_source.items.insert(row+1,item)
			self.tv.data_source.items = self.tv.data_source.items[:row+1] + [item] + self.tv.data_source.items[row+1:]
			#if len(nvals) >= 1:			
			#	# automatic outlines renumbering of next lines 		
			#	fr = range_c[0]+1
			#	self.renumbering('lf', row+1, None, nvals)		
			self.renumbering('all',None,None, None)		
			self.tv.reload_data()
			self.modif = True
			self.setCursor(row+1,0)
			
	def delete_row_and_children(self,row):
		# delete row 
		self.undo_save('dele')
		vals = self.tv.data_source.items[row]['content'][0]
		del self.tv.data_source.items[row]
		# delete children
		# row1 does not change because continuous delete row until break
		row1 = row
		while row1 < len(self.tv.data_source.items):
			dvals = self.tv.data_source.items[row1]['content'][0]		
			if len(dvals) > len(vals):
				# child
				del self.tv.data_source.items[row1]				
			else:
				break
		if len(self.tv.data_source.items) == 0:
			# no more row, add first like a new file
			vals = [0]
			outline = self.OutlineFromLevelValue(vals)
			n = len(outline)
			opts = {}
			item = {'title':'','outline':outline, 'content':(vals,n,opts)}
			self.tv.data_source.items = [item]
			self.setCursor(0,0)
		else:
			self.setCursor(max(0,row-1),0)

		# renumbering 
		self.renumbering('all',None,None, None)
		self.modif = True
		self.tv.reload_data()
			
	def swipe_left_handler(self,data):
		v = data.view
		row = v.row
		self.textview_should_change(None,[row,row],'\x02')				
		
	def swipe_right_handler(self,data):
		v = data.view
		row = v.row
		self.textview_should_change(None,[row,row],'\x01')				
		
	def tableview_title_for_header(self, tv, section):
		return tv.name
				
	def single_or_double_tap_handler(self,data):
		#print('single_or_double_tap_handler_handler',data)
		xp,yp = data.location
		v = data.view
		row = v.row
		#ui.delay(self.cells[row].content_view['text'].end_editing,0.1)
		#v.border_width = 1
		# popover at right of outline
		#print(xp,yp,data.state)
		xp = v.width/2
		yp = v.height/2
		xp,yp = ui.convert_point(point=(xp,yp), from_view=v, to_view=None)
		vals,n,opts = self.tv.data_source.items[row]['content']
		t = self.tv.data_source.items[row]['outline']
		sub_menu = ['hide children', 'show children', 'delete with children', '⏭', '⏮']
		sub_menu.append('🖼')
		if self.checkboxes == 'yes':
			sub_menu = sub_menu +  ['⬜️', '✅', 'no box']
		if self.popup_menu_orientation == 'vertical':
			#=== vertical: popup menu
			tv = ui.TableView('grouped')
			ft = ('Menlo',16)
			wmax = 0
			for act in sub_menu:
				w = ui.measure_string(act,font=ft)[0]
				wmax = max(w,wmax)
			tv.name = 'for outline '+ t
			tblo = ObjCInstance(tv)
			hh = 30
			tblo.sectionHeaderHeight = hh
			tv.outline_row = row
			tv.row_height = hh
			h = tv.row_height*len(sub_menu)
			tv.frame = (0,0,wmax+40,h+hh)
			tv.data_source = ui.ListDataSource(items=sub_menu)
			tv.data_source.tableview_title_for_header = self.tableview_title_for_header
			tv.data_source.font = ft
			tv.allows_multiple_selection = False
			tv.delegate = self
			self.selected_row = None
			self.present_popover(tv, 'popover',popover_location=(xp,yp),hide_title_bar=True)
			#tv.present('popover',popover_location=(xp,yp),hide_title_bar=False)
			#tv.wait_modal()
			if self.device_model == 'iPad':
				if not self.selected_row:
					return
				act = sub_menu[self.selected_row[1]]
				self.popup_menu_action(act, row=row)
		else:
			#=== horizontal popup menu **** not available on iPhone ****
			popup = ui.View()
			h = 40
			x = 0
			ft = ('Menlo',14)			
			for act in [t] + sub_menu:
				b = ui.Button()
				b.title = act
				ib = b.title.find(' ')
				if ib >= 0:
					# split title in two lines
					b.title = b.title[:ib] + '\n' + b.title[ib+1:] # 1st blank only
					for sv in ObjCInstance(b).subviews(): 
						if hasattr(sv,'titleLabel'):
							tl = sv.titleLabel()
							tl.numberOfLines = 0
				w = ui.measure_string(b.title,font=ft)[0] + 10
				x += 8
				b.frame = (x,0,w,h)
				if self.red_delete == 'yes':
					if 'delete' in act:
						b.background_color = 'red'
				x += w
				b.font = ft
				if act == t:
					b.tint_color = 'yellow'
				else:
					b.tint_color = 'white'
					b.row = row
					b.action = self.set_popup_menu_tapped
				popup.add_subview(b)
				l = ui.Label()	
				x += 10		
				l.frame = (x,0,1,h)			
				l.background_color = (0.5,0.5,0.5,0.8)
				popup.add_subview(l)	
			popup.frame = (0,0,x-2,h) # don't show last vertical line
			# "bg" is the color you want to set the popover view to
			popup.background_color = 'black'

			self.popup_menu_tapped = None			
			self.present_popover(popup, 'popover',popover_location=(xp,yp),hide_title_bar=True)
			#print(self.popup_menu_tapped)
			if self.popup_menu_tapped:
				self.popup_menu_action(self.popup_menu_tapped, row=row)
			
	def set_popup_menu_tapped(self,sender):
		self.popup_menu_tapped = sender.title
		sender.superview.close()

	def console_alert(self):
		console.alert(self.alert_title, self.alert_msg, 'ok', hide_cancel_button=True)

	def hide_children_via_button(self,sender):
		#print('hide_children_via_button',sender.data)
		row, fr_level, hide = sender.data
		hide = not hide
		self.hide_children(row, fr_level, hide=hide)
		
	def hide_children(self,fr, fr_level, hide=True):
		#print('hide_children:',fr,fr_level,hide)
		row = fr + 1	# start after row of tapped button
		while row < len(self.tv.data_source.items):
			vals,n,opts = self.tv.data_source.items[row]['content']
			if (len(vals)-1) > fr_level:						
				# level higher that from level, set as (un)hidden
				opts['hidden'] = hide
				self.tv.data_source.items[row]['content'] = vals,n,opts
				self.modif = True
			else:
				# level too high, end of (un)hiding
				break
			row += 1
		self.tv.reload_data()
		
	def check_children(self,fr, fr_level, check='yes'):
		#print('check_children:',fr,fr_level, check)
		row = fr # start from row of tapped button
		while row < len(self.tv.data_source.items):
			vals,n,opts = self.tv.data_source.items[row]['content']
			if row == fr or (len(vals)-1) > fr_level:						
				# tapped row or level higher that from level, set as (un)checked
				opts['checkmark'] = check
				self.tv.data_source.items[row]['content'] = vals,n,opts
				self.modif = True
			else:
				# level too high, end of (un)hiding
				break
			row += 1
		self.tv.reload_data()
			
	def button_show_action(self,sender):
			x = sender.x + sender.width/2
			y = sender.y + sender.height
			sub_menu = ['Collapse all', 'Expand all', 'Hide checked', 'Show checked only']
			tv = ui.TableView(name='show')
			tv.row_height = 30
			h = tv.row_height*len(sub_menu)
			tv.frame = (0,0,180,h)
			tv.data_source = ui.ListDataSource(items=sub_menu)
			tv.allows_multiple_selection = False
			tv.delegate = self
			self.selected_row = None
			self.present_popover(tv, 'popover',popover_location=(x,y),hide_title_bar=True)
			if self.device_model == 'iPad':
				if not self.selected_row:
					return
				act = sub_menu[self.selected_row[1]]
				self.show_action(act)
				
	def show_action(self,act):
		self.show_mode = act
		for row, item in enumerate(self.tv.data_source.items):
			vals,n,opts = item['content']			
			if act == 'Collapse all':	
				if len(vals) > 1:
					opts['hidden'] = True
				else:
					opts['hidden'] = False
			elif act == 'Expand all':	
				opts['hidden'] = False
			elif act == 'Hide checked':	
				if 'checkmark' not in opts:
					opts['hidden'] = False				
				elif opts['checkmark'] == 'yes':
					opts['hidden'] = True
				elif opts['checkmark'] == 'no':
					opts['hidden'] = False
				elif opts['checkmark'] == 'hidden':
					opts['hidden'] = False
			elif act == 'Show checked only':	
				if 'checkmark' not in opts:
					opts['hidden'] = True			
				elif opts['checkmark'] == 'yes':
					opts['hidden'] = False
				elif opts['checkmark'] == 'no':
					opts['hidden'] = True
				elif opts['checkmark'] == 'hidden':
					opts['hidden'] = True
			self.tv.data_source.items[row]['content'] = vals,n,opts	
		self.tv.reload_data()
			
	def int_to_roman(self,n):
		if n >= 0 and n <= 1000:
			d = [{'0':'','1':'M'}, {'0':'','1':'C','2':'CC','3':'CCC','4':'DC','5':'D', '6':'DC','7':'DCC','8':'DCCC','9':'MC'},{'0':'','1':'X','2':'XX','3':'XXX','4':'XL','5':'L', '6':'LX','7':'LXX','8':'LXXX','9':'CX'},{'0':'','1':'I','2':'II','3':'III','4':'IV','5':'V', '6':'VI','7':'VII','8':'VIII','9':'IX'}]
			x = str('0000' + str(n))[-4:]
			r = ''
			for i in range(4):
				r = r + d[i][x[i]]
			return r
			
	def int_to_alpha(self,n):
		r = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[n-1]
		return r
		
	def OutlineFromLevelValue(self,vals):
		'''
		Decimal format
		1.0 Item
		2.0 Item
		  2.1 Child
		  2.2 Child
			  2.2.1 Child at next level
		Alphanumeric format
		I.  Highest level
		   A. Child node
		   B. Second Child node
		II. Second level.
		   A. Child node
		   B. 2nd child
		      i. Next level
		     ii. etc.
		       a. etc.
		Traditional format
		1.  Highest level
		   A. Child node
		   B. Second Child node
		2. Second level.
		   A. Child node
		   B. 2nd child
		      i. Next level
		     ii. etc.
		       a. etc.
		'''
		# vals parameter is an array of level+1 values
		outline_types = self.outline_formats[self.outline_format][0]
		# check if level not too high
		if len(vals) > len(outline_types):
			return None
		blanks = self.outline_formats[self.outline_format][1]
		level = len(vals)-1
		outline_type = outline_types[level] + ' '	# temporary _ will be blank later
		
		v = vals[-1]
		if 'v' in outline_type:
			for v in vals:
				outline_type = outline_type.replace('v',str(v+1),1)
		elif 'I' in outline_type:
			outline_type = outline_type.replace('I', self.int_to_roman(v+1), 1)
		elif 'A' in outline_type:
			outline_type = outline_type.replace('A', self.int_to_alpha(v+1), 1)
		elif 'i' in outline_type:
			outline_type = outline_type.replace('i', self.int_to_roman(v+1), 1).lower()
		elif 'a' in outline_type:
			outline_type = outline_type.replace('a', self.int_to_alpha(v+1), 1).lower()
		elif '1' in outline_type:
			outline_type = outline_type.replace('1', str(v+1), 1)
			
		outline_type = ' ' * blanks * level + outline_type
		#print(vals,outline_type)
		return outline_type	
		
	def file_save(self, save_prm=True):
		#print('file_save')
		t1 = datetime.now()

		# delete .old version
		if os.path.exists(self.path+self.file+'.old'):
			os.remove(self.path+self.file+'.old')
		if os.path.exists(self.path+self.file_content+'.old'):
			os.remove(self.path+self.file_content+'.old')
		# rename current into .old
		if os.path.exists(self.path+self.file):
			os.rename(self.path+self.file, self.path+self.file+'.old')
		if os.path.exists(self.path+self.file_content):
			os.rename(self.path+self.file_content, self.path+self.file_content+'.old')
		# save current
		with open(self.path+self.file, mode='wt') as fil:
			t = ''
			c = []
			for item in self.tv.data_source.items:
				ls = item['title'].split(lf)
				outline = item['outline']
				first = True
				for l in ls:
					if first:
						t += outline          + l + lf #1.1_Word 1
						first = False
					else: 
						t += ' '*len(outline) + l + lf #    Word 2
					c.append(item['content'])									# (vals,n,{options})
			fil.write(t)
			del t
		with open(self.path+self.file_content, mode='wt') as fil:
			prms ={}
			prms['format'] = self.outline_format
			prms['font'] = self.font
			prms['font_size'] = self.font_size			
			t = str(c) + lf + str(prms)
			fil.write(t)
			del t
			del c
		self.modif = False
		self.prms['path'] = self.path
		self.prms['file'] = self.file
		t2 = datetime.now()
		self.save_duration = str(t2-t1)

		if save_prm:		
			self.prms_save()

	def prms_save(self):	
		self.prms['font'] = self.font
		self.prms['font_size'] = self.font_size
		self.prms['font_hidden'] = self.font_hidden
		with open(self.prm_file, mode='wt') as fil:
			x = str(self.prms)
			fil.write(x)
					
	def close_action(self, sender):
		if self.log == 'yes':
			try:
				self.log_fil.close()
			except:
				pass
		if self.modif:
			b = console.alert('⚠️ File has been modified', 'save before leaving?', 'yes', 'no', hide_cancel_button=True)
			if b == 1:
				self.button_files_action('Save')
		self.prms_save()
		self.close()

def main():
	global mv
	
	if appex.is_running_extension():
		# runs in appex mode, only used to get path of "on my device"
		path = appex.get_file_path()
		if not path:
			console.alert('❌ No path passed', '', 'ok', hide_cancel_button=True)
			appex.finish()
			return	
		# /private/var/mobile/Containers/Shared/AppGroup/EF3F9065-AD98-4DE3-B5DB-21170E88B77F/File Provider Storage/.....
		t1 = '/private/var/mobile/Containers/Shared/AppGroup/'
		t2 = '/File Provider Storage/'
		device_model = str(ObjCClass('UIDevice').currentDevice().model())			
		if t1 not in path or t2 not in path:
			console.alert('❌ No share of file from', 'On my ' + device_model, 'ok', hide_cancel_button=True)
			appex.finish()
			return				
		i = path.find(t2)
		i += len(t2)
		path_onmy = path[:i]
		path = sys.argv[0]
		i = path.rfind('.')
		prm_file = path[:i] + '.prm'
		if not os.path.exists(prm_file):
			console.alert('❌ .prm file has to exist', '', 'ok', hide_cancel_button=True)
			appex.finish()
			return				
		with open(prm_file, mode='rt') as fil:
			x = fil.read()
			prms = ast.literal_eval(x)
		prms['on_my_path'] = path_onmy
		with open(prm_file, mode='wt') as fil:
			x = str(prms)
			fil.write(x)
		appex.finish()
		return				
	# normal mode
	mv = Outliner()
	mv.present('fullscreen', hide_title_bar=True)
	
if __name__ == '__main__':
	main()
