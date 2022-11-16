import keyboard
import ui
from objc_util import *
import clipboard
#import speech
import sys
from gestures import *

import time
import threading

version = '00.08'

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
		t = keyboard.get_input_context()	# current line
		if not t:
			return
		l = len(t[1])
		keyboard.move_cursor(+l)
		move = my_thread(1)
		move.start()
		
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
				xx = x + dxdy[i][0] * (self.d+self.dd)
				yy = y + dxdy[i][1]	* (self.d+self.dd)					
				bb = self.make_button(xx,yy,self.d,keys[i],None, super=super)
				bb.hidden = True
				bb.assoc = b
				#ObjCInstance(bb).isAccessibilityElement = True
				#ObjCInstance(bb).accessibilityLabel = keys[i]
				
	def hide_all(self):
		for k in self.vs.keys():
			self.vs[k].hidden = True
				
	def b_japan_action(self, sender):
		self.hide_all()
		self.v_japan.hidden = False
				
	def b_alpha_action(self, sender):
		self.hide_all()
		self.v_alpha.hidden = False
		
	def b_digit_action(self, sender):
		self.hide_all()
		self.v_digit.hidden = False
		
	def b_emoji_action(self, sender):
		self.hide_all()
		self.v_emoji.hidden = False
		
	def make_button(self,x,y,d,title,action, super=None):
		b = ui.Button()
		b.frame = (x,y,d,d)
		b.background_color = 'white'
		b.border_width = 1
		b.corner_radius = self.d/4
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
		
	def typeChar(self,sender):
		keyboard.insert_text(sender.title)

	def nextSet(self,sender):
		i_set = sender.i_set + 1
		if i_set == sender.n_sets:
			i_set = 0
		#attach our accessory to the textfield, and textview
		ww = self.vv_array[i_set]
		ww.bring_to_front()
		
	def prevSet(self,sender):
		i_set = sender.i_set - 1
		if i_set == -1:
			i_set = sender.n_sets - 1
		#attach our accessory to the textfield, and textview
		ww = self.vv_array[i_set]
		ww.bring_to_front()
		
	def dimensions(self):				
		w,h = self.bounds.size
		
		h_icons = 40	# height for emoji's icons
		h_icons =  0
		
		lv = ui.Label()
		lv.text = 'V' + version
		lv.font = ('Menlo', 12)
		lv.text_color = 'blue'
		lvw = ui.measure_string(lv.text, font=lv.font)
		lv.frame = (w-2-lvw[0],h_icons+2,lvw[0],20)
		self.add_subview(lv)
	
		dd = 2
		d = (h-4*dd-h_icons)/4
		x0 = (w -3*d - 2*dd)/2
		self.d = d
		self.dd = dd
		
		self.v_japan = ui.View()
		self.v_japan.background_color = self.background_color
		self.v_japan.frame = (0,0,w,h)
		self.v_japan.hidden = False
		self.add_subview(self.v_japan)
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
		
		self.vs = {'japan':self.v_japan, 'alpha':self.v_alpha, 'digit':self.v_digit, 'emoji':self.v_emoji}
		
		# あ,い,う,え,お
		# か,き,く,け,こ
		# さ,し,す,せ,そ
		# た,ち,つ,て,と
		# な,に,ぬ,ね,の
		# は,ひ,ふ,へ,ほ
		# ま,み,む,め,も
		# や,「,ゆ,」,よ
		# ら,りる,れ,ろ
		# わ,を,ん,ー								

		keyboards = {'japan':[
			[0,0,'文頭',self.b_top_action,''],
			[1,0,'⬆️',self.b_up_action,''],
			[2,0,'read to\ncursor',self.b_read_to_cursor_action,''],
			[3,0,'read\nall',self.b_read_all_action,''],
			[0,1,'⬅️',self.b_left_action,''],
			[1,1,'文末',self.b_bottom_action,''],	# end of sentence
			[2,1,'➡️',self.b_right_action,''],
			[0,2,'copy' if keyboard.has_full_access() else 'no full' ,self.b_copy_action,''],
			[1,2,'⬇️',self.b_down_action,''],
			[2,2,'左削除',self.b_delete_action,''],							
			[3,1,'さ',self.typeChar,'しせすソ'],
			[3,2,'わ',self.typeChar,'ゐゑを '],
			[-1,1,'abc', self.b_alpha_action,''],
			[-1,2,'123', self.b_digit_action,''],
			[-1,3,'😀', self.b_emoji_action,'']
			],
			'alpha':[
			[1,0,'a',self.typeChar,'bc  '],
			[2,0,'d',self.typeChar,'ef  '],
			[3,0,'g',self.typeChar,' hi '],
			[1,1,'j',self.typeChar,' kl '],
			[2,1,'m',self.typeChar,' no '],
			[3,1,'p',self.typeChar,'qrs '],
			[1,2,'t',self.typeChar,' uv '],
			[2,2,'w',self.typeChar,'xyz '],
			[-1,1,'⬅️➡️', self.b_japan_action,''],
			[-1,2,'123', self.b_digit_action,''],
			[-1,3,'😀', self.b_emoji_action,'']
			],
			'digit':[
			[1,0,'1',self.typeChar,''],
			[2,0,'2',self.typeChar,''],
			[3,0,'3',self.typeChar,''],
			[1,1,'4',self.typeChar,''],
			[2,1,'5',self.typeChar,''],
			[3,1,'6',self.typeChar,''],
			[1,2,'7',self.typeChar,''],
			[2,2,'8',self.typeChar,''],
			[3,2,'9',self.typeChar,''],
			[2,3,'0',self.typeChar,''],
			[-1,1,'abc', self.b_alpha_action,''],
			[-1,2,'⬅️➡️', self.b_japan_action,''],
			[-1,3,'😀', self.b_emoji_action,'']
			],	
			'emoji':[
			[-1,1,'abc', self.b_alpha_action,''],
			[-1,2,'123', self.b_digit_action,''],
			[-1,3,'⬅️➡️', self.b_japan_action,'']
			]
			}
			
		# {'a':'bc  ', 'd':'ef  ', 'g':' hi ', 'j':' kl ', 'm':' no ', 'p':'qrs ', 't':' uv ', 'w':'xyz '}

		for kbd in keyboards.keys():		
			for ix,iy,t,act,flick in keyboards[kbd]:
				x = x0 + ix * (d+dd)
				y = h_icons + dd + iy * (d + dd)
				b = self.make_button(x,y,d,t,act,super=self.vs[kbd])
				if flick:
					long_press(b,self.long_press_handler)
					self.sub_keys(x,y,flick,b, わp7super=self.vs[kbd])
		
		# emoticon keys
		d = 32
		dd = 4
		w_buttons = 0

		emojis = '😊😜😱💦☔️(笑)☀️☁️☃️❄️🍙🍔🚗🌈⭐️😀😃😄😁😆😅😂🤣☺️😊😇🙂🙃😉😌😍🥰😘😗😙😚😋😛😝😜🤪🤨🧐🤓😎🤩🥳😏😒😞😔😟😕🙁☹️😣😖😫😩🥺😢😭😤😠😡🤬🤯😳🥵🥶😨😰😥😓🤗🤔🤭🤫🤥😶😐😑😬😦😧😮😲😴'
		n_emojis_in_set = 8
		n_sets = 1 + int((len(emojis)-1)/n_emojis_in_set)
		self.vv_array = []
		for i_set in range(0,n_sets):
			l = int(len(emojis)/n_sets)
			i = i_set * l
			set_emojis = emojis[i:i+l] + '⏩⏪'
			w, h = ui.get_screen_size() 
			vv = ui.View(name='set'+str(i_set))
			vv.background_color = 'lightgray'
			h = 0
			x = dd
			y = dd
			for button_title in set_emojis:
				b = ui.Button(title=button_title)
				if button_title == '⏩':
					b_action = self.nextSet
					b.i_set = i_set
					b.n_sets = n_sets
					b.name = 'nextSet'
				elif button_title == '⏪':
					b_action = self.prevSet
					b.i_set = i_set
					b.n_sets = n_sets
					b.name = 'prevSet'
				else:
					b_action = self.typeChar
				b.action=b_action
				b.frame = (x,y,d,d)
				b.font = ('.SFUIText', d)
				if (y+d+dd) > h:
					h = y + d + dd
				vv.add_subview(b)
				x = x + d + dd
				if (x+d+dd) > w:
					x = dd
					y = y + d + dd
			vv.frame = (w_buttons,0,w-w_buttons,h)
			self.vv_array.append(vv)
			self.v_emoji.add_subview(vv)  
			
		i_set = 0
		self.nextSet(self.vv_array[n_sets-1]['nextSet'])  # display 1st set
		
def main ():
	if not keyboard.is_keyboard():
		return

	v = MyView()
	keyboard.set_view(v, 'expanded')
	
if __name__ == '__main__':
	main()
