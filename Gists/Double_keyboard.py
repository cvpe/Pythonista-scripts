# todo
# - right aligned keys?
import ui
from objc_util import *

import ui
from objc_util import *

def SetTextFieldPad(tf, pad=None, clearButtonMode=False, undo_redo_pasteBarButtons=True, textfield_did_change=None):
	if not pad:

		back_key = (0.7,0.7,0.7)
		pad = [
		{'keys':'йцукенгшщзх'},
		{'key':'⌫','width':2,'back':back_key},
		{'key':'new row'},
		{'keys':'фывапролджэ'},
		{'key':'⏎', 'width':1.5,'back':back_key},
		{'key':'new row'},
		{'key':'△','back':back_key},
		{'keys':'ячсмитьбюъ'},
		{'key':'△','back':back_key, 'width':2},
		{'key':'new row'},
		{'key':'123', 'width':1.2,'back':back_key},
		{'key':'','back':back_key},
		{'key':'','back':back_key},
		{'key':' ', 'width':7},
		{'key':'123', 'width':2,'back':back_key},
		{'key':'dismiss keyboard', 'icon':'SF=keyboard', 'width':2.2,'back':back_key}]
		multi_modes = [
			('123','123','AЪВ','AЪВ'),
			('△','▲','#+=','123'),
			('йцукенгшщзх','ЙЦУКЕНГШЩЗХ','1234567890—','1234567890—'),
			('фывапролджэ','ФЫВАПРОЛДЖЭ','@#№€´&*()\'"','э$£¥±•`^[]{}'),
			('ячсмитьбюъ','ЯЧСМИТЬБЮЪ','%_-+=/;:,.','§|~…≠\<>!?')
			]

	tfo = ObjCInstance(tf).textField() # UITextField is subview of ui.TextField
	# modes: 0=alpha_lower 1=alpha_upper 2=num 3=spec
	tf.mode = 0
	
	def key_pressed(sender):

			if sender.title == 'test':
				return
			tfb = sender.TextField
			tfobjc = ObjCInstance(tfb).textField()
			cursor = tfobjc.offsetFromPosition_toPosition_(tfobjc.beginningOfDocument(), tfobjc.selectedTextRange().start())
			old_mode = tfb.mode
			if sender.name == '':
				return
			elif sender.name == 'delete':
				if cursor <= (len(tfb.text)-1):
					tfb.text = tfb.text[:cursor] + tfb.text[cursor+1:]
			elif sender.name == '⌫':
				if cursor > 0:
					#if tfb.text != '':
					tfb.text = tfb.text[:cursor-1] + tfb.text[cursor:]
					cursor = cursor - 1
			elif sender.name == '⏎':
				tfb.end_editing()
				return
			elif sender.title == '123':
				tfb.mode = 2	# mode 2=num
			elif sender.title == '#+=':
				tfb.mode = 3	# mode 3=spec
			elif sender.title == 'AЪВ':
				tfb.mode = 0	# mode 0=alpha_lower
			elif sender.title == '△':
				tfb.mode = 1	# 1=alpha_upper
			elif sender.title == '▲':
				tfb.mode = 0	# 0=alpha_lower
			elif sender.name == 'dismiss keyboard':
				tfb.end_editing()
				return
			else:
				tfb.text = tfb.text[:cursor] + sender.title + tfb.text[cursor:]
				cursor = cursor + 1
			if tfb.mode!= old_mode:
				# update keys titles
				# tfb.mode_buttons = [(button,'abcd'),(button,('a','b','c','d'))
				font = 'Menlo'
				for b,t in tfb.mode_buttons:
					if isinstance(t,tuple):
						b.title = t[tfb.mode]
					else:
						i = tfb.mode*len(b.title)
						b.title = t[i:i+len(b.title)]
					# eventually reset font size because title could be wider
					# ex: ▲ --> #+=
					font_size = 32
					while True:
						w = ui.measure_string(b.title, font=(font,font_size))[0]
						if w < (b.width-4):
							break
						else:
							font_size -= 1
					b.font = (font, font_size)
					if b.title == '△':
						b.background_color = back_key
					elif b.title == '▲':
						b.background_color = 'white'				
			if textfield_did_change:
				textfield_did_change(tfb)
				
			# set cursor
			cursor_position = tfobjc.positionFromPosition_offset_(tfobjc.beginningOfDocument(), cursor)
			tfobjc.selectedTextRange = tfobjc.textRangeFromPosition_toPosition_(cursor_position, cursor_position)

	# design your keyboard
	# pad = [{key='functionnality',title='title',icon='icon'},...]
	#		'' => empty key, no action
	#		new row => new row
	#		nul => no key
	#		⌫ => left delete
	#		delete => right delete
	#		done => discard the keyboard
	#   other => append the character
	
	# count the maximum width of rows
	db = 99999	# we search a minimum
	dd = 10
	row_max_length = 0
	row_max_number = 0
	row_length = 0
	row_number = 0
	new_pad = []
	rows = []
	for pad_elem in pad:
		if 'keys' in pad_elem:
			for key in pad_elem['keys']:
				elem = {'key':key}
				for k in pad_elem:
					if k != 'keys':
						elem[k] = pad_elem[k]
				new_pad.append(elem)
		else:
			new_pad.append(pad_elem)
	for pad_elem in (new_pad+[{'key':'new row'}]):
		if pad_elem['key'] == 'new row':
			if row_length > row_max_length:
				row_max_length = row_length
			if row_number > row_max_number:
				row_max_number = row_number
			db = min((ui.get_screen_size()[0]-(row_number+1)*dd) / row_length,db)
			rows.append((row_length,row_number))
			row_length = 0		
			row_number = 0		
		else:
			row_number += 1
			if 'width' in pad_elem:	
				row_length += float(pad_elem['width'])
			else:
				row_length += 1
	rows.append((0,0))

	v = ui.View()
	v.background_color = 'lightgray'
	y = dd
	irow = 0
	row_length,row_number = rows[irow]
	x = ui.get_screen_size()[0]-(row_number-1)*dd-row_length*db - dd
	mode_buttons = []
	for pad_elem in new_pad:
		if pad_elem['key'] == 'new row':
			y = y + db + dd
			irow += 1
			row_length,row_number = rows[irow]
			x = ui.get_screen_size()[0]-(row_number-1)*dd-row_length*db - dd
		elif pad_elem['key'] == 'nul':			
			x = x + db + dd
		else:			
			b = ui.Button()
			b.name = pad_elem['key']
			b.background_color = 'white'	# or any other color
			b.tint_color = 'black'
			b.corner_radius = 10 
			b.title = ''
			if 'icon' in pad_elem:
				if pad_elem['icon'].startswith('SF='):
					o = ObjCClass('UIImage').systemImageNamed_(pad_elem['icon'][3:])
					with ui.ImageContext(64,32) as ctx:
						o.drawAtPoint_(CGPoint(16,6))
						if pad_elem['icon'] == 'SF=keyboard':
							h = 12
							ui.draw_string('˅', rect=(28,20,h,h), font=('<System-Bold>',h))
						b.background_image = ctx.get_image().with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
						ObjCInstance(b).setContentMode_(2)
				else:
					b.image = ui.Image.named(pad_elem['icon']).with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			elif 'title' not in pad_elem:
				b.title = pad_elem['key']
			if 'title' in pad_elem:
				b.title = pad_elem['title']
			if 'width' in pad_elem:	
				dbb = db * pad_elem['width']
			else:
				dbb = db
			if 'back' in pad_elem:	
				b.background_color = pad_elem['back']
			b.frame = (x,y,dbb,db)
			font = 'Menlo'
			font_size = 32
			while True:
				w = ui.measure_string(b.title, font=(font,font_size))[0]
				if w < (b.width-4):
					break
				else:
					font_size -= 1
			b.font = (font, font_size)
			b.TextField = tf # store tf as key attribute  needed when pressed
			b.action = pad_elem.get('action', key_pressed)
			v.add_subview(b)
			if b.title != '':
				l = len(b.title)
				for r in multi_modes:
					if b.title in r:
						# key is a function like 123/ABC/▲/△
						mode_buttons.append((b,r))		
						break
					elif l == 1 and b.title in r[0]:
						# key is one letter/dogot/special
						i = r[0].index(b.title)
						c = r[0][i:i+l]+r[1][i:i+l]+r[2][i:i+l]+r[3][i:i+l]
						mode_buttons.append((b,c))		
						break	
			x = x + dbb + dd
	y = y + db + dd
	tf.mode_buttons = mode_buttons

	v.width = ui.get_screen_size()[0]
	v.height = y

	# view of keyboard
	retain_global(v) # see https://forum.omz-software.com/topic/4653/button-action-not-called-when-view-is-added-to-native-view
	tfo.setInputView_(ObjCInstance(v))
	
	# color of cursor and selected text
	tfo.tintColor = UIColor.redColor().colorWithAlphaComponent(0.5)
	
	# clear button
	tfo.clearButtonMode = clearButtonMode

	# comment both lines to keep undo/redo/paste BarButtons above keyboard
	if not undo_redo_pasteBarButtons:
		tfo.inputAssistantItem().setLeadingBarButtonGroups(None)
		tfo.inputAssistantItem().setTrailingBarButtonGroups(None)

class MyView(ui.View):
	def __init__(self):
		self.frame = (0,0,500,500)
		self.background_color = 'white'

		tfl = ui.TextField()
		tfl.frame = (10,10,480,32)
		tfl.placeholder = 'latin'
		tfl.delegate = self
		self.add_subview(tfl)

		tfc = ui.TextField()
		tfc.frame = (10,50,480,32)
		tfc.placeholder = 'cyrillic'
		tfc.delegate = self
		self.add_subview(tfc)
		SetTextFieldPad(tfc)

v = MyView()
v.name = 'Test multiple keyboards for @brumm'
v.present('sheet')
