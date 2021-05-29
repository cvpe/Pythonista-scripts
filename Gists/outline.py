'''
todo
- .. 0️⃣bug: double tab ne peut pas reculer de deux levels
- .. 1️⃣backspace on outline, decrease level, calcul vals
- .. 2️⃣lf in text => insert line
- .. move,drag/drop....renumbering
- .. tab on iphone? new key? in Pythonista keyboard
- .. close => save
- .. save
- .. new text file
- .. load text file 
- ..	- file picker
- ..	- if exists nnnn.txt and .outline self.content
- .. choice font, font_size
- .. multiple font/size/color dans texte
- .. left/right align outline several values, same level ex: see roman
- .. try to generate attrib during typing, not each time all, thus only differences
- .. functionnality to build user format?
- .. button at right of line = hide childs (or via popup menu?)
'''
import console
from   objc_util import *
import re
import ui

Version = 'V00.00'
Versions = '''
Version V00.00
  initial version
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
		self.name = 'outline for @ihf'
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
		self.tvo.setAllowsEditingTextAttributes_(True)
		text_color = UIColor.colorWithRed_green_blue_alpha_(0, 0, 1, 1)
		self.text_attributes = {NSForegroundColorAttributeName:text_color, NSFontAttributeName:font}
		self.add_subview(self.tv)
		self.content = []
		
		b_version = ui.ButtonItem()
		b_version.title = Version
		b_version.tint_color = 'green'
		b_version.action = self.button_version_action	

		self.left_button_items = (b_version,)		
		
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
		
		self.invisible_outline_color = UIColor.colorWithRed_green_blue_alpha_(1,1,1, 1)
		self.invisible_outline_attributes = {NSForegroundColorAttributeName:self.invisible_outline_color, NSFontAttributeName:font}
		
	def button_version_action(self,sender):
		x = 80
		y = 55
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
			self.set_textview_and_content()		
					
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
		t = textview.text
		# check if not typing in an outline 
		if range_c[0] > 0 and range_c[1] < len(self.content):
			# not a begin of text
			if isinstance(self.content[range_c[0]-1],tuple) and isinstance(self.content[range_c[1]],tuple):
				console.alert('Typing in outlines not allowed','','ok', hide_cancel_button=True)
				return False
		keep_outline = 1
		processed = False
		if replacement == tab:
			level = -1			
			if range_c[0] == 0:
				# start of text
				level, nvals = 0,[0]
			else:
				i = range_c[0] - 1
				if isinstance(self.content[i], tuple):
					# previous is already an outline
					#........check level of previous max diff 1
					level, vals = self.content[i]
					# we will replace it by blanks to increase indentation
					t_out = self.OutlineFromLevelValue(level,vals)
					l_out = len(t_out)
					j = range_c[0] - l_out
					t = t[:j] + ' '*l_out 	
					self.content = self.content[:j] + ['\x00']*l_out 		
					level += 1
					nvals = vals + [0]
				elif self.content[i] == lf:
					# tab as 1st character of a new line
					level, nvals = 0,[0]					
			if level >= 0:
				replacement = self.OutlineFromLevelValue(level,nvals)
				c_replacement = [(level,nvals)]*len(replacement)
				processed = True
			else:
				# use tab in text => force lf but without increasing
				replacement = lf
				keep_outline = 0
				# use tab in text, not as indentation
				#console.alert('Tab outside begin of line not allowed','','ok', hide_cancel_button=True)
				#return False	# not allowed
		if processed:
			pass	# already processed
		elif replacement == '':
			# Backspace or cut to remove textfield[range[0]to[range[1]-1]
			# no way to differentiate backspace of cut charcter at left of cursor
			print(self.content)
			n = 0
			del_lf = False
			for j in range(range_c[0],range_c[1]):
				if isinstance(self.content[j],tuple) or self.content[j] == '\x00':
					n += 1
				elif self.content[j] == lf:
					del_lf = True
			if n == 0:
				# only delete normal characters
				if del_lf:
					if isinstance(self.content[range_c[1]],tuple) or self.content[range_c[1]] == '\x00':
						# delete lf where next line begins with an outline
						console.alert('delete line feed followed by a line with an outline not allowed','','ok', hide_cancel_button=True)
						return False	# not allowed
				replacement = ''
				c_replacement = []
			elif n == (range_c[1] - range_c[0]):
				# all outline
				#.......not yet programmmed				
				console.alert('delete outline not yet supported','','ok', hide_cancel_button=True)
				return False	# not allowed
			else:
				# mixt normal and outline
				console.alert('cut mix of normal and outline characters not allowed','','ok', hide_cancel_button=True)
				return False	# not allowed
		else:
			# not a tab
			# replacement unchanged
			c_replacement = list(replacement)
			l_out = 0
			if replacement == lf:
				if range_c[1] != len(self.content):
					console.alert('insert line not yet supported','','ok', hide_cancel_button=True)
					return False	# not allowed

				# search at left last outline and position previous lf
				# keep same level, value + 1
				# generate blanks for missing tabs to align
				i = range_c[0] - 1
				ipreflf = textview.text.rfind(lf,0,i)	# -1 if first line
				j = -1
				for i in range(i,ipreflf+1,-1):
					if isinstance(self.content[i],tuple):
						j = i
						break
				if j >= 0:
					level,vals = self.content[j]
					nvals = vals[:-1] + [vals[-1]+keep_outline]
					t_out = self.OutlineFromLevelValue(level,nvals)
					l_out = len(t_out)
					# put some blanks after lf to align 
					l_blanks = j - ipreflf - l_out
					replacement   += ' '*l_blanks + t_out
					c_replacement += ['\x00']*l_blanks + [(level,nvals)]*l_out 
					
		textview.text = t[:range_c[0]] + replacement + t[range_c[1]:]
		self.content = self.content[:range_c[0]] + c_replacement + self.content[range_c[1]:]		
		#print(self.content)
		
		# set outline attributes	
		self.set_outline_attributes()

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
		i = -1
		pre_outline = None
		for ic in range(len(self.content)):
			c = self.content[ic]
			if isinstance(c,tuple):
				# Not character, thus outline (level,value)
				if i < 0:
					i = ic
					n = 1
				else:
					n += 1
			else:
				if i >= 0:
					if self.content[i] == pre_outline:
						self.outline.setAttributes_range_(self.invisible_outline_attributes, NSRange(i, n))
					else:
						self.outline.setAttributes_range_(self.outline_attributes, NSRange(i, n))
						self.set_outline_button(i,n)
					pre_outline = self.content[i]
					i = -1
		if i >= 0:
			if self.content[i] == pre_outline:
				self.outline.setAttributes_range_(self.invisible_outline_attributes, NSRange(i, n))
			else:
				self.outline.setAttributes_range_(self.outline_attributes, NSRange(i, n))
				self.set_outline_button(i,n)
		@on_main_thread
		def th():
			self.tvo.setAttributedText_(self.outline)
		th()
		return False
		
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
		level,vals = self.content[i]
		t = self.OutlineFromLevelValue(level,vals)
		sub_menu = ['move', '...','...']
		tv = ui.TableView()
		tv.name = t
		tv.frame = (0,0,180,140)
		tv.data_source = ui.ListDataSource(items=sub_menu)
		tv.allows_multiple_selection = False
		tv.delegate = self
		tv.present('popover',popover_location=(x,y),hide_title_bar=False)
		tv.wait_modal()
		
	def set_textview_and_content(self):
		t = ''
		content = []
		i = -1
		pre_type = 0
		for ic in range(len(self.content)):
			c = self.content[ic]
			type = 1 if isinstance(c,tuple) else 2
			if type != pre_type:
				# no more same type
				if pre_type == 1:
					# outline
					level,vals = self.content[i]
					t_out = self.OutlineFromLevelValue(level,vals)
					t += t_out
					content += [(level,vals)]*len(t_out)
				elif pre_type == 2:					
					# normal character
					t_out = self.tv.text[i:ic]
					t += t_out
					content += list(t_out)
				i = ic
				pre_type = type
		# process last part
		if pre_type == 1:
			# outline
			level,vals = self.content[i]
			t_out = self.OutlineFromLevelValue(level,vals)
			t += t_out
			content += [(level,vals)]*len(t_out)
		elif pre_type == 2:					
			# normal character
			t_out = self.tv.text[i:]
			t += t_out
			content += list(t_out)		
		self.tv.text = t
		self.content = content
		
		# set outline attributes	
		self.set_outline_attributes()
		
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
		
	def OutlineFromLevelValue(self,level,vals):
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
		if self.outline_format == 'decimal':
			if level == 0:
				outline_type = 'v.0 '
			else:
				outline_type = 'v.'*(level+1)
				outline_type = outline_type[:-1] + ' '
			for v in vals:
				outline_type = outline_type.replace('v',str(v+1),1)
		elif self.outline_format in ['alphanumeric','traditional']:
			if self.outline_format == 'alphanumeric':
				outline_types = ['I.', 'A.', 'i.', 'a.', '(1).']
			elif self.outline_format == 'traditional':			
				outline_types = ['1.', 'A.', 'i.', 'a.']
			#........quid if higher level
			outline_type = outline_types[level] + ' '
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
		return outline_type	

def main():
	mv = Outliner()
	mv.present('fullscreen')
	
if __name__ == '__main__':
	main()
