''' 
version **00.62** is available with

modifications
  - When Katakana key tapped, read aloud "カタカナが選択されました" with 1.5 sec delay
    
corrections
  - 
    
[https://raw.githubusercontent.com/cvpe/Pythonista-scripts/master/Emojis_Keyboard.py](https://raw.githubusercontent.com/cvpe/Pythonista-scripts/master/Emojis_Keyboard.py)


todo

  - remove whole Katakana sub-keyboard code
		
	- If you turn on the keyboard and tap the first button (which is the same 
		for all buttons), there is a fairly high probability that the app will crash.
		
	- ask: do you use the round arrow key to get internet definition?
	- ask: remove all  process of English sentences containing the Kanji 
	       in the Kanjis list
	       *** check first if seems used ***
	- ask: HiraganaToKanji.db May 2019, could be updated with 20% more
	- ask: .txt file for fixed phrases
	- ask= .txt file for emojis
	- ask: .txt file for symbols
		
'''
import console
import keyboard
import ui
from objc_util import *
import clipboard
#import speech
import sys
from gestures import *
import time
import sqlite3

version = '00.62'

# use ObjectiveC speech: start =================================================
AVSpeechUtterance=ObjCClass('AVSpeechUtterance')
AVSpeechSynthesizer=ObjCClass('AVSpeechSynthesizer')
AVSpeechSynthesisVoice=ObjCClass('AVSpeechSynthesisVoice')

voices=AVSpeechSynthesisVoice.speechVoices()
voice_jp = -1
voice_en = -1
for i in range(0,len(voices)):
	#print(i,voices[i].language(),voices[i].identifier())
	if 'ja-JP' in str(voices[i].identifier()): 
		# if u have Japanese Siri voice, replace from 'ja-JP' to 'siri_O-ren_ja-JP'
		if voice_jp < 0:
			voice_jp = i
	elif 'en-GB' in str(voices[i].identifier()) and 'siri' in str(voices[i].identifier()): 
		if voice_en < 0:
			voice_en = i
		
synthesizer=AVSpeechSynthesizer.new()

def speech_say(t,language='ja-JP'):
	utterance=AVSpeechUtterance.speechUtteranceWithString_(t)
	utterance.rate = 0.5
	utterance.useCompactVoice=False
	if language == 'ja-JP':
		utterance.voice = voices[voice_jp]
	else:
		utterance.voice = voices[voice_en]
	synthesizer.speakUtterance_(utterance)
# use ObjectiveC speech: end ===================================================
			  
