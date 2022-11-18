'''
todo
	- You need new flick input buttons for voiced sound mark, 
 		semi-voiced sound mark and small case conversion. 
 		Also, there is a punctuation mark button.

		For example.

		“は,ひ,ふ,へ,ほ” → “ば,び,ぶ,べ,ぼ”
		“は,ひ,ふ,へ,ほ” → “ぱ,ぴ,ぷ,ぺ,ぽ”

		In order to use this, it is necessary to operate the button after entering characters. After entering characters, you operate the button in the temporary determination state. The muddy point character is completed by the final determination. The temporary determination state is also an operation necessary for Kanji conversion, so this is also a function that cannot be removed.
		
		For example, enter "は". Then tap the voiced sound mark button. Then, the input of "ば" is completed. Press the enter button again. This is the flow to complete the final character.
		Honestly, I'm not sure if this is possible to make.
		If Kanji conversion is necessary, I will choose from the list of Kanji at this stage and decide.
		
bugs
	- flicking letters above first row or at bottom of 4th row are not visible (how to do?)

'''
import keyboard
import ui
from objc_util import *
import clipboard
#import speech
import sys
from gestures import *

import time

version = '00.13'

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
		keyboard.backspace(times=1)
		
	def b_copy_action(self, sender):
		context = keyboard.get_input_context()
		t = keyboard.get_selected_text()
		clipboard.set(t)
		
	def b_read_to_cursor_action(self, sender):
		t = keyboard.get_input_context()
		try:
			speech_say(t[0],'jp-JP')
		except Exception as e:
			pass
		#speech.say(t[0],'en-EN')
		
	def b_read_all_action(self, sender):
		keyboard.move_cursor(-1000)
		t = keyboard.get_input_context()
		try:
			speech_say(t[1],'jp-JP')
		except Exception as e:
			pass
		#speech.say(t[1],'en-EN')
		
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
		dxdy = [(-1,0), (+1,0), (0,-1), (0,+1)]
		for i in range(4):
			if keys[i] != ' ':
				xx = x + dxdy[i][0] * (self.dx+self.dd)
				yy = y + dxdy[i][1]	* (self.dy+self.dd)					
				bb = self.make_button(xx,yy,self.dx,self.dy,keys[i],None, super=super)
				bb.hidden = True
				bb.assoc = b
				if len(keys[i]) == 1:
					bb.font = ('.SFUIText', self.dy-2)
				#ObjCInstance(bb).isAccessibilityElement = True
				#ObjCInstance(bb).accessibilityLabel = keys[i]
				
	def hide_all(self):
		for k in self.vs.keys():
			self.vs[k].hidden = True
				
	def b_japan_action(self, sender):
		self.hide_all()
		self.v_japan.hidden = False
		
	def b_katakana_action(self, sender):
		self.hide_all()
		self.v_katakana.hidden = False
				
	def b_alpha_action(self, sender):
		self.hide_all()
		self.v_alpha.hidden = False
		self.caps = True
		self.caps_lock = False
		self.capsKey('unused')
		
	def b_digit_action(self, sender):
		self.hide_all()
		self.v_digit.hidden = False
		
	def b_emoji_action(self, sender):
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
		nx =6
		ny = 4
		dx = (w - (nx+1)*dd)/nx
		dy = (h - (ny+1)*dd)/ny
		self.dx = dx
		self.dy = dy
		self.dd = dd
		
		self.v_japan = ui.View()
		self.v_japan.background_color = self.background_color
		self.v_japan.frame = (0,0,w,h)
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
		self.v_digit.frame = self.frame
		self.v_digit.hidden = True
		self.add_subview(self.v_digit)
		self.v_emoji = ui.View()
		self.v_emoji.background_color = self.background_color
		self.v_emoji.frame = self.frame
		self.v_emoji.hidden = True
		self.add_subview(self.v_emoji)
				
		self.vs = {'japan':self.v_japan, 'alpha':self.v_alpha, 'digit':self.v_digit, 'emoji':self.v_emoji, 'katakana':self.v_katakana}
		
		keyboards = {'japan':[
			[1,0,'文頭',self.b_top_action,''],
			[2,0,'あ',self.typeChar,'いうえお'],			
			[3,0,'か',self.typeChar,'きくけこ'],			
			[4,0,'さ',self.typeChar,'しすせそ'],
			[5,0,'文末',self.b_bottom_action,''],	# end of sentence
			
			[1,1,'⬅️',self.b_left_action,''],
			[2,1,'た',self.typeChar,'ちつてと'],			
			[3,1,'な',self.typeChar,'にぬねの'],			
			[4,1,'は',self.typeChar,'ひふへほ'],		
			[5,1,'➡️',self.b_right_action,''],	
			
			[1,2,'⬆️',self.b_up_action,''],
			[2,2,'ま',self.typeChar,'みむめも'],			
			[3,2,'や',self.typeChar,'「ゆ」よ'],			
			[4,2,'ら',self.typeChar,'りるれろ'],			
			[5,2,'⬇️',self.b_down_action,''],
			
			[1,3,'copy' if keyboard.has_full_access() else 'no full' ,self.b_copy_action,''],		
			[2,3,'read to\ncursor',self.b_read_to_cursor_action,''],
			[3,3,'わ',self.typeChar,'をんー '],
			[4,3,'read\nall',self.b_read_all_action,''],
			[5,3,'左削除',self.b_delete_action,''],		
			
			[0,0,'カタカナ', self.b_katakana_action,''],
			[0,1,'🔤', self.b_alpha_action,''],
			[0,2,'🔢', self.b_digit_action,''],
			[0,3,'😀', self.b_emoji_action,'']
			],
			'katakana':[
			[2,0,'ア',self.typeChar,'イウエオ'],			
			[3,0,'カ',self.typeChar,'キクケコ'],			
			[4,0,'サ',self.typeChar,'シスセソ'],
			[2,1,'タ',self.typeChar,'チツテト'],						
			[3,1,'ナ',self.typeChar,'ニヌネノ'],				
			[4,1,'ハ',self.typeChar,'ヒフヘホ'],						
			[2,2,'マ',self.typeChar,'ミムメモ'],						
			[3,2,'ヤ',self.typeChar,'「ユ」ヨ'],
			[4,2,'ラ',self.typeChar,'リルレロ'],				
			[3,3,'ワ',self.typeChar,'ヲンー '],			
			[0,0,'   ⬆️\n⬅️➡️\n   ⬇️', self.b_japan_action,''],
			[0,1,'🔤', self.b_alpha_action,''],
			[0,2,'🔢', self.b_digit_action,''],
			[0,3,'😀', self.b_emoji_action,'']
			],
			'alpha':[
			[2,0,'a',self.typeChar,'bc  '],
			[3,0,'d',self.typeChar,'ef  '],
			[4,0,'g',self.typeChar,' hi '],
			[2,1,'j',self.typeChar,' kl '],
			[3,1,'m',self.typeChar,' no '],
			[4,1,'p',self.typeChar,'qrs '],
			[2,2,'t',self.typeChar,' uv '],
			[3,2,'w',self.typeChar,'xyz '],
			[1,3,'⇧',self.capsKey,''],
			[1,2,'⇪',self.capsLock,''],
			[0,0,'カタカナ', self.b_katakana_action,''],
			[0,1,'   ⬆️\n⬅️➡️\n   ⬇️', self.b_japan_action,''],
			[0,2,'🔢', self.b_digit_action,''],
			[0,3,'😀', self.b_emoji_action,'']
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
			[0,0,'カタカナ', self.b_katakana_action,''],
			[0,1,'🔤', self.b_alpha_action,''],
			[0,2,'   ⬆️\n⬅️➡️\n   ⬇️', self.b_japan_action,''],
			[0,3,'😀', self.b_emoji_action,'']
			],	
			'emoji':[
			[0,0,'カタカナ', self.b_katakana_action,''],
			[0,1,'🔤', self.b_alpha_action,''],
			[0,2,'🔢', self.b_digit_action,''],
			[0,3,'   ⬆️\n⬅️➡️\n   ⬇️', self.b_japan_action,''],
			[5,2,'⏩',self.nextSet,''],
			[5,3,'⏪',self.prevSet,'']
			]
			}
		
		#self.emojis = '😊😜😱💦☔️(笑)☀️☁️☃️❄️🍙🍔🚗🌈⭐️😀😃😄😁😆😅😂🤣☺️😊😇🙂🙃😉😌😍🥰😘😗😙😚😋😛😝😜🤪🤨🧐🤓😎🤩🥳😏😒😞😔😟😕🙁☹️😣😖😫😩🥺😢😭😤😠😡🤬🤯😳🥵🥶😨😰😥😓🤗🤔🤭🤫🤥😶😐😑😬😦😧😮😲😴'
		
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

		for kbd in keyboards.keys():		
			for ix,iy,t,act,flick in keyboards[kbd]:
				x = dd + ix * (dx+dd)
				y = dd + iy * (dy + dd)
				b = self.make_button(x,y,dx,dy,t,act,super=self.vs[kbd])
				if t in ['🔤','🔢','😀','⬆️','⬅️','⬇️','➡️', '⇧', '⇪'] or len(t) == 1:
					b.font = ('.SFUIText', dy-2)
				if t in ['⇪','⇧']:
					b.background_color = 'lightgray'
				if flick:
					long_press(b,self.long_press_handler)
					self.sub_keys(x,y,flick,b, super=self.vs[kbd])
				if kbd == 'emoji':
					if t == '⏩':
						b.name = 'nextSet'
					elif t == '⏪':
						b.name = 'prevSet'
					elif act == self.typeChar:
						self.set_emoji_font_size(b)
						
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
						
	def set_emoji_font_size(self,b):		
		# some emojis could be like multiple characters ex: '(笑)' 
		# thus we have to find the font size which permits to see the emoji,
		# else it will be seen as '...' (font size to big)
		fs = self.dy-2
		wt,ht = ui.measure_string(b.title,font=('.SFUIText', fs))
		while wt > self.dy:
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
				self.set_emoji_font_size(b)	
		
	def prevSet(self,sender):
		for b in self.v_emoji.subviews:
			if b.action == self.typeChar:
				self.last_emoji -= 1
				if self.last_emoji < 0:
					self.last_emoji = len(self.emojis)-1
				b.title = self.emojis[self.last_emoji]	
				self.set_emoji_font_size(b)	
				
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
		keyboard.insert_text(sender.title)
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
