'''
version 00.25 is available with

modifications
- wait 1 second before reading out "read to cursor" and "read all"

correction of bugs
- 

https://raw.githubusercontent.com/cvpe/Pythonista-scripts/master/Emojis Keyboard.py 
  
todo
	- The "read all" button doesn't read everything. If a new line,
		it doesn't read from the beginning.
		And if a sentence is too long, you don't read it out from the beginning and start in the middle.
		
		Similarly, the read to cursor button does not read from the beginning if it is a new line.
		And if the sentences are too long, you don't read them out from the beginning and start in the middle.		
						
	- When you select text with the flick input button, if it is out of the frame, 
		you don't enter text. When it is blue at the time of selection, you want sound effects or voice-over tactile response.				

	- Please adjust the flick input button finely.

		Can't I make a simple sound when it changes to blue color of character selection of the flick input button?
		Even if you can't read aloud, just sound effect is fine.

		I can't type when I move it enough to get off 
		the button.
		If you can't see, you won't know if it's off.
		
	- I have a problem with the system of kanji conversion.
		It might be impossible to solve this problem.
		
		If you use voice over, you can pronounce only sounds of Kanji in the Kanji list.
		Usually, there is an explanation of which Kanji you have chosen.
		
		As an example.
		
		"葉" is described as a leaf of a tree.
		
		"葉" and "歯" have the same pronunciation.
		The "歯" are the teeth on the toothbrush.
		It is distinguished by sound, so it is difficult if there is no explanation.
		
		I don't know what to do.
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

version = '00.25'

# use ObjectiveC speech: start =================================================
AVSpeechUtterance=ObjCClass('AVSpeechUtterance')
AVSpeechSynthesizer=ObjCClass('AVSpeechSynthesizer')
AVSpeechSynthesisVoice=ObjCClass('AVSpeechSynthesisVoice')

voices=AVSpeechSynthesisVoice.speechVoices()
for i in range(0,len(voices)):
	#print(i,voices[i].language(),voices[i].identifier())
	if 'ja-JP' in str(voices[i].identifier()): 
		# if u have Japanese Siri voice, replace from 'ja-JP' to 'siri_O-ren_ja-JP'
		vi = i
		break
		
synthesizer=AVSpeechSynthesizer.new()

def speech_say(t,unused):
	utterance=AVSpeechUtterance.speechUtteranceWithString_(t)
	utterance.rate = 0.5
	utterance.useCompactVoice=False
	utterance.voice = voices[vi]
	synthesizer.speakUtterance_(utterance)
# use ObjectiveC speech: end ===================================================
			  
class MyView(ui.View):
	def __init__(self, *args, **kwargs):
		super().__init__(self, *args, **kwargs)
		self.background_color = 'lightgray'
		
		# bounds not yet known in init, let some delay		
		ui.delay(self.dimensions,0.1)
		
	def b_top_action(self, sender):
		t = keyboard.get_input_context()	# current line
		if not t:
			return
		l = len(t[0])
		keyboard.move_cursor(-l)
		
	def b_up_action(self, sender):
		t = keyboard.get_input_context()	# current line
		if not t:
			return
		l0 = len(t[0])
		l1 = len(t[1])
		keyboard.move_cursor(-l0)
		keyboard.move_cursor(-1)					# end of previous line
		t = keyboard.get_input_context()	# previous line
		if not t:
			return
		l2 = len(t[0])
		l3 = len(t[1])
		#sender.title = str(l0)+' '+str(l1)+' '+str(l2)+' '+str(l3)
		if l2 >= l0:
			keyboard.move_cursor(-(l2-l0))
		else:
			pass											# line is shorter than l0, thus stay at end
			
	def b_left_action(self, sender):
		keyboard.move_cursor(-1)
		
	def b_right_action(self, sender):
		keyboard.move_cursor(+1)
		
	def b_bottom_action(self, sender):
		try:
			t = keyboard.get_input_context()	# current line
			l = len(t[1])
			keyboard.move_cursor(+l)
		except Exception as e:
			pass
		
	def b_down_action(self, sender):
		t = keyboard.get_input_context()	# current line
		if not t:
			return
		l0 = len(t[0])
		l1 = len(t[1])
		keyboard.move_cursor(l1)
		keyboard.move_cursor(1)						# begin of next line
		t = keyboard.get_input_context()	# next line
		l2 = len(t[0])
		l3 = len(t[1])
		if (l2+l3) >= l0:
			keyboard.move_cursor(l0)
		else:
			pass
			#keyboard.move_cursor(2)#l0-l2)
			
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
		
	def b_copy_action(self, sender):
		context = keyboard.get_input_context()
		t = keyboard.get_selected_text()
		clipboard.set(t)
		
	def b_read_to_cursor_action(self, sender):
		self.read_t = keyboard.get_input_context()[0]
		ui.delay(self.read_text,1)		
		
	def b_read_all_action(self, sender):
		keyboard.move_cursor(-1000)
		self.read_t = keyboard.get_input_context()[1]
		ui.delay(self.read_text,1)	
		
	def read_text(self):
		try:
			speech_say(self.read_t,'jp-JP')
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
			#speech.say(sv.title,'jp-JP')
			for sv in b.superview.subviews:
				if isinstance(sv, ui.Button):
					if sv.action == None and sv.assoc == b:
						sv.hidden = False
						sv.bring_to_front()
					elif sv != b:
						sv.background_color = 'lightgray'
		elif data.state == 2:
			# move long press
			# if location in one of original + 4 new, set it blue
			for sv in b.superview.subviews:
				if isinstance(sv, ui.Button):
					if (sv.action == None and sv.assoc == b) or sv == b:
						if xp >= sv.x and xp <= (sv.x + sv.width) and yp >= sv.y and yp <= (sv.y + sv.height):
							if sv.background_color != 'blue':	
								sv.background_color = 'blue'	
								#speech_say(sv.title,'jp-JP')
								#ObjCInstance(sv).isAccessibilityElement = True
						else:
							sv.background_color = 'white'							
		elif data.state == 3:
			# end long press
			b.background_color = 'white'
			for sv in b.superview.subviews:
				if isinstance(sv, ui.Button):
					if sv.action == None and sv.assoc == b:
						sv.background_color = 'white'		
						#ObjCInstance(sv).isAccessibilityElement = True					
						sv.hidden = True
					elif sv != b:
						sv.background_color = 'white'
					if (sv.action == None and sv.assoc == b) or sv == b:
						if xp >= sv.x and xp <= (sv.x + sv.width) and yp >= sv.y and yp <= (sv.y + sv.height):
							self.typeChar(sv)							
							
	def sub_keys(self, x,y,keys,b,super=None):	
		dxdy = [(-1,0), (0,-1), (+1,0), (0,+1)]
		for i in range(4):
			if keys[i] != ' ':
				xx = x + dxdy[i][0] * (self.dx+self.dd)
				yy = y + dxdy[i][1]	* (self.dy+self.dd)
				title = keys[i]
				if title == u'\u309A':
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
				
	def b_japan_action(self, sender):
		self.hide_all()
		self.v_japan.hidden = False
		
	def b_katakana_action(self, sender):
		if self.temp_kanji != '':
			keyboard.insert_text(self.temp_kanji)	
			self.set_temp_kanji_lbl('')			
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
		
	def make_button(self,x,y,dx,dy,title,action, super=None):
		b = ui.Button()
		b.frame = (x,y,dx,dy)
		b.background_color = 'white'
		b.border_width = 1
		b.corner_radius = self.dy/4
		if title == '⇪':
			o = ObjCClass('UIImage').systemImageNamed_('capslock')
			UIImagePNGRepresentation = c.UIImagePNGRepresentation
			UIImagePNGRepresentation.restype = c_void_p
			UIImagePNGRepresentation.argtypes = [c_void_p]
			UIImage_data = nsdata_to_bytes(ObjCInstance(UIImagePNGRepresentation(o)))
			b.image = ui.Image.from_data(UIImage_data)
			b.name = title
			b.title = ''
		else:
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
			
		dd = 2
		nx = 7
		dx = (w - (nx+1)*dd)/nx
		
		ny = 5
		dy = (h - (ny+1)*dd)/ny
		
		dyk = dy * 2/3
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
		self.temp_kanji_lbl.alignment = ui.ALIGN_CENTER
		self.temp_kanji_lbl.text_color = 'red'
		self.add_subview(self.temp_kanji_lbl)

		self.v_japan = ui.View()
		self.v_japan.background_color = self.background_color
		self.v_japan.frame = (0,dyk,w,h)
		self.v_japan.hidden = False
		self.add_subview(self.v_japan)
		self.v_katakana = ui.View()
		self.v_katakana.background_color = self.background_color
		self.v_katakana.frame = (0,0,w,h)
		self.v_katakana.hidden = True
		self.add_subview(self.v_katakana)
		self.v_alpha = ui.View()
		self.v_alpha.background_color = self.background_color
		self.v_alpha.frame = (0,0,w,h)
		self.v_alpha.hidden = True
		self.add_subview(self.v_alpha)
		self.v_digit = ui.View()
		self.v_digit.background_color = self.background_color
		self.v_digit.frame = self.v_japan.frame
		self.v_digit.hidden = True
		self.add_subview(self.v_digit)
		self.v_emoji = ui.View()
		self.v_emoji.background_color = self.background_color
		self.v_emoji.frame = self.frame
		self.v_emoji.hidden = True
		self.add_subview(self.v_emoji)

		self.vs = {'japan':self.v_japan, 'alpha':self.v_alpha, 'digit':self.v_digit, 'emoji':self.v_emoji, 'katakana':self.v_katakana}

		'''		

		# https://www.nhk.or.jp/lesson/fr/letters/kanji.html
		
		# https://www.ssec.wisc.edu/~tomw/java/unicode.html#x3040
	
		'''	
		keyboards = {'japan':[
			[1,0,'⬅️',self.b_left_action,''],
			[2,0,'文頭',self.b_top_action,''],
			[3,0,'⬆️',self.b_up_action,''],			
			[4,0,'文末',self.b_bottom_action,''],	# end of sentence
			[5,0,'➡️',self.b_right_action,''],	
			[6,0,'左削除',self.b_delete_action,''],		
			#[3,0,'copy' if keyboard.has_full_access() else 'no full' ,self.b_copy_action,''],					
			# Hirgana: あ, い, う, え, お, や, ゆ,よ, わ			
			[1,1,'あ',self.typeChar,'いうえお'],			
			[2,1,'か',self.typeChar,'きくけこ'],			
			[3,1,'さ',self.typeChar,'しすせそ'],
			[4,1,'た',self.typeChar,'ちつてと'],			
			[5,1,'な',self.typeChar,'にぬねの'],
			[6,1,u'\u3099 ',self.typeChar,u'\u309A    '],
# かんじ 冠詞	
	 		[1,2,'は',self.typeChar,'ひふへほ'],	
			[2,2,'ま',self.typeChar,'みむめも'],			
			[3,2,'や',self.typeChar,'「ゆ」よ'],			
			[4,2,'ら',self.typeChar,'りるれろ'],	
			[5,2,'わ',self.typeChar,'をんー '],						
			[6,2,'漢字',self.b_kanji_action,''], 

			[1,3,'小文字',self.smallKey,''],
			[2,3,'read to\ncursor',self.b_read_to_cursor_action,''],
			[3,3,'⬇️',self.b_down_action,''],
			[4,3,'read\nall',self.b_read_all_action,''],
			[5,3,"。、",self.typeChar,"、？！ "], 	
			[6,3,'return',self.b_return_action,''], 	
		
			[0,0,'カタカナ', self.b_katakana_action,''],
			[0,1,'アルファベット', self.b_alpha_action,''],
			[0,2,'数字', self.b_digit_action,''],
			[0,3,'絵文字', self.b_emoji_action,'']
			
			],
			'katakana':[
			[1,1,'ア',self.typeChar,'イウエオ'],			
			[2,1,'カ',self.typeChar,'キクケコ'],			
			[3,1,'サ',self.typeChar,'シスセソ'],
			[4,1,'タ',self.typeChar,'チツテト'],						
			[5,1,'ナ',self.typeChar,'ニヌネノ'],
			[6,1,u'\u3099 ',self.typeChar,u'\u309A    '],		
					
			[1,2,'ハ',self.typeChar,'ヒフヘホ'],						
			[2,2,'マ',self.typeChar,'ミムメモ'],						
			[3,2,'ヤ',self.typeChar,'「ユ」ヨ'],
			[4,2,'ラ',self.typeChar,'リルレロ'],				
			[5,2,'ワ',self.typeChar,'ヲンー '],			
			
			[1,3,'小文字',self.smallKey,''],
			[5,3,"。、",self.typeChar,"、？！ "], 	
			
			[0,0,'   ⬆️\n⬅️➡️\n   ⬇️', self.b_japan_action,''],
			[0,1,'アルファベット', self.b_alpha_action,''],
			[0,2,'数字', self.b_digit_action,''],
			[0,3,'絵文字', self.b_emoji_action,'']
			],
			'alpha':[
			[2,1,'a',self.typeChar,'bc  '],
			[3,1,'d',self.typeChar,'ef  '],
			[4,1,'g',self.typeChar,'hi  '],
			[2,2,'j',self.typeChar,'kl  '],
			[3,2,'m',self.typeChar,'no  '],
			[4,2,'p',self.typeChar,'qrs '],
			[2,3,'t',self.typeChar,'uv  '],
			[3,3,'w',self.typeChar,'xyz '],
			[1,3,'⇧',self.capsKey,''],
			[1,2,'⇪',self.capsLock,''],
			[0,0,'カタカナ', self.b_katakana_action,''],
			[0,1,'   ⬆️\n⬅️➡️\n   ⬇️', self.b_japan_action,''],
			[0,2,'数字', self.b_digit_action,''],
			[0,3,'絵文字', self.b_emoji_action,'']
			],
			'digit':[
			[2,0,'1',self.typeChar,''],
			[3,0,'2',self.typeChar,''],
			[4,0,'3',self.typeChar,''],
			[2,1,'4',self.typeChar,''],
			[3,1,'5',self.typeChar,''],
			[4,1,'6',self.typeChar,''],
			[2,2,'7',self.typeChar,''],
			[3,2,'8',self.typeChar,''],
			[4,2,'9',self.typeChar,''],
			[3,3,'0',self.typeChar,''],
			[6,2,'漢字',self.b_kanji_action,''], 
			[0,0,'カタカナ', self.b_katakana_action,''],
			[0,1,'アルファベット', self.b_alpha_action,''],
			[0,2,'   ⬆️\n⬅️➡️\n   ⬇️', self.b_japan_action,''],
			[0,3,'絵文字', self.b_emoji_action,'']
			],	
			'emoji':[
			[0,0,'カタカナ', self.b_katakana_action,''],
			[0,1,'アルファベット', self.b_alpha_action,''],
			[0,2,'数字', self.b_digit_action,''],
			[0,3,'   ⬆️\n⬅️➡️\n   ⬇️', self.b_japan_action,''],
			[5,2,'⏩',self.nextSet,''],
			[5,3,'⏪',self.prevSet,'']
			]
			}
			
		self.small_keys = {
			# Hirgana: あ, い, う, え, お, や, ゆ,よ, つ
			'japan':{
				"あ":"ぁ", 
				"い":"ぃ", 
				"う":"ぅ", 
				"え":"ぇ", 
				"お":"ぉ", 
				"や":"ゃ", 
				"ゆ":"ゅ", 
				"よ":"ょ", 
				"つ":"っ"
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
				"ツ":"ッ"
				}
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

		dxdy = [(-1,0), (0,-1), (+1,0), (0,+1)]
		for kbd in keyboards.keys():		
			for ix,iy,t,act,flick in keyboards[kbd]:
				x = dd + ix * (dx+dd)
				y = dd + iy * (dy + dd)
				b = self.make_button(x,y,dx,dy,t,act,super=self.vs[kbd])
				if act == self.b_kanji_action:
					b.name = 'kanji_button'

				if kbd in self.small_keys:
					if t in self.small_keys[kbd]:
						ts = self.small_keys[kbd][t]
						bs = self.make_button(x,y,dx,dy,ts,self.typeChar,super=self.vs[kbd])
						bs.name = 'smallkey'
						bs.hidden = True					
				if t in ['⇪','⇧']:
					b.background_color = 'lightgray'
				if flick:
					long_press(b,self.long_press_handler, minimum_press_duration=0.01)
					#self.sub_keys(x,y,flick,b, super=self.vs[kbd])
					for i in range(4):
						if flick[i] != ' ':
							xx = x + dxdy[i][0] * (self.dx+self.dd)
							yy = y + dxdy[i][1]	* (self.dy+self.dd)
							title = flick[i]
							if title == u'\u309A':
								title += ' '
							bb = self.make_button(xx,yy,self.dx,self.dy,title, None, super=self.vs[kbd])
							bb.hidden = True
							bb.assoc = b
							if kbd in self.small_keys:
								if title in self.small_keys[kbd]:
									# special pisition
									if title in  ['つ', 'ツ'] :
										yy += (dy + dd)
									ts = self.small_keys[kbd][title]
									bs = self.make_button(xx,yy,dx,dy,ts,self.typeChar,super=self.vs[kbd])
									bs.name = 'smallkey'
									bs.hidden = True					
				if kbd == 'emoji':
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
		self.v_japan.add_subview(lv)
	
		self.small = False
		self.notsmall_keys = {}

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
			'kanjis_other':'その他の説明',						# add 1.6	# mod 1.7
			'kanjis_ok':'漢字は大丈夫'
		}
		self.select_text = '選択する '
		
		self.v_kanji = ui.View()
		self.v_kanji.background_color = 'white' # self.background_color
		self.v_kanji.frame = self.frame
		self.v_kanji.hidden = True
		self.add_subview(self.v_kanji)

		wk,hk = w,h		
		#hirganas = ui.Label(name='hirganas')
		#hirganas.frame = (wk/2,2,0,32)
		#hirganas.text = ''
		#hirganas.font = ('Menlo',32)
		#hirganas.text_color = (0,0,1,1)	
		#hirganas.border_color = 'lightgray'
		#hirganas.border_width = 1
		#self.v_kanji.add_subview(hirganas)
		
		#hirgana = ui.Label(name='hirgana')
		#hirgana.frame = (0,0,32,32)
		#hirgana.text = ''
		#hirgana.font = ('Menlo',32)
		#hirgana.text_color = 'gray'	
		#hirganas.add_subview(hirgana
			
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
		
		b4 = ui.Button(name='kanjis_other')											# add 1.6
		b4.background_image = ui.Image.named('iob:refresh_32')	# add 1.6
		b4.background_color = (0,1,0,0.5)												# add 1.6
		b4.frame =(0,y,d_b,d_b)																	# add 1.6
		b4.corner_radius = b2.width/2														# add 1.6
		b4.action = self.tableview_other												# add 1.6
		self.v_kanji.add_subview(b4)																		# add 1.6
		
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
		#self.v_kanji['hirganas'].text = self.temp_kanji
		# display not yet confirmed hirgana in hirganas field
		#w1,h = ui.measure_string(self.v_kanji['hirganas'].text, font=self.v_kanji['hirganas'].font)
		#w2,h = ui.measure_string(temp_hirgana, font=self.v_kanji['hirganas']['hirgana'].font)
		#self.v_kanji['hirganas']['hirgana'].text = temp_hirgana
		#self.v_kanji['hirganas']['hirgana'].x = w1
		#self.v_kanji['hirganas']['hirgana'].width = w2
		#self.v_kanji['hirganas'].width = w1 # + w2		
		#self.v_kanji['hirganas'].x = (self.width - w1)/2	

		self.conversion_button_action()
		
	def set_temp_kanji_lbl(self,t):
		self.temp_kanji = t
		w,h = ui.measure_string(t,font=self.temp_kanji_lbl.font)
		self.temp_kanji_lbl.text = t
		self.v_japan['kanji_button'].enabled = (self.temp_kanji != '')
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
		for t in items:
			w,h = ui.measure_string(t, font=self.v_kanji['kanjis'].data_source.font)
			w_max = max(w_max,w+50)
		self.v_kanji['kanjis'].data_source.items = items
		if len(items) == 1:
			self.tableview_did_select(self.v_kanji['kanjis'], 0, 0)
			return
		# Kanji's exist, display a TableView
		self.v_kanji['kanjis'].x = (self.width - w_max)/2
		self.v_kanji['kanjis'].width = w_max
		self.v_kanji['kanjis'].height = min(self.bounds.size[1]-(2+32+2), len(items)*self.v_kanji['kanjis'].row_height)
		#self.v_kanji['kanjis'].hidden = False
		x = self.v_kanji['kanjis'].x + self.v_kanji['kanjis'].width + 10
		#self.v_kanji['kanjis_up'].hidden = False
		self.v_kanji['kanjis_up'].x = x
		#self.v_kanji['kanjis_ok'].hidden = False
		self.v_kanji['kanjis_ok'].x = x
		#self.v_kanji['kanjis_other'].hidden = False												# add 1.6
		e_b = self.v_kanji['kanjis_ok'].y - self.v_kanji['kanjis_up'].y - self.v_kanji['kanjis_other'].height																# add 1.6
		self.v_kanji['kanjis_other'].x = self.v_kanji['kanjis'].x - self.v_kanji['kanjis_other'].width - e_b																												# add 1.6
		#self.v_kanji['kanjis_down'].hidden = False
		self.v_kanji['kanjis_down'].x = x
		ui.delay(self.tableview_say_current,0.01)
		self.v_kanji['kanjis_ok'].title = self.select_text+self.get_kanji(0)
		self.v_kanji['kanjis_other'].title = self.select_text + self.get_kanji(0,next_sentence=True)													# add 1.9
		#self.v_kanji['kanjis_up'].title = self.get_kanji(-1)
		#self.v_kanji['kanjis_down'].title = self.get_kanji(+1)
		
	def get_kanji(self,delta,next_sentence=False):									# mod 1.6
		i = self.v_kanji['kanjis'].current + delta
		if i < 0 or i == len(self.v_kanji['kanjis'].data_source.items):
			i = self.v_kanji['kanjis'].current
		kanji = self.v_kanji['kanjis'].data_source.items[i]
		sentence = ''
		if not next_sentence:																					# add 1.6
			self.i_sentence = 0																					# add 1.6
		else:																													# add 1.6
			self.i_sentence = self.i_sentence + 1												# add 1.6
		i_found = 0																										# add 1.6
		for li in self.sentences:
			s = li.split('\t')
			try:
				if kanji not in s[1]:
					continue
				if not next_sentence:																			# add 1.8
					sentence = s[1]			# 1 = Japanese  0 = English (test)
				else:																											# add 1.8
					sentence = s[0]			# 1 = Japanese  0 = English (test)	# add 1.8
				#print(sentence)
				if i_found != self.i_sentence:														# add 1.6
					# not yet the right sentence number reached							# add 1.6
					i_found = i_found + 1																		# add 1.6
					continue																								# add 1.6
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
		cell.text_label.font = ('Menlo',32)
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
		self.v_kanji['kanjis_other'].title = self.select_text + self.get_kanji(0,next_sentence=True)													# add 1.9
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
		self.v_kanji['kanjis_other'].title = self.select_text + self.get_kanji(0,next_sentence=True)													# add 1.9
		#self.v_kanji['kanjis_down'].title = self.get_kanji(+1)
		
	def tableview_other(self,sender):																# add 1.6
		# del 1.9 self['kanjis_ok'].title = self.select_text + self.get_kanji(0,next_sentence=True)	
		self.v_kanji['kanjis_ok'].title = self.v_kanji['kanjis_other'].title					# add 1.9
		self.v_kanji['kanjis_other'].title = self.select_text + self.get_kanji(0,next_sentence=True)													# add 1.9

	def table_view_scroll(self,tableview):
		x,y = tableview.content_offset
		y = float(tableview.current*tableview.row_height)
		#print(y)
		tableview.content_offset = (x,y)
		tableview.reload()
		#tableview.selected_row = tableview.current
		
	def tableview_ok(self,sender):
		tableview = self.v_kanji['kanjis']
		row = tableview.current
		self.tableview_did_select(tableview, 0, row)
		
	def tableview_say_current(self):
		return
		t = self.v_kanji['kanjis'].data_source.items[self.v_kanji['kanjis'].current]
		#speech.say(t,'jp-JP')
		utterance = AVSpeechUtterance.speechUtteranceWithString_(t)
		#the value that sounds good apparantly depends on ios version
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
		self.v_japan.hidden = False
					
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
							
	def nextSet(self,sender):
		for b in self.v_emoji.subviews:
			if b.action == self.typeChar:
				self.last_emoji += 1
				if self.last_emoji == len(self.emojis):
					self.last_emoji = 0
				b.title = self.emojis[self.last_emoji]	
				self.set_font_size(b)	
		
	def prevSet(self,sender):
		for b in self.v_emoji.subviews:
			if b.action == self.typeChar:
				self.last_emoji -= 1
				if self.last_emoji < 0:
					self.last_emoji = len(self.emojis)-1
				b.title = self.emojis[self.last_emoji]	
				self.set_font_size(b)	

	def smallKey(self, sender):
		self.small = not self.small
		if not self.v_japan.hidden:
			v = self.v_japan
		elif not self.v_katakana.hidden:
			v = self.v_katakana
		for b in v.subviews:
			if isinstance(b, ui.Button):
				if b.title == '小文字': # small keys
					pass
				elif b.name == 'smallkey':
					b.hidden = not self.small
				else:
					# other buttons
					if self.small:
						self.notsmall_keys[b] = b.hidden
						b.hidden = True
					else:
						b.hidden = self.notsmall_keys[b]						
				
	def capsKey(self, sender):
		self.caps = not self.caps
		if not self.caps:
			self.caps_lock = False
		for b in self.v_alpha.subviews:
			if b.title == '⇧': # caps
				b.background_color = 'white' if self.caps else 'lightgray'
			elif b.name == '⇪': # caps lock
				b.background_color = 'lightgray'
			elif b.title.isalpha():
				b.title = b.title.upper()    if self.caps else b.title.lower()
				
	def capsLock(self, sender):
		self.caps_lock = not self.caps_lock
		for b in self.v_alpha.subviews:
			if b.title == '⇧': # caps
				b.background_color = 'lightgray'
			elif b.name == '⇪': # caps lock
				b.background_color = 'white' if self.caps_lock else 'lightgray'
			elif b.title.isalpha():
				b.title = b.title.upper()    if self.caps_lock else b.title.lower()
		
	def typeChar(self,sender):
		if not self.v_emoji.hidden:
			t = sender.title
		else:
			t = sender.title[0]
		if t in [u'\u3099']:
			# we should check if previous character is Hirgana or Katakana
			#  (Python import re ....)
			if self.temp_kanji != '':
				t = self.temp_kanji[-1]
				t = chr(ord(t)+1)
				self.set_temp_kanji_lbl(self.temp_kanji[:-1] + t)	
			return			
		elif t in [u'\u309A']:
			# we should check if previous character is Hirgana or Katakana
			#  (Python import re ....)
			self.set_temp_kanji_lbl(self.temp_kanji + t)	
			return
		#elif self.small:
		#	# small keys is active in Hirgana or Katakana
		#	# only keys having a small one are visible and may thus be tapped
		#	t = self.small_keys[t]
		#	self.smallKey('unused') # force end of small keys
		if not self.v_japan.hidden:
			self.set_temp_kanji_lbl(self.temp_kanji + t)
		elif not self.v_digit.hidden:
			self.set_temp_kanji_lbl(self.temp_kanji + t)
		else:
			keyboard.insert_text(t)

		if not self.v_alpha.hidden:
			if sender.title.isalpha():
				if self.caps:
					self.capsKey('unused')

def main ():
	if not keyboard.is_keyboard():
		return

	v = MyView()
	keyboard.set_view(v, 'expanded')
	
if __name__ == '__main__':
	main()
