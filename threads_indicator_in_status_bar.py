# todo


from objc_util import *
import ui
import console
import time
import threading

class my_thread_(threading.Thread):
	def __init__(self,name):
		threading.Thread.__init__(self)
		self.name = name
		app = UIApplication.sharedApplication()
		self.bar = app.statusBar()
		b = self.bar.bounds()
		sv = self.bar.subviews()
		for v in sv:
			if v._get_objc_classname().startswith(b'SUIButton_PY3') or v._get_objc_classname().startswith(b'SUICustomViewNoDrawRect_PY3'):
				v.removeFromSuperview()
				del v
		btn = ui.Button()
		btn.action = self.button_action
		btn.frame = (140,1,50,18)
		btn.tint_color = 'red'
		btn.font = ('Courier-Bold',16)
		self.btn = btn
		self.bar.addSubview_(btn)
	def run(self):
		import threading
		import ui
		import time
		while self.btn:
			threads = threading.enumerate()
			t = ''
			for thread in threads:
				if t != '':
					t = t + '\n'
				t = t + thread.name
			self.btn.threads = t
			self.btn.title = str(threading.active_count())
			time.sleep(2)
	def button_action(self,sender):
		import ui
		x = sender.x + sender.width/2
		y = sender.y + sender.height
		tv = ui.TextView()
		tv.name = 'threads'
		tv.background_color = 'yellow'
		tv.font = ('Memlo', 15)
		tv.frame = (0,0,180,200)
		tv.text = sender.threads
		tv.height = len(tv.text.split('\n'))*(tv.font[1]+4)+4
		self.tv = tv
		cl_th = ui.ButtonItem()
		cl_th.title = 'end'
		cl_th.tint_color = 'red'
		cl_th.action = self.close_th_btn
		tv.left_button_items = (cl_th,)
		cl_tv = ui.ButtonItem()
		cl_tv.title = 'x'
		cl_tv.action = self.close_tv_btn
		tv.right_button_items = (cl_tv,)
		tv.present('popover', popover_location=(x,y), hide_title_bar=False, title_bar_color='yellow')
		tv.wait_modal()
		tv = None
	def close_tv_btn(self,sender):
		# close of textview
		self.tv.close()
		self.tv = None		
	def close_th_btn(self,sender):
		self.close_tv_btn('auto')
		# close of this program		
		sv = self.bar.subviews()
		for v in sv:
			if v._get_objc_classname().startswith(b'SUIButton_PY3') or v._get_objc_classname().startswith(b'SUICustomViewNoDrawRect_PY3'):
				v.removeFromSuperview()
				del v
		self.btn = None

# check if this thread is not already running
name = 'threads indicator in status bar'
threads = threading.enumerate()
already = False
for thread in threads:
	if thread.name	== name:
		already = True
		break
if already:
	console.hud_alert('this thread runs already, close it first','error',2)
else:
	__my_thread = my_thread_(name)	# dunder retains in globals...
	__my_thread.start()
