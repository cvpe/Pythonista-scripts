# Version 0.3
# - new: use keychain to save and restore Braille dots positions
#        service=Braille account=Portrait or Landscape
#        password = '{'dot n°':(x,y),...}'
# - bug corrected: if dots not tapped together, some ones can be lost 
#                  due to reuse by system of same touch_id 
# Version 0.2
# - bug corrected: back after close (x), gray hirgana was not cleared
# - bug corrected: TextField not visible on iPhone
# - bug corrected: automatic buttons dimensions and positions for
#	                 ipad/iphone portrait/landscape Pythonista/custom keyboard
# Version 0.1
# - bug corrected: delete when cursor in TextField shows old Hirganas
# - bug corrected: tap ourside buttons was processed as invalid Braille dots
# - bug corrected: conversion button disappears if conversion gives no Kanji
# - bug corrected: hide conversion buttons if all hirganas deleted
# - bug corrected: back after close (x), closed conversion db error
# - bug corrected: back after close (x), hirganas were not cleared
# - bug corrected: ok button was even if dots combination was invalid
# - new: delete button deletes in textfield if no Hirgana in progress
# Version 0.0
# - initial draft version 
#
# still todo
# ==========
# - use 6 fingers for dots placement, 3 seconds after first dot touched
# - ask if @shinya.ta prefers horizontal scrollview with Kanjis as buttons
#		not sure if is ok with voiceover
import ast
from datetime import datetime
import keychain
import Image, ImageDraw		
import io
from   objc_util import *
import os
import plistlib
import sqlite3
import sys
import ui

# @ccc code to get Pythonista Version 
# https://github.com/cclauss/Ten-lines-or-less/blob/master/pythonista_version.py
def pythonista_version():  # 2.0.1 (201000)
	plist = plistlib.readPlist(os.path.abspath(os.path.join(sys.executable, '..', 'Info.plist')))
	return '{CFBundleShortVersionString} ({CFBundleVersion})'.format(**plist)
w = pythonista_version()		# ex: 3.3 (330012)
PythonistaVersion = float(w.split(' ')[0])
#print(PythonistaVersion)
if PythonistaVersion >= 3.3:
	import keyboard	
	
