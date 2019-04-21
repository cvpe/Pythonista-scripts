# todo:	
# - bug: swipe 3 fingers up not ok in landscape mode
# - position of circles:
#		- way to set each or all together?
#		- store in keychain
# - speech:
#		- bug: does not work
# - sound: 
#		- when finger arrives in circle
#		- not if move in same circle
#		- quid if severaal sounds together?
# - is it possible to do it as keyboard extension? for input in any app
import ui
from objc_util import *
#import speech
#import sound

class MyView(ui.View):
	
	def __init__(self,tf):
		self.tf = tf
		self.tfo = ObjCInstance(tf).textField() # UITextField is subview of ui.TextField
		self.multitouch_enabled = True
		self.touch_actives = {}
		self.touch_n = 0
		#self.sounds = ['piano:C3', 'piano:D3', 'piano:E3', 'piano:F3', 'piano:G3', 'piano:A3']
		
		self.Japanese_Braille = {
		'1':'あ',
		'12':'い',
		'14':'う',
		'124':'え',
		'24':'お',
		'16':'か',
		'1246':'け'
		}
		
	def touch_began(self,touch):
		bn = self.touch_button(touch)
		x0,y0 = touch.location
		self.touch_actives[touch.touch_id] = ((x0,y0),bn,touch.location)
		self.touch_n += 1
		self.touch_buttons()
		
	def touch_moved(self,touch):
		if touch.touch_id not in self.touch_actives:
			return
		bn = self.touch_button(touch)
		x0,y0 = self.touch_actives[touch.touch_id][0]
		self.touch_actives[touch.touch_id] = ((x0,y0),bn,touch.location)
		self.touch_buttons()
		
	def touch_ended(self,touch):
		x ,y  = touch.location
		if len(self.touch_actives) == 1:
			# only one touch is active
			x0,y0 = self.touch_actives[touch.touch_id][0]
			#self.tf.name = str(x-x0)+','+str(y-y0)
			if (x - x0) >= 200 and abs(y - y0) <= 100:
				# swipe from left to right: insert space
				self.touch_n = 0
				self.touch_actives = {}
				self.key_pressed(' ')
				return
			elif (x0 - x) >= 200 and abs(y - y0) <= 100:
				# swipe from right to left: left delete
				self.touch_n = 0
				self.touch_actives = {}
				self.key_pressed('back space')
				return
		elif len(self.touch_actives) == 3:
			# 3 touches were active
			up = 0
			for touch_id in self.touch_actives.keys(): 
				x0,y0 = self.touch_actives[touch_id][0]
				x ,y  = self.touch_actives[touch_id][2]
				if (y0 - y) >= 200 and abs(x - x0) <= 100:
					# swipe from bottom to top
					up += 1
			if up == 3:
				# swipe 3 fingers up: return
				self.touch_n = 0
				self.touch_actives = {}
				self.key_pressed('return')
				return
		self.touch_n -= 1			# but keep dict of touches
		if self.touch_n == 0:	# all fingers removed from screen
			self.touch_actives = {}
			self.key_pressed(self.seq)
			
	def touch_button(self,touch):
		xt,yt = touch.location
		for b in self.subviews:
			r = b.width/2
			x = b.x + r
			y = b.y + r
			if ((xt-x)**2+(yt-y)**2) <= r**2:
				#sound.play_effect(self.sounds[int(b.name)-1])
				return b.name
		return ''
		
	def touch_buttons(self):
		self.seq = ''
		for touch_id in self.touch_actives.keys():
			bn = self.touch_actives[touch_id][1]
			if bn not in self.seq:
				self.seq += bn
		self.seq = ''.join(sorted(self.seq))
		if self.seq not in self.Japanese_Braille:
			self.tf.name = self.seq
		else:
			self.tf.name = self.seq + '=' + self.Japanese_Braille[self.seq]
		
	def key_pressed(self,key):
			cursor = self.tfo.offsetFromPosition_toPosition_(self.tfo.beginningOfDocument(), self.tfo.selectedTextRange().start())
			if key == 'back space':
				if cursor > 0:
					self.tf.text = self.tf.text[:cursor-1] + self.tf.text[cursor:]
					cursor = cursor - 1
			elif key == 'return':
				self.tf.end_editing()
				return
			elif key == ' ':
				ch = ' '
				self.tf.text = self.tf.text[:cursor] + ch + self.tf.text[cursor:]
				cursor = cursor + 1
			elif key not in self.Japanese_Braille:
				return
			else:
				ch = self.Japanese_Braille[key]
				self.tf.text = self.tf.text[:cursor] + ch + self.tf.text[cursor:]
				cursor = cursor + 1
				#speech.say(ch)#,'jp-JP')
								
			# set cursor
			cursor_position = self.tfo.positionFromPosition_offset_(self.tfo.beginningOfDocument(), cursor)
			self.tfo.selectedTextRange = self.tfo.textRangeFromPosition_toPosition_(cursor_position, cursor_position)
			
			
def SetTextFieldPad(tf, pad=None, clearButtonMode=False):
	if not pad:
		pad = [
		{'key':'1','x':2,'y':1},
		{'key':'2','x':2,'y':2},
		{'key':'3','x':2,'y':3},
		{'key':'4','x':5,'y':1},
		{'key':'5','x':5,'y':2},
		{'key':'6','x':5,'y':3},
		]
	tfo = ObjCInstance(tf).textField() # UITextField is subview of ui.TextField
	
	# design your keyboard

	v = MyView(tf)
	w,h = ui.get_screen_size()
	h = h
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
		b.touch_enabled = False
		v.add_subview(b)
		y_max = max(y_max,y+db+dd)

	v.width = ui.get_screen_size()[0]
	v.height = h

	# view of keyboard
	retain_global(v) # see https://forum.omz-software.com/topic/4653/button-action-not-called-when-view-is-added-to-native-view
	tfo.setInputAccessoryView_(ObjCInstance(v))	# attach accessory to textview
	#print(dir(tfo))
	
	# remove standard keyboard
	v.height = ui.get_screen_size()[1]
	vk = ui.View()
	vk.frame = (0,0,w,0)
	tfo.setInputView_(ObjCInstance(vk))
	#  remove undo/redo/paste BarButtons above standard keyboard
	tfo.inputAssistantItem().setLeadingBarButtonGroups(None)
	tfo.inputAssistantItem().setTrailingBarButtonGroups(None)

if __name__ == '__main__':		
	import ui 
	tf = ui.TextField()
	SetTextFieldPad(tf)
	tf.text = ''
	tf.width = 250
	tf.name = 'Japanese Braille (点字)'
	tf.present('sheet')
	tf.begin_editing()
	tf.wait_modal()
