'''
todo
====
- ok tab
-	.. imbed tab level > previous tab of more than 1
-	ok lf
-	.. renumbering tab
-	.. bug: renumbering tab on 3.0 even if 2.1 exists
-	ok normal
-	ok backspace
-	.. lf insert
-	.. lf renumbering
-	ok back tab
-	.. bug: enter renumbering on 3.1 sets 4.2
-	.. renumering back tab
-	.. cursor after
- .. quid si paste plus d'une ligne, empecher?
- .. left/right align outline several values, same level ex: see roman
niceties optional todo
======================
- .. move,drag/drop....renumbering, quid not same level? from and to location
- .. hide/show children
- .. choice font, font_size
- .. multiple bold/italic/font/size/color... in text?
- .. try to generate attrib during typing, not each time all, thus only differences
- .. functionnality to build user format? with bullets or emojis?
- ..	- memo infos in .content
'''
import ast
import console
import File_Picker		# https://github.com/cvpe/Pythonista-scripts/blob/master/File_Picker.py
import Folder_Picker	# https://github.com/cvpe/Pythonista-scripts/blob/master/Folder_Picker.py
from   objc_util import *
import os
import re
import ui

Version = 'V00.02'
Versions = '''
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

bs = '\b'
lf ='\n'
tab = '\t'

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
		
		text_color = UIColor.colorWithRed_green_blue_alpha_(0, 0, 1, 1)
		self.text_attributes = {NSForegroundColorAttributeName:text_color, NSFontAttributeName:font}
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
		
		self.right_button_items = (b_format, b_color)
		
		self.outline_attributes = {NSForegroundColorAttributeName:self.outline_color, NSFontAttributeName:font}
		
		self.invisible_outline_color = UIColor.colorWithRed_green_blue_alpha_(0.8,0.8, 0.8,1)
		self.invisible_outline_attributes = {NSForegroundColorAttributeName:self.invisible_outline_color, NSFontAttributeName:font}
		
		self.modif = False
		self.file = None
		
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
		x,y = self.getButtonItemFrame(sender)
		sub_menu = ['New', 'Open','Save']
		tv = ui.TableView()
		tv.frame = (0,0,180,120)
		tv.data_source = ui.ListDataSource(items=sub_menu)
		tv.allows_multiple_selection = False
		tv.delegate = self
		tv.present('popover',popover_location=(x,y),hide_title_bar=True)
		tv.wait_modal()
		act = sub_menu[tv.selected_row[1]]
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
		elif act == 'Open':
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
		tv.present('popover',popover_location=(x,y),hide_title_bar=True)
		tv.wait_modal()
		loc_format = sub_menu[tv.selected_row[1]]
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
				# check if not increase level of more than 1 versus previous line level
				#....... todo begin ..............................
				previous_level = -1	# if no previous outline
				ilf = textview.text.rfind(lf,i-1)	# -1 if not found
				k = ilf+1
				print(self.content[k])
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
				fr = range_c[0]
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
			if isinstance(self.content[k],tuple):
				# line after lf has an outline
				vals,l_bef = self.content[k]
				if (len(vals)-1) >= fr_level:						
					# modify vals array 
					nvals = vals[:fr_level] + [vals[fr_level]+delta] + vals[fr_level+1:]
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
		
	def set_outline_button(self,i,n):
		p1 = self.tvo.positionFromPosition_offset_(self.tvo.beginningOfDocument(), i)
		p2 = self.tvo.positionFromPosition_offset_(self.tvo.beginningOfDocument(), i+n)
		rge = self.tvo.textRangeFromPosition_toPosition_(p1,p2)
		rect = self.tvo.firstRectForRange_(rge)	# CGRect
		x,y = rect.origin.x,rect.origin.y
		w,h = rect.size.width,rect.size.height
		#print(x,y,w,h)
		b = ui.Button()
		b.outline = i
		b.frame = (x,y,w,h)
		#b.background_color = (1,0,0,0.2)
		#b.corner_radius = 2
		#b.border_width = 1
		b.action = self.outline_button_action
		self.tv.add_subview(b)
		
	def outline_button_action(self,sender):
		x = sender.x + sender.width/2
		y = 65 + self.tv.y + sender.y + sender.height
		i = sender.outline
		vals,n = self.content[i]
		t = self.OutlineFromLevelValue(vals)
		sub_menu = ['move', 'hide children','show children']
		tv = ui.TableView()
		tv.name = t
		tv.frame = (0,0,180,140)
		tv.data_source = ui.ListDataSource(items=sub_menu)
		tv.allows_multiple_selection = False
		tv.delegate = self
		tv.present('popover',popover_location=(x,y),hide_title_bar=False)
		tv.wait_modal()
		act = sub_menu[tv.selected_row[1]]
		if act == 'move':
			console.alert('⚠️ move not yet supported','','ok', hide_cancel_button=True)
		elif act == 'hide children':
			console.alert('⚠️ hide children not yet supported','','ok', hide_cancel_button=True)
		elif act == 'show children':
			console.alert('⚠️ show children not yet supported','','ok', hide_cancel_button=True)
		
	def set_textview_and_content(self):
		t = ''
		content = []
		i = 0
		while i < len(self.content):
			if isinstance(self.content[i],tuple):
				# Not character, thus outline ([vals], nbr_chr)		
				vals,n = self.content[i]
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
		self.outline.setAttributes_range_(self.text_attributes, NSRange(0, len(self.tv.text)))	
		# remove all outline buttons
		for sv in self.tv.subviews:
			self.tv.remove_subview(sv)
			del sv
		# set attributes for outlines
		#print(textview.text)
		#print(self.content)
		pre_outline = None
		i = 0
		while i < len(self.content):
			if isinstance(self.content[i],tuple):
				# Not character, thus outline ([value of level 0, ...], nbr_chr)		
				n = self.content[i][1]
				if self.content[i] == pre_outline:
					self.outline.setAttributes_range_(self.invisible_outline_attributes, NSRange(i, n))
				else:
					self.outline.setAttributes_range_(self.outline_attributes, NSRange(i, n))
					self.set_outline_button(i,n)
					pre_outline = self.content[i]
			ilf = self.tv.text.find(lf,i)
			i = ilf + 1 if ilf >= 0 else len(self.content)					
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
		return outline_type	
		
	def file_save(self):
		with open(self.path+self.file, mode='wt') as fil:
			fil.write(self.tv.text)
		with open(self.path+self.file_content, mode='wt') as fil:
			t = str(self.content) + lf + self.outline_format
			fil.write(t)
			del t
		self.modif = False
		
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
