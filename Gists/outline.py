'''
todo
====
-	.. bug: imbed tab level > previous tab of more than 1
- move/drag/drop
	.. drop: process
	..				- paste before of after target line?
	..				- delete old lines
	..				- loop add lines one by one
-	.. lf insert
-	.. lf renumbering
-	.. cursor after
- .. quid if paste more than one, do not allow?

niceties optional todo
======================
- .. bug: revoir memo/load/init de font et font_size prms et color dans prms
- .. try to generate attrib during typing, not each time all, thus only differences
- .. functionnality to build user format? with bullets or emojis?
- ..	- memo infos in .prm
- ..	- show all formats types with their parameters
'''
import ast
import console
import File_Picker		# https://github.com/cvpe/Pythonista-scripts/blob/master/File_Picker.py
import Folder_Picker	# https://github.com/cvpe/Pythonista-scripts/blob/master/Folder_Picker.py
from   gestures  import *
from   objc_util import *
import os
import re
import sys
import ui

Version = 'V00.06'
Versions = '''
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
  - correction of (one) bug of automatic renumbering after line feed
  - correction of (one) bug of automatic renumbering after tab
  - correction of (one) bug of automatic renumbering after back tab
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
font = UIFont.fontWithName_size_('Menlo', 14)
font_hidden = UIFont.fontWithName_size_('Menlo', 6)

SUIViewController = ObjCClass('SUIViewController')
UIFontPickerViewController = ObjCClass('UIFontPickerViewController')
UIFontPickerViewControllerConfiguration = ObjCClass('UIFontPickerViewControllerConfiguration')

bs = '\b'
lf ='\n'
tab = '\t'

def fontPickerViewControllerDidPickFont_(_self, _cmd, _controller):
	global mv
	controller = ObjCInstance(_controller)
	font = str(controller.selectedFontDescriptor().objectForKey_('NSFontFamilyAttribute'))
	mv.set_font(font)

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
		self.tv.border_width = 1
		self.tv.frame = (0,0,ws,hs)
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

		self.left_button_items = (b_version, b_files)		
		
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
		b_font.title = '🔤'
		b_font.action = self.button_font_action
		
		b_fsize = ui.ButtonItem()
		b_fsize.title = 'font_size'
		b_fsize.action = self.button_fsize_action
		
		self.font = 'Menlo'
		self.font_size = 14
		font = UIFont.fontWithName_size_('Menlo', self.font_size)
		
		self.right_button_items = (b_format, b_color, b_font, b_fsize)
		
		self.text_color = UIColor.colorWithRed_green_blue_alpha_(0, 0, 1, 1)
		self.text_attributes = {NSForegroundColorAttributeName:self.text_color, NSFontAttributeName:font}
		self.text_attributes_hidden = {NSForegroundColorAttributeName:self.text_color, NSFontAttributeName:font_hidden}
		self.outline_attributes = {NSForegroundColorAttributeName:self.outline_color, NSFontAttributeName:font}
		self.outline_attributes_hidden = {NSForegroundColorAttributeName:self.outline_color, NSFontAttributeName:font_hidden}
		
		self.invisible_outline_color = UIColor.colorWithRed_green_blue_alpha_(0.8,0.8, 0.8,1)
		self.invisible_outline_attributes = {NSForegroundColorAttributeName:self.invisible_outline_color, NSFontAttributeName:font}
		
		self.modif = False 
		self.file = None
		
		path = sys.argv[0]
		i = path.rfind('.')
		self.prm_file = path[:i] + '.prm'
		if os.path.exists(self.prm_file):
			with open(self.prm_file, mode='rt') as fil:
				x = fil.read()
				self.prms = ast.literal_eval(x)
		else:
			self.prms = {'font':self.font}
		if 'file' in self.prms:	
			# simulate files button and open last file	
			if not os.path.exists(self.prms['path']+self.prms['file']):
				console.alert('❌ '+self.prms['file']+' in .prm does not exist','prm will be cleaned','ok', hide_cancel_button=True)
				del self.prms['path']
				del self.prms['file']
			else:
				self.button_files_action('open')

			tap(self.tv, self.tap_handler)				
			long_press(self.tv, self.long_press_handler)
			swipe(self.tv, self.swipe_left_handler,direction=LEFT)
			swipe(self.tv, self.swipe_right_handler,direction=RIGHT)
						
	def button_font_action(self,sender):
		root = self

		conf = UIFontPickerViewControllerConfiguration.alloc().init()
		picker = UIFontPickerViewController.alloc().initWithConfiguration_(conf)

		delegate = PickerDelegate.alloc().init()
		picker.setDelegate_(delegate)
		
		vc = SUIViewController.viewControllerForView_(root.objc_instance)
		vc.presentModalViewController_animated_(picker, True)
		
	def button_fsize_action(self,sender):
		try:
			n = int(console.input_alert('enter font size','in pixels', str(self.font_size), hide_cancel_button=True))
			self.set_font(n)
		except:				
			console.alert('❌ font size not integer','','ok', hide_cancel_button=True)
		
	def set_font(self,ft):
		if isinstance(ft,str):
			self.font = ft
		else:
			self.font_size = ft
		font = UIFont.fontWithName_size_(self.font, self.font_size)
		font_hidden = UIFont.fontWithName_size_(self.font, 6)

		self.text_attributes = {NSForegroundColorAttributeName:self.text_color, NSFontAttributeName:font}
		self.text_attributes_hidden = {NSForegroundColorAttributeName:self.text_color, NSFontAttributeName:font_hidden}		
		self.outline_attributes = {NSForegroundColorAttributeName:self.outline_color, NSFontAttributeName:font}
		self.outline_attributes_hidden = {NSForegroundColorAttributeName:self.outline_color, NSFontAttributeName:font_hidden}
		self.invisible_outline_attributes = {NSForegroundColorAttributeName:self.invisible_outline_color, NSFontAttributeName:font}
		
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
			sub_menu = ['New', 'Open','Save']
			tv = ui.TableView()
			tv.frame = (0,0,180,120)
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
			self.file_save()
			self.font = 'Menlo'
			self.prms_save()
			# simulate tab pressed
			self.textview_should_change(self.tv, [0,0], '\x01')
			self.tv.begin_editing()
		elif act == 'Open':
			if sender == 'open':
				self.path = self.prms['path']
				self.file = self.prms['file']
				if 'font' in self.prms:
					self.set_font(self.prms['font'])		
				if 'font_size' in self.prms:
					self.set_font(self.prms['font_size'])	
			else:
				f = File_Picker.file_picker_dialog('Pick a text file', root_dir=os.path.expanduser('~/Documents'))
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
					t,self.outline_format = t.split(lf)
					self.content = ast.literal_eval(t)
					del t
			self.set_outline_attributes()
			self.prms_save()
		elif act == 'Save':
			if not self.file:
				console.alert('❌ No active file','','ok', hide_cancel_button=True)
				return
			if not self.modif:
				console.alert('⚠️ File has not been modified since last save','','ok', hide_cancel_button=True)
				return	
			self.file_save()
		
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
		y = 55
		sub_menu = ['decimal', 'alphanumeric','traditional']
		tv = ui.TableView()
		tv.frame = (0,0,180,120)
		tv.data_source = ui.ListDataSource(items=sub_menu)
		tv.allows_multiple_selection = False
		i = sub_menu.index(self.outline_format)
		tv.selected_row = (0,i)
		tv.delegate = self
		self.selected_row = None
		tv.present('popover',popover_location=(x,y),hide_title_bar=True)
		tv.wait_modal()
		if not self.selected_row:
			return
		loc_format = sub_menu[self.selected_row[1]]
		if loc_format != self.outline_format:
			self.outline_format = loc_format
			if not self.set_textview_and_content():
				# too high level
				console.alert('❌ too high outline level','for this outline format','ok', hide_cancel_button=True)
				return
			self.modif = True
					
	def button_color_action(self,sender):				
		rgb = OMColorPickerViewController(title='choose outline color', rgb=self.outline_rgb)
		self.outline_rgb = rgb
		self.outline_color = UIColor.colorWithRed_green_blue_alpha_(self.outline_rgb[0], self.outline_rgb[1], self.outline_rgb[2], 1)
		self.outline_attributes = {NSForegroundColorAttributeName:self.outline_color, NSFontAttributeName:font}
		
		# set outline attributes	
		self.set_outline_attributes()
						
	def tableview_did_select(self, tableview, section, row):
		self.selected_row = (section,row)
		tableview.close()
		
	def textview_should_change(self, textview, range_c, replacement):
		#print('textview_should_change', range_c,'|'+replacement+'|')
		# check if file active
		if not self.file:
			console.alert('❌ No file is active','','ok', hide_cancel_button=True)
			return False
		# check if not typing in an outline 
		if range_c[0] > 0 and range_c[1] < len(self.content):
			# not a begin of text
			if isinstance(self.content[range_c[0]-1],tuple) and isinstance(self.content[range_c[1]],tuple):
				console.alert('❌ Typing in outlines not allowed','','ok', hide_cancel_button=True)
				return False
		# special process for drop: begin ---------------------
		# special process for drop: end -----------------------
		t = textview.text
		processed = False
		if replacement == '\x01':
			# next level outline
			# ==================
			iprevlf = textview.text.rfind(lf,0,range_c[0])	# -1 if first line
			i = iprevlf + 1
			if len(self.content) == 0 or i == len(self.content):
				# tab as 1st character of file
				range_c = (i,i)
				nvals = [0]	
			elif isinstance(self.content[i], tuple):
				vals,n = self.content[i]
				n = abs(n)	# used by hiding children
				# check if not increase level of more than 1 versus previous line level
				#....... todo begin ..............................
				previous_level = -1	# if no previous outline
				ilf = textview.text.rfind(lf,i-1)	# -1 if not found
				k = ilf+1
				#....... todo end ..............................
				nvals = vals[:-1] + [vals[-1]-1] + [0]
				if not self.OutlineFromLevelValue(nvals):
					# too high level
					console.alert('❌ too high outline level','','ok', hide_cancel_button=True)
					return False	# not allowed		
				# remove old outline
				t = t[:i] + t[i+n:]
				self.content = self.content[:i] + self.content[i+n:]
				range_c = (i,i)
			else:
				# 1st character of line is normal
				range_c = (i,i)
				nvals = [0]	
			replacement = self.OutlineFromLevelValue(nvals)
			c_replacement = [(nvals,len(replacement))]*len(replacement)							
			textview.text = t[:range_c[0]] + replacement + t[range_c[1]:]
			self.content = self.content[:range_c[0]] + c_replacement + self.content[range_c[1]:]	

			if len(nvals) > 1:			
				# automatic outlines renumbering of next lines 		
				fr = range_c[0]
				self.renumbering(fr, len(nvals)-2, -1)		
			
			self.set_outline_attributes()
			self.modif = True
			return False	# no replacement to process				
		elif replacement == lf:
			# line feed
			# ========
			c_replacement = list(replacement)
			l_out = 0
			# search last outline before lf
			# keep same level, value + 1
			i = range_c[0]
			iprevlf = textview.text.rfind(lf,0,i)	# -1 if first line
			j = iprevlf + 1
			if isinstance(self.content[j], tuple):
				# previous line has an outline
				vals,n = self.content[j]
				n = abs(n)	# used by hiding children
				# new line will have same level, nvalue + 1
				nvals = vals[:-1] + [vals[-1]+1]
				t_out = self.OutlineFromLevelValue(nvals)
				l_out = len(t_out)
				replacement   += t_out
				c_replacement += [(nvals,l_out)]*l_out 
			textview.text = t[:range_c[0]] + replacement + t[range_c[1]:]
			self.content = self.content[:range_c[0]] + c_replacement + self.content[range_c[1]:]	
			
			if len(nvals) > 1:			
				# automatic outlines renumbering of next lines 		
				fr = range_c[0]+1
				self.renumbering(fr, len(nvals)-2, +1)		

			self.set_outline_attributes()
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
				vals,n = self.content[i]
				n = abs(n)	# used by hiding children
				# replace old outline by a new one with one level less					
				# remove old outline
				t = t[:i] + t[i+n:]
				self.content = self.content[:i] + self.content[i+n:]
				range_c = (i,i)
				nvals = vals[:-1]
				if len(nvals) > 0:
					nvals = nvals[:-1] + [nvals[-1]+1]
					replacement = self.OutlineFromLevelValue(nvals)
					c_replacement = [(nvals,len(replacement))]*len(replacement)							
					t = t[:range_c[0]] + replacement + t[range_c[1]:]
					self.content = self.content[:range_c[0]] + c_replacement + self.content[range_c[1]:]			

				textview.text = t
				
				if len(nvals) >= 1:			
					# automatic outlines renumbering of next lines 		
					fr = range_c[0]
					#print('renum  after back tab to ',replacement)
					self.renumbering(fr, len(nvals)-1, +1)		
						
				# set outline attributes	
				self.set_outline_attributes()
				self.modif = True
				return False	# no replacement to process		
				
			console.alert('❌ no outline level to decrease','','ok', hide_cancel_button=True)
			return False	# not allowed		
		elif replacement == '':
			# Backspace or cut to remove textfield[range[0]to[range[1]-1]
			# ===========================================================
			# no way to differentiate backspace of cut character at left of cursor
			#print(self.content)
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
					if isinstance(self.content[range_c[1]],tuple):
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
		else:
			# normal character, tab
			# =====================
			# replacement unchanged
			c_replacement = list(replacement)
			l_out = 0
					
		textview.text = t[:range_c[0]] + replacement + t[range_c[1]:]
		self.content = self.content[:range_c[0]] + c_replacement + self.content[range_c[1]:]		
		#print(self.content)
		#print(textview.text)
		
		# set outline attributes	
		self.set_outline_attributes()
		self.modif = True
		return False	# no replacement to process				
		
	def renumbering(self, fr, fr_level, delta):			
		#return
		# automatic outlines renumbering of next lines 
		t = self.tv.text
		ilf = t.find(lf,fr)
		if ilf < 0:
			# no lf after line of added outline
			return	# no action
		# lf after added outline
		k = ilf + 1
		while k >= 0:
			if isinstance(self.content[k],tuple):
				# line after lf has an outline
				vals,l_bef = self.content[k]
				l_bef = abs(l_bef)	# used by hiding children
				if (len(vals)-1) >= fr_level:						
					# modify vals array 
					nvals = vals[:fr_level] + [vals[fr_level]+delta] + vals[fr_level+1:]
					#print(vals,nvals)
					t_aft = self.OutlineFromLevelValue(nvals)
					l_aft = len(t_aft)
					t = t[:k] + t_aft + t[k+l_bef:]	
					self.content = self.content[:k] + [(nvals,l_aft)]*l_aft + self.content[k+l_bef:]				
				ilf = t.find(lf,k)
				if ilf < 0:
					# no lf after line of added outline, end of renumbering
					break
				k = ilf + 1
			else:
				# line after lf does not have an outline, thus end of renumbering
				break
		self.tv.text = t
				
	def tap_handler(self,data):
		xp,yp = data.location
		i = self.xy_to_i(xp,yp)
		if i == None:
			return
		vals,n = self.content[i]
		n = abs(n)	# used by hiding children
		t = self.OutlineFromLevelValue(vals)
		sub_menu = ['hide children', 'show children']
		tv = ui.TableView()
		tv.name = t
		tv.frame = (0,0,180,140)
		tv.data_source = ui.ListDataSource(items=sub_menu)
		tv.allows_multiple_selection = False
		tv.delegate = self
		self.selected_row = None
		tv.present('popover',popover_location=(xp,yp+70),hide_title_bar=False)
		tv.wait_modal()
		if not self.selected_row:
			return
		act = sub_menu[self.selected_row[1]]
		if act == 'hide children':
			self.hide_children(i,len(vals)-1,hide=True)
		elif act == 'show children':
			self.hide_children(i,len(vals)-1,hide=False)
			
	def long_press_handler(self,data):
		global line1,xp1
		#print(dir(data))
		xp,yp = data.location
		#print(xp,yp,data.state)
		# get outline
		if data.state == 1:
			# start long_press
			self.tvm = None
			found = self.xy_to_i(xp,yp)
			if found == None:
				return
			line1 = found
			xp1 = xp
			self.drag_children(found,xp,yp)
		elif data.state == 2:
			# move
			if self.tvm:
				self.tvm.x = xp
				self.tvm.y = yp-100
				#--------- show a gray line where moving text would be inserted: begin ----
				found = self.xy_to_i(0,yp-100)
				if found == None:
					if (yp-100) >= self.lines_ymax:
						y = self.lines_ymax + 2
					else: 
						return
				else:
					y = self.lines[found][1] - 2
				try:
					self.target.y = y
				except:
					self.target = ui.Label()
					self.target.frame = (0,y,self.width,1)
					#self.target.border_width = 1
					#self.target.border_color = 'gray'
					self.target.background_color = 'red'
					self.tv.add_subview(self.target)
				#--------- show a gray line where moving text would be inserted: begin ----
		elif data.state == 3:
			# end
			if self.tvm:
				self.tv.remove_subview(self.tvm)
				del self.tvm
				found = self.xy_to_i(xp,yp-100)
				if found == None:
					return
				if found == line1:
					if xp > xp1:
						# move left to right => simulate tab
						self.textview_should_change(self.tv,[found,found],'\x01')					
					else:
						# move right to left => simulate back tab
						self.textview_should_change(self.tv,[found,found],'\x02')				
				else:
					self.textview_should_change(self.tv,[found,found],self.drag)
						
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
		bvals,n = self.content[fr]
		ilf = t.find(lf,fr)
		if ilf < 0:
			# no lf after line of added outline
			ilf = len(t)
		# lf after added outline
		self.drag = ''
		k = ilf + 1
		while k >= 0:
			if k >= len(t):
				k1 = k
				break
			elif isinstance(self.content[k],tuple):
				# line after lf has an outline
				vals,ni  = self.content[k]
				n = abs(ni)	# used by hiding children
				#print('to hide?',vals,len(vals)-1,fr_level)
				if (len(vals)-1) > (len(bvals)-1):						
					# level higher that from level, set as selected
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
		tvm.font = ('Menlo',12)
		#tvm.size_to_fit()
		w = self.tv.width - 20
		h = 100
		xdrag = xp
		ydrag = yp - 100 # only to see the finger
		w,h = ui.measure_string(tvm.text,font=tvm.font)
		tvm.frame = (xdrag,ydrag,w,h)
		tvm.border_width = 1
		r = 10
		tvm.corner_radius = r
		tvm.background_color = (0.9,0.9,0.9,0.5)
		self.tvm = tvm
		pt = ui.View()
		pt.frame = (0,0,r,r)
		pt.corner_radius = r/2
		pt.background_color = 'blue'
		tvm.add_subview(pt)
		self.tv.add_subview(tvm)
			
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
				vals,ni  = self.content[k]
				n = abs(ni)	# used by hiding children
				#print('to hide?',vals,len(vals)-1,fr_level)
				if (len(vals)-1) > fr_level:						
					# level higher that from level, set as (un)hidden
					if hide:
						n = -n
					#print(ni,n)
					if n != ni:
						self.content[k] = (vals,n)
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
				vals,n = self.content[i]
				n = abs(n)	# used by hiding children
				t_out = self.OutlineFromLevelValue(vals)
				if not t_out:
					# too high level
					return False
				newn = len(t_out)
				t += t_out
				content += [(vals,newn)]*newn
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

	def set_outline_attributes(self):			
		# set attributes for general text
		self.outline = NSMutableAttributedString.alloc().initWithString_(self.tv.text)
		#self.outline.setAttributes_range_(self.text_attributes, NSRange(0, len(self.tv.text)))	
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
				n = self.content[i][1]
				n = abs(n)	# used by hiding children
				if self.content[i] == pre_outline:
					self.outline.setAttributes_range_(self.invisible_outline_attributes, NSRange(i, n))
				else:
					if self.content[i][1] >= 0:
						self.outline.setAttributes_range_(self.outline_attributes, NSRange(i, n))
						hidden = False
					else:
						self.outline.setAttributes_range_(self.outline_attributes_hidden, NSRange(i, n))
						hidden = True
					pre_outline = self.content[i]
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

		@on_main_thread
		def th():
			self.tvo.setAttributedText_(self.outline)
		th()
		
	def setCursor(self,i):
		p1 = self.tvo.positionFromPosition_offset_(self.tvo.beginningOfDocument(), i)
		self.tvo.selectedTextRange = self.tvo.textRangeFromPosition_toPosition_(p1, p1)
		return

	#......... find better		
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
		level = len(vals) - 1
		if self.outline_format == 'decimal':
			if level == 0:
				outline_type = 'v.0_'
			else:
				outline_type = 'v.'*(level+1)
				outline_type = outline_type[:-1] + '_'
			for v in vals:
				outline_type = outline_type.replace('v',str(v+1),1)
			blanks = 2
		elif self.outline_format in ['alphanumeric','traditional']:
			if self.outline_format == 'alphanumeric':
				outline_types = ['I.', 'A.', 'i.', 'a.', '(1).', '(a).', '((1)).', '((a)).']
				blanks = 3
			elif self.outline_format == 'traditional':			
				outline_types = ['1.', 'A.', 'i.', 'a.', '(1).', '(a).', '((1)).', '((a)).']
				blanks = 3
			if level > (len(outline_types)-1):
				return None
			#........quid if higher level
			outline_type = outline_types[level] + '_'
			v = vals[-1]
			if 'I' in outline_type:
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
		
	def file_save(self):
		with open(self.path+self.file, mode='wt') as fil:
			fil.write(self.tv.text)
		with open(self.path+self.file_content, mode='wt') as fil:
			t = str(self.content) + lf + self.outline_format
			fil.write(t)
			del t
		self.modif = False

	def prms_save(self):		
		self.prms['path'] = self.path
		self.prms['file'] = self.file
		self.prms['font'] = self.font
		self.prms['font_sizz'] = self.font_size
		with open(self.prm_file, mode='wt') as fil:
			x = str(self.prms)
			fil.write(x)
		
	def will_close(self):
		if self.modif:
			b = console.alert('⚠️ File has been modified', 'save before leaving?', 'yes', 'no', hide_cancel_button=True)
			if b == 2:
				return
			self.file_save()

def main():
	global mv
	mv = Outliner()
	mv.present('fullscreen')
	
if __name__ == '__main__':
	main()
