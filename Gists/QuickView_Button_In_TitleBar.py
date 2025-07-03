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
		tb = get_toolbar(v)
		if tb:
			return tb
			
def create_toolbar_button(action,index=0):
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
	#btn.frame = (tb.size().width - tb.rightItemsWidth()-(index+1)*40,22,40,40)
	btn.frame = (tb.size().width - 210,22,40,40)
	btn.flex='L'
	btn.image=ui.Image.named('iob:ios7_eye_outline_32').with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
	btn.action=action
	btn_obj=ObjCInstance(btn)
	__persistent_views[index]=(btn,action)
	on_main_thread(tb.superview().superview().addSubview_)(btn_obj) # in front of all buttons
	return btn
	
def remove_toolbar_button(index):
	global __persistent_views
	try:
		btn,action = __persistent_views.pop(index)
		btn.action= None
		on_main_thread(ObjCInstance(btn).removeFromSuperview)()
	except KeyError:
		pass

if 1==1:#__name__=='__main__': # if imported by pythonista startup

	@ui.in_background
	def QuickView(sender):		
		import console
		import editor
		path = editor.get_path()
		console.quicklook(path)
		
	create_toolbar_button(QuickView)
		
