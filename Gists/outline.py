'''
todo 
====
- .. new: save in Files folders
		onmydevice '/private/var/mobile/Containers/Shared/AppGroup/EF3F9065-AD98-4DE3-B5DB-21170E88B77F/File Provider Storage/'
		sys.argv private/var/mobile/Containers/Shared/AppGroup/1B829014-77B3-4446-9B65-034BDDC46F49/Pythonista3/Documents/
		icloud drive '/private/var/mobile/Library/Mobile Documents/com~apple~CloudDocs/'

		
- .. bug: ❗️type => scroll maximum when typing 
					sans doute dû au fait que outlines set le texte entier
					
- .. new: why not have the user specify a name and location when they save
          (could be reminded at exit?). I prefer to be able to start the script and just begin writing rather than naming the file, selecting its location, changing font prefs, etc.
		- not if autosave
		- new file: not ask folder and name at new tapped
		- name = ? as view title
		- when first save (auto or not), ex: at end, locate folder and ask name
					
- .. 1️⃣think about a better way to process outlines
			- content = array of outlines infos: levels[0,1,2],n,i,{options like checkbox}
				- no repeat, no normal characters
				- memo index in text?  and reverse i -> array?
			- insert,del,add line is easier
			- get previous or next line is easier
			- no need to set content = content + ... + content
			- store, by example, in checkbox button, index ipo position in text
			- quicker process
			BUT review of entire process is needed and remove all .content files
			
			************************
			* month of August 2021 *
			************************
	
- .. 2️⃣do not rebuild outlines when normal character typed
				only text attributes of one line should be done
				but indexes of outlines change thus self.content[i] where i changes,
				at least part after typed character
				*** EASIER if new way for .content ***
	
- .. .log with new or open file name +.log

- .. new: delete line with or without children
			- options de popumenu
			- afficher zone original a detruire + confirmation?
			- del comme drop del part
			- renumbering after del area, comme drop del part

- .. new: drag with copy
			- start how? popupmenu: move line with its children
			- display moving box
			- touch state = 1 = take it
			-               2 = move it
			-               3 = drop it copy without delete and remove box
			- how to cancel it without drop: drop outside

- .. Q?: long lines, auto lf => outline not visible
- .. - if changing font size or font generates longer/shorter lines, 
					automatic redo because set_outline_attributes called
- .. - def set_outline_attributes, 
				before generation of attribute texts
				
					... remove previous soft lf
					# support automatic lf due to line break: begin ============
					t = ''
					c = []
					i = 0
					while i < len(self.tv.text):
						ilf = self.tv.text.find(lf,i)
						if ilf < 0:
							then ilf = len(self.tv.text)
						tt = t[i:ilf]
						w = ui.measure_string(tt,font=(self.font or ...hidden, self.font_size))
						if w > self.tv.width:
							.... où faire le(s) break(s)?
						else:
							t += tt + lf
							c += self.content[i:lf] + [lf]
						i = ilf + 1
					self.tv.text = t
					self.content = c
					
					// This method takes in the `UITextView` and returns the string
// representation which includes the newline characters
- (NSString*)textViewWithNewLines:(UITextView*)textView {

    // Create a variable to store the new string
    NSString *stringWithNewlines = @"";

    // Get the height of line one and store it in
    // a variable representing the height of the current
    // line
    int currentLineHeight = textView.font.lineHeight;

    // Go through the text view character by character
    for (int i = 0 ; i < textView.text.length ; i ++) {

        // Place the cursor at the current character
        textView.selectedRange = NSMakeRange(i, 0);

        // And use the cursor position to help calculate
        // the current line height within the text view
        CGPoint cursorPosition = [textView caretRectForPosition:textView.selectedTextRange.start].origin;

        // If the y value of the cursor is greater than
        // the currentLineHeight, we've moved onto the next line
        if (cursorPosition.y > currentLineHeight) {

            // Increment the currentLineHeight such that it's
            // set to the height of the next line
            currentLineHeight += textView.font.lineHeight;

            // If there isn't a user inputted newline already,
            // add a newline character to reflect the new line.
            if (textView.text.length > i - 1 &&
                [textView.text characterAtIndex:i-1] != '\n') {
                stringWithNewlines = [stringWithNewlines stringByAppendingString:@"\n"];
            }

            // Then add the character to the stringWithNewlines variable
            stringWithNewlines = [stringWithNewlines stringByAppendingString:[textView.text substringWithRange:NSMakeRange(i, 1)]];
        } else {

            // If the character is still on the "current line" simply
            // add the character to the stringWithNewlines variable
            stringWithNewlines = [stringWithNewlines stringByAppendingString:[textView.text substringWithRange:NSMakeRange(i, 1)]];
        }
    }

    // Return the string representation of the text view
    // now containing the newlines
    return stringWithNewlines;
    
					# support automatic lf due to line break: end ==============
					loop on lines
						if line too large
							generate soft lf (text=lf but content = special lf)
							content:
								if previous line is tuple: outline identic to previous
										
- .. main menu: style => modif font,font_size, color for each level
- ..	- memo not per line but per file in .content general, like format type
- .. filter: show up to choozen level, hide higher
- .. revoir memo/load/init de font et font_size prms et color dans prms
- .. try to generate attrib during typing, not each time all, thus only diff
- .. functionnality to build/modify user format?
- ..	- memo infos in .prm if detail modifiable
- .. 	- formats=tableview {item:type,accessorytype:detail} ou swipe avec user 
- ..	- explication: I->roman A->alpha 1.->n i-> a-> level+1
'''
import ast
import collections
import console
from   datetime import datetime
import dialogs
import File_Picker		# https://github.com/cvpe/Pythonista-scripts/blob/master/File_Picker.py
import Folder_Picker	# https://github.com/cvpe/Pythonista-scripts/blob/master/Folder_Picker.py
from   gestures  import *
import inspect
from   math      import isinf
from   objc_util import *
import os
import re
from   SetTextFieldPad import SetTextFieldPad # https://github.com/cvpe/Pythonista-scripts/blob/master/SetTextFieldPad.py
import sys
import ui
import unicodedata