class BrailleKeyboardInputAccessoryViewForTextField(ui.View):
	def __init__(self, frame=None,*args, **kwargs):
		super().__init__(self, *args, **kwargs)
		self.background_color = 'white' 
		
		self.multitouch_enabled = True
		self.touch_actives = {}
		self.touch_n = 0
		if frame:
			self.frame=frame

		# https://en.wikipedia.org/wiki/Japanese_Braille		
		# there are hiragana syllabes
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
		
		self.conn = sqlite3.connect("HiraganaToKanji.db",check_same_thread=False)
		self.cursor = self.conn.cursor()

		# build dots buttons but bounds not yet known in init, let some delay		
		ui.delay(self.dimensions,0.1)
		
	def dimensions(self):		
		wk, hk = self.bounds.size
		#wk,hk = 756,237		# ipad mini 4
		#wk,hk = 320,237	 	# iphone 5S
		d = 48		# size of other buttons (close, delete, ...)
		db = 4
		dy = int(((hk-d)/4))
		diam = int((wk-d-7*db)/6)
		dy = int((hk - d - diam - db)/2)
		dx = int((wk - d - 6*diam)/7)
		if wk < hk:
			self.mode = 'Portrait'
		else:
			self.mode = 'Landscape'
		#print(wk,hk,r,d)
		
		# get/set circle positions	
		settings_str = None	
		settings_str = keychain.get_password('Braille',self.mode)
		if settings_str:
			self.settings = ast.literal_eval(settings_str) # convert str -> dict
		else:	
			self.settings = {}

		x = dx + d 
		y = d 
		for i in range(1,7):
			b = ui.Button()
			b.name = str(i)
			b.background_color = (1,0,0,0.5)
			b.tint_color = (1,1,1,0.8)
			b.font = ('Academy Engraved LET',diam/2)
			b.corner_radius = diam/2
			b.title = b.name
			if settings_str:
				x,y = self.settings[b.name]
			else:
				self.settings[str(i)] = (x,y)
			b.frame = (x,y,diam,diam)
			#b.TextField = tf # store tf as key attribute  needed when pressed
			b.touch_enabled = False
			self.add_subview(b)
			x = x + dx + diam
			if i < 3:
				y = y + dy
			elif i > 3:
				y = y - dy
				
		if not settings_str:
			self.save_settings()
		
		b_close = ui.Button(name='b_close')
		b_close.frame = (2,2,d,d)
		b_close.corner_radius = d/2
		b_close.background_color = (0.8,0,0,0.5)
		b_close.background_image = ui.Image.named('iob:ios7_close_outline_32')
		b_close.action = self.close_button_action
		self.add_subview(b_close)
		
		b_delete = ui.Button(name='b_delete')
		b_delete.frame = (2,hk-d-10,d,d)
		b_delete.corner_radius = 24
		b_delete.background_color = (0.8,0,0,0.5)
		b_delete.background_image = ui.Image.named('typb:Delete')
		b_delete.action = self.delete_button_action
		self.add_subview(b_delete)
					
		b_decision = ui.Button(name='b_decision')
		b_decision.frame = (wk-d-2,hk-d-10,d,d)
		b_decision.corner_radius = 24
		b_decision.background_color = (0.8,0,0,0.5)
		b_decision.background_image = ui.Image.named('iob:ios7_checkmark_outline_32')
		b_decision.action = self.decision_button_action
		b_decision.hidden = True
		self.add_subview(b_decision)
		
		dots = ui.ImageView(name='dots')
		self.dots_e = e = 3
		self.dots_d = d = 9
		self.dots_h = h = 4*e + 3*d
		dots.frame = (100,0,h,h)
		dots.hidden = True
		self.add_subview(dots)
		self.dots_xy = [(e,e),(e,e+(d+e)),(e,e+2*(d+e)),(14,e),(14,e+(d+e)),(14,e+2*(d+e))]
		
		hirganas = ui.Label(name='hirganas')
		hirganas.frame = (wk/2,2,0,32)
		hirganas.text = ''
		hirganas.font = ('Menlo',32)
		hirganas.text_color = (0,0,1,1)	
		hirganas.border_color = 'lightgray'
		hirganas.border_width = 1
		self.add_subview(hirganas)
		self.hirganas = []
		
		hirgana = ui.Label(name='hirgana')
		hirgana.frame = (0,0,32,32)
		hirgana.text = ''
		hirgana.font = ('Menlo',32)
		hirgana.text_color = 'gray'	
		hirganas.add_subview(hirgana)
		
		b_conversion = ui.Button(name='b_conversion')
		b_conversion.frame = (0,2,32,32)
		b_conversion.corner_radius = 32/2
		b_conversion.background_color = (0.8,0,0,0.5)
		b_conversion.title = '漢字'
		b_conversion.hidden = True
		#b_conversion.background_image = ui.Image.named('iob:ios7_checkmark_outline_32')
		b_conversion.action = self.conversion_button_action
		self.add_subview(b_conversion)
		
		kanjis = ui.TableView(name='kanjis')
		kanjis.frame = (0,2+32,32,hk-(2+32+2))
		kanjis.border_color = 'lightgray'
		kanjis.border_width = 1
		kanjis.corner_radius = 5
		kanjis.data_source = ui.ListDataSource(items=[])
		kanjis.data_source.font = ('Menlo',32)
		kanjis.row_height = 32
		kanjis.delegate =self
		kanjis.hidden = True
		self.add_subview(kanjis)
		
	def save_settings(self):
		settings_str = str(self.settings) # convert dict -> str
		settings_str = keychain.set_password('Braille',self.mode,settings_str)	
		
		
	def close_button_action(self,sender):
		#self.conn.close()
		if self.touch_actives != {}:
			self.touch_n = 0
			self.touch_actives = {}
		self['dots'].hidden = True
		self['kanjis'].hidden = True
		self['hirganas'].text = ''
		self['hirganas']['hirgana'].text = ''
		self.hirganas =[]
		self['b_conversion'].hidden = True
		self['hirganas'].width = 0
		if not self.custom_keyboard:
			self.tf.end_editing()	
			return
		# we simulate 'dismiss keybord key' pressed
		o = ObjCInstance(sender)	# objectivec button
		while True:
			o = o.superview()
			if 'KeyboardInputView' in str(o._get_objc_classname()):
				KeyboardInputView = o
				break	
		self.b_lowest_right = None
		self.xo = 0
		self.yo = 0
		def analyze(v):	
			for sv in v.subviews():
				if 'uibuttonlabel' in str(sv._get_objc_classname()).lower():
					x = sv.superview().frame().origin.x
					y = sv.superview().frame().origin.y
					if y > self.yo:
						self.b_lowest_right = sv
						self.xo = x
						self.yo = y
					elif y == self.yo:
						if x > self.xo:
							self.b_lowest_right = sv
							self.xo = x
							self.yo = y			
				ret = analyze(sv)
		analyze(KeyboardInputView)

		b = self.b_lowest_right.superview()
		if 'uibutton' in str(b._get_objc_classname()).lower() or 'ckbkeybutton' in str(b._get_objc_classname()).lower():
			# simulate press the button	
			UIControlEventTouchUpInside = 255
			b.sendActionsForControlEvents_(UIControlEventTouchUpInside)
		
	def delete_button_action(self,sender):

		if len(self.hirganas) > 0:
			# Hirhanas in progress
			# process to delete last hirgana
			# one hirganas uses a variable number of characters, thus not easy to remove it at right of a text
			del self.hirganas[-1]
			t = ''
			for ch in self.hirganas:
				t += ch
			self['hirganas'].text = t
			self.draw_hirganas()
		else:		
			# process to delete in textfield
			if self.custom_keyboard:	
				keyboard.backspace(times=1)
			else:
				cursor = self.tfo.offsetFromPosition_toPosition_(self.tfo.beginningOfDocument(), self.tfo.selectedTextRange().start())
				if cursor > 0:
					self.tf.text = self.tf.text[:cursor-1] + self.tf.text[cursor:]
					cursor = cursor - 1
				# set cursor
				cursor_position = self.tfo.positionFromPosition_offset_(self.tfo.beginningOfDocument(), cursor)
				self.tfo.selectedTextRange = self.tfo.textRangeFromPosition_toPosition_(cursor_position, cursor_position)
		
	def decision_button_action(self,sender):	
		if self.touch_actives != {}:
			self.touch_n = 0
			self.touch_actives = {}
			self.key_pressed(self.seq)
			self['dots'].hidden = True
			self['b_decision'].hidden = True
			
	def conversion_button_action(self,sender):
		t = self['hirganas'].text
		self.cursor.execute(
			'select hiragana, kanji from Hiragana_to_Kanji where hiragana = ?',
			(t,))
		items = []
		w_max = 0
		for row in self.cursor:
			t = row[1]
			w,h = ui.measure_string(t, font=self['kanjis'].data_source.font)
			w_max = max(w_max,w+50)
			items.append(t)
		if len(items) == 0:
			return
		sender.hidden = True
		self['kanjis'].data_source.items = items
		self['kanjis'].x = (self.width - w_max)/2
		self['kanjis'].width = w_max
		self['kanjis'].hidden = False
		
	def tableview_did_select(self, tableview, section, row):
		t = tableview.data_source.items[row]
		# insert kanji
		if self.custom_keyboard:	
			keyboard.insert_text(t)	
		else:	
			cursor = self.tfo.offsetFromPosition_toPosition_(self.tfo.beginningOfDocument(), self.tfo.selectedTextRange().start())
			self.tf.text = self.tf.text[:cursor] + t + self.tf.text[cursor:]
			cursor = cursor + 1
			# set cursor
			cursor_position = self.tfo.positionFromPosition_offset_(self.tfo.beginningOfDocument(), cursor)
			self.tfo.selectedTextRange = self.tfo.textRangeFromPosition_toPosition_(cursor_position, cursor_position)
		self['kanjis'].hidden = True
		self['hirganas'].text = ''
		self.hirganas =[]
		self['b_conversion'].hidden = True
		self['hirganas'].width = 0
		
	def touch_began(self,touch):
		bn = self.dot_touched(touch)
		if bn == '':
			return
		x0,y0 = touch.location
		self.touch_actives[touch.touch_id] = ((x0,y0),bn,touch.location)
		self.touch_n += 1
		if len(self.touch_actives) == 6:
			self.six_fingers_touch = datetime.now()
		self.dots_touched()
		
	def touch_moved(self,touch):
		if touch.touch_id not in self.touch_actives:
			return
		bn = self.dot_touched(touch)
		x0,y0 = self.touch_actives[touch.touch_id][0]
		self.touch_actives[touch.touch_id] = ((x0,y0),bn,touch.location)
		self.dots_touched()
		
	def touch_ended(self,touch):
		if touch.touch_id not in self.touch_actives:
			return
		x ,y  = touch.location
		self.touch_n -= 1			# but keep dict of touches
		# change key in self.touch_actives because if a new touch
		# begins, its touch_id could be reused, thus the same
		new_key = 'T'+str(len(self.touch_actives))+str(touch.touch_id)
		self.touch_actives[new_key] = self.touch_actives[touch.touch_id]
		del self.touch_actives[touch.touch_id]
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
		return #-------------------------- wait decision button pressed ------
			
	def dot_touched(self,touch):
		xt,yt = touch.location
		for b in self.subviews:
			if type(b) is not ui.Button:
				continue
			if b.name[0] == 'b':	# not dots button
				continue
			r = b.width/2
			x = b.x + r
			y = b.y + r
			if ((xt-x)**2+(yt-y)**2) <= r**2:
				return b.name
		return ''
		
	def draw_dots(self):	
		im = Image.new("RGB", (self.dots_h,self.dots_h), 'white')
		draw = ImageDraw.Draw(im)
		for c in range(1,7):
			x,y = self.dots_xy[c-1]
			draw.ellipse((x,y,x+10,y+10),'lightgray','lightgray')
		for ch in self.seq:
			c = int(ch)
			x,y = self.dots_xy[c-1]
			draw.ellipse((x,y,x+10,y+10),'red','red')
		del draw
		with io.BytesIO() as fp:
			im.save(fp, 'PNG')
			self['dots'].image = ui.Image.from_data(fp.getvalue())		
			self['dots'].hidden = False
		
	def dots_touched(self):
		self.seq = ''
		for touch_id in self.touch_actives.keys():
			bn = self.touch_actives[touch_id][1]
			if bn not in self.seq:
				self.seq += bn
		self.seq = ''.join(sorted(self.seq))
		
		# display touched dots, symbol, Hirgana
		self.draw_dots()
		if self.seq not in self.Japanese_Braille:
			temp_hirgana = '?'
		else:
			temp_hirgana = self.Japanese_Braille[self.seq]
			self['b_decision'].hidden = False
		
		# display not yet confirmed hirgana in hirganas field
		w1,h = ui.measure_string(self['hirganas'].text, font=self['hirganas'].font)
		w2,h = ui.measure_string(temp_hirgana, font=self['hirganas']['hirgana'].font)
		self['hirganas']['hirgana'].text = temp_hirgana
		self['hirganas']['hirgana'].x = w1
		self['hirganas']['hirgana'].width = w2
		self['dots'].x = self['hirganas'].x + self['hirganas']['hirgana'].x 
		self['dots'].y = self['hirganas'].y + self['hirganas'].height
		self['hirganas'].width = w1 + w2
		
	def key_pressed(self,key):
		self['hirganas']['hirgana'].width = 0
		if key in self.Japanese_Braille:
			ch = self.Japanese_Braille[key]
			self.hirganas.append(ch)
			self['hirganas'].text += ch
			self.draw_hirganas()
			
	def draw_hirganas(self):
		w,h = ui.measure_string(self['hirganas'].text, font=self['hirganas'].font)
		self['hirganas'].width = w
		self['hirganas'].x = (self.width - w)/2
		self['b_conversion'].x = self['hirganas'].x - self['b_conversion'].width
		self['b_conversion'].hidden = len(self.hirganas) == 0
		
	def layout(self):
		#print(self.bounds.size)
		pass
		
