import keyboard
import ui
from objc_util import *
import clipboard
#import speech
import sys
from gestures import *

import time
import threading

version = '00.07'

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
		
	def dimensions(self):				
		w,h = self.bounds.size
		
		h_icons = 40
		
		lv = ui.Label()
		lv.text = 'V' + version
		lv.font = ('Menlo', 12)
		lv.text_color = 'blue'
		lvw = ui.measure_string(lv.text, font=lv.font)
		lv.frame = (w-2-lvw[0],h_icons+2,lvw[0],20)
		self.add_subview(lv)
	
		dd = 2
		d = (h-4*dd-h_icons)/3
		x0 = (w -3*d - 2*dd)/2

		x = x0 - d/2
		y = h_icons + dd		
		def b_top_action(sender):
			t = keyboard.get_input_context()	# current line
			l = len(t[0])
			keyboard.move_cursor(-l)
		self.d = d
		self.make_button(x,y,d,'文頭',b_top_action) # begin of sentence

		x = x0 + 1 * (d + dd)
		y = h_icons + dd
		def b_up_action(sender):
			t = keyboard.get_input_context()	# current line
			l0 = len(t[0])
			l1 = len(t[1])
			keyboard.move_cursor(-l0)
			keyboard.move_cursor(-1)					# end of previous line
			t = keyboard.get_input_context()	# previous line
			l2 = len(t[0])
			l3 = len(t[1])
			#sender.title = str(l0)+' '+str(l1)+' '+str(l2)+' '+str(l3)
			if l2 >= l0:
				keyboard.move_cursor(-(l2-l0))
			else:
				pass											# line is shorter than l0, thus stay at end
		self.make_button(x,y,d,'⬆️',b_up_action)
		
		x = x0 + 2 * (d + dd)
		y = h_icons + dd
		def b_read_to_cursor_action(sender):
			t = keyboard.get_input_context()
			try:
				speech_say(t[0],'jp-JP')
			except Exception as e:
				pass
			#speech.say(t[0],'en-EN')
		self.make_button(x,y,d,'read to\ncursor',b_read_to_cursor_action)
		
		x = x0 + 3 * (d + dd)
		y = h_icons + dd
		def b_read_all_action(sender):
			keyboard.move_cursor(-1000)
			t = keyboard.get_input_context()
			try:
				speech_say(t[1],'jp-JP')
			except Exception as e:
				pass
			#speech.say(t[1],'en-EN')
		self.make_button(x,y,d,'read\nall',b_read_all_action)
		
		# flick button: start =================================================
		def long_press_handler(data):
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
								
		def sub_keys(x,y,keys,b,super=None):	
			dxdy = [(-1,0), (+1,0), (0,-1), (0,+1)]
			for i in range(4):
				if keys[i] != ' ':
					xx = x + dxdy[i][0] * (d+dd)
					yy = y + dxdy[i][1]	* (d+dd)					
					bb = self.make_button(xx,yy,d,keys[i],None, super=super)
					bb.hidden = True
					bb.assoc = b
					#ObjCInstance(bb).isAccessibilityElement = True
					#ObjCInstance(bb).accessibilityLabel = keys[i]
								
		x = x0 + 3 * (d + dd)
		y = h_icons + dd + 1 * (d + dd)
		b = self.make_button(x,y,d,'さ',self.typeChar)
		long_press(b,long_press_handler)
		#sub_keys(x,y,'BCDE', b)
		sub_keys(x,y,'しせすソ', b)
		x = x0 + 3 * (d + dd)
		y = h_icons + dd + 2 * (d + dd)
		b = self.make_button(x,y,d,'わ',self.typeChar)
		long_press(b,long_press_handler)
		sub_keys(x,y,'ゐゑを ',b)
		# flick button: end ===================================================

		x = x0
		y = h_icons + dd + 1 * (d + dd)
		def b_left_action(sender):
			keyboard.move_cursor(-1)
		self.make_button(x,y,d,'⬅️',b_left_action)
		
		x = x0 + 1 * (d + dd)
		y = h_icons + dd + 1 * (d + dd)
		def b_bottom_action(sender):
			t = keyboard.get_input_context()	# current line
			l = len(t[1])
			keyboard.move_cursor(+l)
			move = my_thread(1)
			move.start()
		self.make_button(x,y,d,'文末',b_bottom_action)   # end of sentence

		x = x0 + 2 * (d + dd)
		y = h_icons + dd + 1 * (d + dd)
		def b_right_action(sender):
			keyboard.move_cursor(+1)
		self.make_button(x,y,d,'➡️',b_right_action)

		x = x0 - d/2
		y = h_icons + dd + 2 * (d + dd)		
		def b_copy_action(sender):
			context = keyboard.get_input_context()
			t = keyboard.get_selected_text()
			clipboard.set(t)
		if keyboard.has_full_access():
			self.make_button(x,y,d,'copy',b_copy_action)
		else:
			self.make_button(x,y,d,'no full',b_copy_action)    

		x = x0 + 1 * (d + dd)
		y = h_icons + dd + 2 * (d + dd)
		def b_down_action(sender):
			t = keyboard.get_input_context()	# current line
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
		self.make_button(x,y,d,'⬇️',b_down_action)
		
		x = x0 + 2 * (d + dd) + dd # + d/2
		y = h_icons + dd + 2 * (d + dd)
		def b_delete_action(sender):
			keyboard.backspace(times=1)
		self.make_button(x,y,d,'左削除',b_delete_action)  # delete
		
		# globe button: start =================================================				
		xmin = x0 - d/2 - (d+dd)
		ymin = h_icons + dd	
		xmax = x0 + 3 * (d + dd) + d
		ymax = h_icons + dd + 2 * (d + dd) + d
		vhide = ui.View()
		vhide.frame = (xmin,ymin,xmax-xmin+1,ymax-ymin+1)
		vhide.background_color = self.background_color	
		vhide.hidden = True
		vhide.bring_to_front()
		self.add_subview(vhide)	
		
		x = dd
		y = h_icons + dd + 1 * (d + dd)
		def b_123abc_action(sender):
			vhide.hidden = not vhide.hidden
			sender.title = '123\nabc' if vhide.hidden else '↔️'
		
		self.make_button(x,y,d,'123\nabc', b_123abc_action)

		# digits
		n = 0
		for i in range(3):
			y = i * (d+dd)
			for j in range(3):
				x = j * (d+dd)
				n += 1
				#self.make_button(x,y,d,str(n), self.typeChar, super=vhide)
				
		# alphabet
		al = {'a':'bc  ', 'd':'ef  ', 'g':' hi ', 'j':' kl ', 'm':' no ', 'p':'qrs ', 't':' uv ', 'w':'xyz '}
		n = 0
		for i in range(3):
			y = i * (d+dd)
			for j in range(3):
				x = (j+1) * (d+dd)
				t = ' adgjmptw'[n]
				if t != ' ':
					b = self.make_button(x,y,d,t, self.typeChar, super=vhide)
					long_press(b,long_press_handler)
					sub_keys(x,y,al[t], b, super=vhide)
				n += 1		
		# globe button: end ===================================================	adgjmwtp	

		d = 32
		dd = 4
		w_buttons = 0

		#create normal keys
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
			self.add_subview(vv)  
			
		i_set = 0
		self.nextSet(self.vv_array[n_sets-1]['nextSet'])  # display 1st set
		
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
		
def main ():
	if not keyboard.is_keyboard():
		return

	v = MyView()
	keyboard.set_view(v, 'expanded')
	
if __name__ == '__main__':
	main()
