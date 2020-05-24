import keyboard
import ui
from objc_util import *
import clipboard
import speech
import sys

import time
import threading
			  
class MyView(ui.View):
	def __init__(self, *args, **kwargs):
		super().__init__(self, *args, **kwargs)
		self.background_color = 'lightgray'
		
		# bounds not yet known in init, let some delay		
		ui.delay(self.dimensions,0.1)
		
	def dimensions(self):				
		w,h = self.bounds.size
		
		h_icons = 40
		
		dd = 2
		d = (h-4*dd-h_icons)/3
		x0 = (w -3*d - 2*dd)/2

		x = x0 - d/2
		y = h_icons + dd		
		b_top = ui.Button()
		b_top.frame = (x,y,d,d)
		b_top.corner_radius = d/4
		b_top.title = '文頭' # begin of sentence
		b_top.background_color = 'white'
		b_top.	border_width = 1
		def b_top_action(sender):
			t = keyboard.get_input_context()	# current line
			l = len(t[0])
			keyboard.move_cursor(-l)
		b_top.action = b_top_action
		self.add_subview(b_top)

		x = x0 + 1 * (d + dd)
		y = h_icons + dd
		b_up = ui.Button()
		b_up.frame = (x,y,d,d)
		b_up.corner_radius = d/4
		b_up.title = '⬆️'
		b_up.background_color = 'white'
		b_up.border_width = 1
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
		b_up.action = b_up_action
		self.add_subview(b_up)

		x = x0
		y = h_icons + dd + 1 * (d + dd)
		b_left = ui.Button()
		b_left.frame = (x,y,d,d)
		b_left.corner_radius = d/4
		b_left.title = '⬅️'
		b_left.background_color = 'white'
		b_left.border_width = 1
		def b_left_action(sender):
			keyboard.move_cursor(-1)
		b_left.action = b_left_action
		self.add_subview(b_left)
		x = x0 + 1 * (d + dd)
		y = h_icons + dd + 1 * (d + dd)
		b_bottom = ui.Button()
		b_bottom.frame = (x,y,d,d)
		b_bottom.corner_radius = d/4
		b_bottom.title = '文末'	# end of sentence
		b_bottom.background_color = 'white'
		b_bottom.border_width = 1
		def b_bottom_action(sender):
			t = keyboard.get_input_context()	# current line
			l = len(t[1])
			keyboard.move_cursor(+l)
			move = my_thread(1)
			move.start()
		b_bottom.action = b_bottom_action
		self.add_subview(b_bottom)

		x = x0 + 2 * (d + dd)
		y = h_icons + dd + 1 * (d + dd)
		b_right = ui.Button()
		b_right.frame = (x,y,d,d)
		b_right.corner_radius = d/4
		b_right.title = '➡️'
		b_right.background_color = 'white'
		b_right.border_width = 1
		def b_right_action(sender):
			keyboard.move_cursor(+1)
		b_right.action = b_right_actio
		self.add_subview(b_right)

		x = x0 - d/2
		y = h_icons + dd + 2 * (d + dd)		
		b_copy = ui.Button()
		b_copy.frame = (x,y,d,d)
		b_copy.corner_radius = d/4
		if keyboard.has_full_access():
			b_copy.title = 'copy'
		else:
			b_copy.title = 'no full'			
		b_copy.background_color = 'white'
		b_copy.border_width = 1
		def b_copy_action(sender):
			context = keyboard.get_input_context()
			t = keyboard.get_selected_text()
			clipboard.set(t)
		b_copy.action = b_copy_action
		self.add_subview(b_copy)

		x = x0 + 1 * (d + dd)
		y = h_icons + dd + 2 * (d + dd)
		b_down = ui.Button()
		b_down.frame = (x,y,d,d)
		b_down.corner_radius = d/4
		b_down.title = '⬇️'
		b_down.background_color = 'white'
		b_down.border_width = 1
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
		b_down.action = b_down_action
		self.add_subview(b_down)
		
		x = x0 + 2 * (d + dd) + dd + d/2
		y = h_icons + dd + 2 * (d + dd)
		b_delete = ui.Button()
		b_delete.frame = (x,y,d,d)
		b_delete.corner_radius = d/4
		b_delete.title = '左削除' 	# delete
		b_delete.background_color = 'white'
		b_delete.border_width = 1
		def b_delete_action(sender):
			keyboard.backspace(times=1)
		b_delete.action = b_delete_action
		self.add_subview(b_delete)
		
		d = 32
		dd = 4
		w_buttons = 0

		#create normal keys
		emojis = '😊😜😱💦☔️(笑)☀️☁️☃️❄️🍙🍔🚗🌈⭐️😀😃😄😁😆😅😂🤣☺️😊😇🙂🙃😉😌😍🥰😘😗😙😚😋😛😝😜🤪🤨🧐🤓😎🤩🥳😏😒😞😔😟😕🙁☹️😣😖😫😩🥺😢😭😤😠😡🤬🤯😳🥵🥶😨😰😥😓🤗🤔🤭🤫🤥😶😐😑😬😦😧😮😲😴'
		n_emojis_in_set = 10
		n_sets = 1 + int((len(emojis)-1)/n_emojis_in_set)
		self.vv_array = []
		for i_set in range(0,n_sets):
			l = int(len(emojis)/n_sets)
			i = i_set * l
			set_emojis = emojis[i:i+l] + '⏩'
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
		
	def typeChar(self,sender):
		keyboard.insert_text(sender.title)

	def nextSet(self,sender):
		i_set = sender.i_set + 1
		if i_set == sender.n_sets:
			i_set = 0
		#attach our accessory to the textfield, and textview
		ww = self.vv_array[i_set]
		ww.bring_to_front()
		
def main():
	if not keyboard.is_keyboard():
		return
	v = MyView()
	keyboard.set_view(v, 'expanded')
	
if __name__ == '__main__':
	main()