def main():
	if PythonistaVersion >= 3.3:
		if keyboard.is_keyboard():
			v = BrailleKeyboardInputAccessoryViewForTextField()
			v.custom_keyboard = True
			keyboard.set_view(v, 'expanded')
			return
	# Before Pythonista supporting keyboard or run in Pythonista app
	w,h = ui.get_screen_size()
	mv = ui.View()
	mv.name = 'Test keyboard in Pythonista'
	mv.background_color = 'white'
	tf = ui.TextField()
	tf.text = ''
	tf.frame = (2,2,w-4,32)
	mv.add_subview(tf)
	tfo = ObjCInstance(tf).textField() # UITextField is subview of ui.TextField
	kv = ui.View()

	kv.frame = (0,0,w,min(363,h*(3/5)))
	unused = ' unused, only to simulate height of custom keyboard with Pythonista 3.3'
	kv.add_subview(ui.Label(frame=(0,0,w,kv.height/7),text=unused))
	kv.background_color = 'lightgray'

	frame = (0,kv.height/7,w,kv.height*5/7)
	v = BrailleKeyboardInputAccessoryViewForTextField(frame=frame)
	v.custom_keyboard = False
	kv.add_subview(v)
	kv.add_subview(ui.Label(frame=(0,v.y+v.height,w,kv.height/7),text=unused))
	
	tfo.setInputView_(ObjCInstance(kv))
	v.tf = tf
	v.tfo = ObjCInstance(tf).textField() # UITextField is subview of ui.TextField
	
	# view of keyboard
	retain_global(v) # see https://forum.omz-software.com/topic/4653/button-action-not-called-when-view-is-added-to-native-view
	
	#  remove undo/redo/paste BarButtons above standard keyboard
	tfo.inputAssistantItem().setLeadingBarButtonGroups(None)
	tfo.inputAssistantItem().setTrailingBarButtonGroups(None)

	mv.present('full_screen')
	tf.begin_editing()
	mv.wait_modal()

if __name__ == '__main__':
	main()
