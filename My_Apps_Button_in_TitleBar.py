# todo
# - bug: sometimes two buttons are created, one on the run button, but why?
# - bug: if too much rows, should use ScrollView instead View
# coding: utf-8
from objc_util import *
import os,ui,console
import weakref
from functools import partial

w=ObjCClass('UIApplication').sharedApplication().keyWindow()
main_view=w.rootViewController().view()

def get_toolbar(view):
	#get main editor toolbar, by recursively walking the view
	sv=view.subviews()
	for v in sv:
		if v._get_objc_classname().startswith(b'OMTabViewToolbar'):
			return v
		tb= get_toolbar(v)
		if tb:
			return tb
def create_toolbar_button(action,image,index=0):
	assert(callable(action))
	tb=get_toolbar(main_view)
	global __persistent_views
	try:
		__persistent_views
	except NameError:
		__persistent_views={}
	#check for existing button in this index and delete if needed
	remove_toolbar_button(index)	
	btn = ui.Button()
	btn.frame = (tb.size().width - tb.rightItemsWidth()-(index+1)*40,22,40,40)
	#btn.frame = (tb.size().width - 210,22,100,40)
	btn.flex='L'
	btn.image=ui.Image.named(image)
	if btn.image:
		btn.image = btn.image.with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
	else:
		btn.image = ui.Image.named('iob:alert_circled_32')				
	btn.action=action
	btn_obj=ObjCInstance(btn)
	__persistent_views[index]=(btn,action)
	tb.superview().superview().addSubview_(btn_obj) # in front of all buttons
	return btn
def remove_toolbar_button(index):
	global __persistent_views
	try:
		btn,action = __persistent_views.pop(index)
		btn.action= None
		ObjCInstance(btn).removeFromSuperview()
	except KeyError:
		pass

if 1==1:#__name__=='__main__': # if imported by pythonista startup
	def my_wrench(sender):
		import ui
		import os
		from objc_util import ObjCInstance,ObjCClass
		from PIL import Image
		import io
						
		def run_script(sender):
			import os
			#sender.superview.close()
			app,arg = sender.name.split(('|'))
			dir = os.path.expanduser('~/Documents/'+app)		
			I3=ObjCClass('PYK3Interpreter').sharedInterpreter()
			# run a script like in wrench menu (path, args, reset env yesy/no)
			I3.runScriptAtPath_argv_resetEnvironment_(dir, [arg], True)

		menu_lines = [
			[0,os.path.expanduser('~/Documents/....../your icon for app.png'), 'Examples/Animation/AnalogClock.py', 'AnalogClock',''],
			[0,os.path.expanduser('~/Documents/....../your icon for app.png'), 'Examples/Animation/Magic Text.py', 'Magic Text',''],
			[1,os.path.expanduser('~/Documents/....../your icon for app.png'), 'Examples/Games/BrickBreaker.py', 'BrickBreaker','Args app'],		
			[1,os.path.expanduser('~/Documents/....../your icon for app.png'), 'Examples/Animation/Stopwatch.py', 'Stopwatch','Args app'],						
								 ]	
		v = ui.View()
		v.frame = (0,0,600,10)
		y_col = [10,10]
		for btn_col,btn_image,btn_name,btn_title,btn_arg in menu_lines:
			bs = ui.Button()
			bs.image = ui.Image.named(btn_image)
			if bs.image:
				bs.image = bs.image.with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			else:
				bs.image = ui.Image.named('iob:alert_circled_32')				
			bs.name = btn_name + '|' + btn_arg
			bs.title = '  ' + btn_title
			ObjCInstance(bs).button().contentHorizontalAlignment= 1	# left	
			bs.action = run_script
			bs.frame = (10+btn_col*v.width/2,y_col[btn_col],v.width/2-10,40)
			v.height = max(v.height,bs.y + bs.height + 10)
			y_col[btn_col] = y_col[btn_col] + 40
			v.add_subview(bs)

		v.present('popover',popover_location=(sender.x+20,sender.y+40), hide_title_bar=True)
		
	create_toolbar_button(my_wrench,os.path.expanduser('~/Documents/...../your image for the button.png'),0)
