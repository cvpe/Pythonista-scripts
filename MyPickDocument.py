import ui
from objc_util import *
import urllib

#===================== delegate of UIDocumentPickerViewController: begin
def documentPickerWasCancelled_(_self, _cmd, _controller):
	#print('documentPickerWasCancelled_')
	UIDocumentPickerViewController = ObjCInstance(_controller)
	UIDocumentPickerViewController.uiview.close()
	if UIDocumentPickerViewController.callback:
		UIDocumentPickerViewController.callback('canceled')
	UIDocumentPickerViewController.picked = 'canceled'
	UIDocumentPickerViewController.done = True

def documentPicker_didPickDocumentsAtURLs_(_self, _cmd, _controller, _urls):
	#print('documentPicker_didPickDocumentsAtURLs_')
	UIDocumentPickerViewController = ObjCInstance(_controller)
	UIDocumentPickerViewController.uiview.close()
	urls = ObjCInstance(_urls)
	url = urllib.parse.unquote(str(urls[0]))
	if UIDocumentPickerViewController.callback:
		UIDocumentPickerViewController.callback(url)
	UIDocumentPickerViewController.picked = url
	UIDocumentPickerViewController.done = True

methods = [documentPicker_didPickDocumentsAtURLs_,documentPickerWasCancelled_]
protocols = ['UIDocumentPickerDelegate']
try:
		MyUIDocumentPickerViewControllerDelegate = ObjCClass('MyUIDocumentPickerViewControllerDelegate')
except:
	MyUIDocumentPickerViewControllerDelegate = create_objc_class('MyUIDocumentPickerViewControllerDelegate', methods=methods, protocols=protocols)
#===================== delegate of UIDocumentPickerViewController: end

#def handler(_cmd):
#	print('here')
#handler_block = ObjCBlock(handler, restype=None, argtypes=[c_void_p])
				
@on_main_thread	
def MyPickDocument(w, h, mode='sheet', popover_location=None, callback=None, title=None, UTIarray=['public.item'], PickerMode=1):
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

	UIDocumentPickerMode = PickerMode
														# 1 = UIDocumentPickerMode.open
														#   this mode allows a search field
														#   and url in delegate is the original one
														# of mode import (), 
														# 0 = UIDocumentPickerMode.import
														#   url is url of a copy
	UIDocumentPickerViewController = ObjCClass('UIDocumentPickerViewController').alloc().initWithDocumentTypes_inMode_(UTIarray,UIDocumentPickerMode)

	objc_uiview = ObjCInstance(uiview)
	SUIViewController = ObjCClass('SUIViewController')
	vc = SUIViewController.viewControllerForView_(objc_uiview)	
	
	if title:
		l = ui.Label()
		wb = 80										
		wl = uiview.width - 2*wb		# title width
		#l.border_width = 1					# for tests only
		l.text = title
		l.alignment = ui.ALIGN_CENTER
		# find greatest font size allowing to display title between buttons
		fs = 16
		while True:
			wt,ht = ui.measure_string(title,font=('Menlo',fs))
			if wt <= wl:
				break
			fs = fs - 1
		l.frame = (wb,0,wl,fs)
		l.text_color = 'green'
		UIDocumentPickerViewController.view().addSubview_(ObjCInstance(l))
	
	UIDocumentPickerViewController.setModalPresentationStyle_(3) #currentContext
	
	# Use new delegate class:
	delegate = MyUIDocumentPickerViewControllerDelegate.alloc().init()
	UIDocumentPickerViewController.delegate = delegate	
	UIDocumentPickerViewController.callback = callback	# used by delegate
	UIDocumentPickerViewController.uiview   = uiview		# used by delegate
	UIDocumentPickerViewController.done = False
	vc.presentViewController_animated_completion_(UIDocumentPickerViewController, True, None)#handler_block)
	UIDocumentPickerViewController.view().setTintColor_(ObjCClass('UIColor').colorWithRed_green_blue_alpha_(1.0,0.0,0.0,1.0))
	
	return UIDocumentPickerViewController

def main():
		# demo code
		def callback(param):
			# you could check if file save at hoped place...
			print(param)
		MyPickDocument(600,500, callback=callback, title='test')
		#MyPickDocument(600,500, mode ='popover', popover_location=(mv.width-40,60))

if __name__ == '__main__':
	main()