Version = 'V00.27'
Versions = '''
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
	
def my_form_dialog(title='', fields=None, sections=None, done_button_title='Done'):
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

	cc = dialogs._FormDialogController(title, sections, done_button_title=done_button_title)

	#==================== dialogs.form_dialog modification 1: begin	
	for i in range(0,len(cc.cells[0])):			# loop on rows of section 0
		cell = cc.cells[0][i]									# ui.TableViewCell of row i
		# some fields types are subviews of the cell:
		#   text,number,url,email,password,switch
		#  but check, date and time are not set as subviews of cell.content_view
		if len(cell.content_view.subviews) > 0:
			tf = cell.content_view.subviews[0] 		# ui.TextField of value in row
			# attention: tf.name not set for date fields
			item = cc.sections[0][1][i]	# section 0, 1=items, row i
			if 'segmented' in tf.name:
				segmented = ui.SegmentedControl()
				#print(dir(ObjCInstance(segmented)))
				#for sv in ObjCInstance(segmented).subviews():
				#	print(sv._get_objc_classname())		
				#	print(dir(sv))
				segmented.name = cell.text_label.text
				segmented.frame = tf.frame
				segmented.width = 240
				segmented.x = cc.view.width - segmented.width-10 # cc.view is tableview
				segmented.segments = item['segments']
				value = item.get('value', '')
				segmented.selected_index = item['segments'].index(value)
				cell.content_view.remove_subview(tf)
				del cc.values[tf.name]
				del tf
				cell.content_view.add_subview(segmented)
			elif isinstance(tf, ui.TextField):
				#print(tf.name)
				#tf.item = item	# if needed during checks
				tf.alignment=ui.ALIGN_RIGHT
				tf.bordered = True
				tf.font = ('Menlo',16)
				tf.flex = ''
				h = cell.content_view.height
				if 'pad' in item:
					SetTextFieldPad(tf, pad=item['pad'], textfield_did_change=cc.textfield_did_change)
					w = 80					
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
	def __init__(self, *args, **kwargs):
		#super().__init__(self, *args, **kwargs)	
		self.width = ui.get_screen_size()[0]			# width of keyboard = screen
		self.background_color = 'lightgray'#(0,1,0,0.2)
		d = 4
		hb = 44
		self.height = 2*d + hb
		self.pad = [
		{'key':'tab','data':'\x01', 'sf':'text.chevron.right', 'x':10},
		{'key':'shift-tab','data':'\x02', 'sf':'text.chevron.left', 'x':self.width-10-hb}
		]
		
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
		# get actual cursor position					
		cursor = tv.offsetFromPosition_toPosition_(tv.beginningOfDocument(), tv.selectedTextRange().start())
		mv.textview_should_change(mv.tv, [cursor,cursor], sender.data)
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
	
class Outliner(ui.View):
	def __init__(self, *args, **kwargs):
		ui.View.__init__(self, *args, **kwargs)
		ws,hs = ui.get_screen_size()
		self.name = 'Outliner'
		self.background_color = 'white'
		self.tv = ui.TextView()
		self.tv.autocapitalization_type = ui.AUTOCAPITALIZE_NONE
		self.tv.autocorrection_type = None
		self.tv.background_color = (1,1,1)
		#self.tv.auto_content_inset = False
		#self.tv.border_width = 1
		d = 20*2
		
		self.tv.frame = (0,0,ws-2,hs-80)
		self.tv.delegate = self
		#self.tv.font = ('Menlo',14)
		self.tvo = ObjCInstance(self.tv)
		#print(dir(self.tvo))
		self.tvo.setAllowsEditingTextAttributes_(True)
				
		# create ui.View for InputAccessoryView above keyboard
		v = MyInputAccessoryView()
		vo = ObjCInstance(v)									# get ObjectiveC object of v
		retain_global(v) # see https://forum.omz-software.com/topic/4653/button-action-not-called-when-view-is-added-to-native-view
		self.tvo.inputAccessoryView = vo	# attach accessory to textview
		#  remove undo/redo/paste BarButtons above standard keyboard
		#self.tvo.inputAssistantItem().setLeadingBarButtonGroups(None)
		#self.tvo.inputAssistantItem().setTrailingBarButtonGroups(None)
		
		self.add_subview(self.tv)
		self.content = []
		
		b_version = ui.ButtonItem()
		b_version.title = Version
		b_version.tint_color = 'green'
		b_version.action = self.button_version_action	
		
		b_files = ui.ButtonItem()
		b_files.title = 'Files'
		b_files.tint_color = 'blue'
		b_files.action = self.button_files_action	
		
		b_settings = ui.ButtonItem()
		#b_settings.image = ui.Image.named('iob:gear_a_32')
		b_settings.title = '⚙️'
		b_settings.action = self.button_settings_action			

		self.left_button_items = (b_version, b_files, b_settings)		
		
		b_format = ui.ButtonItem()
		o = ObjCClass('UIImage').systemImageNamed_('list.number')
		with ui.ImageContext(32,32) as ctx:
			o.drawAtPoint_(CGPoint(4,4))
			b_format.image = ctx.get_image()					
		b_format.action = self.button_format_action
		self.outline_format = 'decimal'
		
		b_color = ui.ButtonItem()
		b_color.image = ui.Image.named('emj:Artist_Palette').with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		b_color.action = self.button_color_action
		self.outline_rgb = (1,0,0)
		self.outline_color = UIColor.colorWithRed_green_blue_alpha_(self.outline_rgb[0], self.outline_rgb[1], self.outline_rgb[2], 1)
		
		b_font = ui.ButtonItem()
		#b_font.title = '🔤'
		with ui.ImageContext(32,32) as ctx:
			ui.draw_string('A', rect=(16,9,16,16), font=('Academy Engraved LET',24))
			b_font.image = ctx.get_image()
		b_font.action = self.button_font_action
		
		b_fsize = ui.ButtonItem()
		#b_fsize.title = 'font_size'
		with ui.ImageContext(32,32) as ctx:
			ui.draw_string('A', rect=(8,12,12,12), font=('Menlo',12))
			ui.draw_string('A', rect=(16,9,16,16), font=('Menlo',16))
			b_fsize.image = ctx.get_image()
		b_fsize.action = self.button_fsize_action

		b_search = ui.ButtonItem()
		b_search.image = ui.Image.named('iob:ios7_search_32')
		b_search.action = self.button_search_action
		
		b_undo = ui.ButtonItem()
		b_undo.action = self.button_undo_action
		b_undo.enabled = False
		
		self.right_button_items = (b_format, b_color, b_font, b_fsize, b_search, b_undo)
		
		self.button_undo_enable(False,'')
				
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
			
		if 'popup menu orientation' not in self.prms:
			self.prms['popup menu orientation'] = 'horizontal'
		self.popup_menu_orientation = self.prms['popup menu orientation']
		if 'same outline option' not in self.prms:
			self.prms['same outline option'] = 'no'
		self.same_outline_option = self.prms['same outline option']
		if 'same outline invisible' not in self.prms:
			self.prms['same outline invisible'] = 'no'
		self.same_outline_invisible = self.prms['same outline invisible']
		if 'show original area' not in self.prms:
			self.prms['show original area'] = 'no'
		self.show_original_area = self.prms['show original area']
		if 'show lines separator' not in self.prms:
			self.prms['show lines separator'] = 'yes'
		self.show_lines_separator = self.prms['show lines separator']
		if 'checkboxes' not in self.prms:
			self.prms['checkboxes'] = 'yes'
		self.checkboxes = self.prms['checkboxes']
		# temporary protection vs invalid data in .prm
		if 'auto_save' in self.prms:
			del self.prms['auto_save']
		if 'auto-save' not in self.prms:
			self.prms['auto-save'] = 'no'
		else:
			# temporary protection vs invalid data in .prm
			if 'auto-save' in self.prms['auto-save']:
				self.prms['auto-save'] = 'no'
		self.auto_save = self.prms['auto-save']
		
		#doubletap(self.tv, self.doubletap_handler)				
		#long_press(self.tv, self.long_press_handler)
		swipe(self.tv, self.swipe_left_handler,direction=LEFT)
		swipe(self.tv, self.swipe_right_handler,direction=RIGHT)
			
		self.outline_formats = {
			'decimal':(['v.0','v.v','v.v.v','v.v.v.v','v.v.v.v.v','v.v.v.v.v.v', 'v.v.v.v.v.v.v', 'v.v.v.v.v.v.v.v'],2),
			'alphanumeric':(['I.', 'A.', 'i.', 'a.', '(1).', '(a).'],3),
			'traditional':(['1.', 'A.', 'i.', 'a.', '(1).', '(a).', '((1)).',   '((a)).'],3),
			'bullets':(['•', '‣', '◦', '⦿', '⁃', '⦾', '◘'],3)
			}
			
		self.checkmark_ui_image  = ui.Image.named('emj:Checkmark_3').with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		
		self.save_duration = None

		# must be last process of init		
		if 'file' in self.prms:	
			# simulate files button and open last file	
			if not os.path.exists(self.prms['path']+self.prms['file']):
				#console.hud_alert(self.prms['file']+' in .prm does not exist\nprm will be cleaned','error',1)
				del self.prms['path']
				del self.prms['file']
			else:
				self.button_files_action('open')
				
	def button_undo_action(self,sender):
		self.tv.text = self.undo_text
		self.content = self.undo_content
		self.set_outline_attributes()
		self.button_undo_enable(False,'')
		
	def undo_save(self,action):
		self.undo_text = self.tv.text
		self.undo_content = self.content
		self.button_undo_enable(True,action)
		
	def button_undo_enable(self,enabled,text):
		b = self.right_button_items[5]
		b.enabled = enabled
		b.image = ui.Image.named('iob:ios7_undo_outline_32')
		if enabled:
			with ui.ImageContext(32,32) as ctx:
				b.image.draw(0,0)
				ui.draw_string(text, rect=(0,20,32,12), font=('<system>', 12), color='red')
				b.image = ctx.get_image().with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			
	def button_search_action(self,sender):
		x = self.width - 315
		y = 58
		tf = ui.TextField()
		tf.name = 'search'
		tf.frame = (x,y,400,20)
		tf.placeholder = 'type text to be searched'
		tf.delegate = self
		tf.text = ''
		tf.present('popover', popover_location=(x,y),hide_title_bar=True)
		tf.begin_editing()
		tf.wait_modal()	
		# reset no search
		tf.text = ''
		self.textfield_did_change(tf)
		self.set_outline_attributes()

	def textfield_did_change(self, textfield):
		#print('textfield_did_change:', textfield.name, textfield.text)
		if textfield.name == 'search':
			txt = textfield.text
			txt = unicodedata.normalize('NFKD', txt).encode('ASCII', 'ignore')
			txt = str(txt,'utf-8').upper()
			#........... not yet for invisible and hidden	
			# set attributes for general text
			self.outline = NSMutableAttributedString.alloc().initWithString_(self.tv.text)
			pre_outline = None
			i = 0
			y = 10	# 1st line of textview has some y offset
			while i < len(self.content):
				if isinstance(self.content[i],tuple):
					# Not character, thus outline ([value of level 0, ...], nbr_chr)		
					vals_n_opt = self.content[i]	# ([l,l],n,{...})
					vals = vals_n_opt[0]
					n    = vals_n_opt[1]
					opts = {} if len(self.content[i]) < 3 else self.content[i][2]
				else:
					n = 0
				j = i + n
				ilf = self.tv.text.find(lf,i)
				if ilf < 0:
					ilf = len(self.content)+1
				k = min(ilf + 1,len(self.content))
				lin = self.tv.text[j:k]
				lin = unicodedata.normalize('NFKD', lin).encode('ASCII', 'ignore')
				lin = str(lin,'utf-8').upper()			
				opts['hidden'] = (lin.find(txt) < 0)
				i = k
			self.set_outline_attributes()
								
	def button_settings_action(self,sender):
		fields = []
		fields.append({'title':'popup menu orientation', 'type':'text', 'value':self.popup_menu_orientation, 'key':'segmented1', 'segments':['vertical', 'horizontal']})
		fields.append({'title':'same outline option', 'type':'text', 'value':self.same_outline_option, 'key':'segmented2', 'segments':['yes', 'no']})
		fields.append({'title':'same outline invisible', 'type':'text', 'value':self.same_outline_invisible, 'key':'segmented3', 'segments':['yes', 'no']})
		fields.append({'title':'show original area', 'type':'text', 'value':self.show_original_area, 'key':'segmented4', 'segments':['yes', 'no']})
		fields.append({'title':'log active', 'type':'text', 'value':self.log, 'key':'segmented5', 'segments':['yes', 'no']})
		fields.append({'title':'font size of hidden outlines', 'type':'number', 'pad':pad_integer, 'value':str(self.font_hidden)})
		fields.append({'title':'show lines separator', 'type':'text', 'value':self.show_lines_separator, 'key':'segmented6', 'segments':['yes', 'no']})
		fields.append({'title':'checkboxes', 'type':'text', 'value':self.checkboxes, 'key':'segmented7', 'segments':['yes', 'no']})
		auto_save = 'auto-save'
		if self.save_duration:
			auto_save += ' [' + self.save_duration + ']'
		fields.append({'title':auto_save, 'type':'text', 'value':self.auto_save, 'key':'segmented8', 'segments':['no','each char','each line']})
		f = my_form_dialog('settings', fields=fields)		
		#print(f)
		if not f:
			# canceled
			return
			
		self.popup_menu_orientation = f['popup menu orientation']
		self.prms['popup menu orientation'] = self.popup_menu_orientation
		
		self.same_outline_option = f['same outline option']
		self.prms['same outline option'] = self.same_outline_option
		
		self.same_outline_invisible = f['same outline invisible']
		self.prms['same outline invisible'] = self.same_outline_invisible
		
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
		
		self.set_invisible_outline_attributes()
		self.set_outline_attributes()
		
	def set_invisible_outline_attributes(self):
		global font, font_hidden
		if self.same_outline_invisible == 'no':
			self.invisible_outline_color = UIColor.colorWithRed_green_blue_alpha_(0.8,0.8, 0.8,1)
		else:
			self.invisible_outline_color = UIColor.colorWithRed_green_blue_alpha_(1,1,1,1)
		self.invisible_outline_attributes = {NSForegroundColorAttributeName:self.invisible_outline_color, NSFontAttributeName:font}
		self.invisible_outline_attributes_hidden = {NSForegroundColorAttributeName:self.invisible_outline_color, NSFontAttributeName:font_hidden}
						
	def button_font_action(self,sender):
		root = self

		conf = UIFontPickerViewControllerConfiguration.alloc().init()
		picker = UIFontPickerViewController.alloc().initWithConfiguration_(conf)

		delegate = PickerDelegate.alloc().init()
		picker.setDelegate_(delegate)
		
		vc = SUIViewController.viewControllerForView_(root.objc_instance)
		vc.presentModalViewController_animated_(picker, True)
		
	def button_fsize_action(self,sender):
		x = self.width - 260
		y = 58
		tf = ui.TextField()
		tf.name = 'font_size'
		tf.frame = (x,y,200,24)
		tf.placeholder = 'type font size in pixels'
		tf.delegate = self
		SetTextFieldPad(tf, pad_integer)
		tf.text = str(self.font_size)
		tf.present('popover', popover_location=(x,y),hide_title_bar=True)
		tf.begin_editing()
		tf.wait_modal()	
		try:
			n = int(tf.text)
			self.set_font(font_size=n)
		except:				
			console.alert('❌ font size not integer','','ok', hide_cancel_button=True)			

	def textfield_should_return(self, textfield):
		#print('textfield_should_return:', textfield.name)
		textfield.end_editing()
		textfield.close()   
		
	def textfield_did_end_editing(self,textfield):
		#print('textfield_did_end_editing:', textfield.name)
		if textfield.name == 'font_size':
			if sys._getframe(1).f_code.co_name == 'key_pressed':
				# return key pressed in SetTextFieldPad
				textfield.close()
			else:
				# tap outside popover
				pass
		
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
		
		if not set:
			return
				
		self.set_invisible_outline_attributes()
				
		self.set_outline_attributes()
					
	def getButtonItemFrame(self,sender):
		t = str(ObjCInstance(sender).view())
		i = t.find('frame = (')
		j = t.find(')')
		t = t[i+len('frame : ('):j]
		t = t.replace(';',' ')
		xywh = t.split()
		x = float(xywh[0])
		y = float(xywh[1])
		w = float(xywh[2])
		h = float(xywh[3])
		x = x + w/2
		y = 10 + y + h
		#print(x,y,w,h)
		return x,y
		
	def button_files_action(self,sender):	
		if sender == 'open':
			act = 'Open'
		else:
			x,y = self.getButtonItemFrame(sender)
			sub_menu = ['New', 'Open','Save', 'Rename']
			if self.log == 'yes':
				sub_menu.append('Play log')
			tv = ui.TableView()
			tv.row_height = 30
			h = tv.row_height*len(sub_menu)
			tv.frame = (0,0,180,h)
			tv.data_source = ui.ListDataSource(items=sub_menu)
			tv.allows_multiple_selection = False
			tv.delegate = self
			self.selected_row = None
			tv.present('popover',popover_location=(x,y),hide_title_bar=True)
			tv.wait_modal()
			if not self.selected_row:
				return
			act = sub_menu[self.selected_row[1]]
		if act in ['New', 'Open']:
			if self.file:
				# current file loaded
				if self.modif:
					# current file modified
					b = console.alert('⚠️ File has been modified', 'save before loading another?', 'yes', 'no', hide_cancel_button=True)
					if b == 1:
						self.file_save()
		if act == 'New':
			txt_dir = Folder_Picker.folder_picker_dialog('Select a folder where to create the new')
			if not txt_dir:
				console.alert('❌ No folder has been selected','','ok', hide_cancel_button=True)
				return
			self.path = txt_dir + '/'
			f = console.input_alert('Name of new file', hide_cancel_button=True)
			if not f:
				console.alert('❌ No file name has been entered','','ok', hide_cancel_button=True)
				return
			if os.path.exists(self.path+f):
				console.alert('❌ '+f+' file already exists','in selected folder','ok', hide_cancel_button=True)
				return
			i = f.rfind('.')
			if i < 0:
				i = len(f)
			file_content = f[:i] + '.content'
			if os.path.exists(self.path+file_content):
				console.alert('❌ '+file_content+' file already exists','in selected folder','ok', hide_cancel_button=True)
				return
			self.file = f
			self.name = f
			self.file_content = file_content
			self.tv.text = ''
			self.content =[]
			self.outline_format = 'decimal'
			self.set_font(font_type='Menlo', set=False)		
			self.set_font(font_size=18, set=False)	
			# simulate tab pressed
			self.open_log()
			self.textview_should_change(self.tv, [0,0], '\x01')
			self.tv.begin_editing()
		elif act == 'Open':
			if sender == 'open':
				self.path = self.prms['path']
				self.file = self.prms['file']
				if 'font' in self.prms:
					self.set_font(font_type=self.prms['font'])		
				if 'font_size' in self.prms:
					self.set_font(font_size=self.prms['font_size'])	
				if 'font_hidden' in self.prms:
					self.set_font(font_hidden_size=self.prms['font_hidden'])	
			else:

				path = '~/Documents'								
				f = File_Picker.file_picker_dialog('Pick a text file', root_dir=os.path.expanduser(path))
				if not f:
					console.alert('❌ No file has been picked','','ok', hide_cancel_button=True)
					return
				i = f.rfind('/')
				self.path = f[:i+1]
				self.file = f[i+1:]
			self.name = self.file
			i = self.file.rfind('.')
			if i < 0:
				i = len(self.file)
			self.file_content = self.file[:i] + '.content'
			with open(self.path+self.file,mode='rt') as fil:
				self.tv.text = fil.read()
			self.content = []
			if os.path.exists(self.path+self.file_content):
				with open(self.path+self.file_content,mode='rt') as fil:
					t = fil.read()
					t,prms = t.split(lf)
					if prms.startswith('{'):
						prms = ast.literal_eval(prms)
						self.outline_format = prms['format']
						self.set_font(font_type=prms['font'], set=False)		
						self.set_font(font_size=prms['font_size'], set=False)	
					else:
						self.outline_format = prms
					self.content = ast.literal_eval(t)
					del t
			self.set_outline_attributes()
			self.prms_save()
			self.open_log()
		elif act == 'Save':
			if not self.file:
				console.alert('❌ No active file','','ok', hide_cancel_button=True)
				return
			if not self.modif:
				console.alert('⚠️ File has not been modified since last save','','ok', hide_cancel_button=True)
				return	
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
			f = File_Picker.file_picker_dialog('Pick a log file', root_dir=os.path.expanduser('~/Documents'))
			if not f:
				console.alert('❌ No file has been picked','','ok', hide_cancel_button=True)
				return
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
						rge = (int(fs[0]), int(fs[1]))
						rep = bytes.fromhex(fs[2]).decode('utf-8')
						self.textview_should_change(self.tv, rge, rep, play=True)
			
	def open_log(self):			
		if self.log == 'yes':
			try:
				self.log_fil.close()
			except:
				pass
			self.log_fil = open(self.log_file, mode='wt')
					
	def button_version_action(self,sender):
		x,y = self.getButtonItemFrame(sender)
		tv = ui.TextView()
		tv.editable = False
		w,h = ui.get_screen_size()
		w -= 100
		h -= 200
		tv.frame = (0,0,w,h)
		tv.font = ('Menlo',14)
		tv.text = Versions
		tv.present('popover',popover_location=(x,y),hide_title_bar=True)
		
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
		
		tv.wait_modal()
		
	def button_format_action(self,sender):
		x = self.width - 44
		y = 58
		#sub_menu = ['decimal', 'alphanumeric','traditional','bullets']
		sub_menu = [{'title':'decimal','accessory_type':'detail_button'}, {'title':'alphanumeric','accessory_type':'detail_button'}, {'title':'traditional','accessory_type':'detail_button'}, {'title':'bullets','accessory_type':'detail_button'}]
		tv = ui.TableView()
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
		tv.present('popover',popover_location=(x,y),hide_title_bar=True)
		tv.wait_modal()
		if not self.selected_row:
			return
		loc_format = sub_menu[self.selected_row[1]]['title']
		if loc_format != self.outline_format:
			self.outline_format = loc_format
			if not self.set_textview_and_content():
				# too high level
				console.alert('❌ too high outline level','for this outline format','ok', hide_cancel_button=True)
				return
			self.modif = True
			
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
		for l in range(len(outline_types)):
			a.append(' '*blanks*l + outline_types[l])
		tv = ui.TableView()
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
		tv.present('popover',popover_location=(x,y),hide_title_bar=True)
		tv.wait_modal()		
					
	def button_color_action(self,sender):				
		rgb = OMColorPickerViewController(title='choose outline color', rgb=self.outline_rgb)
		self.outline_rgb = rgb
		self.outline_color = UIColor.colorWithRed_green_blue_alpha_(self.outline_rgb[0], self.outline_rgb[1], self.outline_rgb[2], 1)
		self.outline_attributes = {NSForegroundColorAttributeName:self.outline_color, NSFontAttributeName:font}
		
		# set outline attributes	
		self.set_outline_attributes()
						
	def tableview_did_select(self, tableview, section, row):
		#print('tableview_did_select')
		self.selected_row = (section,row)
		tableview.close()
		
	def textview_should_change(self, textview, range_c, replacement, play=False):
		#print('textview_should_change', range_c,'|'+replacement+'|')
		# problem occurs when replacement is a predictive (non typed) text
		# textview_should_change is called by itself, what forces either crash,
		# either unwanted additional characters
		if len(inspect.stack()) > 1:
			if inspect.stack()[1][3] == 'textview_should_change':
				return False
		#print('before:',textview.text)
		# check if file active
		if not self.file:
			console.alert('❌ No file is active','','ok', hide_cancel_button=True)
			return False
			
		# eventual log
		if self.log == 'yes' and not play:
			rec = f"{range_c[0]},{range_c[0]},"
			for character in replacement:
				rec += character.encode('utf-8').hex()
			rec += lf
			try:
				self.log_fil.write(rec)
			except:
				console.alert('❌ You did activate the log on an open file, do that only on a new file','automatically desactivated','ok', hide_cancel_button=True)
				self.log = 'no'
			
		# check if not typing in an outline 
		if range_c[0] > 0 and range_c[1] < len(self.content):
			# not a begin of text
			if isinstance(self.content[range_c[0]-1],tuple) and isinstance(self.content[range_c[1]],tuple):
				if replacement not in ['\x01', '\x02', '\x03']:
					console.alert('❌ Typing in outlines not allowed','','ok', hide_cancel_button=True)
					return False
		t = textview.text
		processed = False
		vals_before = None
		if replacement == '\x01':
			# next level outline
			# ==================
			iprevlf = t.rfind(lf,0,range_c[0])	# -1 if first line
			i = iprevlf + 1
			remove_old = False
			if len(self.content) == 0:
				# tab as 1st character of file
				range_c = (i,i)
				nvals = [0]
				opts = {}	
			elif i == len(self.content):			
				# tab as last character of file
				range_c = (i,i)
				nvals = [0]	
				opts = {}	
			elif not isinstance(self.content[i], tuple):
				# 1st character of line is normal
				range_c = (i,i)
				nvals = [0]	
				opts = {}	
			else:
				# i = outline
				vals = self.content[i][0]	# ([l,l],n,{...})
				opts = {} if len(self.content[i]) < 3 else self.content[i][2]
				if vals == [0]:
					console.alert('❌ increase first level ','not allowed','ok', hide_cancel_button=True)
					return False	# not allowed						
				vals_before = vals.copy()
				# check if not increase level of more than 1: begin ====
				ilf = t.rfind(lf,0,i-1)	# alwas found becuse  ot [0]
				k = ilf + 1
				# k must be an outline because next one is not [0]
				pvals = self.content[k][0]
				nvals = vals[:-1] + [vals[-1]-1] + [0] # add a level
				if len(pvals) > len(vals):
					a = pvals[len(vals)] + 1
				else:
					a = 0
				nvals = pvals[:len(vals)] +[a] # add one level
				#print(pvals,vals,nvals)
				if nvals == vals:
					console.alert('❌ no change','','ok', hide_cancel_button=True)
					return False	# not allowed	
				if len(nvals) > (len(pvals)+1):
					console.alert('❌ increase level two consecutive times','not allowed','ok', hide_cancel_button=True)
					return False	# not allowed	
				# check if not increase level of more than 1: end ====
				if not self.OutlineFromLevelValue(nvals):
					# too high level
					console.alert('❌ too high outline level','','ok', hide_cancel_button=True)
					return False	# not allowed		
				# remove old outline
				n = self.content[i][1]	# ([l,l],n,{...})
				remove_old = True
			self.undo_save('tab')			
			if remove_old:
				t = t[:i] + t[i+n:]
				self.content = self.content[:i] + self.content[i+n:]
				range_c = (i,i)
			replacement = self.OutlineFromLevelValue(nvals)
			c_replacement = [(nvals,len(replacement),opts)]*len(replacement)							
			textview.text = t[:range_c[0]] + replacement + t[range_c[1]:]
			self.content = self.content[:range_c[0]] + c_replacement + self.content[range_c[1]:]	

			if len(nvals) > 1:			
				# automatic outlines renumbering of next lines 		
				fr = range_c[0]
				self.renumbering('tab', fr, vals_before, nvals)		
				self.renumbering('all',None,None, None)		
			
			self.set_outline_attributes(typ='line')
			self.setCursor(range_c[0]+len(replacement))	
			self.modif = True
			return False	# no replacement to process				
		elif replacement in [lf,'\x03']:
			# line feed
			# =========
			if range_c[0] == 0:
				# insert CR at begin of file
				# should generate an [0] and automatic renumbering
				pass
			elif range_c[0] == len(t):
				# CR at end of file
				pass
			elif isinstance(self.content[range_c[0]],tuple):
				console.alert('❌ CR before an outline not allowed','type it at end of previous line','ok', hide_cancel_button=True)
				return False	# not allowed
			same_outline = (replacement == '\x03')
			if same_outline:
				replacement = lf
			c_replacement = list(replacement)
			l_out = 0
			# search last outline before lf
			# keep same level, value + 1
			i = range_c[0]
			iprevlf = textview.text.rfind(lf,0,i)	# -1 if first line
			j = iprevlf + 1
			if isinstance(self.content[j], tuple):
				# previous line has an outline
				vals_n_opt = self.content[j]	# ([l,l],n,{...})
				vals = vals_n_opt[0]
				n    = vals_n_opt[1]
				if i == 0:
					nvals = [0]
				elif not same_outline:
					# new line will have same level, nvalue + 1
					nvals = vals[:-1] + [vals[-1]+1]
				else:
					# new line with same outline as previous
					nvals = vals.copy()
				t_out = self.OutlineFromLevelValue(nvals)
				l_out = len(t_out)
				if i == 0:
					replacement   = t_out + lf
					c_replacement = [(nvals,l_out,{})]*l_out + [lf]
				else:
					replacement   += t_out
					c_replacement += [(nvals,l_out,{})]*l_out 
			else:
				nvals = []
			self.undo_save('CR')
			textview.text = t[:range_c[0]] + replacement + t[range_c[1]:]
			self.content = self.content[:range_c[0]] + c_replacement + self.content[range_c[1]:]	
			
			if len(nvals) >= 1 and not same_outline:			
				# automatic outlines renumbering of next lines 		
				# no renumbering if new line wit same outline as previous
				fr = range_c[0]+1
				self.renumbering('lf', fr, None, nvals)		
				self.renumbering('all',None,None, None)		

			self.set_outline_attributes(typ='line')
			self.setCursor(range_c[0]+len(replacement))	
			self.modif = True
			return False	# no replacement to process				
		elif replacement == '\x02':
			# back level outline
			# ==================
			iprevlf = textview.text.rfind(lf,0,range_c[0])	# -1 if first line
			i = iprevlf + 1
			if len(self.content) == 0 or i == len(self.content):
				# tab as 1st character of file
				pass
			elif isinstance(self.content[i], tuple):
				vals_n_opt = self.content[i]	# ([l,l],n,{...})
				vals = vals_n_opt[0]
				if len(vals) ==1:
					console.alert('❌ no outline level to decrease','','ok', hide_cancel_button=True)
					return False	# not allowed		
				n    = vals_n_opt[1]
				opts = {} if len(self.content[i]) < 3 else self.content[i][2]
				vals_before = vals.copy()
				# replace old outline by a new one with one level less					
				# remove old outline
				self.undo_save('back')			
				t = t[:i] + t[i+n:]
				self.content = self.content[:i] + self.content[i+n:]
				range_c = (i,i)
				nvals = vals[:-1]
				if len(nvals) > 0:
					nvals = nvals[:-1] + [nvals[-1]+1]
					replacement = self.OutlineFromLevelValue(nvals)
					c_replacement = [(nvals,len(replacement),opts)]*len(replacement)
					t = t[:range_c[0]] + replacement + t[range_c[1]:]
					self.content = self.content[:range_c[0]] + c_replacement + self.content[range_c[1]:]			

				textview.text = t
				
				if len(nvals) >= 1:			
					# automatic outlines renumbering of next lines 		
					fr = range_c[0]
					#print('renum  after back tab to ',replacement)
					self.renumbering('backtab', fr, vals_before, nvals)		
					self.renumbering('all',None,None, None)		
						
				# set outline attributes	
				self.set_outline_attributes(typ='line')
				self.setCursor(range_c[0]+len(replacement))	
				self.modif = True
				return False	# no replacement to process		
				
			console.alert('❌ no outline level to decrease','','ok', hide_cancel_button=True)
			return False	# not allowed		
		elif replacement == '':
			# Backspace or cut to remove textfield[range[0]to[range[1]-1]
			# ===========================================================
			# no way to differentiate backspace of cut character at left of cursor
			#print(self.content)
			self.button_undo_enable(False,'')
			n = 0
			del_lf = False
			for j in range(range_c[0],range_c[1]):
				if isinstance(self.content[j],tuple):
					n += 1
				elif self.content[j] == lf:
					del_lf = True
			if n == 0:
				# only delete normal characters
				if del_lf:
					if range_c[1] > (len(self.content)-1):
						# no next line
						pass
					elif isinstance(self.content[range_c[1]],tuple):
						# delete lf where next line begins with an outline
						console.alert('❌ delete line feed followed by a line with an outline not allowed','','ok', hide_cancel_button=True)
						return False	# not allowed
				replacement = ''
				c_replacement = []
			elif n == (range_c[1] - range_c[0]):
				# all outline
				console.alert('❌ delete outline not allowed, use "back level" key','','ok', hide_cancel_button=True)
				return False	# not allowed
			else:
				# mixt normal and outline
				console.alert('❌ cut mix of normal and outline characters not allowed','','ok', hide_cancel_button=True)
				return False	# not allowed
				
			t = t[:range_c[0]] + replacement + t[range_c[1]:]
			textview.text = t
			self.content = self.content[:range_c[0]] + c_replacement + self.content[range_c[1]:]	
			#print(self.content)
			
			# set outline attributes	
			self.set_outline_attributes(typ='char')
	
			self.setCursor(range_c[0]+len(replacement))	
			
			self.modif = True
			return False	# no replacement to process				
		else:
			# normal character, tab
			# =====================
			self.button_undo_enable(False,'')
			if lf in replacement:
				# check if not paste of a string containing CR
				# if replacement contains CR, console.alert did lock the script
				self.alert_title = '❌ paste of text containing CR'
				self.alert_msg   = 'not allowed'
				ui.delay(self.console_alert, 0.1)
				return False	# not allowed
			if range_c[0] <= (len(self.content)-1):
				if isinstance(self.content[range_c[0]],tuple):
					console.alert('❌ insertion before an outline not allowed','','ok', hide_cancel_button=True)
					return False	# not allowed
			# replacement unchanged
			c_replacement = list(replacement)
			l_out = 0

			#print('ici1')
			textview.text = t[:range_c[0]] + replacement + t[range_c[1]:]
			# textview_should_change seems to be re-called here when auto text
			#print('ici2')
			self.content = self.content[:range_c[0]] + c_replacement + self.content[range_c[1]:]	
			#print('after', textview.text)
			#print(self.content)
			
			# set outline attributes	
			self.set_outline_attributes(typ='char')
	
			self.setCursor(range_c[0]+len(replacement))	
			
			self.modif = True
			return False # no replacement to process				
		
	def console_alert(self):
		console.alert(self.alert_title, self.alert_msg, 'ok', hide_cancel_button=True)
		
	def renumbering(self, typ, fr, vals_before, vals_after):		
		if typ == 'all':
			# automatic renumbering of all (no parameters needed)
			t = ''
			c = []
			i = 0
			pre_vals = []
			while i < len(self.tv.text):
				if isinstance(self.content[i], tuple):
					# outline
					vals = self.content[i][0]
					n    = self.content[i][1]
					opts = {} if len(self.content[i]) < 3 else self.content[i][2]
					if len(vals) > len(pre_vals):
						nvals = pre_vals + vals[len(pre_vals):len(vals)-1] + [0]
					elif len(vals) == len(pre_vals):
						nvals = pre_vals[:-1] + [pre_vals[-1]+1]
					else:
						nvals = pre_vals[:len(vals)-1] + [pre_vals[len(vals)-1]+1]
					tout = self.OutlineFromLevelValue(nvals)
					nn = len(tout)
					pre_vals = nvals	
					cc = [(pre_vals,nn,opts)]	* len(tout)
				else:
					# line without outline
					tout = ''
					n = 0
					cc = []
				ilf = self.tv.text.find(lf,i)
				if ilf < 0:
					ilf = len(self.tv.text)-1
				t += tout + self.tv.text[i+n:ilf+1]
				c += cc + self.content[i+n:ilf+1]
				i = ilf + 1		
			self.tv.text = t
			self.content = c
			return
		# automatic outlines renumbering of next lines 
		t = self.tv.text
		ilf = t.find(lf,fr)
		if ilf < 0:
			# no lf after line of added outline
			return	# no action
		# lf after added outline
		k = ilf + 1
		while k >= 0:
			if k > (len(self.content)-1):
				# end of file reached, end of renumbering
				break
			elif isinstance(self.content[k],tuple):
				# line after lf has an outline
				vals_n_opt = self.content[k]	# ([l,l],n,{...})
				vals = vals_n_opt[0]
				l_bef= vals_n_opt[1]
				opts = {} if len(self.content[k]) < 3 else self.content[k][2]
				nvals = None
				# ============ renumbering process of an outline: begin ===========
				if typ == 'tab':
					# tabbed outline level already increased
					if vals[:len(vals_before)] == vals_before:
						# child of tabbed outline
						nvals = vals_after + vals[len(vals_before):]
					elif len(vals) >= len(vals_before):					
						fr_level = len(vals_before) - 1
						nvals = vals[:fr_level] + [vals[fr_level]-1] + vals[fr_level+1:]
				elif typ == 'backtab':
					# tabbed outline level already decreased
					if vals[:len(vals_before)] == vals_before:
						# child of tabbed outline
						nvals = vals_after + vals[len(vals_before):]
					elif len(vals) >= len(vals_after):					
						fr_level = len(vals_after) - 1
						nvals = vals[:fr_level] + [vals[fr_level]+1] + vals[fr_level+1:]
					#print(vals_before,vals,vals_after,nvals)
				elif typ == 'lf':
					if len(vals) >= len(vals_after):			
						fr_level = len(vals_after) - 1
						nvals = vals[:fr_level] + [vals[fr_level]+1] + vals[fr_level+1:]
				elif typ == 'del':
					if len(vals) >= len(vals_before):			
						#print(vals,vals_before,vals_after,nvals)
						fr_level = len(vals_before) - 1
						nvals = vals[:fr_level] + [vals[fr_level]-1] + vals[fr_level+1:]
						#print(vals,vals_before,vals_after,nvals)
					#print(vals_before,vals,self.OutlineFromLevelValue(vals),nvals)
				# ============ renumbering process of an outline: end =============
				if nvals:
					#print(vals,nvals)
					t_aft = self.OutlineFromLevelValue(nvals)
					l_aft = len(t_aft)
					t = t[:k] + t_aft + t[k+l_bef:]	
					self.content = self.content[:k] + [(nvals,l_aft,opts)]*l_aft + self.content[k+l_bef:]				
				ilf = t.find(lf,k)
				if ilf < 0:
					# no lf after line of added outline, end of renumbering
					break
				k = ilf + 1
			else:
				# line after lf does not have an outline, thus end of renumbering
				break
		self.tv.text = t
		
	# this code came from elsewhere on the forum: given a view, it finds the objc UIViewController which is presenting it:
	def getUIViewController(self,view):
		UIViewController = ObjCClass('UIViewController')
		#UIView = objc_util.ObjCClass('UIView')
		viewobj = view.objc_instance
		viewResponder = viewobj.nextResponder()
		try:
			while not viewResponder.isKindOfClass_(UIViewController):
				viewResponder = viewResponder.nextResponder()
		except AttributeError:
			return None
		return viewResponder
		
	def popup_menu_action(self,sender, i=None):
		if isinstance(sender, ui.Button):
			act = sender.title
			i = sender.i
			sender.superview.close()
		else:
			act = sender
			i = i
		vals_n_opt = self.content[i]	# ([l,l],n,{...})
		vals = vals_n_opt[0]
		n    = vals_n_opt[1]
		if act == 'hide children':
			self.hide_children(i,len(vals)-1,hide=True)
		elif act == 'show children':
			self.hide_children(i,len(vals)-1,hide=False)
		elif act == '⏭':			
			self.textview_should_change(self.tv,[i,i],'\x01')				
		elif act == '⏮':			
			self.textview_should_change(self.tv,[i,i],'\x02')				
		elif act == 'new line with same outline':			
			ilf = self.tv.text.find(lf,i) # find lf after i
			if ilf < 0:
				ilf = len(self.tv.text) 
			self.textview_should_change(self.tv,[ilf,ilf],'\x03')				
				
	def doubletap_handler(self,data):
		xp,yp = data.location
		v = data.view
		#v.border_width = 1
		# popover at right of outline
		xp = v.x + v.width
		yp = v.y + v.height/2
		#print(xp,yp,data.state)
		i = self.xy_to_i(xp,yp)
		if i == None:
			return
		vals_n_opt = self.content[i]	# ([l,l],n,{...})
		vals = vals_n_opt[0]
		n    = vals_n_opt[1]
		t = self.OutlineFromLevelValue(vals)
		sub_menu = ['hide children', 'show children', '⏭', '⏮']
		if self.same_outline_option:
			sub_menu.append('new line with same outline')
		if self.popup_menu_orientation == 'vertical':
			#=== vertical: popup menu
			tv = ui.TableView()
			ft = ('Menlo',16)
			wmax = 0
			for act in sub_menu:
				w = ui.measure_string(act,font=ft)[0]
				wmax = max(w,wmax)
			tv.name = t
			tv.row_height = 30
			h = tv.row_height*len(sub_menu)
			tv.frame = (0,0,wmax+40,h)
			tv.data_source = ui.ListDataSource(items=sub_menu)
			tv.data_source.font = ft
			tv.allows_multiple_selection = False
			tv.delegate = self
			self.selected_row = None
			y = 70 + self.lines[i][1] + self.lines[i][3]/2 - self.tv.content_offset[1]
			tv.present('popover',popover_location=(xp,y),hide_title_bar=False)
			tv.wait_modal()
			if not self.selected_row:
				return
			act = sub_menu[self.selected_row[1]]
			self.popup_menu_action(act, i=i)
		else:
			#=== horizontal popup menu
			popup = ui.View()
			h = 40
			x = 0
			ft = ('Menlo',14)
			for act in [t] + sub_menu:
				b = ui.Button()
				b.title = act
				if act == 'new line with same outline':
					w = ui.measure_string('1.0 line 1',font=ft)[0] + 10
					with ui.ImageContext(w,h) as ctx:
						ui.draw_string('1.0 line 1',rect=(0,0,w,h/2), font=ft)
						ui.draw_string('    line 2',rect=(0,h/2,w,h/2), font=ft)
						b.image = ctx.get_image()
					w = h
				else:
					b.title = act
					w = ui.measure_string(act,font=ft)[0] + 10
				x += 10
				b.frame = (x,0,w,h)
				x += w
				b.font = ft
				if act == t:
					b.tint_color = 'yellow'
				else:
					b.tint_color = 'white'
					b.i = i
					b.action = self.popup_menu_action
				popup.add_subview(b)
				l = ui.Label()	
				x += 10		
				l.frame = (x,0,1,h)			
				l.background_color = (0.5,0.5,0.5,0.8)
				popup.add_subview(l)	
			popup.frame = (0,0,x-2,h) # don't show last vertical line
			# "bg" is the color you want to set the popover view to
			popup.background_color = 'black'
			y = 70 + self.lines[i][1] + self.lines[i][3]/2 - self.tv.content_offset[1]
			popup.present(style="popover", popover_location=(xp,y), hide_title_bar=True)
	
			# this is the bit that colors the enclosing view
			parentvc = self.getUIViewController(popup)
			popovervc = parentvc.popoverPresentationController()
			if popovervc is not None:
				popovervc.backgroundColor =  UIColor.colorWithRed_green_blue_alpha_(*popup.background_color)	
			return
			
	def long_press_handler(self,data):
		global line1,xp1
		#print(dir(data))
		xp,yp = data.location
		xp += data.view.x
		yp += data.view.y
		#print(xp,yp,data.state)
		# get outline
		if data.state == 1:
			# start long_press
			self.tvm = None
			self.target = None
			self.orig_area = None
			found = self.xy_to_i(xp,yp)
			if found == None:
				return
			line1 = found
			xp1 = xp
			self.drag_children(found,xp,yp)
		elif data.state == 2:
			# move
			if self.tvm:
				self.tvm.x = xp+100
				self.tvm.y = yp
				#--------- show a red line where moving text would be inserted: begin ----
				found = self.xy_to_i(0,yp)
				#print(found)
				if found == None:
					if yp >= self.lines_ymax:
						y = self.lines_ymax + 2
						found = len(self.tv.text)
					else: 
						return
				else:
					y = self.lines[found][1]
				self.found_redline = found
				try:
					p1 = self.tvo.positionFromPosition_offset_(self.tvo.beginningOfDocument(), found)
					rge = self.tvo.textRangeFromPosition_toPosition_(p1,p1)
					rect = self.tvo.firstRectForRange_(rge)	# CGRect
					y = rect.origin.y
					h = rect.size.height
					self.target.y = self.tv.y + y		
				except:
					self.target = ui.Label()
					self.target.frame = (0,y,self.tv.width-2,1)
					self.target.background_color = 'red'
					self.tv.add_subview(self.target)
					
				# under outline or under text?
				# search level of previous line
				if found == 0:
					vals = []
				else:
					ilf = self.tv.text.rfind(lf,0,found-1)
					k = ilf + 1
					if isinstance(self.content[k],tuple):
						vals = self.content[k][0]
					else:
						vals = []
				if vals != []:
					tout = self.OutlineFromLevelValue(vals)
					w = ui.measure_string(tout,font=(self.font,self.font_size))[0]
					if (xp-100) > w:
						self.target.x = w
					else:
						self.target.x = 0
				else:
					# no outline
					self.target.x = 0
					
				#--------- show a gray line where moving text would be inserted: begin ----
		elif data.state == 3:
			# end
			if self.tvm:
				tgx = 0
				self.tv.remove_subview(self.tvm)
				del self.tvm
				if self.target:
					tgx = self.target.x
					self.tv.remove_subview(self.target)
					del self.target
				if self.orig_area:
					self.tv.remove_subview(self.orig_area)
					del self.orig_area

				found = self.xy_to_i(xp-100,yp)
				if found == None:
					if yp >= self.lines_ymax:
						# drop after text
						found = len(self.tv.text)
					else:
						return
				if found == line1:
					if xp > xp1:
						# move left to right => simulate tab
						self.textview_should_change(self.tv,[found,found],'\x01')					
					else:
						# move right to left => simulate back tab
						self.textview_should_change(self.tv,[found,found],'\x02')				
					return
				if self.drag_range[0] <= found and found <= self.drag_range[1]:
					#console.alert('❌ no drop of a box of text into it-self','','ok', hide_cancel_button=True)
					return					 
				else:
					fm,tm = self.drag_range
					self.drop(self.found_redline,fm,tm,tgx)
					del self.drag
						
	def swipe_left_handler(self,data):
		xp,yp = data.location
		found = self.xy_to_i(xp,yp)
		if found == None:
			return
		self.textview_should_change(self.tv,[found,found],'\x02')				
		
	def swipe_right_handler(self,data):
		xp,yp = data.location 
		found = self.xy_to_i(xp,yp)
		if found == None:
			return
		self.textview_should_change(self.tv,[found,found],'\x01')				

	def xy_to_i(self,xp,yp):	
		found = None
		for i in self.lines.keys():
			x,y,w,h = self.lines[i]
			#print(xp,yp,i,y,y+h)
			if y <= yp and yp <= (y+h):
				# tap in line
				found = i
				break
		return found			
	
	def drag_children(self,fr,xp,yp):
		#print('drag_children',fr,xp,yp)
		# prepare text to drag
		t = self.tv.text
		vals_n_opt = self.content[fr]	# ([l,l],n,{...})
		bvals = vals_n_opt[0]
		n     = vals_n_opt[1]
		ilf = t.find(lf,fr)
		if ilf < 0:
			# no lf after line of added outline
			ilf = len(t)
		# lf after added outline
		self.drag = ''
		i_outlines = [fr]
		k = ilf + 1
		while k >= 0:
			if k >= len(t):
				k1 = k
				break
			elif isinstance(self.content[k],tuple):
				# line after lf has an outline
				vals_n_opt = self.content[k]	# ([l,l],n,{...})
				vals = vals_n_opt[0]
				n    = vals_n_opt[1]
				#print('to hide?',vals,len(vals)-1,fr_level)
				if (len(vals)-1) > (len(bvals)-1):						
					# level higher that from level, set as selected
					i_outlines.append(k)
					pass # continue
				else:
					# level too high, end of select
					k1 = k
					break
				ilf = t.find(lf,k)
				if ilf < 0:
					# no lf after line of added outline, end of select
					k1 = len(t)
					break
				k = ilf + 1
			else:
				# line after lf does not have an outline, thus end of select
				k1 = k
				break
		self.drag = t[fr:k1]
		self.drag_range = (fr,k1)
		#print(self.drag)				
		if not self.drag:
			console.alert('❌ no children to move','','ok', hide_cancel_button=True)
			return
		try:
			self.remove_subview(self['tvm'])
		except:
			pass
		tvm = ui.Label(name='tvm')
		tvm.number_of_lines = 0
		tvm.text = self.drag
		if tvm.text[-1] == lf:
			tvm.text = tvm.text[:-1]
		tvmo = ObjCInstance(tvm) # ._objc_ptr)
		outline = NSMutableAttributedString.alloc().initWithString_(tvm.text)
		#outline.setAttributes_range_(self.text_attributes, NSRange(0, len(tvm.text)))
		for k in i_outlines:
			n = self.content[k][1]
			#print(fr,k,n,tvm.text[k-fr:k-fr+n])
			outline.setAttributes_range_(self.outline_attributes, NSRange(k-fr, n))
		del i_outlines
		self.set_attributed_text(tvmo, outline)
		tvm.font = (self.font,self.font_size)
		#tvm.size_to_fit()
		w = self.tv.width - 20
		h = 100
		xdrag = xp - 100 # only to not hide the moving box by the finger
		ydrag = yp 
		w,h = ui.measure_string(tvm.text,font=tvm.font)
		tvm.frame = (xdrag,ydrag,w,h)
		tvm.border_width = 1
		r = 10
		tvm.corner_radius = r/2
		tvm.background_color = (0.9,0.9,0.9,0.5)
		self.tvm = tvm
		# blue dot at top/left
		#pt = ui.View()
		#pt.frame = (0,0,r,r)
		#pt.corner_radius = r/2
		#pt.background_color = 'blue'
		#tvm.add_subview(pt)
		self.tv.add_subview(tvm)

		if self.show_original_area == 'yes':		
			# show original area in TextView
			if k1 > len(self.tv.text):
				k1 -= 1
			p1 = self.tvo.positionFromPosition_offset_(self.tvo.beginningOfDocument(), fr)
			p2 = self.tvo.positionFromPosition_offset_(self.tvo.beginningOfDocument(), k1)
			rge = self.tvo.textRangeFromPosition_toPosition_(p1,p2)
			rect = self.tvo.firstRectForRange_(rge)	# CGRect
			x,y = rect.origin.x,rect.origin.y
			w,h = rect.size.width,rect.size.height
			# down the area a little else a redline above would be not visible 
			y = y + 3
			h = h - 3
			# we have a problem: last line is not in the showed original area if its last  
			# line is not followed by a lf AND a character
			if k1 > (len(self.tv.text)-1):
				h = h + self.font_size + 2
			l = ui.Button()
			l.frame = (x,y,w,h)
			l.background_color = (1,0,0,0.1)
			l.corner_radius = 10
			l.border_width = 1
			self.tv.add_subview(l)
			self.orig_area = l
		
	def drop(self,found, fm, tm, tgx, play=False):
		#print('drop:', found, fm,tm, len(self.tv.text))
		self.undo_save('move')
		
		# eventual log
		if self.log == 'yes' and not play:
			rec = f"drop,{found},{fm},{tm},{tgx}"
			rec += lf
			self.log_fil.write(rec)
			
		under_outline = (tgx == 0)

		t = self.tv.text
		if found == len(t) and t[-1] != lf:
			replacement = lf
			c_replacement = [lf]
		else:
			replacement = ''
			c_replacement = [] 
		# search level of previous line
		if found == 0:
			pre_vals = []
		else:
			ilf = t.rfind(lf,0,found-1)
			k = ilf + 1
			pre_vals = self.content[k][0]
		# process dropped lines
		first = True
		i = fm
		while i < tm:
			if isinstance(self.content[i],tuple):
				vals_n_opt = self.content[i]	# ([l,l],n,{...})
				vals = vals_n_opt[0]
				n    = vals_n_opt[1]
				opts = {} if len(self.content[i]) < 3 else self.content[i][2]
				#print('vals=',vals)
				if first:
					vals1 = vals.copy()
					if pre_vals == []:
						nvals = [0]
					else:	
						if pre_vals != []:		
							if under_outline:
								# drop under outline
								# same level as previous
								nvals = pre_vals[:-1] + [pre_vals[-1]+1]
							else:
								# drop under text
								# next level vs previous
								nvals = pre_vals + [0]
						else:
							# drop after a line without outline
							nvals = [0]
					nvals1 = nvals.copy()
					first = False
				else:
					ndiff = len(vals) - len(vals1) 
					nvals = nvals1 + vals[-ndiff:]  
				tout = self.OutlineFromLevelValue(nvals)
				#print(pre_vals,vals,nvals)
				nn = len(tout)
				replacement += tout				
				c_replacement += [(nvals,nn,opts)] * nn
				i = i + n
			ilf = t.find(lf,i)
			if ilf < 0:
				ilf = len(t)
			line = t[i:ilf]
			replacement += line + lf
			c_replacement += list(line+lf)
			i = ilf + 1
		self.tv.text = t[:found]            + replacement   + t[found:]
		self.content = self.content[:found] + c_replacement + self.content[found:]	
		# remove original
		if tm > found:
			# deleted part after insertion, thus increase indexes
			fm += len(replacement)	# needed for removal
			tm += len(replacement)
		# if copy instead of move, comment these lines: begin ========
		self.tv.text = self.tv.text[:fm] + self.tv.text[tm:]
		self.content = self.content[:fm] + self.content[tm:]
		# if copy instead of move, comment these lines: end  ==========
		
		# renumbering after old removed
		self.renumbering('all',None,None, None)		
		
		# set outline attributes	
		self.set_outline_attributes()
		self.setCursor(found)	
		self.modif = True
		
		return
			
	def hide_children(self,fr, fr_level, hide=True):
		#print('hide_children:',fr,fr_level,hide)
		t = self.tv.text
		ilf = t.find(lf,fr)
		if ilf < 0:
			# no lf after line of added outline
			return
		# lf after added outline
		k = ilf + 1
		modif = False
		while k >= 0:
			if isinstance(self.content[k],tuple):
				# line after lf has an outline
				vals_n_opt = self.content[k]	# ([l,l],n,{...})
				vals = vals_n_opt[0]
				n    = vals_n_opt[1]
				opts = {} if len(self.content[k]) < 3 else self.content[k][2]
				#print('to hide?',vals,len(vals)-1,fr_level)
				if (len(vals)-1) > fr_level:						
					# level higher that from level, set as (un)hidden
					opts['hidden'] = hide
					self.content[k] = (vals,n,opts)
					modif = True
				else:
					# level too high, end of (un)hiding
					break
				ilf = t.find(lf,k)
				if ilf < 0:
					# no lf after line of added outline, end of (un)hiding
					break
				k = ilf + 1
			else:
				# line after lf does not have an outline, thus end of (un)hiding
				break
		if modif:
			# set outline attributes	
			self.set_outline_attributes()
			self.modif = True
	
	def set_textview_and_content(self):
		t = ''
		content = []
		i = 0
		while i < len(self.content):
			if isinstance(self.content[i],tuple):
				# Not character, thus outline ([vals], nbr_chr)		
				vals_n_opt = self.content[i]	# ([l,l],n,{...})
				vals = vals_n_opt[0]
				n    = vals_n_opt[1]
				opts = {} if len(self.content[i]) < 3 else self.content[i][2]
				t_out = self.OutlineFromLevelValue(vals)
				if not t_out:
					# too high level
					return False
				newn = len(t_out)
				t += t_out
				content += [(vals,newn,opts)]*newn
				i += n
			ilf = self.tv.text.find(lf,i)
			if ilf < 0:
				ilf = len(self.content)-1
			# normal characters between i+n and ilf
			t       += self.tv.text[i:ilf+1]
			content += list(self.tv.text[i:ilf+1])
			i = ilf + 1 
		self.tv.text = t
		self.content = content		
		self.modif = True
		# set outline attributes	
		self.set_outline_attributes()
		return True

	def set_outline_attributes(self, typ=None):			
		#print('set_outline_attributes')
		self.prev_content_offset = self.tv.content_offset
		
		self.set_content_inset()

		# set attributes for general text
		self.outline = NSMutableAttributedString.alloc().initWithString_(self.tv.text)
		
		# set attributes for outlines
		#print(textview.text)
		#print(self.content)
		self.lines = {}
		pre_outline = None
		i = 0
		y = 10	# 1st line of textview has some y offset
		while i < len(self.content):
			if isinstance(self.content[i],tuple):
				# Not character, thus outline ([value of level 0, ...], nbr_chr)		
				vals_n_opt = self.content[i]	# ([l,l],n,{...})
				vals = vals_n_opt[0]
				n    = vals_n_opt[1]
				if len(vals_n_opt) > 2:
					opt = vals_n_opt[2]
				else:
					opt = {}
				if self.content[i][0] == pre_outline:
					if hidden:
						self.outline.setAttributes_range_(self.invisible_outline_attributes_hidden, NSRange(i, n))
					else:
						self.outline.setAttributes_range_(self.invisible_outline_attributes, NSRange(i, n))
				else:
					if 'hidden' not in opt:
						self.outline.setAttributes_range_(self.outline_attributes, NSRange(i, n))
						hidden = False
					elif opt['hidden']:
						self.outline.setAttributes_range_(self.outline_attributes_hidden, NSRange(i, n))
						hidden = True
					else:
						self.outline.setAttributes_range_(self.outline_attributes, NSRange(i, n))
						hidden = False
					pre_outline = self.content[i][0]
			else:
				n = 0
				hidden = False
			j = i + n
			ilf = self.tv.text.find(lf,i)
			if ilf < 0:
				ilf = len(self.content)+1
			w,h = ui.measure_string(self.tv.text[i:ilf]+'*', font=(self.font,self.font_size))
			x = 0
			self.lines[i] = (x,y,w,h)
			self.lines_ymax = y + h
			y += h
			i = min(ilf + 1,len(self.content))

			if hidden:
				self.outline.setAttributes_range_(self.text_attributes_hidden, NSRange(j,i-j))	
			else:	
				self.outline.setAttributes_range_(self.text_attributes, NSRange(j,i-j))	

				t = self.tv.text[j:i].lower()
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
					link = self.tv.text[j+lk:j+lj]
					self.link_attributes = {NSForegroundColorAttributeName:self.link_color, NSFontAttributeName:font, NSLinkAttributeName:link, NSUnderlineStyleAttributeName:1}
					self.outline.setAttributes_range_(self.link_attributes, NSRange(j+lk,lj-lk))	
					li = lj
		#print(self.lines)

		self.set_attributed_text(self.tvo, self.outline)

		for sv in self.tv.subviews:
			self.tv.remove_subview(sv)
			del sv
		
		i = 0	
		prev = []	
		b = None
		while i < len(self.tv.text):
			if isinstance(self.content[i], tuple):
				# outline
				v = self.content[i][0]				# [levels]
				if len(v) > len(prev):
					# could be child of previous
					if v[:len(prev)] == prev:
						# child of previous
						opts = self.content[i][2]				# {... like 'hidden'=True}
						if 'hidden' in opts:
							if opts['hidden']:
								# change icon of previous button
								if b:
									b.image = ui.Image.named('iob:arrow_down_b_32')
									b.data = b.data[:2] + (True,)
				prev = v 
				n = self.content[i][1]				# length of outline
				t = self.tv.text[i:i+n]				# outline
				opts = self.content[i][2]				# {... like 'hidden'=True}
				build_b = True
				if 'hidden' in opts:
					if opts['hidden']:
						build_b = False
			else:
				# no outline
				build_b = True
			if build_b:
					j = len(t) - len(t.lstrip())	# length of blanks
					p1 = self.tvo.positionFromPosition_offset_(self.tvo.beginningOfDocument(), i+j)
					p2 = self.tvo.positionFromPosition_offset_(self.tvo.beginningOfDocument(), i+j+1)
					rge = self.tvo.textRangeFromPosition_toPosition_(p1,p2)
					rect = self.tvo.firstRectForRange_(rge)	# CGRect
					x,y = rect.origin.x,rect.origin.y
					#w,h = rect.size.width,rect.size.height
					#print(x,y,w,h)
					x += self.tv.x
					b = ui.Button(name='hide_show_'+str(i))
					b.image = ui.Image.named('iob:arrow_right_b_32')
					b.frame = (x-self.font_size,y,self.font_size,self.font_size)
					b.action = self.hide_children_via_button
					b.data = (i,len(v)-1,False)
					self.tv.add_subview(b)
					
					p1 = self.tvo.positionFromPosition_offset_(self.tvo.beginningOfDocument(), i+j)
					p2 = self.tvo.positionFromPosition_offset_(self.tvo.beginningOfDocument(), i+n)
					rge = self.tvo.textRangeFromPosition_toPosition_(p1,p2)
					rect = self.tvo.firstRectForRange_(rge)	# CGRect
					x,y = rect.origin.x,rect.origin.y
					w,h = rect.size.width,rect.size.height
					bb = ui.View()
					bb.frame = (x,y,w,h)
					#bb.border_width = 1
					doubletap(bb,self.doubletap_handler)
					long_press(bb,self.long_press_handler)
					self.tv.add_subview(bb)

					if self.show_lines_separator == 'yes':					
						sep = ui.Label()
						ysep = self.tv.y + y + h
						sep.frame = (0,ysep,self.tv.width,1)
						sep.border_width = 1
						sep.border_color = 'lightgray'
						self.tv.add_subview(sep)
						
					if self.checkboxes == 'yes':					
						chk = ui.Button()
						d = 4
						chk.frame = (d,y+d,h-2*d,h-2*d)
						chk.border_width = 1
						chk.border_color = 'black'
						chk.corner_radius = 4
						chk.font = ('<System>',10)#h-2*d)
						chk.action = self.checkbox_button_action
						chk.i = i
						chk.checkmark = False
						if 'checkmark' in opts:
							chk.checkmark = True
							if opts['checkmark'] == 'yes':
								chk.checkmark = True
								chk.image = self.checkmark_ui_image
								chk.border_width = 0
						self.tv.add_subview(chk)
										
			ilf = self.tv.text.find(lf,i)
			if ilf < 0:
				ilf = len(self.tv.text)
			i = ilf + 1	

		if typ:			
			if self.auto_save == 'each char':
				self.file_save(save_prm=False)
			elif self.auto_save == 'line':
				if typ == 'line':
					self.file_save(save_prm=False)			
			else: # no
				pass
			
	@on_main_thread
	def set_content_inset(self):
		h = ui.measure_string('A', font=(self.font,self.font_size))[1]
		self.tvo.textContainerInset = UIEdgeInsets(0,2*h,0,0)

	def checkbox_button_action(self,sender):
		i = sender.i
		if len(self.content[i]) > 2:
			opts = self.content[i][2]
		else:
			opts = {}
		if sender.checkmark:
			opts['checkmark'] = 'no'
			sender.image = None			
			sender.border_width = 1
		else:
			opts['checkmark'] = 'yes'
			sender.image = self.checkmark_ui_image
			sender.border_width = 0
		sender.checkmark = not sender.checkmark
		n = self.content[i][1]
		new = (self.content[i][0],self.content[i][1],opts)
		for j in range(i,i+n):
			self.content[j] = new
		self.modif = True
		
	def hide_children_via_button(self,sender):
		#print(sender.data)
		fr, fr_level, hide = sender.data
		hide = not hide
		self.hide_children(fr, fr_level, hide=hide)

	@on_main_thread
	def set_attributed_text(self,tvo,t):
		tvo.setAttributedText_(t)

	def setCursor(self,i):
		#print('setCursor')
		p1 = self.tvo.positionFromPosition_offset_(self.tvo.beginningOfDocument(), i)
		self.tvo.selectedTextRange = self.tvo.textRangeFromPosition_toPosition_(p1, p1)

		rge = self.tvo.textRangeFromPosition_toPosition_(p1,p1)
		rect = self.tvo.firstRectForRange_(rge)	# CGRect
		y = rect.origin.y
		h = rect.size.height

		#print(y,self.tv.content_offset[1])
		#if not isinf(y) and self.tv.content_offset[1] > 0:
		if not isinf(y):
			self.tv.content_offset = (0,y)
			#self.tvo.scrollRectToVisible_animated_(rect,True)#CGRect(CGPoint(0, y), CGSize(self.tv.width,h)),True)

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
		outline_type = outline_types[level] + '_'	# temporary _ will be blank later
		
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
			fil.write(self.tv.text)
		with open(self.path+self.file_content, mode='wt') as fil:
			prms ={}
			prms['format'] = self.outline_format
			prms['font'] = self.font
			prms['font_size'] = self.font_size
			t = str(self.content) + lf + str(prms)
			fil.write(t)
			del t
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
					
	def will_close(self):
		if self.log == 'yes':
			try:
				self.log_fil.close()
			except:
				pass
		if self.modif:
			b = console.alert('⚠️ File has been modified', 'save before leaving?', 'yes', 'no', hide_cancel_button=True)
			if b == 2:
				return
			self.file_save()
		self.prms_save()

def main():
	global mv
	mv = Outliner()
	mv.present('fullscreen')
	
if __name__ == '__main__':
	main()
