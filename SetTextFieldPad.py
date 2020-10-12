import ui
from objc_util import *
from math import cos,sin,pi
from random import random

def SetTextFieldPad(tf, pad=None, clearButtonMode=False, undo_redo_pasteBarButtons=False, textfield_did_change=None, broken=False):
	if not pad:
		pad = [{'key':'1'},{'key':'2'},{'key':'3'},
		{'key':'back space','icon':'typb:Delete'},
		{'key':'new row'},
		{'key':'4'},{'key':'5'},{'key':'6'},
		{'key':'delete','icon':'emj:Multiplication_X'},
		{'key':'new row'},
		{'key':'7'},{'key':'8'},{'key':'9'},
		{'key':'⏎',  'SFicon':'keyboard.chevron.compact.down'},#done','icon':'emj:Checkmark_3'},
		{'key':'new row'},    
		{'key':'nul'},{'key':'0'},{'key':'nul'},{'key':'.'}]
	tfo = ObjCInstance(tf).textField() # UITextField is subview of ui.TextField
	
	def key_pressed(sender):

			if sender.title == 'test':
				return
			tfb = sender.TextField
			tfobjc = ObjCInstance(tfb).textField()
			cursor = tfobjc.offsetFromPosition_toPosition_(tfobjc.beginningOfDocument(), tfobjc.selectedTextRange().start())
			if sender.name == 'delete':
				if cursor <= (len(tfb.text)-1):
					tfb.text = tfb.text[:cursor] + tfb.text[cursor+1:]
			elif sender.name == 'back space':
				if cursor > 0:
					#if tfb.text != '':
					tfb.text = tfb.text[:cursor-1] + tfb.text[cursor:]
					cursor = cursor - 1
			elif sender.name == '⏎':#done':
				tfb.end_editing()
				return
			else:
				tfb.text = tfb.text[:cursor] + sender.title + tfb.text[cursor:]
				cursor = cursor + 1
				
			if textfield_did_change:
				textfield_did_change(tfb)
				
			# set cursor
			cursor_position = tfobjc.positionFromPosition_offset_(tfobjc.beginningOfDocument(), cursor)
			tfobjc.selectedTextRange = tfobjc.textRangeFromPosition_toPosition_(cursor_position, cursor_position)

	# design your keyboard
	# pad = [{key='functionnality',title='title',icon='icon'},...]
	#		new row => new row
	#		nul => no key
	#		back space => left delete
	#		delete => right delete
	#		done => discard the keyboard
	#   other => append the character
	
	# count the maximum width of rows
	row_max_length = 0
	row_length = 0
	for pad_elem in pad:
		if pad_elem['key'] == 'new row':
			if row_length > row_max_length:
				row_max_length = row_length
			row_length = 0		
		else:
			row_length = row_length + 1
	if row_length > row_max_length:
		row_max_length = row_length

	v = ui.View()
	db = 50
	dd = 10
	x0 = (ui.get_screen_size()[0]-row_max_length*db-(row_max_length-1)*dd)/2
	x = x0
	y = dd

	for pad_elem in pad:
		if pad_elem['key'] == 'new row':
			y = y + db + dd
			x = x0
		elif pad_elem['key'] == 'nul':			
			x = x + db + dd
		else:			
			b = ui.Button()
			b.name = pad_elem['key']
			b.background_color = 'white'	# or any other color
			b.tint_color = 'black'
			b.corner_radius = 10 
			b.title = ''
			b.font = ('<system>',32)
			if 'icon' in pad_elem:
				b.image = ui.Image.named(pad_elem['icon']).with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			elif 'SFicon' in pad_elem:
				o = ObjCClass('UIImage').systemImageNamed_(pad_elem['SFicon'])
				wsf,hsf = o.size().width,o.size().height
				with ui.ImageContext(db,db) as ctx:
					o.drawInRect_(CGRect(CGPoint(0.1*db,0.1*db), CGSize(0.8*db,0.8*db)))
					b.image = ctx.get_image()					
			elif 'title' not in pad_elem:
				b.title = pad_elem['key']
			if 'title' in pad_elem:
				b.title = pad_elem['title']
			b.frame = (x,y,db,db)
			if broken:
				r = random()			# generate between 0 and 1
				# angle between -10° and 10°
				a = (pi/180) * (r-0.5)*20
				rot = CGAffineTransform(cos(a),-sin(a),sin(a),cos(a),0,0)
				ObjCInstance(b).transform = rot
			b.TextField = tf # store tf as key attribute  needed when pressed
			if 'action' in pad_elem:
				b.action = pad_elem['action']
			else:
				b.action = key_pressed
			v.add_subview(b)
			x = x + db + dd
	y = y + db + dd

	v.width = ui.get_screen_size()[0]
	v.height = y

	# view of keyboard
	retain_global(v) # see https://forum.omz-software.com/topic/4653/button-action-not-called-when-view-is-added-to-native-view
	tfo.setInputView_(ObjCInstance(v))
	#print(dir(ObjCInstance(v)))
	
	# color of cursor and selected text
	tfo.tintColor = UIColor.redColor().colorWithAlphaComponent(0.5)
	
	# clear button
	tfo.clearButtonMode = clearButtonMode

	# comment both lines to keep undo/redo/paste BarButtons above keyboard
	if not undo_redo_pasteBarButtons:
		tfo.inputAssistantItem().setLeadingBarButtonGroups(None)
		tfo.inputAssistantItem().setTrailingBarButtonGroups(None)

if __name__ == '__main__':		
	import ui 
	tf = ui.TextField()
	SetTextFieldPad(tf)#,broken=True)
	tf.text = ''
	tf.width = 400
	tf.present('sheet')
	tf.begin_editing()
	tf.wait_modal()
	#print(tf.text)
