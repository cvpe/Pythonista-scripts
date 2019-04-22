# todo:	
# - speech:
#		- bug: does not work
# - sound: 
#		- when finger arrives in circle
#		- not if move in same circle
#		- quid if several sounds together?
# - is it possible to do it as keyboard extension? for input in any app
import ast
from datetime import datetime
import keychain
from objc_util import *
#import sound
#import speech
import ui

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
		'1246':'け',
		'123456':'め'
		}

		# get/set circle positions		
		settings_str = keychain.get_password('Braille','settings')
		if settings_str:
			self.settings = ast.literal_eval(settings_str) # convert str -> dict
		else:	
			self.settings = {
				'portrait':{'1':(100,100),'2':(100,400),'3':(100,700),'4':(500,100),'5':(500,400),'6':(500,700)},
				'landscape':{'1':(100,100),'2':(100,320),'3':(100,540),'4':(700,100),'5':(700,320),'6':(700,540)}
				}
			self.save_settings()
			
		b_close = ui.Button()
		b_close.frame = (0,30,48,48)
		b_close.background_image =ui.Image.named('iob:ios7_close_outline_32')
		b_close.action = self.close_button_action
		self.add_subview(b_close)
		
	def close_button_action(self,sender):
		self.key_pressed('return')	
			
	def save_settings(self):
		settings_str = str(self.settings) # convert dict -> str
		settings_str = keychain.set_password('Braille','settings',settings_str)		
		
	def touch_began(self,touch):
		bn = self.touch_button(touch)
		x0,y0 = touch.location
		self.touch_actives[touch.touch_id] = ((x0,y0),bn,touch.location)
		self.touch_n += 1
		if self.touch_n == 6:
			self.six_fingers_touch = datetime.now()
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
		if self.touch_n > 0:
			# still at least one finger on screen
			return	
		# all fingers removed from screen
		if len(self.touch_actives) == 6:
			# 6 touches were active
			if (datetime.now() - self.six_fingers_touch).total_seconds() > 3:
				# six fingers stay on the screen at least 3 seconds
				# else, normal process for 6 dots tapped
				l = []
				for touch_id in self.touch_actives.keys():
					x,y = self.touch_actives[touch_id][2]
					l.append((x,y))
				# sort on ascending x
				l = sorted(l,key=lambda x: x[0])
				l_left  = l[0:3]
				# sort the 3 first ones (thus at left) on ascending y
				l_left  = sorted(l_left ,key=lambda x: x[1])			
				l_right = l[3:6]
				# sort the 3 others on ascending y
				l_right = sorted(l_right,key=lambda x: x[1])			
				l = l_left + l_right	
				if self.width < self.height:
					mode = 'portrait'
				else:
					mode = 'landscape'
				n = 0
				for x,y in l:
					n += 1
					bn = str(n)
					r = self[bn].width/2
					self[bn].x = x - r	
					self[bn].y = y - r	
					self.settings[mode][bn]	= (x-r,y-r)
				self.save_settings()
				self.touch_actives = {}
				self.set_needs_display()
				return	
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
			
			
def SetTextFieldPad(tf):
	
	tfo = ObjCInstance(tf).textField() # UITextField is subview of ui.TextField
	
	# design your keyboard

	v = MyView(tf)
	w,h = ui.get_screen_size()
	if w < h:
		mode = 'portrait'
	else:
		mode = 'landscape'
	r = w/12

	for i in range(1,7):
		b = ui.Button()
		b.name = str(i)
		b.background_color = (1,0,0,0.5)
		b.tint_color = (1,1,1,0.8)
		b.font = ('Academy Engraved LET',r*1.2)
		b.corner_radius = r
		b.title = b.name
		x,y = v.settings[mode][b.name]
		b.frame = (x,y,r*2,r*2)
		b.TextField = tf # store tf as key attribute  needed when pressed
		b.touch_enabled = False
		v.add_subview(b)

	v.width  = w
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
