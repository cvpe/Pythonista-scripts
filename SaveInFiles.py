from objc_util import *
import os
import ui

#===================== delegate of UIDocumentPickerViewController: begin
def documentPickerWasCancelled_(_self, _cmd, _controller):
	#print('documentPickerWasCancelled_')
	UIDocumentPickerViewController = ObjCInstance(_controller)
	UIDocumentPickerViewController.uiview.close()
	if UIDocumentPickerViewController.callback:
		UIDocumentPickerViewController.callback('canceled')

def documentPicker_didPickDocumentsAtURLs_(_self, _cmd, _controller, _urls):
	#print('documentPicker_didPickDocumentsAtURLs_')
	UIDocumentPickerViewController = ObjCInstance(_controller)
	UIDocumentPickerViewController.uiview.close()
	if UIDocumentPickerViewController.callback:
		urls = ObjCInstance(_urls)
		UIDocumentPickerViewController.callback(str(urls[0]))

methods = [documentPicker_didPickDocumentsAtURLs_,documentPickerWasCancelled_]
protocols = ['UIDocumentPickerDelegate']
try:
		MyUIDocumentPickerViewControllerDelegate = ObjCClass('MyUIDocumentPickerViewControllerDelegate')
except Exception as e:
	MyUIDocumentPickerViewControllerDelegate = create_objc_class('MyUIDocumentPickerViewControllerDelegate', methods=methods, protocols=protocols)
#===================== delegate of UIDocumentPickerViewController: end

@on_main_thread	
def SaveInFiles(file, w, h, mode='sheet', popover_location=None, callback=None, title=None):
	# view needed for picker
	uiview = ui.View()
	uiview.frame = (0,0,w,h)
	if mode == 'sheet':
		uiview.present('sheet',hide_title_bar=True)
	elif mode == 'popover':
		if popover_location:
			uiview.present('popover', hide_title_bar=True, popover_location=popover_location)
		else:
			return
	else:
		return
	url = nsurl(file)
	urls = [url]
	UIDocumentPickerMode = 2	# 2 = UIDocumentPickerModeExportToService (copy)
														# 3 = UIDocumentPickerModeMoveToService   (move)⚠️
	UIDocumentPickerViewController = ObjCClass('UIDocumentPickerViewController').alloc().initWithURLs_inMode_(urls, UIDocumentPickerMode)
	
	# Use new delegate class:
	delegate = MyUIDocumentPickerViewControllerDelegate.alloc().init()
	UIDocumentPickerViewController.delegate = delegate	
	UIDocumentPickerViewController.setModalPresentationStyle_(3) #currentContext
	UIDocumentPickerViewController.callback = callback	# used by delegate
	UIDocumentPickerViewController.uiview   = uiview		# used by delegate

	# only to show it is possible to add controls on ViewController
	if title:	
		l =ui.Label()
		wb = 100										# button width
		wl = uiview.width - 2*wb		# title width
		#l.border_width = 1					# for tests only
		l.text = title
		# find greatest font size allowing to display title between buttons
		fs = 32
		while True:
			wt,ht = ui.measure_string(title,font=('Menlo',fs))
			if wt <= wl:
				break
			fs = fs - 1
		l.frame = (wb,42,wl,32)
		l.text_color = 'green'
		UIDocumentPickerViewController.view().addSubview_(ObjCInstance(l))
	
	objc_uiview = ObjCInstance(uiview)
	SUIViewController = ObjCClass('SUIViewController')
	vc = SUIViewController.viewControllerForView_(objc_uiview)	
	vc.presentViewController_animated_completion_(UIDocumentPickerViewController, True, None)
					
if __name__ == '__main__':
	# demo code
	mv = ui.View()
	mv.background_color = 'white'
	mv.name = 'Test Save local file to Files without open_in'
	b = ui.ButtonItem()
	b.title = 'save to Files'
	def b_action(sender):
		file  = os.path.expanduser('~/Documents/Welcome.md')
		title = 'your title, ex: telling user where he would save'
		#SaveInFiles(file, 600,400, callback=callback, title=title)
		SaveInFiles(file, 600,500, callback=callback, title=title, mode ='popover', popover_location=(mv.width-40,60))
	b.action = b_action
	mv.right_button_items = (b,)
	l_urls = ui.TextView(name='urls')
	l_urls.flex = 'W'
	l_urls.frame =(10,10,mv.width-20,32)
	mv.add_subview(l_urls)
	def callback(param):
		# you could check if file save at hoped place...
		l_urls.text = param
	mv.present()
