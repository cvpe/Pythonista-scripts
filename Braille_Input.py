import ui
from objc_util import *
from Gestures import Gestures

def SetTextFieldPad(tf, pad=None, clearButtonMode=False, undo_redo_pasteBarButtons=False, textfield_did_change=None):
	if not pad:
		pad = [
		{'key':'1','x':2,'y':1},
		{'key':'2','x':2,'y':2},
		{'key':'3','x':2,'y':3},
		{'key':'4','x':5,'y':1},
		{'key':'5','x':5,'y':2},
		{'key':'6','x':5,'y':3},

		]
	Japanese_Braille = {
		'1':'あ',
		'12':'い',
		'14':'う',
		'124':'え',
		'24':'お',
		'16':'か',
		'1246':'け'
		}
	tfo = ObjCInstance(tf).textField() # UITextField is subview of ui.TextField
	
	def key_pressed(key):
			cursor = tfo.offsetFromPosition_toPosition_(tfo.beginningOfDocument(), tfo.selectedTextRange().start())
			if key == 'back space':
				if cursor > 0:
					#if tfb.text != '':
					tf.text = tf.text[:cursor-1] + tf.text[cursor:]
					cursor = cursor - 1
			elif key == 'return':
				tf.end_editing()
				return
			elif key == ' ':
				ch = ' '
				tf.text = tf.text[:cursor] + ch + tf.text[cursor:]
				cursor = cursor + 1
			elif key not in Japanese_Braille:
				return
			else:
				ch = Japanese_Braille[key]
				tf.text = tf.text[:cursor] + ch + tf.text[cursor:]
				cursor = cursor + 1
				
			if textfield_did_change:
				textfield_did_change(tfb)
				
			# set cursor
			cursor_position = tfo.positionFromPosition_offset_(tfo.beginningOfDocument(), cursor)
			tfo.selectedTextRange = tfo.textRangeFromPosition_toPosition_(cursor_position, cursor_position)
			
	def tapped(data):
		#print('tapped',data.number_of_touches)
		#print(len(data.recognizer.touches()))
		bs = []
		for t in data.recognizer.touches():
			pt = t.locationInView_(ObjCInstance(v))
			for b in v.subviews:
				r = b.width/2
				x = b.x + r
				y = b.y + r
				if ((pt.x-x)**2+(pt.y-y)**2) <= r**2:
					# touch in circle of button
					if b.name not in bs:
						# avoid two times same button
						bs.append(b.name)
		if len(bs) != data.number_of_touches:
			# at least one touch outside buttons, no way to recognize
			return
		seq = ''
		for b in sorted(bs):
			seq = seq + b
		key_pressed(seq)

	# like IOS left swipe: delete at left		
	def left_swipe_handler(data):
		key_pressed('back space')
		
	# like IOS right swipe: space		
	def right_swipe_handler(data):
		key_pressed(' ')
		
	# like IOS up swipe with 3 fingers: return
	def up_swipe_handler(data):
		key_pressed('return')

	# design your keyboard

	v = ui.View()
	v.border_color = 'red'
	v.border_width = 4
	w,h = ui.get_screen_size()
	h = h# - 350
	db = w/6 
	dd = (h-3*db)/4
	y_max = 0

	for pad_elem in pad:
		b = ui.Button()
		b.name = pad_elem['key']
		b.background_color = (1,0,0,0.5)
		b.tint_color = 'red'
		b.font = ('Academy Engraved LET',36)
		b.corner_radius = db/2
		b.title = b.name
		x = (pad_elem['x']-1)*db
		y = dd + (pad_elem['y']-1)*(db+dd)
		b.frame = (x,y,db,db)
		b.TextField = tf # store tf as key attribute  needed when pressed
		b.enabled = False
		v.add_subview(b)
		y_max = max(y_max,y+db+dd)

	v.width = ui.get_screen_size()[0]
	v.height = h
	g = Gestures()
	for n in range(1,7):
		g.add_tap(v, tapped,number_of_touches_required=n)
	g.add_swipe(v, left_swipe_handler, direction = Gestures.LEFT)
	g.add_swipe(v, right_swipe_handler, direction = Gestures.RIGHT)
	g.add_swipe(v, up_swipe_handler, direction = Gestures.UP, number_of_touches_required=3)

	# view of keyboard
	retain_global(v) # see https://forum.omz-software.com/topic/4653/button-action-not-called-when-view-is-added-to-native-view
	tfo.setInputAccessoryView_(ObjCInstance(v))	# attach accessory to textview
	#print(dir(tfo))
	
	# remove normal keyboard
	v.height = ui.get_screen_size()[1]
	vk = ui.View()
	vk.frame = (0,0,w,0)
	tfo.setInputView_(ObjCInstance(vk))
	# comment both lines to keep undo/redo/paste BarButtons above keyboard
	if not undo_redo_pasteBarButtons:
		tfo.inputAssistantItem().setLeadingBarButtonGroups(None)
		tfo.inputAssistantItem().setTrailingBarButtonGroups(None)

if __name__ == '__main__':		
	import ui 
	tf = ui.TextField()
	SetTextFieldPad(tf)
	tf.text = ''
	tf.width = 200
	tf.name = 'Japanese Braille'
	tf.present('sheet')
	tf.begin_editing()
	tf.wait_modal()