class MyView(ui.View):
	def __init__(self, *args, **kwargs):
		super().__init__(self, *args, **kwargs)
		self.background_color = 'lightgray'
		#self.border_width = 1
		
		# bounds not yet known in init, let some delay		
		ui.delay(self.dimensions,0.1)
				
	def b_up_action(self, sender):
		# locate cursor at begin of current line
		t_bef,t_aft = keyboard.get_input_context()
		if t_bef:
			l = t_bef.rfind('\n')
			t_bef = t_bef[l+1:] # works also if l=-1 -> l+1=0
			l = len(t_bef)
			keyboard.move_cursor(-l)
			
	def b_left_action(self, sender):
		keyboard.move_cursor(-1)
		
	def b_right_action(self, sender):
		keyboard.move_cursor(+1)
				
	def b_down_action(self, sender):
		# locate cursor at end of current line
		t_bef,t_aft = keyboard.get_input_context()
		if t_aft:
			l = t_aft.find('\n')
			if l >= 0:
				t_aft = taft[:l]
		else:
			t_aft = ''
		l = len(t_aft)
		keyboard.move_cursor(l)
			
	def b_delete_action(self, sender):
		if self.temp_kanji != '':
			self.set_temp_kanji_lbl(self.temp_kanji[:-1])
		else:
			keyboard.backspace(times=1)	
	
	def b_return_action(self, sender):
		if self.temp_kanji != '':
			keyboard.insert_text(self.temp_kanji)	
			self.set_temp_kanji_lbl('')			
		else:
			keyboard.insert_text('\n')		
		
	def b_read_to_cursor_action(self, sender):
		# read from begin of line to cursor
		t_bef,t_aft = keyboard.get_input_context()
		l = t_bef.rfind('\n')
		t_bef = t_bef[l+1:] # works also if l=-1 -> l+1=0
		self.read_t = t_bef
		#speech_say(self.read_t,language='en-GB')
		ui.delay(self.read_text,1.5)		
		
	def b_read_all_action(self, sender):
		# read current line
		t_bef,t_aft = keyboard.get_input_context()
		l = t_bef.rfind('\n')
		t_bef = t_bef[l+1:] # works also if l=-1 -> l+1=0
		if t_aft:
			l = t_aft.find('\n')
			if l >= 0:
				t_aft = taft[:l]
		else:
			t_aft = ''
		self.read_t = t_bef + t_aft
		#speech_say(self.read_t,language='en-GB')
		ui.delay(self.read_text,1.5)	
		
	def read_text(self):
		try:
			speech_say(self.read_t)
			#speech.say(self.read_t,'jp-JP')
		except Exception as e:
			pass
		
	def long_press_handler(self, data):
		#print('long_press')
		b = data.view
		xp,yp = data.location
		xp,yp = ui.convert_point(point=(xp,yp), from_view=b, to_view=b.superview)
		#print(b.name)
		if data.state == 1:
			# start long press
			b.background_color = 'blue'
			# resize flicking key bigger at same center position
			b.original_frame = b.frame
			x,y,w,h = b.frame
			xc = x+w/2
			yc = y+h/2
			w *= 1.0
			h *= 1.0
			x = xc - w/2
			y = yc - h/2
			b.frame = x,y,w,h
			b.bring_to_front()
			#speech.say(sv.title,'jp-JP')
			sub_outside = 0
			self.flicked = [b] # array of flicking key )its subflicked keys
			for sv in b.superview.subviews:
				if isinstance(sv, ui.Button):
					if sv.action == None and sv.assoc == b:
						sv.hidden = False
						# resize flicked sub-key bigger at same relative position
						sv.original_frame = sv.frame
						x1,y1,w1,h1 = sv.frame
						xc1 = x1+w1/2
						yc1 = y1+h1/2
						if xc1 < xc:
							# flicked sub-key at left
							x1 = x - w - self.dd
							y1 = y
						elif xc1 > xc:
							# flicked sub-key at right
							x1 = x + w + self.dd
							y1 = y
						elif yc1 < yc:
							# flicked sub-key at top
							y1 = y - h - self.dd
							x1 = x
						elif yc1 > yc:
							# flicked sub-key at bottom
							y1 = y + h + self.dd
							x1 = x
						if y1 < 0:
							sub_outside = y1
						elif (y1+h)> b.superview.height:
							sub_outside = (y1+h)-b.superview.height
						sv.frame = x1,y1,w,h
						sv.bring_to_front()
						self.flicked.append(sv)
					elif sv != b:
						sv.background_color = 'lightgray'
			if sub_outside != 0:
				b.y += -sub_outside
				for sv in b.superview.subviews:
					if isinstance(sv, ui.Button):
						if sv.action == None and sv.assoc == b:
							sv.y += -sub_outside
		elif data.state == 2:
			# move long press
			# if location in one of original + 4 new, set it blue
			for sv in self.flicked:
				if xp >= sv.x and xp <= (sv.x + sv.width) and yp >= sv.y and yp <= (sv.y + sv.height):
					if sv.background_color != (0.0, 0.0, 1.0, 1.0): # not blue
						sv.background_color = 'blue'	
						if sv.title[0] in self.accessibility_labels:
							#speech_say(self.accessibility_labels[sv.title[0]])
							self.read_t = self.accessibility_labels[sv.title[0]]
						else:
							#speech_say(sv.title)
							self.read_t = sv.title
						ui.delay(self.read_text,0.01)	
						#ObjCInstance(sv).isAccessibilityElement = True
					else:
						# same key is already blue, stop loop, 
						# other are also already white
						break
				else:
					if sv.background_color != (1.0, 1.0, 1.0, 1.0): # not white
						sv.background_color = 'white'							
		elif data.state == 3:
			# end long press
			b.background_color = 'white'
			key_sel = False
			for sv in b.superview.subviews:
				if isinstance(sv, ui.Button):
					if (sv.action == None and sv.assoc == b) or sv == b:
						if xp >= sv.x and xp <= (sv.x + sv.width) and yp >= sv.y and yp <= (sv.y + sv.height):
							key_sel = True
							self.typeChar(sv)	
							speech_say(sv.title)
							#continue # only to test if we have released the finger in a blue key	
					if sv.action == None and sv.assoc == b:
						sv.background_color = 'white'		
						#ObjCInstance(sv).isAccessibilityElement = True					
						sv.hidden = True
						sv.frame = sv.original_frame
					elif sv != b:
						sv.background_color = 'white'
			b.frame = b.original_frame
			if not key_sel:
				# no key selected, warn the user?
				#speech_say('no key selected',language='en-GB')
				speech_say( "キーが選択されていません")							
						
	def sub_keys(self, x,y,keys,b,super=None):	
		dxdy = [(-1,0), (0,-1), (+1,0), (0,+1)]
		for i in range(4):
			if keys[i] != ' ':
				xx = x + dxdy[i][0] * (self.dx+self.dd)
				yy = y + dxdy[i][1]	* (self.dy+self.dd)
				title = keys[i]
				if title == u'\u309C':
					title += ' '
				bb = self.make_button(xx,yy,self.dx,self.dy,title, None, super=super)
				bb.hidden = True
				bb.assoc = b
				#if len(title) == 1:
				#	bb.font = ('.SFUIText', self.dy-2)
				#ObjCInstance(bb).isAccessibilityElement = True
				#ObjCInstance(bb).accessibilityLabel = keys[i]
			
	def hide_all(self):
		for k in self.vs.keys():
			self.vs[k].hidden = True
				
	def b_hiragana_action(self, sender):
		self.hide_all()
		self.v_hiragana.hidden = False
		
	def b_katakana_action(self, sender):
		# katakana is no more a sub-keyboard but a conversion of temporary storage
		if self.temp_kanji != '':
			t = ''
			for c in self.temp_kanji:
				if c in self.hirgana_to_katakana:
					t += self.hirgana_to_katakana[c]
				else:
					t += c
			keyboard.insert_text(t)
			self.set_temp_kanji_lbl('')	
			self.read_t = 'カタカナが選択されました'
			ui.delay(self.read_text,1.5)
		return
				
		self.hide_all()
		self.v_katakana.hidden = False
				
	def b_alpha_action(self, sender):
		if self.temp_kanji != '':
			keyboard.insert_text(self.temp_kanji)	
			self.set_temp_kanji_lbl('')			
		self.hide_all()
		self.v_alpha.hidden = False
		self.caps = True
		self.caps_lock = False
		self.capsKey('unused')
		
	def b_digit_action(self, sender):
		self.hide_all()
		self.v_digit.hidden = False
		
	def b_emoji_action(self, sender):
		if self.temp_kanji != '':
			keyboard.insert_text(self.temp_kanji)	
			self.set_temp_kanji_lbl('')			
		self.hide_all()
		self.v_emoji.hidden = False
		
	def b_symbol_action(self, sender):
		if self.temp_kanji != '':
			keyboard.insert_text(self.temp_kanji)	
			self.set_temp_kanji_lbl('')			
		self.hide_all()
		self.v_symbol.hidden = False
		
	def b_fixed_phrases_action(self, sender):
		if self.temp_kanji != '':
			keyboard.insert_text(self.temp_kanji)	
			self.set_temp_kanji_lbl('')			
		self.hide_all()
		self.v_phrases.hidden = False
		
	def make_button(self,x,y,dx,dy,title,action, super=None):
		b = ui.Button()
		b.frame = (x,y,dx,dy)
		b.background_color = 'white'
		b.border_width = 1
		b.corner_radius = self.dy/4
		b.title = title
		if '\n' in title:
			bo = ObjCInstance(b)
			for sv in bo.subviews(): 
				if hasattr(sv,'titleLabel'):
					tl = sv.titleLabel()
					tl.numberOfLines = 0
		self.set_font_size(b)	
		b.action = action
		if super:
			super.add_subview(b)
		else:
			self.add_subview(b)
		b.assoc = None
		return b
		
	def dimensions(self):				
		w,h = self.bounds.size
			
		dd = 0
		nx = 7
		dx = (w - (nx+1)*dd)/nx
		
		ny = 5
		dy = (h - (ny+1)*dd)/ny
		
		dyk = dy * 2/3
		#dyk = 12
		h = h - dd - dyk
		ny = 4
		dy = (h - (ny+1)*dd)/ny
		
		self.ny = ny
		self.dx = dx
		self.dy = dy
		self.dd = dd
		
		self.temp_kanji_lbl = ui.Label()
		self.temp_kanji_lbl.frame = (self.dd,self.dd,self.width-2*self.dd,dyk)
		self.temp_kanji_lbl.font = ('Arial',dyk)
		self.temp_kanji_lbl.text = ''
		#self.temp_kanji_lbl.alignment = ui.ALIGN_CENTER
		self.temp_kanji_lbl.alignment = ui.ALIGN_LEFT	#========あかさか
		self.temp_kanji_lbl.text_color = 'red'
		self.add_subview(self.temp_kanji_lbl)

		self.v_hiragana = ui.View()
		self.v_hiragana.background_color = self.background_color
		#self.v_hiragana.frame = (0,dyk,w,h)
		self.v_hiragana.frame = (0,0,w,h+dyk)	#=========
		self.v_hiragana.hidden = False
		self.add_subview(self.v_hiragana)
		self.v_katakana = ui.View()
		self.v_katakana.background_color = self.background_color
		self.v_katakana.frame = self.v_hiragana.frame
		self.v_katakana.hidden = True
		#self.add_subview(self.v_katakana)
		self.v_alpha = ui.View()
		self.v_alpha.background_color = self.background_color
		self.v_alpha.frame = self.v_hiragana.frame
		self.v_alpha.hidden = True
		self.add_subview(self.v_alpha)
		self.v_digit = ui.View()
		self.v_digit.background_color = self.background_color
		self.v_digit.frame = self.v_hiragana.frame
		self.v_digit.hidden = True
		self.add_subview(self.v_digit)
		self.v_emoji = ui.View()
		self.v_emoji.background_color = self.background_color
		self.v_emoji.frame = self.v_hiragana.frame
		self.v_emoji.hidden = True
		self.add_subview(self.v_emoji)
		self.v_symbol = ui.View()
		self.v_symbol.background_color = self.background_color
		self.v_symbol.frame = self.v_hiragana.frame
		self.v_symbol.hidden = True
		self.add_subview(self.v_symbol)
		self.v_phrases = ui.View()
		self.v_phrases.background_color = self.background_color
		self.v_phrases.frame = self.v_hiragana.frame
		self.v_phrases.hidden = True
		self.add_subview(self.v_phrases)
		
		self.temp_kanji_lbl.bring_to_front()	#=========


		self.vs = {'hiragana':self.v_hiragana, 'alpha':self.v_alpha, 'digit':self.v_digit, 'emoji':self.v_emoji, 'katakana':self.v_katakana, 'symbol':self.v_symbol, 'phrases':self.v_phrases}

		'''		

		# https://www.nhk.or.jp/lesson/fr/letters/kanji.html
		
		# https://www.ssec.wisc.edu/~tomw/java/unicode.html#x3040
		
		# https://en.wikipedia.org/wiki/List_of_Japanese_typographic_symbols#Punctuation_marks

		'''	
		keyboards = {'hiragana':[
			[0,0,'文頭',self.b_up_action,''],		# begin of line	
			[1,0,'⬅️',self.b_left_action,''],
			[2,0,'あ',self.typeChar,'いうえお'],					
			[3,0,'か',self.typeChar,'きくけこ'],			
			[4,0,'さ',self.typeChar,'しすせそ'],
			[5,0,'➡️',self.b_right_action,''],	
			[6,0,'文末',self.b_down_action,''],	# end of line
			
			[0,1,'ABC', self.b_alpha_action,''],			
			[1,1,'read to\ncursor',self.b_read_to_cursor_action,''],	
			[2,1,'た',self.typeChar,'ちつてと'],			
			[3,1,'な',self.typeChar,'にぬねの'],
			[4,1,'は',self.typeChar,'ひふへほ'],	
			[5,1,'read\nall',self.b_read_all_action,''],
			[6,1,'左削除',self.b_delete_action,''],		

			[0,2,'数字', self.b_digit_action,''],
			[1,2,'記号', self.b_symbol_action,''],
			[2,2,'ま',self.typeChar,'みむめも'],			
			[3,2,'や',self.typeChar,'「ゆ」よ'],			
			[4,2,'ら',self.typeChar,'りるれろ'],	
			[5,2,'定型文',self.b_fixed_phrases_action,''],					
			[6,2,'漢字',self.b_kanji_action,''], 

			[0,3,'絵文字', self.b_emoji_action,''],
			[1,3,'小文字',self.smallKey,''],
			[2,3,u'\u309B'+'濁点',self.typeChar,u'\u309C    '],	
			[3,3,'わ',self.typeChar,'をんー '],	
			[4,3,"、。",self.typeChar,"。？！ "], 
			[5,3,'カタカナ', self.b_katakana_action,''],
			[6,3,'return',self.b_return_action,'']				
			],

			'katakana':[
 			[0,0,'文頭',self.b_up_action,''],		# begin of line	
			[1,0,'⬅️',self.b_left_action,''],
			[2,0,'ア',self.typeChar,'イウエオ'],
			[3,0,'カ',self.typeChar,'キクケコ'],			
			[4,0,'サ',self.typeChar,'シスセソ'],
			[5,0,'➡️',self.b_right_action,''],	
			[6,0,'文末',self.b_down_action,''],	# end of line
			
			[0,1,'ABC', self.b_alpha_action,''],			
			[1,1,'read to\ncursor',self.b_read_to_cursor_action,''],	
			[2,1,'タ',self.typeChar,'チツテト'],						
			[3,1,'ナ',self.typeChar,'ニヌネノ'],
			[4,1,'ハ',self.typeChar,'ヒフヘホ'],						
			[5,1,'read\nall',self.b_read_all_action,''],
			[6,1,'左削除',self.b_delete_action,''],		
			
			[0,2,'数字', self.b_digit_action,''],
			[1,2,'平仮名', self.b_hiragana_action,''],
			[2,2,'マ',self.typeChar,'ミムメモ'],						
			[3,2,'ヤ',self.typeChar,'「ユ」ヨ'],
			[4,2,'ラ',self.typeChar,'リルレロ'],				

			[0,3,'絵文字', self.b_emoji_action,''],
			[1,3,'小文字',self.smallKey,''],
			[2,3,u'\u309B'+'濁点',self.typeChar,u'\u309C    '],	
			[3,3,'ワ',self.typeChar,'ヲンー '],		
			[4,3,"、。",self.typeChar,"。？！ "], 	
			[5,3,'記号', self.b_symbol_action,''],
			[6,3,'return',self.b_return_action,'']				
			],
			
			'alpha':[
			#[0,0,'カタカナ', self.b_katakana_action,''],
			[1,0,'(',self.typeChar,''],
			[2,0,'@',self.typeChar,''],
			[3,0,'a',self.typeChar,'bc  '],
			[4,0,'d',self.typeChar,'ef  '],
			[5,0,')',self.typeChar,''],

			[0,1,'平仮名', self.b_hiragana_action,''],			
			[1,1,'&',self.typeChar,''],	
			[2,1,'g',self.typeChar,'hi  '],
			[3,1,'j',self.typeChar,'kl  '],
			[4,1,'m',self.typeChar,'no  '],
			[5,1,'#',self.typeChar,''],	
			[6,1,'左削除',self.b_delete_action,''],	

			[0,2,'数字', self.b_digit_action,''],
			[1,2,'CapsLock',self.capsLock,''],			
			[2,2,'p',self.typeChar,'qrs '],
			[3,2,'t',self.typeChar,'uv  '],
			[4,2,'w',self.typeChar,'xyz '],
			[5,2,'.',self.typeChar,''],	

			[0,3,'絵文字', self.b_emoji_action,''],		
			[1,3,'Shift',self.capsKey,''],
			[2,3,'!',self.typeChar,''],	
			[3,3,'?',self.typeChar,''],	
			[4,3,'/',self.typeChar,''],	
			[5,3,'space',self.b_space_action,''],	
			[6,3,'return',self.b_return_action,'']				
			],
			
			'digit':[
			#[0,0,'カタカナ', self.b_katakana_action,''],
			[1,0,'¥',self.typeChar,''],
			[2,0,'1',self.typeChar,''],
			[3,0,'2',self.typeChar,''],
			[4,0,'3',self.typeChar,''],
			[5,0,'(',self.typeChar,''],

			[0,1,'ABC', self.b_alpha_action,''],
			[1,1,'%',self.typeChar,''],		
			[2,1,'4',self.typeChar,''],
			[3,1,'5',self.typeChar,''],
			[4,1,'6',self.typeChar,''],
			[5,1,')',self.typeChar,''],	
			[6,1,'左削除',self.b_delete_action,''],	
			
			[0,2,'平仮名', self.b_hiragana_action,''],	
			[1,2,'$',self.typeChar,''],
			[2,2,'7',self.typeChar,''],
			[3,2,'8',self.typeChar,''],
			[4,2,'9',self.typeChar,''],
			[5,2,'=',self.typeChar,''],
			[6,2,'漢字',self.b_kanji_action,''], 

			[0,3,'絵文字', self.b_emoji_action,''],		
			[1,3,'+',self.typeChar,''],
			[2,3,'-',self.typeChar,''],
			[3,3,'0',self.typeChar,''],
			[4,3,'×',self.typeChar,''],
			[5,3,'÷',self.typeChar,''],
			[6,3,'return',self.b_return_action,'']				
			],
				
			'emoji':[
			#[0,0,'カタカナ', self.b_katakana_action,''],
			[0,1,'ABC', self.b_alpha_action,''],
			[0,2,'数字', self.b_digit_action,''],
			[0,3,'平仮名', self.b_hiragana_action,''],
			[5,2,'⏩',self.emoji_nextSet,''],
			[5,3,'⏪',self.emoji_prevSet,'']
			],			
			'symbol':[
			#[0,0,'カタカナ', self.b_katakana_action,''],
			[0,1,'ABC', self.b_alpha_action,''],
			[0,2,'数字', self.b_digit_action,''],
			[1,2,'平仮名', self.b_hiragana_action,'']
			#[5,2,'⏩',self.symbol_nextSet,''],
			#[5,3,'⏪',self.symbol_prevSet,'']
			],
			
			'phrases':[
			[1,0,'おはよう😊',self.typeChar,''],
			[1,1,'おはようございます☀️',self.typeChar,''],
			[1,2,'こんにちは✨',self.typeChar,''],
			[1,3,'こんばんは🌙',self.typeChar,''],
			[2,0,'お疲れ様です🙇',self.typeChar,''],
			[2,1,'そんなの知らん😜',self.typeChar,''],
			[2,2,'今から帰る🛵',self.typeChar,''],
			[2,3,'買い物してから帰る🏪',self.typeChar,''],
			#[0,0,'カタカナ', self.b_katakana_action,''],
			[0,1,'ABC', self.b_alpha_action,''],
			[0,2,'数字', self.b_digit_action,''],
			[0,3,'平仮名', self.b_hiragana_action,'']
			]
			}
			
		self.small_keys = {
			# Hiragana: あ, い, う, え, お, や, ゆ,よ, つ
			'hiragana':{
				"あ":"ぁ", # medium of あ 
				"い":"ぃ", # left   of あ
				"う":"ぅ", # up     of あ
				"え":"ぇ", # right  of あ 
				"お":"ぉ", # bottom of あ
				"や":"ゃ", # medium of や 
				"ゆ":"ゅ", # up     of や
				"よ":"ょ", # bottom of や
				"つ":"っ", # up     of た
				"わ":"ゎ"
				},
			'katakana':{
			# Katakana: ア、イ、ウ、エ、オ、ヤ、ユ、ヨ、ツ
				"ア":"ァ", 
				"イ":"ィ",
				"ウ":"ゥ",
				"エ":"ェ",
				"オ":"ォ",
				"ヤ":"ャ",
				"ユ":"ュ",
				"ヨ":"ョ",
				"ツ":"ッ",
				"ワ":"ヮ"
				}
			}	
			
		# build dictionnary of conversion Hirgana to Katakana
		hirganas  = 'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもや「ゆ」よらりるれろわをんー'
		katakanas = 'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤ「ユ」ヨラリルレロワヲンー'
		self.japanese_letters_voiced = 'かきくけこさしすせそたちつてとはひふへほカキクケコサシスセソタチツテトハヒフヘホ'
		self.japanese_letters_half_voiced = 'はひふへほハヒフヘホ'
		self.hirgana_to_katakana = {}
		k = 0
		for c in hirganas:
			kc = katakanas[k]
			self.hirgana_to_katakana[c] = kc 
			if c in self.japanese_letters_voiced:
				# character has an existing specific character (ucode + 1)
				cv = chr(ord(c)+1)
				kcv = chr(ord(kc)+1)
				self.hirgana_to_katakana[cv] = kcv 
			if c in self.japanese_letters_half_voiced:
				# character has an existing specific character (ucode + 2)
				chv = chr(ord(c)+2)
				kchv = chr(ord(kc)+2)
				self.hirgana_to_katakana[chv] = kchv 
			k += 1
			
		k = 0
		for c in self.small_keys['hiragana']:		
			sc = self.small_keys['hiragana'][c]		# あ -> ぁ
			kc = self.hirgana_to_katakana[c]			# あ -> ア
			skc = self.small_keys['katakana'][kc]	# ア -> ァ 
			self.hirgana_to_katakana[sc] = skc		# ぁ -> ァ
			k += 1
						
		self.accessibility_labels = {
		'。':'まる',
		'、':'てん',
		'゛':'濁点',
		'゜':'半濁点',
		'「':'ひだりかぎかっこ',
		'」':'みぎかぎかっこ'
		}
			
		
		# an emoji can use more than one character, thus if you define emojis as a str,
		# and you scan it by character, you could get a part of an emoji and seen it
		# as blank in a key. Thus we devine the set of emojis as an array and thus
		# scan it by element will give each emoji as a str of 1 to 4 characters.
		
		self.emojis = ['😊','😜','😱','💦','☔️','(笑)','☀️','☁️','☃️','❄️','🍙','🍔','🚗','🌈', '⭐️','😀','😃','😄','😁','😆','😅','😂','🤣','☺️','😊','😇','🙂','🙃', '😉','😌','😍','🥰','😘','😗','😙','😚','😋','😛','😝','😜','🤪','🤨', '🧐','🤓','😎','🤩','🥳','😏','😒','😞','😔','😟','😕','🙁','☹️','😣', '😖','😫','😩','🥺','😢','😭','😤','😠','😡','🤬','🤯','😳','🥵','🥶', '😨','😰','😥','😓','🤗','🤔','🤭','🤫','🤥','😶','😐','😑','😬','😦', '😧','😮','😲','😴']
		self.last_emoji = -1
		for ix in range(1,5):
			for iy in range(0,4):
				self.last_emoji += 1
				keyboards['emoji'].append([ix,iy,self.emojis[self.last_emoji],
				self.typeChar,''])

		self.symbols = ['←','→','↑','↓','•','●','○','◎','△','▲','□','■','〜','ー', '(',')']
		#['＋','−','×','÷','＝','@','-','/',',',':',';','(',')','¥','&','“','.',',','?',     '!','’','[',']','{','}','#','%','^','*','_','|','~','<','>','$','€','£','•','.','?','!','←','→','↑','↓','●','○','◎','△','▲','□','■']	
		
		self.last_symbol = -1
		for iy in range(0,4):
			for ix in range(2,6):
				self.last_symbol += 1
				if self.last_symbol == len(self.symbols):
					break
				keyboards['symbol'].append([ix,iy,self.symbols[self.last_symbol],
				self.typeChar,''])

		dxdy = [(-1,0), (0,-1), (+1,0), (0,+1)] # left up right down
		self.japanese_letters = {}

		for kbd in keyboards.keys():
			for ix,iy,t,act,flick in keyboards[kbd]:
				if kbd == 'phrases' and ix > 0:
					dx = self.dx * 3 
					x = dd + (self.dx+dd) + (ix-1) * (dx+dd)					
				else:
					dx = self.dx 
					x = dd + ix * (dx+dd)
				y = dd + iy * (dy + dd) + dyk
				b = self.make_button(x,y,dx,dy,t,act,super=self.vs[kbd])
			
				if t in self.accessibility_labels:
					# to be pronunciated, the button needs to not have a title
					#   but an image
					bo = ObjCInstance(b)
					bo.isAccessibilityElement = True
					bo.accessibilityLabel = self.accessibility_labels[t]
					
				if kbd in ['hiragana', 'katakana']:
					if act == self.typeChar and t not in [u'\u309B'+'濁点', u'\u309C']:
						self.japanese_letters[t] = False
				if act == self.b_kanji_action:
					b.name = 'kanji_button'

				if t in ['CapsLock','Shift']:
					b.background_color = 'lightgray'
				elif t in ['小文字']:
					# "small keys" key
					b.name = 'smallkey_button'
				if flick:
					long_press(b,self.long_press_handler, minimum_press_duration=0.01, allowable_movement=int(self.dy/2))
					#self.sub_keys(x,y,flick,b, super=self.vs[kbd])
					for i in range(4):
						if flick[i] != ' ':
							xx = x + dxdy[i][0] * (self.dx+self.dd)
							yy = y + dxdy[i][1]	* (self.dy+self.dd)
							title = flick[i]
							if kbd in ['hiragana', 'katakana']:
								self.japanese_letters[title] = False
							if title == u'\u309C':
								title += ' '
							if yy < 0:
								yy = 0 
								ddy = dyk
							else:
								ddy = self.dy
							bb = self.make_button(xx,yy,self.dx,ddy,title, None, super=self.vs[kbd])
							bb.hidden = True
							bb.assoc = b
				if kbd in ['emoji', 'symbol']:
					if t == '⏩':
						b.name = 'nextSet'
					elif t == '⏪':
						b.name = 'prevSet'
					elif act == self.typeChar:
						self.set_font_size(b)
						
		lv = ui.Label()
		lv.text = 'V' + version
		lv.font = ('Menlo', 12)
		lv.text_color = 'red'
		lvw = ui.measure_string(lv.text, font=lv.font)
		ix = nx-1
		iy = 0
		x = dd + ix * (dx + dd) + dx - lvw[0] - dd*2
		y = dd + iy * (dy + dd) + dy - lvw[1] - dd*2
		lv.frame = (x,y,lvw[0],20)
		lv.bring_to_front()
		self.v_hiragana.add_subview(lv)
	
		# Kanji process: begin =========================================================
		
		# a lot of code copied from Japanese Braille Input.py
						
		# https://github.com/Doublevil/JmdictFurigana		
		self.conn = sqlite3.connect("HiraganaToKanji.db",check_same_thread=False)
		self.cursor = self.conn.cursor()
		
		# read and store eventual supplementar Kanji's
		suppl_kanjis = 'HiraganaToKanji.txt'
		if os.path.exists(suppl_kanjis):
			with open(suppl_kanjis,encoding='utf-8') as fil:
				self.local_kanjis = fil.read().split('\n')
		else:
			self.local_kanjis = []
		
		# get sentences as examples for Kanjis
		# https://www.manythings.org/anki/
		with open('SentencesEngJpn.dat',encoding='utf-8') as fil:
			self.sentences = fil.read().split('\n')

		self.kanji_digits = {		
			"1":"一",
			"2":"二",
			"3":"三",
			"4":"四",
			"5":"五",
			"6":"六",
			"7":"七",
			"8":"八",
			"9":"九",
			"0":"零"
			} 
			
		self.buttons_titles = {
			'b_close':'キーボードを閉じる',
			'b_delete':'左削除',
			'b_left':'左に移動',
			'b_right':'右に動く',
			'b_decision':'点字OK',
			'b_conversion':'漢字',
			'kanjis_up':'漢字アップ',
			'kanjis_down':'漢字',
			'kanjis_other':'その他の説明',						
			'kanjis_ok':'漢字は大丈夫'
		}
		self.select_text = '選択する '
		
		self.v_kanji = ui.View()
		self.v_kanji.background_color = 'white' # self.background_color
		self.v_kanji.frame = self.frame
		self.v_kanji.hidden = True
		self.add_subview(self.v_kanji)

		wk,hk = self.width,self.height		

		kanjis = ui.TableView(name='kanjis')
		kanjis.frame = (0,2,32,hk-2)
		kanjis.allows_multiple_selection = False
		kanjis.border_color = 'lightgray'
		kanjis.border_width = 1
		kanjis.corner_radius = 5
		kanjis.data_source = ui.ListDataSource(items=[])
		kanjis.data_source.font = ('Menlo',64)
		kanjis.row_height = 64
		kanjis.delegate = self
		kanjis.current = 0
		kanjis.data_source.tableview_cell_for_row = self.tableview_cell_for_row	
		self.v_kanji.add_subview(kanjis)	
		
		# up, down play on content_offset of TableView (subclass of ScrollView)
		# y positions so buttons are equidistants
		# x position set later when tableview width is set
		h = kanjis.height
		d_b = 64
		e_b = (h-3*d_b)/4
		b1 = ui.Button(name='kanjis_up')
		b1.background_image = ui.Image.named('iob:arrow_up_c_32')
		b1.background_color = (0,1,0,0.5)
		y = kanjis.y + e_b
		b1.frame =(0,y,d_b,d_b)
		b1.corner_radius = b1.width/2
		b1.action = self.tableview_up
		self.v_kanji.add_subview(b1)
		
		b2 = ui.Button(name='kanjis_ok')
		b2.background_image = ui.Image.named('iob:checkmark_round_32')
		b2.background_color = (0,1,0,0.5)
		y = y + d_b + e_b
		b2.frame =(0,y,d_b,d_b)
		b2.corner_radius = b2.width/2
		b2.action = self.tableview_ok
		self.v_kanji.add_subview(b2)
		
		b4 = ui.Button(name='kanjis_other')											
		b4.background_image = ui.Image.named('iob:refresh_32')	
		b4.background_color = (0,1,0,0.5)												
		b4.frame =(0,y,d_b,d_b)																	
		b4.corner_radius = b2.width/2														
		b4.action = self.tableview_other												
		self.v_kanji.add_subview(b4)																		
		
		b3 = ui.Button(name='kanjis_down')
		b3.background_image = ui.Image.named('iob:arrow_down_c_32')
		b3.background_color = (0,1,0,0.5)
		y = y + d_b + e_b
		b3.frame =(0,y,d_b,d_b)
		b3.corner_radius = b3.width/2
		b3.action = self.tableview_down
		self.v_kanji.add_subview(b3)
		
		self.set_temp_kanji_lbl('')
		
		for sv in self.v_kanji.subviews:
			if isinstance(sv, ui.Button):
				sv_title = self.buttons_titles.get(sv.name, '')
				if sv_title:
					sv.title = sv_title
					if sv.background_image:
						sv.tint_color = (0,0,0,0)	# title color transparent so invisible
																				# but title still said by VoiceOver
					sv.image = None
					#sv.background_image = None
				
	def b_kanji_action(self, sender):
		if self.temp_kanji == '':
			return
		self.hide_all()
		self.v_kanji.hidden = False
		self.conversion_button_action()
				
	def set_temp_kanji_lbl(self,t):
		self.temp_kanji = t
		#w,h = ui.measure_string(t,font=self.temp_kanji_lbl.font)
		self.temp_kanji_lbl.text = t
		# check if temporary storage last letter has a small version
		kbd = None
		if not self.v_hiragana.hidden:
			kbd = 'hiragana'
			v = self.v_hiragana
		if not self.v_katakana.hidden:
			kbd = 'katakana'	
			v = self.v_katakana
		if kbd:	
			v['smallkey_button'].enabled = False
			if t != '':
				if t[-1] in self.small_keys[kbd]:
					v['smallkey_button'].enabled = True					
		self.v_hiragana['kanji_button'].enabled = (self.temp_kanji != '')
		self.v_digit['kanji_button'].enabled = (self.temp_kanji != '')
		
	def conversion_button_action(self):
		t = self.temp_kanji
		td = ''
		for c in t:
			if c in self.kanji_digits:
				td += self.kanji_digits[c]
			else:
				td += c
		t = td
		items = [t]
		try:		
			self.cursor.execute(
			'select hiragana, kanji from Hiragana_to_Kanji where hiragana = ?',
			(t,))
		except Exception as e:
			console.hud_alert('be sure that HiraganaToKanji.db file is present', 'error', 3)

		for li in self.local_kanjis:
			s = li.split('\t')
			try:
				if t not in s[0]:
					continue
				items.append(s[1])
				break
			except Exception as e:
				# lome could be erroneously typed
				continue	

		w_max = 0
		for row in self.cursor:
			t = row[1]
			items.append(t)
		font = ('Menlo',64)
		for t in items:
			w,h = ui.measure_string(t, font=font)
			w_max = max(w+50,w_max)
		w_max = min(w_max, self.width-self.v_kanji['kanjis_up'].width*2-4*10-20)
		self.v_kanji['kanjis'].data_source.font = font		
		self.v_kanji['kanjis'].data_source.items = items
		if len(items) == 1000:
			self.tableview_did_select(self.v_kanji['kanjis'], 0, 0)
			return
		# Kanji's exist, display a TableView
		self.v_kanji['kanjis'].x = (self.width - w_max)/2
		self.v_kanji['kanjis'].width = w_max
		self.v_kanji['kanjis'].height = min(self.bounds.size[1]-(2+2), len(items)*self.v_kanji['kanjis'].row_height)
		#self.v_kanji['kanjis'].hidden = False
		x = self.v_kanji['kanjis'].x + self.v_kanji['kanjis'].width + 10
		#self.v_kanji['kanjis_up'].hidden = False
		self.v_kanji['kanjis_up'].x = x
		#self.v_kanji['kanjis_ok'].hidden = False
		self.v_kanji['kanjis_ok'].x = x
		#self.v_kanji['kanjis_other'].hidden = False												
		e_b = self.v_kanji['kanjis_ok'].y - self.v_kanji['kanjis_up'].y - self.v_kanji['kanjis_other'].height																
		self.v_kanji['kanjis_other'].x = self.v_kanji['kanjis'].x - self.v_kanji['kanjis_other'].width - e_b																					
								
		#self.v_kanji['kanjis_down'].hidden = False
		self.v_kanji['kanjis_down'].x = x
		ui.delay(self.tableview_say_current,0.01)
		self.v_kanji['kanjis_ok'].title = self.select_text+self.get_kanji(0)
		self.v_kanji['kanjis_other'].title = self.select_text + self.get_kanji(0,next_sentence=True)													
		#self.v_kanji['kanjis_up'].title = self.get_kanji(-1)
		#self.v_kanji['kanjis_down'].title = self.get_kanji(+1)
		
	def get_kanji(self,delta,next_sentence=False):									
		i = self.v_kanji['kanjis'].current + delta
		if i < 0 or i == len(self.v_kanji['kanjis'].data_source.items):
			i = self.v_kanji['kanjis'].current
		kanji = self.v_kanji['kanjis'].data_source.items[i]
		sentence = ''
		if not next_sentence:																					
			self.i_sentence = 0																					
		else:																													
			self.i_sentence = self.i_sentence + 1												
		i_found = 0																										
		for li in self.sentences:
			s = li.split('\t')
			try:
				if kanji not in s[1]:
					continue
				if not next_sentence:																			
					sentence = s[1]			# 1 = Japanese  0 = English (test)
				else:																											
					sentence = s[0]			# 1 = Japanese  0 = English (test)	
				#print(sentence)
				if i_found != self.i_sentence:														
					# not yet the right sentence number reached							
					i_found = i_found + 1																		
					continue																								
				#print(kanji,s)				# test without VoiceOver
				break
			except Exception as e:
				# some lines are blank
				continue	
		kanji = kanji + ' ' + sentence
		return kanji
		
	def tableview_cell_for_row(self,tableview, section, row):
		cell = ui.TableViewCell()
		data = tableview.data_source.items[row]
		font_size = 32
		font = ('Menlo',font_size)
		w = ui.measure_string(data, font=font)[0]
		while w > cell.text_label.width:
			font_size += -1
			font = ('Menlo',font_size)
			w = ui.measure_string(data, font=font)[0]
		cell.text_label.font = font
		#cell.text_label.alignment = ui.ALIGN_LEFT
		if row == tableview.current:
			cell.text_label.text_color = 'red'
			cell.bg_color = 'lightgray'
		elif row == 0:
			cell.text_label.text_color = 'green'
		else:
			cell.text_label.text_color = 'black'
		cell.text_label.text = data
		return cell
		
	def tableview_up(self,sender):
		tableview = self.v_kanji['kanjis']
		if tableview.current > 0:
			tableview.current = tableview.current - 1
			self.table_view_scroll(tableview)
			ui.delay(self.tableview_say_current,0.01)
		#self.v_kanji['kanjis_up'].title = self.get_kanji(-1)	# future title to hear
		self.v_kanji['kanjis_ok'].title = self.select_text+self.get_kanji(0)
		self.v_kanji['kanjis_other'].title = self.select_text + self.get_kanji(0,next_sentence=True)													
		#self['kanjis_down'].title = self.get_kanji(+1)
		
	def tableview_down(self,sender):
		tableview = self.v_kanji['kanjis']
		#print(dir(ObjCInstance(tableview)))
		if tableview.current < (len(tableview.data_source.items)-1):
			tableview.current = tableview.current + 1
			self.table_view_scroll(tableview)
			ui.delay(self.tableview_say_current,0.01)
		#self.v_kanji['kanjis_up'].title = self.get_kanji(-1)	# future title to hear
		self.v_kanji['kanjis_ok'].title = self.select_text+self.get_kanji(0)
		self.v_kanji['kanjis_other'].title = self.select_text + self.get_kanji(0,next_sentence=True)													
		#self.v_kanji['kanjis_down'].title = self.get_kanji(+1)
		
	def tableview_other(self,sender):		
		import requests
		kanji = self.v_kanji['kanjis'].data_source.items[self.v_kanji['kanjis'].current]
		for k in kanji:
			url = 'https://kanjiapi.dev/v1/kanji/' + k
			response = requests.get(url).json()
			# {'kanji': '歯', 'grade': 3, 'stroke_count': 12, 'meanings': ['tooth', 'cog'],  'kun_readings': ['よわい', 'は', 'よわ.い', 'よわい.する'], 'on_readings': ['シ'], 'name_readings': [], 'jlpt': 2, 'unicode': '6b6f', 'heisig_en': 'tooth'}
			try:
				t = response['meanings'][0]
				speech_say(t,language='en-GB')
			except Exception as e:
				pass
		return
		# unused
		self.v_kanji['kanjis_ok'].title = self.v_kanji['kanjis_other'].title					
		self.v_kanji['kanjis_other'].title = self.select_text + self.get_kanji(0,next_sentence=True)													

	def table_view_scroll(self,tableview):
		tvo = ObjCInstance(tableview)
		#x,y = tableview.content_offset
		#y = float(tableview.current*tableview.row_height)
		#tvo.setContentOffset_(CGPoint(0,y))
		#tableview.content_offset = (x,y)
		NSIndexPath = ObjCClass("NSIndexPath")
		nsindex = NSIndexPath.indexPathForRow_inSection_(tableview.current,0	)
		# UITableViewScrollPosition = 0 None
		#															1 Top
		#															2 Middle
		#															3 Bottom
		UITableViewScrollPosition = 2
		tvo.scrollToRowAtIndexPath_atScrollPosition_animated_(nsindex, UITableViewScrollPosition, True)
		tableview.reload()		
		
	def tableview_ok(self,sender):
		tableview = self.v_kanji['kanjis']
		row = tableview.current
		self.tableview_did_select(tableview, 0, row)
		
	def tableview_say_current(self):
		return
		t = self.v_kanji['kanjis'].data_source.items[self.v_kanji['kanjis'].current]
		#speech.say(t,'jp-JP')
		utterance = AVSpeechUtterance.speechUtteranceWithString_(t)
		#the value that sounds good apparently depends on ios version
		utterance.rate = 0.5
		if self.voice_def == None:
			# not yet defined
			try:
				synthesizer, voice = get_synthesizer_and_voice()
			except ValueError as e:
				#print(e)
				synthesizer, voice = get_synthesizer_and_voice("en-US")
				console.hud_alert('voice not found, call your support','error')
			self.voice_def = voice
			self.synthesizer =synthesizer
		utterance.voice = self.voice_def
		utterance.useCompactVoice = False 
		self.synthesizer.speakUtterance_(utterance)
		
	def tableview_did_select(self, tableview, section, row):
		tableview.current = row
		self.tableview_say_current()
		t = tableview.data_source.items[row]
		# insert kanji
		keyboard.insert_text(t)	
		self.set_temp_kanji_lbl('')
		self.v_kanji.hidden = True
		self.v_hiragana.hidden = False
					
	# Kanji process: end ===========================================================
								
	def set_font_size(self,b):		
		# some emojis could be like multiple characters ex: '(笑)' 
		# thus we have to find the font size which permits to see the emoji,
		# else it will be seen as '...' (font size to big)
		fs = self.dy-2
		wt,ht = ui.measure_string(b.title,font=('.SFUIText', fs))
		while wt > (b.width-2) or ht > (b.height-2) :
			fs = fs/2
			wt,ht = ui.measure_string(b.title,font=('.SFUIText', fs))
		b.font = ('.SFUIText', fs)
							
	def emoji_nextSet(self,sender):
		for b in self.v_emoji.subviews:
			if b.action == self.typeChar:
				self.last_emoji += 1
				if self.last_emoji == len(self.emojis):
					self.last_emoji = 0
				b.title = self.emojis[self.last_emoji]	
				self.set_font_size(b)	
		
	def emoji_prevSet(self,sender):
		for b in self.v_emoji.subviews:
			if b.action == self.typeChar:
				self.last_emoji -= 1
				if self.last_emoji < 0:
					self.last_emoji = len(self.emojis)-1
				b.title = self.emojis[self.last_emoji]	
				self.set_font_size(b)	
				
	def symbol_nextSet(self,sender):
		for b in self.v_symbol.subviews:
			if b.action == self.typeChar:
				self.last_symbol += 1
				if self.last_symbol == len(self.symbols):
					self.last_symbol = 0
				b.title = self.symbols[self.last_symbol]	
				self.set_font_size(b)	
		
	def symbol_prevSet(self,sender):
		for b in self.v_symbol.subviews:
			if b.action == self.typeChar:
				self.last_symbol -= 1
				if self.last_symbol < 0:
					self.last_symbol = len(self.symbols)-1
				b.title = self.symbols[self.last_symbol]	
				self.set_font_size(b)	
				
	def smallKey(self, sender):
		if not self.v_hiragana.hidden:
			kbd = 'hiragana'
		if not self.v_katakana.hidden:
			kbd = 'katakana'
		t = self.temp_kanji_lbl.text	
		s = self.small_keys[kbd][t[-1]]
		self.set_temp_kanji_lbl(t[:-1]+s)
				
	def capsKey(self, sender):
		self.caps = not self.caps
		if not self.caps:
			self.caps_lock = False
		for b in self.v_alpha.subviews:
			if b.title == 'Shift': # caps
				b.background_color = 'white' if self.caps else 'lightgray'
			elif b.title == 'CapsLock': # capslock
				b.background_color = 'lightgray'
			elif b.title.isalpha():
				b.title = b.title.upper()    if self.caps else b.title.lower()
				
	def capsLock(self, sender):
		self.caps_lock = not self.caps_lock
		for b in self.v_alpha.subviews:
			if b.title == 'Shift': # caps
				b.background_color = 'lightgray'
			elif b.title == 'CapsLock': # caps 
				b.background_color = 'white' if self.caps_lock else 'lightgray'
			elif b.title.isalpha():
				b.title = b.title.upper()    if self.caps_lock else b.title.lower()
		
	def typeChar(self,sender):
		if not self.v_emoji.hidden:
			t = sender.title
		elif not self.v_symbol.hidden:
			t = sender.title
		elif not self.v_phrases.hidden:
			t = sender.title
		else:
			t = sender.title[0]
		# particular process
		if t in [u'\u309B', u'\u309C']: # standalone phonetic voiced or half-voiced mark
			in_temp_storage = False
			if (not self.v_katakana.hidden) or (not self.v_hiragana.hidden):
				# Hiragana or Katakana
				if self.temp_kanji == '':
					# temporary storage empty	
					# use character as left of cursor as previous character
					try:
						previous_c = keyboard.get_input_context()[0][-1]
					except:
						previous_c = ''		
				else:
					# temporary storage not empty	
					in_temp_storage = True				
					# use last character of temporary storage as previous character
					previous_c = self.temp_kanji[-1]
			appnd = True 	
			if previous_c not in self.japanese_letters:
				# previous character not an Hiragana nor a Katakana character
				t = t # append the standalone character of the phonetic mark
			else:
				# previous character is an Hiragana or a Katakana character		
				if t == u'\u309C':	
					# mark is the half-voiced mark
					if previous_c in self.japanese_letters_half_voiced:
						# previous character has an existing specific character (ucode + 1)
						t = chr(ord(previous_c)+2)
						appnd = False # replace previous character by this specific one
					else:
						# previous character doesn't have an specific character (ucode + 2)
						t = u'\u309A' # append the combining phonetic half-voiced mark
				else:
					# mark is the voiced mark '濁点'
					if previous_c in self.japanese_letters_voiced:
						# previous character has an existing specific character (ucode + 1)
						t = chr(ord(previous_c)+1)
						appnd = False # replace previous character by this specific one
					else:
						# previous character doesn't have an specific character (ucode + 1)
						t = u'\u3099' # append the combining phonetic voiced mark
						
			if in_temp_storage:
				# in temporary storage
				if appnd:
					# append
					self.set_temp_kanji_lbl(self.temp_kanji + t)					
				else:
					# replace last character
					self.set_temp_kanji_lbl(self.temp_kanji[:-1] + t)					
			else:
				# in general keyboard.text															
				if appnd:
					# append
					keyboard.insert_text(t)					
				else:
					# replace last character
					keyboard.backspace(times=1)
					keyboard.insert_text(t)
			return
		elif t in "。、？！": 
			# punctuation 
			if (not self.v_katakana.hidden) or (not self.v_hiragana.hidden):
				# Hiragana or Katakana
				if self.temp_kanji == '':	
					# if temporary storage not yet active in Hiragana keyboard,
					# insert directly the punctuation in the TextView
					keyboard.insert_text(t)
					return
		# general process
		if not self.v_hiragana.hidden:
			# Hiragana: store in temporary storage
			self.set_temp_kanji_lbl(self.temp_kanji + t)
		elif not self.v_katakana.hidden:
			# Katakana: store in temporary storage
			self.set_temp_kanji_lbl(self.temp_kanji + t)
		elif not self.v_digit.hidden:
			# Digit
			if t in '0123456789':
				# Digit: store in temporary storage if digit
				self.set_temp_kanji_lbl(self.temp_kanji + t)
			else:
				# Digit: direct insert in text if not digit
				keyboard.insert_text(t)
		else:
			# Alphabet, Emoji, Symbol: direct insert in text
			keyboard.insert_text(t)

		if not self.v_alpha.hidden:
			if sender.title.isalpha():
				if self.caps:
					self.capsKey('unused')
					
	def b_space_action(self, sender):
		keyboard.insert_text(' ')

def main ():
	if not keyboard.is_keyboard():
		return

	v = MyView()
	keyboard.set_view(v, 'expanded')
	
if __name__ == '__main__':
	main()
