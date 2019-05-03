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

class BrailleKeyboardInputAccessoryViewForTextField(ui.View):
	
	def __init__(self,tf):
		self.tf = tf
		self.tfo = ObjCInstance(tf).textField() # UITextField is subview of ui.TextField
		self.multitouch_enabled = True
		self.touch_actives = {}
		self.touch_n = 0
		#self.sounds = ['piano:C3', 'piano:D3', 'piano:E3', 'piano:F3', 'piano:G3', 'piano:A3']

		# https://en.wikipedia.org/wiki/Japanese_Braille		
		self.Japanese_Braille = {
		'1':'あ',			# ⠁
		'12':'い',			# ⠃
		'14':'う',			# ⠉
		'124':'え', 		# ⠋
		'24':'お',			# ⠊
		'16':'か',			# ⠡
		'126':'き',		# ⠣
		'146':'く',		# ⠩
		'1246':'け',		# ⠫
		'246':'こ',		# ⠪
		'156':'さ',		# ⠱
		'1256':'し',		# ⠳
		'1456':'す',		# ⠹
		'12456':'せ',	# ⠻
		'2456':'そ',		# ⠺
		'156':'さ',		# ⠱
		'1256':'し',		# ⠳
		'1456':'す',		# ⠹
		'12456':'せ',	# ⠻
		'2456':'そ',		# ⠺
		'135':'た',		# ⠕
		'1235':'ち',		# ⠗
		'1345':'つ',		# ⠝
		'12345':'て',	# ⠟
		'2345':'と',		# ⠞
		'13':'な',			# ⠅
		'123':'に',		# ⠇ 
		'134':'ぬ',		# ⠍
		'1234':'ね',		# ⠏
		'234':'の',		# ⠎
		'136':'は',		# ⠥
		'1236':'ひ',		# ⠧
		'1346':'ふ',		# ⠭
		'12346':'へ',	# ⠯
		'2346':'ほ',		# ⠮
		'1356':'ま',		# ⠵
		'12356':'み',	# ⠷
		'13456':'む',	# ⠽
		'123456':'め',	# ⠿
		'23456':'も',	# ⠾
		'356':'ん',		# ⠴
		'34':'や',			# ⠌
		'346':'ゆ',		# ⠬
		'345':'よ',		# ⠜ 
		'15':'ら',			# ⠑
		'125':'り',		# ⠓
		'145':'る',		# ⠙
		'1245':'れ',		# ⠛
		'245':'ろ'	,		# ⠚
		'3':'わ',			# ⠄
		'23':'ゐ',			# ⠆
		'235':'ゑ',		# ⠖
		'35':'を'			# ⠔
		}
		# other symbols exist: sokuon, chōon, yōon, handakuten, gōyōon
		# see https://en.wikipedia.org/wiki/Japanese_Braille
		# for their dots combinations

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
			
		w,h = ui.get_screen_size()
		d = 48
			
		b_close = ui.Button()
		b_close.frame = (2,30,d,d)
		b_close.corner_radius = d/2
		b_close.background_color = (0.8,0,0,0.5)
		b_close.background_image = ui.Image.named('iob:ios7_close_outline_32')
		b_close.action = self.close_button_action
		self.add_subview(b_close)
		
		b_delete = ui.Button()
		b_delete.frame = (2,h-d-10,d,d)
		b_delete.corner_radius = 24
		b_delete.background_color = (0.8,0,0,0.5)
		b_delete.background_image = ui.Image.named('typb:Delete')
		b_delete.action = self.delete_button_action
		self.add_subview(b_delete)
		
		b_decision = ui.Button()
		b_decision.frame = (w-d-2,h-d-10,d,d)
		b_decision.corner_radius = 24
		b_decision.background_color = (0.8,0,0,0.5)
		b_decision.background_image = ui.Image.named('iob:ios7_checkmark_outline_32')
		b_decision.action = self.decision_button_action
		self.add_subview(b_decision)
		
		
		dots_label = ui.Label(name='dots')
		x = b_close.x + b_close.width + 10
		dots_label.frame = (x,b_close.y,200,b_close.height)
		dots_label.flex
		dots_label.font = ('Menlo',32)
		dots_label.text_color = (1,0,0,0.5)
		dots_label.border_color = (0.8,0,0,0.5)
		dots_label.border_width = 2
		dots_label.hidden = True
		self.add_subview(dots_label)
		
	def close_button_action(self,sender):
		self.key_pressed('return')	
		
	def delete_button_action(self,sender):	
		self.key_pressed('back space')	
		
	def decision_button_action(self,sender):	
		if self.touch_actives != {}:
			self.touch_actives = {}
			self.key_pressed(self.seq)
			self['dots'].hidden = True
			
	def save_settings(self):
		settings_str = str(self.settings) # convert dict -> str
		settings_str = keychain.set_password('Braille','settings',settings_str)		
		
	def touch_began(self,touch):
		bn = self.touch_button(touch)
		x0,y0 = touch.location
		self.touch_actives[touch.touch_id] = ((x0,y0),bn,touch.location)
		self.touch_n += 1
		if len(self.touch_actives) == 6:
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
		return #-------------------------- wait decision button pressed ------
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
		self['dots'].hidden = True
			
	def touch_button(self,touch):
		xt,yt = touch.location
		for b in self.subviews:
			if type(b) is not ui.Button:
				continue
			r = b.width/2
			x = b.x + r
			y = b.y + r
			if ((xt-x)**2+(yt-y)**2) <= r**2:
				#sound.play_effect(self.sounds[int(b.name)-1])
				return b.name
		return ''
		
	def GenDotsChar(self):
		# see https://en.wikipedia.org/wiki/Braille_Patterns
		#            dots 87654321 
		# seq = '125' -> '00010011' -> 19 -> 13base 16
		n = 40*256						# 2800 in base 16
		for c in self.seq:
			n += 2**(int(c)-1)	# ex: '5' -> 5 -> 2exp4 = 16
		return chr(n)					# '\u2813' = ⠓
		
	def touch_buttons(self):
		self.seq = ''
		for touch_id in self.touch_actives.keys():
			bn = self.touch_actives[touch_id][1]
			if bn not in self.seq:
				self.seq += bn
		self.seq = ''.join(sorted(self.seq))
		if self.seq not in self.Japanese_Braille:
			self['dots'].text = self.seq
		else:
			self['dots'].text = self.seq + ' ' + self.GenDotsChar() + ' ' + self.Japanese_Braille[self.seq]
		w,h = ui.measure_string(self['dots'].text, font=self['dots'].font)
		self['dots'].width = w
		self['dots'].hidden = False
		
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
				#speech.say(ch,'jp-JP')
								
			# set cursor
			cursor_position = self.tfo.positionFromPosition_offset_(self.tfo.beginningOfDocument(), cursor)
			self.tfo.selectedTextRange = self.tfo.textRangeFromPosition_toPosition_(cursor_position, cursor_position)
			
			
def SetBrailleKeyboardForTextField(tf):
	tfo = ObjCInstance(tf).textField() # UITextField is subview of ui.TextField
	
	# design your keyboard

	v = BrailleKeyboardInputAccessoryViewForTextField(tf)
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
	SetBrailleKeyboardForTextField(tf)
	tf.text = ''
	tf.width = 250
	tf.name = 'Japanese Braille (点字)'
	tf.present('sheet')
	tf.begin_editing()
	tf.wait_modal()
