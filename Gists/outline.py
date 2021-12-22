'''
todo Action.sequence
==== 
- new: 0️⃣ use scrollview instead of tableview
- bug: 0️⃣ landscape, cursor on lst row, keyboard hides row
- bug: 0️⃣ You can try beginUpdates() before updating your data 
					(adding or deleting rows) then end updates() after reloading on the tableview ObjCInstance)
- bug: 0️⃣ I was deleting a line from an outline (it may have had one child note) 
					and got this:
					Traceback (most recent call last):
						File "/private/var/mobile/Containers/Shared/AppGroup/6CCAAFF1-947E-4DC8-B33B-58EE87A0823C/Pythonista3/Documents/outline.py", line 575, in tableView_heightForRowAtIndexPath_
					return tv_py.delegate.tableview_height_for_section_row(tv_py,section,row)
						File "/private/var/mobile/Containers/Shared/AppGroup/6CCAAFF1-947E-4DC8-B33B-58EE87A0823C/Pythonista3/Documents/outline.py", line 1250, in tableview_height_for_section_row
					vals,n,opts = tv.data_source.items[row]['content']
						IndexError: list index out of range
					Traceback (most recent call last):
						File "/private/var/mobile/Containers/Shared/AppGroup/6CCAAFF1-947E-4DC8-B33B-58EE87A0823C/Pythonista3/Documents/outline.py", line 575, in tableView_heightForRowAtIndexPath_
 					return tv_py.delegate.tableview_height_for_section_row(tv_py,section,row)
						File "/private/var/mobile/Containers/Shared/AppGroup/6CCAAFF1-947E-4DC8-B33B-58EE87A0823C/Pythonista3/Documents/outline.py", line 1250, in tableview_height_for_section_row
					vals,n,opts = tv.data_source.items[row]['content']
						IndexError: list index out of range
					Traceback (most recent call last):
						File "/private/var/mobile/Containers/Shared/AppGroup/6CCAAFF1-947E-4DC8-B33B-58EE87A0823C/Pythonista3/Documents/outline.py", line 2928, in tableview_cell_for_row
					hrow = self.tableview_height_for_section_row(tableview,section,row)
						File "/private/var/mobile/Containers/Shared/AppGroup/6CCAAFF1-947E-4DC8-B33B-58EE87A0823C/Pythonista3/Documents/outline.py", line 1250, in tableview_height_for_section_row
					vals,n,opts = tv.data_source.items[row]['content']
						IndexError: list index out of range
- bug: 0️⃣  @jonB said: I haven't tested it, but it looks like
						https://github.com/andy-landy/traceback_with_variables
						Should work with pythonista.
						This might provide some more useful tracebacks -- that traceback implies that kwargs got stomped on somehow. It could be useful to know what it was stomped with.
- bug: 0️⃣ - no more use of eventIdentifier for due date event
					- unique id in location for outline in 2022
					- unique id in location for due date
- bug: 0️⃣ undo: bad successive (ex: font)
					- explain: multiple undo's is heavy about memory usage
					- setting? maximum number of successiveundo's (ex:100)
					- undo which reset rows would have to recreate events
						- better: no undo possible if file saved
					- undo but format switch 'has ouTline' changed...
					- think a better way: memo only differences between successive .items
						- add characters only updates one row
							memo= ([row],{'text':text})
						- font attributes only updates one row
							memo = {'content':(vals,n,opts)} because attribs in opts
						- set due date only updates one row and add/del event
						- setting switch 'has outline' changes all rows (['outline'])
							memo switch?
						- add new row change vals of next rows
							memo = ([row],'content':(vals,n,opts))
						- promote/demote idem
						- hide/unhide children
							memo = {'content':(vals,n,opts)} because 'hidden' in opts
						- add image only updates one row
							memo = {'content':(vals,n,opts)} because 'images' in opts
						- how to memo updates? rows, parts of items
						- each dates update at each row text update 'content':(vals,n,opts))
						- actually: memo items before
							future: memo changes before and after?
							
						- exemple
							- action = change attributes of text of row
							- save previous (row,items[row]['content']) 
							- undo is to reset previous items[row]['content']
- new: 0️⃣ events
					- 🔟 ask: update txt/outline => update event title, notes, if event exists
					- 🔟 ask: rename file => update event title, notes, url
						- scan all items, if due date eventid, update	title and url
- new: 🔟	If the program gets a wider audience you might also consider making
					the calendar event functionality an option or else there will be errors if the calendar is not setup , as well as making the calendar name settable and perhaps the script should create the Calendar if it doesn’t exist
					- calendar events yes/no option 
						- import calendar only if option is yes
					- check: actions on self.store only if option is yes
					- calendar name as setting
					- create the calendar if not exists (so easy manually)
- new: 🔟 - 2nd color for underline, strike, outline fill, shadow *** in progress
						*** attention: support o alone and o(r,g,b) in existing opts['attribs']
					- exponent baselineOffset = font_size/4 font_size=1/2 *** in progress
					- indice font_size=1/2 *** in progress
					- image in switch a²
- new: 🔟 2nd arg as a path to open 1st arg outline from other path than current
					*** in progress
					should work for arg1 = file 
											for arg1 = .ext 
- new: 🔟 font_size by level
					- ask: quid for outline "1.2" nicer if same size for each level?
					- bouton level size
					- tableview levels max number of levels in formats types
					- enter value by level (init = actual font size in each level)
					- store in outline.prm or in content? think, ask @ihf
					- row height
					- cell for row
					- sure that no self.font_size * number rows
- new: 🔟 create drawing as image, save like other images
					- other way: draw string or strokes via path, store commands as strings
						not as images in content? 
'''
import appex
from   ast        import literal_eval
import clipboard
from   collections import Sequence
import console
from   datetime  import datetime
from   dialogs   import _FormDialogController
from   functools import partial
from   inspect   import stack
from   io        import BytesIO
from   math      import isinf
from   objc_util import *
import os
from   photos    import get_assets, pick_asset
from   PIL       import Image
from   PyPDF2    import PdfFileMerger
import requests
from   re        import finditer
from   sys       import _getframe, argv, version_info
from   threading import Event
from   time      import sleep
import ui
from   unicodedata import normalize
import urllib.parse
import webbrowser

load_framework('EventKitUI')

mytrace_file = open('outline.trace', mode='wt', buffering=1)	
def mytrace(called):
	# inspect.stack()[1][3])
	prt = str(called)
	#print(prt)
	i = prt.find("function='")
	i += 10
	j = prt.find("'", i)
	prt = prt[i:j]
	#print('mytrace: ',prt)
	t = datetime.now()
	prt = f'{t:%Y%m%d %H%M%S.%f} {prt} \n'
	try:
		mytrace_file.write(prt)
	except:
		pass	
	
def automatic_download(module, url, target):
	if target:
		path = os.path.expanduser('~/Documents/' + target + '/' + module)
	else:
		path = module
	if not os.path.exists(path):
		b = console.alert('Needed module\n'+module+'\ndoes not exist', 'do you want to automatically download it?', 'yes', 'no', hide_cancel_button=True)
		if b == 1:
			try:
				if module == 'blackmamba':
					exec(requests.get('http://bit.ly/get-blackmamba').text)
				else:
					data = requests.get(url).content
					with open(path,mode='wb') as out_file:
						out_file.write(data)
			except Exception as E:
				#print('error',E)
				console.alert('Automatic download of\n' + module, 'did not work', 'ok', hide_cancel_button=True)				
				if not target:
					target = 'same folder as outline.py'
				if url:
					print('try to download manually ' + module + ' in ' + target + ' from ' + url)
				else:
					print('try to download manually blackmamba by typing in console:\n\n' + "import requests as r; exec(r.get('http://bit.ly/get-blackmamba').text)")
			
automatic_download('SetTextFieldPad.py', 'https://raw.githubusercontent.com/cvpe/Pythonista-scripts/master/SetTextFieldPad.py', 'site-packages')
automatic_download('File_Picker.py', 'https://raw.githubusercontent.com/cvpe/Pythonista-scripts/master/File_Picker.py', 'site-packages')
automatic_download('gestures.py', 'https://raw.githubusercontent.com/mikaelho/pythonista-gestures/master/gestures.py', 'site-packages')
automatic_download('swizzle.py', 'https://raw.githubusercontent.com/jsbain/objc_hacks/master/swizzle.py', 'site-packages')
automatic_download('outline.versions', 'https://raw.githubusercontent.com/cvpe/Pythonista-scripts/master/Gists/outline.versions', '')
automatic_download('blackmamba', '', 'site-packages-3')
	
try:
	from   SetTextFieldPad import SetTextFieldPad
	import File_Picker
	from   gestures  import *
	from   blackmamba.uikit.keyboard import (register_key_event_handler, UIEventKeyCode,           UIKeyModifier, unregister_key_event_handlers)
	if not appex.is_running_extension():
		import swizzle
		
	Version = 'V01.32'
	with open('outline.versions', mode='rt', encoding='utf-8', errors="surrogateescape") as fil:	
		Versions = fil.read()
		
except:
	console.alert('Not all imported modules exist', 'see errors in console', 'ok', hide_cancel_button=True)
	exit()	
	
# check if new version is available
try:
	url = 'https://raw.githubusercontent.com/cvpe/Pythonista-scripts/master/Gists/outline.versions'
	data = requests.get(url).content
	new_version = data.decode("utf-8")[8:14]
	# ex: b'Version Vxx.yy\n
	if new_version > Version:
		b = console.alert(f"A new version {new_version} is available", 'do you want to install it?', 'yes', 'no', hide_cancel_button = True)
		if b == 1:
			# install new versions file
			with open('outline.versions', mode='wb') as out_file:
				out_file.write(data)
			# install new outline program
			url = 'https://raw.githubusercontent.com/cvpe/Pythonista-scripts/master/Gists/outline.py'
			data = requests.get(url).content
			with open('outline.py', mode='wb') as out_file:
				out_file.write(data)
			del data
			console.alert(f"New version {new_version} has been installed\n\n.py\n.versions", 'Pythonista will now automatically abort!\nPlease restart it afterwards', 'ok', hide_cancel_button = True)
			os.abort()
except Exception as e:
	#print('error',e)
	pass
	
#===================== delegate of UIDocumentPickerViewController: begin
def documentPickerWasCancelled_(_self, _cmd, _controller):
	mytrace(inspect.stack())
	#print('documentPickerWasCancelled_')
	UIDocumentPickerViewController = ObjCInstance(_controller)
	UIDocumentPickerViewController.uiview.close()
	if UIDocumentPickerViewController.callback:
		UIDocumentPickerViewController.callback('canceled')
	UIDocumentPickerViewController.picked = 'canceled'
	UIDocumentPickerViewController.done = True

def documentPicker_didPickDocumentsAtURLs_(_self, _cmd, _controller, _urls):
	mytrace(inspect.stack())
	#print('documentPicker_didPickDocumentsAtURLs_')
	UIDocumentPickerViewController = ObjCInstance(_controller)
	UIDocumentPickerViewController.uiview.close()
	urls = ObjCInstance(_urls)
	if len(urls) == 1:
		url = urllib.parse.unquote(str(urls[0]))
	else:
		url = []
		for i in range(0,len(urls)):
			url.append(urllib.parse.unquote(str(urls[i])))
	if UIDocumentPickerViewController.callback:
		UIDocumentPickerViewController.callback(url)
	UIDocumentPickerViewController.picked = url
	UIDocumentPickerViewController.done = True

methods = [documentPicker_didPickDocumentsAtURLs_,documentPickerWasCancelled_]
protocols = ['UIDocumentPickerDelegate']
try:
		MyUIDocumentPickerViewControllerDelegate = ObjCClass('MyUIDocumentPickerViewControllerDelegate')
except Exception as e:
	MyUIDocumentPickerViewControllerDelegate = create_objc_class('MyUIDocumentPickerViewControllerDelegate', methods=methods, protocols=protocols)
#===================== delegate of UIDocumentPickerViewController: end

#===================== delegate of EKEventEditViewController: begin
EKEventEditViewController = ObjCClass('EKEventEditViewController')
def eventEditViewController_didCompleteWithAction_(_self, _cmd, _controller, _action):
    global mv
    #print(_action)	# 0=canceled 1=saved
    mv.eventEditViewControllerAction = _action
    mv.eventEditViewControllerUIView.close()
        
try:
  MyEventEditViewDelegate = ObjCClass('MyEventEditViewDelegate')
except:
  MyEventEditViewDelegate = create_objc_class(
    'MyEventEditViewDelegate',
    methods=[eventEditViewController_didCompleteWithAction_,],
    protocols=['EKEventEditViewDelegate']
)
#===================== delegate of EKEventEditViewController: end

NSMutableAttributedString = ObjCClass('NSMutableAttributedString')
NSForegroundColorAttributeName = ns('NSColor')
NSBackgroundColorAttributeName = ns('NSBackgroundColor')
UIColor = ObjCClass('UIColor')
NSStrikethroughStyleAttributeName = ns('NSStrikethrough')
NSStrikethroughColorAttributeName = ns('NSStrikethroughColor')
NSStrokeColorAttributeName = ns('NSStrokeColor')
NSStrokeWidthAttributeName = ns('NSStrokeWidth')
NSObliquenessAttributeName = ns('NSObliqueness')
NSBaselineOffsetAttributeName = ns('NSBaselineOffset')
NSShadow = ObjCClass('NSShadow')
NSShadowAttributeName = ns('NSShadow')
UIFont = ObjCClass('UIFont')
NSFontAttributeName = ns('NSFont')
NSLinkAttributeName = ns('NSLink')
NSUnderlineStyleAttributeName = ns('NSUnderline')
font = UIFont.fontWithName_size_('Menlo', 18)
font_hidden = UIFont.fontWithName_size_('Menlo', 6)

SUIViewController = ObjCClass('SUIViewController')
UIFontPickerViewController = ObjCClass('UIFontPickerViewController')
UIFontPickerViewControllerConfiguration = ObjCClass('UIFontPickerViewControllerConfiguration')

pad_integer = [{'key':'1'},{'key':'2'},{'key':'3'},
	{'key':'back space','icon':'typb:Delete'},
	{'key':'new row'},
	{'key':'4'},{'key':'5'},{'key':'6'},
	#{'key':'delete','icon':'emj:Multiplication_X'},
	{'key':'new row'},
	{'key':'7'},{'key':'8'},{'key':'9'},
	{'key':'new row'},
	{'key':'nul'},{'key':'0'},{'key':'nul'},{'key':'⏎','SFicon':'return'}]

bs = '\b'
lf ='\n'
tab = '\t'

PY3 = version_info[0] >= 3
if PY3:
	basestring = str
	
def my_form_dialog(title='', fields=None, sections=None, done_button_title='Done', wd=500, hd=500, kbd_button=False):
	global cc, mv
	mytrace(inspect.stack())
	wd = min(wd,mv.get_screen_size()[0])
	# copy of dialogs.form_dialog
	if not sections and not fields:
		raise ValueError('sections or fields are required')
	if not sections:
		sections = [('', fields)]
	if not isinstance(title, basestring):
		raise TypeError('title must be a string')
	for section in sections:
		if not isinstance(section, Sequence):
			raise TypeError('Sections must be sequences (title, fields)')
		if len(section) < 2:
			raise TypeError('Sections must have 2 or 3 items (title, fields[, footer]')
		if not isinstance(section[0], basestring):
			raise TypeError('Section titles must be strings')
		if not isinstance(section[1], Sequence):
			raise TypeError('Expected a sequence of field dicts')
		for field in section[1]:
			if not isinstance(field, dict):
				raise TypeError('fields must be dicts')
				
	header0 = sections[0][0]
	if header0 != '':
		sections[0] = (' ',sections[0][1])
		#sections = [('',sections[0][1])] + [sections[1:]]

	cc = _FormDialogController(title, sections, done_button_title=done_button_title)
	cc.container_view.frame = (0, 0, wd, hd)
	cc.view.frame = (0, 0, wd, hd)

	# assure that path in he<der title is not shown in capitals
	if header0 != '':
		tblo = ObjCInstance(cc.view)
		hh = 60
		tblo.sectionHeaderHeight = hh
		header = ui.Label()
		header.number_of_lines = 0
		header.text = header0
		dx = 15
		header.frame = (dx,0,wd-dx,hh)
		header.font = ('Menlo',12)
		header.text_color = 'blue'
		# uncomment next line of you want to see room of label
		#header.border_width = 1 # only for tests
		cc.view.add_subview(header)


	#==================== dialogs.form_dialog modification 1: begin	
	w_for_segments = 240
	w_for_label = wd - w_for_segments - 10 - 10
	# first loop to compute max width of labels
	nc = 0
	for i in range(0,len(cc.cells[0])):			# loop on rows of section 0
		cell = cc.cells[0][i]									# ui.TableViewCell of row i
		if len(cell.content_view.subviews) > 0:
			nc = max(nc, len(cell.text_label.text))
	ft = ('Menlo',14)
	wt = ui.measure_string(' '*nc, font=ft)[0] + 10
	font_size = min(14, int(14*w_for_label/wt))
	ft = ('Menlo',font_size)
	
	for i in range(0,len(cc.cells[0])):			# loop on rows of section 0
		cell = cc.cells[0][i]									# ui.TableViewCell of row i
		# some fields types are subviews of the cell:
		#   text,number,url,email,password,switch
		#  but check, date and time are not set as subviews of cell.content_view
		if len(cell.content_view.subviews) > 0:
			tf = cell.content_view.subviews[0] 		# ui.TextField of value in row
			cell.text_label.font = ft
			# attention: tf.name not set for date fields
			item = cc.sections[0][1][i]	# section 0, 1=items, row i
			if 'segmented' in tf.name:
				segmented = ui.SegmentedControl()
				segmented.name = cell.text_label.text
				if 'action' in item:
					segmented.action = item['action']
				segmented.frame = tf.frame
				segmented.width = w_for_segments
				segmented.x = cc.view.width - segmented.width-10 # cc.view is tableview
				segmented.segments = item['segments']
				value = item.get('value', '')
				segmented.selected_index = item['segments'].index(value)
				cell.content_view.remove_subview(tf)
				del cc.values[tf.name]
				del tf
				cell.content_view.add_subview(segmented)
				# multiline segments
				for sv in ObjCInstance(segmented).subviews():
					if sv._get_objc_classname().startswith(b'UISegmentedControl'):
						if 'accessible' in item:
							accessible = item['accessible']
							for i,access in enumerate(accessible):
								#print(item['segments'][i],access)
								if not access:
									sv.setEnabled_forSegmentAtIndex_(False,i)
						for ssv in sv.subviews():
							if ssv._get_objc_classname().startswith(b'UISegment'):
								ssv.label().numberOfLines = 0	
								ssv.label().adjustsFontSizeToFitWidth = True # auto resize font to fit
			elif isinstance(tf, ui.TextField):
				#print(tf.name)
				#tf.item = item	# if needed during checks
				tf.alignment=ui.ALIGN_RIGHT
				tf.bordered = True
				tf.font = ('Menlo',16)
				tf.flex = ''
				enabled = item.get('enabled', True)
				tf.enabled = enabled
				h = cell.content_view.height
				if 'pad' in item:
					SetTextFieldPad(tf, pad=item['pad'], textfield_did_change=cc.textfield_did_change)
					w = 80
				elif 'dates format' in tf.name:
					w = 200
				else:
					tf.font = ('Menlo',12)
					w = 50				
				tf.frame = (cc.view.width-w-10,(h-20)/2,w,20)
		
	#==================== dialogs.form_dialog modification 1: end
	
	if kbd_button:
		# Add a next button
		kbd_button = ui.ButtonItem()
		kbd_button.tint_color = 'blue'
		o = ObjCClass('UIImage').systemImageNamed_('keyboard')
		db = 32
		with ui.ImageContext(db,db) as ctx:
			o.drawAtPoint_(CGPoint(0,10))
			#o.drawInRect_(CGRect(CGPoint(0, 0), CGSize(db,db)))
			kbd_button.image = ctx.get_image()				
		kbd_button.action = kbd_button_action
		# right buttons is a tuple, the way to add an element is "+(element,)"
		cc.container_view.right_button_items = cc.container_view.right_button_items + (kbd_button,)

		
	cc.kbd = False	
	cc.container_view.present('sheet')
	cc.container_view.wait_modal()
	# Get rid of the view to avoid a retain cycle:
	cc.container_view = None
	if cc.was_canceled:
		return None
	if cc.kbd:
		return 'kbd'
	
#==================== dialogs.form_dialog modification 2: begin	
	for i in range(0,len(cc.cells[0])):			# loop on rows of section 0
		cell = cc.cells[0][i]									# ui.TableViewCell of row i
		# some fields types are subviews of the cell:
		#   text,number,url,email,password,switch
		#  but check, date and time are not set as subviews of cell.content_view
		for tf in cell.content_view.subviews:
			if 'SegmentedControl' in str(type(tf)):
				item = cc.sections[0][1][i]	# section 0, 1=items, row i
				if tf.selected_index >= 0:
					cc.values[tf.name] = item['segments'][tf.selected_index]
#==================== dialogs.form_dialog modification 2: end

	return cc.values
#==================== copied from dialogs: end

def kbd_button_action(sender):
	mytrace(inspect.stack())
	global cc
	cc.kbd = True
	cc.done_action(sender)

def fontPickerViewControllerDidPickFont_(_self, _cmd, _controller):
	global mv
	mytrace(inspect.stack())
	controller = ObjCInstance(_controller)
	font = str(controller.selectedFontDescriptor().objectForKey_('NSFontFamilyAttribute'))
	mv.set_font(font_type=font)

PickerDelegate = create_objc_class(
    'PickerDelegate',
    methods=[fontPickerViewControllerDidPickFont_],
    protocols=['UIFontPickerViewControllerDelegate']
)

class MyInputAccessoryView(ui.View):
	def __init__(self, row, *args, **kwargs):
		global mv
		mytrace(inspect.stack())
		#super().__init__(self, *args, **kwargs)	
		self.row = row
		self.width = mv.get_screen_size()[0]			# width of keyboard = screen
		self.background_color = 'lightgray'#(0,1,0,0.2)
		d = 4
		hb = 44
		self.height = 2*d + hb
		self.pad = [
		{'key':'tab','data':'\x01', 'sf':'text.chevron.right', 'x':10},
		{'key':'shift-tab','data':'\x02', 'sf':'text.chevron.left', 'x':self.width-10-hb}
		]
		self.pad.append({'key':'tab','data':'attrib', 'sf':'bold.italic.underline', 'x':self.width/4})
		if mv.device_model == 'iPhone':
			self.pad.append({'key':'tab','data':'\x00', 'sf':'keyboard.chevron.compact.down', 'x':self.width/2})
		
		# build buttons
		for pad_elem in self.pad:
			button = ui.Button()									# Button for user functionality
			button.frame = (int(pad_elem['x']),d,hb,hb)
			button.name = pad_elem['key']
			button.background_color = 'white'			# or any other color
			button.tint_color = 'black'
			button.corner_radius = 5		
			button.title = ''
			db = hb
			o = ObjCClass('UIImage').systemImageNamed_(pad_elem['sf'])
			with ui.ImageContext(db,db) as ctx:
				#o.drawAtPoint_(CGPoint(0,0))
				o.drawInRect_(CGRect(CGPoint(0, 0), CGSize(db,db)))
				button.image = ctx.get_image()				
			button.data = pad_elem['data']
			button.action = self.key_pressed
			retain_global(button) # see https://forum.omz-software.com/topic/4653/button-action-not-called-when-view-is-added-to-native-view
			self.add_subview(button)	
		
	def key_pressed(self, sender):
		global mv
		mytrace(inspect.stack())
		#import ui
		#from objc_util import ObjCClass
		tvo = sender.objc_instance.firstResponder()	# associated TextView		
		row = self.row
		#row = int(str(tvo.name()))
		if sender.data == '\x00':
			tvo.endEditing_(None)
			return
		elif sender.data == 'attrib':
			#print(row)
			mv.selected_text_attributes(row)					
			return
		mv.textview_should_change(None, [row,row], sender.data, key=True)
		#tv.insertText_(sender.data)	
		
def OMColorPickerViewController(title=None, rgb=None):
	mytrace(inspect.stack())
	v = ui.View()
	if title:
		v.name = title
	v.rgb = None
	vc = ObjCInstance(v)
	colorpicker = ObjCClass('OMColorPickerViewController').new().autorelease()
	clview = colorpicker.view()
	v.frame = (0,0,512,960)
	vc.addSubview_(clview)
	done_button = ui.ButtonItem(title='ok')
	def tapped(sender):
		mytrace(inspect.stack())
		cl = colorpicker.color()
		v.rgb = (cl.red(),cl.green(),cl.blue())
		v.close()
	done_button.action = tapped
	v.right_button_items = [done_button]
	if rgb:
		color = ObjCClass('UIColor').colorWithRed_green_blue_alpha_(rgb[0], rgb[1], rgb[2], 1.0)
		colorpicker.setColor_(color)
	v.rgb = rgb
	v.present('sheet')
	v.wait_modal()
	return v.rgb 	
	
@on_main_thread
def tableView_heightForRowAtIndexPath_(_self,_sel,tv,path):
	mytrace(inspect.stack())
	try:
		import sys, objc_util, ctypes
		# For some reason, tv returns a NSNumber.  But, our tableview is in _self
		tv_o=objc_util.ObjCInstance(_self)
		# get row and section from the path
		indexPath=objc_util.ObjCInstance(path)
		row=indexPath.row()
		#print('tableView_heightForRowAtIndexPath_',row)
		section=indexPath.section()
		# get the pyObject.  get as an opaque pointer, then cast to py_object and deref 
		pyo=tv_o.pyObject(restype=ctypes.c_void_p,argtypes=[])
		tv_py=ctypes.cast(pyo.value,ctypes.py_object).value
		# if the delegate has the right method, call it
		if tv_py.delegate and hasattr(tv_py.delegate,'tableview_height_for_section_row'):
			return tv_py.delegate.tableview_height_for_section_row(tv_py,section,row)
		else:
			return tv_py.row_height
	except Exception as e:
		import traceback
		traceback.print_exc()
		return 44
		
# set up the swizzle.. only needs to be done once
def setup_tableview_swizzle(override=False):
	mytrace(inspect.stack())
	t=ui.TableView()
	t_o=ObjCInstance(t)

	encoding=ObjCInstanceMethod(t_o,'rowHeight').encoding[0:1]+b'@:@@'
	if hasattr(t_o,'tableView_heightForRowAtIndexPath_') and not override:
		return
	swizzle.swizzle(ObjCClass(t_o._get_objc_classname()),
								('tableView:heightForRowAtIndexPath:'),
								tableView_heightForRowAtIndexPath_,encoding)

if not appex.is_running_extension():								
	#upon import, swizzle the textview class. this only ever needs to be done once 
	setup_tableview_swizzle(1)	

class Outliner(ui.View):
	def __init__(self, only_formats=False, *args, **kwargs):
		
		# only 3 variables are used if Outliner instance created with only_formats=True
		# see at main start for appex and CLIPBOARD mode
		self.first_level_has_outline = True
		self.outline_format = 'decimal'
		self.outline_formats = {
			'decimal':(['v.0','v.v','v.v.v','v.v.v.v','v.v.v.v.v','v.v.v.v.v.v', 'v.v.v.v.v.v.v', 'v.v.v.v.v.v.v.v'],2),
			'alphanumeric':(['I.', 'A.', 'i.', 'a.', '(1).', '(a).'],3),
			'traditional':(['1.', 'A.', 'i.', 'a.', '(1).', '(a).', '((1)).',   '((a)).'],3),
			'bullets':(['•', '‣', '◦', '⦿', '⁃', '⦾', '◘'],3),
			'decimal with title':(['','w.0','w.w','w.w.w','w.w.w.w','w.w.w.w.w','w.w.w.w.w.w', 'w.w.w.w.w.w.w', 'w.w.w.w.w.w.w.w'],2),
			'alphanumeric with title':(['', 'I.', 'A.', 'i.', 'a.', '(1).', '(a).'],3),
			'traditional with title':(['', '1.', 'A.', 'i.', 'a.', '(1).', '(a).', '((1)).',   '((a)).'],3),
			'bullets with title':(['', '•', '‣', '◦', '⦿', '⁃', '⦾', '◘'],3)
			}
		if only_formats:
			return
		
		ui.View.__init__(self, *args, **kwargs)
		mytrace(inspect.stack())		
		self.keyboard_y = 0
		self.edited_textview = None
		
		
		# EKEventStore = calendar database
		self.store = ObjCClass('EKEventStore').alloc().init()
		
		self.cal = None
		for cal in self.store.calendars():
			#print(cal.title())
			if str(cal.title())	== 'Outline':
				self.cal = cal
				break

		if not self.cal:
			console.alert('Pythonista not authorized to access Calendars', '\nrun once Pythonista\nwith argument\ngrant_access_to_calendar\n\nand be sure there is a calendar\nnamed "Outline"', 'ok', hide_cancel_button=True)
		
		ws,hs = self.get_screen_size()
		self.width, self.height = ws,hs
		#self.frame = (0,0,375,667)						# iPhone SE
		self.name = 'Outliner'
		self.background_color = 'white'
		
		nb = 13
		w = self.get_screen_size()[0]
		dd = 4
		wb = (w - (nb+1)*dd)/nb
		if wb > 32:
			wb = 32
			dd = (w - wb*nb)/(nb+1)
		d = int(w/nb)
		y = 10 + wb
		
		x = dd
		b_close	= ui.Button(name='b_close')
		b_close.frame = (x,y,wb,wb)
		b_close.image = ui.Image.named('iob:close_round_32')
		b_close.action = self.close_action
		self.add_subview(b_close)

		x = x + wb + dd		
		b_version = ui.Button(name='b_version')
		b_version.frame = (x,y,wb,wb)
		w12 = ui.measure_string(Version+'_',font=('Menlo',12))[0]
		fs = 12 * wb/w12
		b_version.font = ('Menlo',fs)
		b_version.title = Version
		b_version.tint_color = 'green'
		b_version.action = self.button_version_action	
		self.add_subview(b_version)

		x = x + wb + dd				
		b_files = ui.Button(name='b_files')
		b_files.frame = (x,y,wb,wb)
		b_files.image = ui.Image.named('iob:ios7_folder_outline_32')
		b_files.tint_color = 'blue'
		b_files.action = self.button_files_action	
		self.add_subview(b_files)

		x = x + wb + dd				
		b_settings = ui.Button(name='b_settings')
		b_settings.frame = (x,y,wb,wb)
		b_settings.image = ui.Image.named('iob:ios7_gear_outline_32')
		b_settings.action = self.button_settings_action			
		self.add_subview(b_settings)

		x = self.width - wb - dd			
		b_format = ui.Button(name='b_format')
		b_format.frame = (x,y,wb,wb)
		o = ObjCClass('UIImage').systemImageNamed_('list.number')
		with ui.ImageContext(32,32) as ctx:
			o.drawAtPoint_(CGPoint(4,4))
			b_format.image = ctx.get_image()					
		b_format.action = self.button_format_action
		self.add_subview(b_format)
		self.outline_format = 'decimal'
		self.first_level_has_outline = True

		x = x - wb - dd				
		b_color = ui.Button(name='b_color')
		b_color.frame = (x,y,wb,wb)
		b_color.image = ui.Image.named('emj:Artist_Palette').with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		b_color.action = self.button_color_action
		self.add_subview(b_color)
		self.outline_rgb = (1,0,0)
		self.outline_color = UIColor.colorWithRed_green_blue_alpha_(self.outline_rgb[0], self.outline_rgb[1], self.outline_rgb[2], 1)

		x = x - wb - dd				
		b_font = ui.Button(name='b_font')
		b_font.frame = (x,y,wb,wb)
		with ui.ImageContext(32,32) as ctx: 
			ui.draw_string('A', rect=(16,9,16,16), font=('Academy Engraved LET',24))
			b_font.image = ctx.get_image()
		b_font.action = self.button_font_action
		self.add_subview(b_font)

		x = x - wb - dd				
		b_fsize = ui.Button(name='b_fsize')
		b_fsize.frame = (x,y,wb,wb)
		#b_fsize.title = 'font_size'
		with ui.ImageContext(32,32) as ctx:
			ui.draw_string('A', rect=(8,12,12,12), font=('Menlo',12))
			ui.draw_string('A', rect=(16,9,16,16), font=('Menlo',16))
			b_fsize.image = ctx.get_image()
		b_fsize.action = self.button_fsize_action
		self.add_subview(b_fsize)		

		x = x - wb - dd		
		b_search = ui.Button(name='b_search')
		b_search.frame = (x,y,wb,wb)
		b_search.image = ui.Image.named('iob:ios7_search_32')
		b_search.action = self.button_search_action
		self.add_subview(b_search)
		
		x = x - wb - dd		
		b_select = ui.Button(name='b_select')
		b_select.frame = (x,y,wb,wb)
		b_select.image = ui.Image.named('iob:ios7_checkmark_outline_32')
		b_select.action = self.button_select_action
		self.add_subview(b_select)

		x = x - wb - dd				
		b_undo = ui.Button(name='undo_button')
		b_undo.frame = (x,y,wb,wb)
		b_undo.action = self.button_undo_action
		b_undo.image = ui.Image.named('iob:ios7_undo_outline_32')
		b_undo.enabled = False
		self.add_subview(b_undo)
		
		b_redo = ui.Button(name='redo_button')
		b_redo.frame = (x,10,wb,wb)
		b_redo.action = self.button_redo_action
		b_redo.image = ui.Image.named('iob:ios7_redo_outline_32')
		b_redo.enabled = False
		self.add_subview(b_redo)
		
		title = ui.Label(name='title')
		title.frame = (0,10,b_redo.x - 10,wb)
		title.font = ('Menlo',16)
		title.text_color = 'green'
		title.alignment = ui.ALIGN_CENTER
		self.add_subview(title)

		x = x - wb - dd				
		b_show = ui.Button(name='b_show')
		b_show.frame = (x,y,wb,wb)
		b_show.action = self.button_show_action
		b_show.image = ui.Image.named('iob:ios7_eye_outline_32')
		self.add_subview(b_show)

		x = x - wb - dd				
		b_filter = ui.Button(name='b_filter')
		b_filter.frame = (x,y,wb,wb)
		b_filter.action = self.button_filter_action
		b_filter.image = ui.Image.named('iob:levels_32')
		self.add_subview(b_filter)
		
		sep = ui.Label(name='sep')
		sep.frame = (0,y+wb,self.width,1)
		sep.background_color = 'lightgray'
		self.add_subview(sep)
		
		self.button_undo_enable(False,'')
		self.button_redo_enable(False,'')
		
		self.tv = ui.TableView(name='outliner')
		#self.tv.border_width = 2
		#self.tv.border_color = 'red'
		self.tv.allows_selection = False
		self.tv.data_source = ui.ListDataSource(items=[])
		self.tv.data_source.delete_enabled = False
		self.tv.separator_color=(1,0,0,0)
		self.tv.delegate = self
		self.tv.data_source.tableview_cell_for_row = self.tableview_cell_for_row
		self.tv.data_source.tableview_number_of_rows = self.tableview_number_of_rows
		self.tv.data_source.tableview_height_for_section_row = self.tableview_height_for_section_row
		self.tv.background_color = (1,1,1)
		#self.tv.border_width = 1
		#d = 20*2
		self.ht = 10 + wb*2
		
		self.tv.frame = (0,self.ht,ws-2,hs-self.ht)
		self.tv.delegate = self
						
		dtt = ui.Label(name='dates_title')
		dtt.frame = (5,self['sep'].y,self.width,wb)
		dtt.text_color = 'gray'
		dtt.hidden = True
		tap(dtt,self.dates_sort)
		self.add_subview(dtt)
				
		#======== to be moved for textfikd in cell for row
		#self.tv.font = ('Menlo',14)
		self.tvo = ObjCInstance(self.tv)
		#print(dir(self.tvo))
		self.tv.row_height = -1
		self.tvo.estimatedRowHeight = 44
		
		self.add_subview(self.tv)
				
		self.font = 'Menlo'
		self.font_size = 18
		self.font_hidden_size = 6
		#font = UIFont.fontWithName_size_('Menlo', self.font_size)
		font = UIFont.fontWithName_size_traits_(self.font, self.font_size,2)
		font_hidden = UIFont.fontWithName_size_('Menlo', self.font_hidden_size)
		
		self.text_color = UIColor.colorWithRed_green_blue_alpha_(0, 0, 1, 1)
		self.text_attributes = {NSForegroundColorAttributeName:self.text_color, NSFontAttributeName:font}
		self.text_attributes_hidden = {NSForegroundColorAttributeName:self.text_color, NSFontAttributeName:font_hidden}
		self.outline_attributes = {NSForegroundColorAttributeName:self.outline_color, NSFontAttributeName:font}
		self.outline_attributes_hidden = {NSForegroundColorAttributeName:self.outline_color, NSFontAttributeName:font_hidden}
		self.link_color = UIColor.colorWithRed_green_blue_alpha_(0, 1, 1, 1)
				
		self.modif = False 
		self.file = None
		self.log = 'no'
		self.filter = ('>',0)
		self.device_model = str(ObjCClass('UIDevice').currentDevice().model())		
		#self.device_model = 'iPhone'	# force for tests
		self.dev = False
		self.cursor = (0,0)
		self.undo_multiples = []
		self.undo_multiples_index = -1
		
		path = argv[0]
		i = path.rfind('.')
		self.prm_file = path[:i] + '.prm'
		if os.path.exists(self.prm_file):
			with open(self.prm_file, mode='rt', encoding='utf-8', errors="surrogateescape") as fil:
				x = fil.read()
				self.prms = literal_eval(x)
		else:
			self.prms = {}
			self.prms['font'] = self.font
			self.prms['font_hidden'] = self.font_hidden_size
			
		self.log_file = path[:i] + '.log'
		
		if 'current path' not in self.prms:
			self.prms['current path'] = path # default = script path
		self.current_path = self.prms['current path']
			
		if 'popup menu orientation' not in self.prms:
			self.prms['popup menu orientation'] = 'horizontal'
		self.popup_menu_orientation = self.prms['popup menu orientation']
		if self.device_model != 'iPad':
			self.popup_menu_orientation = 'vertical'
		if 'show original area' not in self.prms:
			self.prms['show original area'] = 'no'
		self.show_original_area = self.prms['show original area']
		if 'show lines separator' not in self.prms:
			self.prms['show lines separator'] = 'yes'
		self.show_lines_separator = self.prms['show lines separator']
		if 'checkboxes' not in self.prms:
			self.prms['checkboxes'] = 'yes'
		self.checkboxes = self.prms['checkboxes']
		if 'delete option in red' not in self.prms:
			self.prms['delete option in red'] = 'yes'
		self.red_delete = self.prms['delete option in red']
		if 'tap for popup' not in self.prms:
			self.prms['tap for popup'] = 'single'
		self.tap_for_popup = self.prms['tap for popup']
		if 'autocapitalize type' not in self.prms:
			self.prms['autocapitalize type'] = 'none'
		self.autocapitalize_type = self.prms['autocapitalize type']
		if 'dates format' not in self.prms:
			self.prms['dates format'] = '%Y-%m-%d'
		self.dates_format = self.prms['dates format']
		
		# remove old prm and create new
		default = True
		if 'external keyboard' in self.prms:
			if self.prms['external keyboard'] == 'no':
				self.prms['external combinations'] = {}
			del self.prms['external keyboard']
		if 'external combinations' not in self.prms:
			self.prms['external combinations'] = {
																						'promote':('Ctrl', 'Left'),
																						'demote' :('Ctrl', 'Right')
																						}
		self.external_combinations = self.prms['external combinations']		
		
		# temporary protection vs invalid data in .prm
		if 'delete in red' in self.prms:
			del self.prms['delete in red']
		if 'auto_save' in self.prms:
			del self.prms['auto_save']
		if 'auto-save' not in self.prms:
			self.prms['auto-save'] = 'no'
		else:
			# temporary protection vs invalid data in .prm
			if 'auto-save' in self.prms['auto-save']:
				self.prms['auto-save'] = 'no'
		self.auto_save = self.prms['auto-save']
		
		if 'folder' in self.prms:
			del self.prms['folder']

		local_path = argv[0]
		#print(local_path)
		path = os.path.expanduser('~/Documents/')
		# /private/var/mobile/Containers/Shared/AppGroup/1B829014-77B3-4446-9B65-034BDDC46F49/Pythonista3/Documents/
		i = len('/private/var/mobile/Containers/Shared/AppGroup/')
		j = path.find('/',i)
		# on my ipad does not have same device_id as local Pythonista....
		device_id_local = path[i:j]
		#print(local_path,device_id_local)
		if 'on_my_path' in self.prms:
			path_on_my = self.prms['on_my_path']
		else:
			path_on_my = '?'
		
		self.path_to_name = {}
		
		self.path_to_name['/private/var/mobile/Containers/Shared/AppGroup/'+device_id_local+'/Pythonista3/Documents/'] = 'Pythonista local'
		
		self.path_to_name['/private/var/mobile/Library/Mobile Documents/iCloud~com~omz-software~Pythonista3/Documents/'] = 'Pythonista iCloud'

		if 'on_my_path' in self.prms:		
			if os.path.exists(path_on_my):
				self.path_to_name[path_on_my] = 'On my ' + self.device_model
		
		path_icloud_drive = '/private/var/mobile/Library/Mobile Documents/com~apple~CloudDocs/'
		if os.path.exists(path_icloud_drive):
			self.path_to_name[path_icloud_drive] = 'iCloud Drive'
					
		self.checkmark_ui_image  = ui.Image.named('emj:Checkmark_3').with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		
		self.save_duration = None
		self.orig_area = None
		self.cells = {}
		self.show_mode = 'Expand all'
		self.select = False

		# register Blackmamba key_event_handlers		
		self.external_actions = {						
				'promote':self.external_promote,
				'demote':self.external_demote,
				'font attributes':self.external_fontattributes,
				'set due date':self.external_duedate,
				'collapse all':self.external_collapseall,
				'expand all':self.external_expandall	
				}
		self.external_modifiers = {
				'none':UIKeyModifier.NONE, 
				'Lock':UIKeyModifier.ALPHA_SHIFT, 
				'Alt':UIKeyModifier.ALTERNATE, 
				'Ctrl':UIKeyModifier.CONTROL, 
				'Cmd':UIKeyModifier.COMMAND, 
				'Shift':UIKeyModifier.SHIFT
				}
		self.external_keys = {
				'Right':UIEventKeyCode.RIGHT,
				'Left':UIEventKeyCode.LEFT,
				'Down':UIEventKeyCode.DOWN,
				'Up':UIEventKeyCode.UP,
				'Enter':UIEventKeyCode.ENTER,
				'Space':UIEventKeyCode.SPACE,
				'Backspace':UIEventKeyCode.BACKSPACE,
				'Escape':UIEventKeyCode.ESCAPE,
				'[':UIEventKeyCode.LEFT_SQUARE_BRACKET,
				'Dot':UIEventKeyCode.DOT
				}

		self._handlers = []
		self.set_key_event_handlers()
		
		ui.delay(self.init2,1)
		
	def set_key_event_handlers(self):
		mytrace(inspect.stack())
		# unregister old 
		if self._handlers:
			unregister_key_event_handlers(self._handlers)
						
		# register new
		self._handlers = []
		dels = []
		for action in self.external_combinations:
			if action not in self.external_actions:
				# old action, no more existing
				dels.append(action)
				continue
			defaction = self.external_actions  [action]
			modifier  = self.external_modifiers[self.external_combinations[action][0]]
			key       = self.external_keys     [self.external_combinations[action][1]]
			self._handlers.append(register_key_event_handler(key, defaction, modifier=modifier))
		for dele in dels:
			del self.external_combinations[dele]
		
	def external_demote(self):
		mytrace(inspect.stack())
		#print('external_right')
		if self.edited_textview:
			# external keyboard pressed while an ui.TextView is active
			if self.edited_textview.name == 'text':
				# sure textview is an outline text
				row = self.edited_textview.row
				self.textview_should_change(None,[row,row],'\x01')				
		
	def external_promote(self):
		mytrace(inspect.stack())
		#print('external_left')
		if self.edited_textview:
			# external keyboard pressed while an ui.TextView is active
			if self.edited_textview.name == 'text':
				# sure textview is an outline text
				row = self.edited_textview.row
				self.textview_should_change(None,[row,row],'\x02')			
				
	def external_fontattributes(self):	
		mytrace(inspect.stack())
		#print('external_fontattributes')
		if self.edited_textview:
			# external keyboard pressed while an ui.TextView is active
			if self.edited_textview.name == 'text':
				# sure textview is an outline text
				row = self.edited_textview.row
				self.selected_text_attributes(row)					
		
	def external_duedate(self):	
		mytrace(inspect.stack())
		#print('external_duedate')
		if self.edited_textview:
			# external keyboard pressed while an ui.TextView is active
			if self.edited_textview.name == 'text':
				# sure textview is an outline text
				row = self.edited_textview.row
				self.popup_menu_action('due date', row=row)
				
	def external_expandall(self):
		mytrace(inspect.stack())
		self.show_action('Expand all')
		
	def external_collapseall(self):
		mytrace(inspect.stack())
		self.show_action('Collapse all')
		
	def init2(self):
		mytrace(inspect.stack())
		# code only to be sure keyboard height will be knwon at begin of program: begin
		tf = ui.TextField()
		tf.frame = (0,0,10,10)
		self.add_subview(tf)
		tf.begin_editing()
		tf.end_editing()
		self.remove_subview(tf)
		# code only to be sure keyboard height will be knwon at befin of program: end		
		# must be last process of init	
		local_path = argv[0]
		if len(argv) > 1:
			# 1st argument passed
			if len(argv) > 2:
				# 2nd argument passed 
				param = argv[2].lower()
				if param.startswith('local/'):
					l = 6
					folder = 'Pythonista local'
				elif param.startswith('icloud/'):
					l = 7
					folder = 'Pythonista iCloud'
				elif param.startswith('onmy'+self.device_model+'/'):
					l = len('onmy'+self.device_model+'/')
					folder = 'On my ' + self.device_model
				elif param.startswith('iclouddrive'):			
					l = 12
					folder = 'iCloud Drive'
				else:
					console.hud_alert('incorrect base folder', 'error',3)
					return
				for p in self.path_to_name.keys():
					if self.path_to_name[p] == folder:
						path = p
						break
				path = path[l:]				
				path = os.path.expanduser(path)   
			else:
				path = self.current_path
			param = argv[1]
			if param == 'dev':
				self.dev = True
			elif param.startswith('.'):
				# extension passed
				ext = param
				f = self.pick_file('from where to open the file', uti=['public.item'], callback=self.pick_open_callback, ask=False, init=self.current_path, ext=ext)
				if not f:
					console.hud_alert('No file has been picked','error',3)
					return
				if f == 'delayed':
					# Files app via UIDocumentPickerViewController needs delay
					return
				# immediate return for Files_Picker use for local Pythonista files
				simul = 'file://' + f
				self.pick_open_callback(simul)		
			else:
				# file passed
				file = param
				files = os.listdir(path=path)
				fnd = file			
				for f in files:
					if f.startswith(file+'_20') and f.endswith('.outline'):
						if f > fnd:
							# keep newest
							fnd = f
				file = fnd
				if not os.path.exists(path+file):
					console.hud_alert('file argument does not exist','error', 3)
				else:
					self.prms['path'] = path
					self.prms['file'] = file										
		if 'file' in self.prms:	
			# simulate files button and open last file	
			if not os.path.exists(self.prms['path']+self.prms['file']):
				#console.hud_alert(self.prms['file']+' in .prm does not exist\nprm will be cleaned','error',1)
				del self.prms['path']
				del self.prms['file']
			else:
				self.button_files_action('Open')
				
	def get_screen_size(self):				
		mytrace(inspect.stack())
		app = UIApplication.sharedApplication().keyWindow() 
		for window in UIApplication.sharedApplication().windows():
			ws = window.bounds().size.width
			hs = window.bounds().size.height
			break
		return ws,hs
				
	def layout(self):	
		mytrace(inspect.stack())	
		ws,hs = self.get_screen_size()
		#print('layout:',ws,hs)
		self.width, self.height = ws,hs
		
		app = UIApplication.sharedApplication().keyWindow()
		self.safeAreaInsets = app.safeAreaInsets()		
		ws = ws - self.safeAreaInsets.left - self.safeAreaInsets.right
		hs = hs - self.safeAreaInsets.top  - self.safeAreaInsets.bottom
		
		nb = 13
		dd = 4
		wb = (ws - (nb+1)*dd)/nb
		if wb > 32:
			wb = 32
			dd = (ws - wb*nb)/(nb+1)
		d = int(ws/nb)
		
		self.ht = self.safeAreaInsets.top + wb*2
		y = self.safeAreaInsets.top + wb

		self.tv.frame = (self.safeAreaInsets.left,self.ht,ws-2, self.height - self.ht - self.safeAreaInsets.bottom)
		if self.show_mode == 'View dates':		
			self.tv.y += self['dates_title'].height
			self.tv.height -= self['dates_title'].height
		
		x = dd + self.safeAreaInsets.left
		self['b_close'].frame = (x,y,wb,wb)
		x = x + wb + dd		
		self['b_version'].frame = (x,y,wb,wb)
		x = x + wb + dd				
		self['b_files'].frame = (x,y,wb,wb)
		x = x + wb + dd				
		self['b_settings'].frame = (x,y,wb,wb)
		x = self.width - wb - dd			
		self['b_format'].frame = (x,y,wb,wb)
		x = x - wb - dd				
		self['b_color'].frame = (x,y,wb,wb)
		x = x - wb - dd				
		self['b_font'].frame = (x,y,wb,wb)
		x = x - wb - dd				
		self['b_fsize'].frame = (x,y,wb,wb)
		x = x - wb - dd		
		self['b_search'].frame = (x,y,wb,wb)
		x = x - wb - dd	
		self['b_select'].frame = (x,y,wb,wb)
		x = x - wb - dd							
		self['undo_button'].frame = (x,y,wb,wb)
		self['redo_button'].frame = (x,self.safeAreaInsets.top,wb,wb)
		self['title'].frame = (0,self.safeAreaInsets.top,x-10,wb)
		x = x - wb - dd				
		self['b_show'].frame = (x,y,wb,wb)
		x = x - wb - dd				
		self['b_filter'].frame = (x,y,wb,wb)
		self['sep'].frame = (0,y+wb-1,self.width,1)
		self['dates_title'].frame = (5,self['sep'].y,self.width,wb)

		# shield if visible		
		try:
			self.shield.frame = (0,0,self.width, self.shield.shield_height)
		except:
			pass

		# attributes popup if visible			
		try:	
			v = self['attributes']
			v.height = min(v.content_size[1],self.height - 40)
			v.x = (self.width - v.width) / 2
			v.y = (self.height - v.height) / 2
		except:
			pass
			
		# external_keyboard_keys_combinations popup if visible			
		try:	
			v = self['external_keyboard_keys_combinations']
			tv1 = v['keys_combinations']
			tv2 = v['modifiers']
			tv3 = v['keys']
			h1 = tv1.row_height*len(tv1.data_source.items)
			h2 = tv2.row_height*len(tv2.data_source.items)
			h3 = tv3.row_height*len(tv3.data_source.items)
			v.height = min(self.height*0.8, tv1.y + max(h1,h2,h3)+ 4)
			hmax = v.height-4-tv1.y
			tv1.height = min(hmax, h1)
			tv2.height = min(hmax, h2)
			tv3.height = min(hmax, h3)			
			v.x = (self.width - v.width) / 2
			v.y = (self.height - v.height) / 2
		except:
			pass
			
		# searched files popup if visible			
		try:	
			v = self['searched_files']
			tv = v['searched_files_list']
			h = tv.row_height*len(tv.data_source.items)
			v.height = min(self.height*0.8, tv.y + h + 4)
			hmax = v.height-4-tv.y
			tv.height = min(hmax, h)
			wmax = 0
			for f in tv.data_source.items:
				w = ui.measure_string(f, font=('Menlo',16))[0]
				wmax = max(wmax,w)
			wmax += 20
			v.width = min(self.width*0.8,wmax+8)
			tv.width = v.width - 8
			v.x = self['b_files'].x + self['b_files'].width/2
			v.y = self['b_files'].y + self['b_files'].height
		except:
			pass
			
		self.tv.reload_data()

	def tableview_height_for_section_row(self,tv,section,rowin, nosort=False):
		mytrace(inspect.stack())
		#print('tableview_height_for_section_row', row)
								
		if tv.name != 'outliner':
			return tv.row_height
			
		#=========
		if nosort:
			row = rowin
		elif self.show_mode == 'View dates':
			# sort rows
			dtnow = datetime.now() # to be sure all items have same date
			rows_with_dates = []
			ir = 0
			for item in self.tv.data_source.items:
				vals,n,opts = item['content']
				dates = opts.get('dates',None)
				dt = None
				if dates:
					dt =  dates[self.selected_date]
				if dt:
					dt = datetime.strptime(dt,'%Y-%m-%d %H:%M:%S') # datetime	
				else:
					dt = dtnow
				rows_with_dates.append((ir,dt))
				ir += 1
			# sort f(self.dates_sort_mode): 0=normal 1=descending 2=ascending
			if self.dates_sort_mode == 0:
				pass # no sort
			elif self.dates_sort_mode == 1:
				rows_with_dates.sort(key=lambda x:x[1], reverse=True) # sort descending
			elif self.dates_sort_mode == 2:
				rows_with_dates.sort(key=lambda x:x[1]) # sort ascending
			# get sorted row
			row = rows_with_dates[rowin][0]
		elif 'completed checkboxes' in self.show_mode:
			# sort rows on completed checkbox
			rows_with_chk = []
			ir = 0
			for item in self.tv.data_source.items:
				vals,n,opts = item['content']
				checkmark = opts.get('checkmark',None)
				chk = 1 if checkmark == 'yes' else 0
				rows_with_chk.append((ir,chk))
				ir += 1
			if 'sort at beginning' in self.show_mode:
				rows_with_chk.sort(key=lambda x:x[1], reverse=True) # sort descending
			elif 'sort at end' in self.show_mode:
				rows_with_chk.sort(key=lambda x:x[1]) # sort ascending
			# get sorted row
			row = rows_with_chk[rowin][0]	
		else:
			row = rowin		
		#=========
								
		vals,n,opts = tv.data_source.items[row]['content']
		ft = (self.font, self.font_size)
		hidden = False
		if 'hidden' in opts:
			if opts['hidden']:
				hidden = True
				ft = (self.font,self.font_hidden_size)

		x = self.font_size * 2 + ui.measure_string(tv.data_source.items[row]['outline'], font=ft)[0]

		if self.show_mode == 'View dates':		
			fsd = int(self.font_size*0.8)
			x += 10+ui.measure_string('0000-00-00', font=(self.font,fsd))[0]
		
		if not hidden and 'image' in opts:
			himg = opts['image'][1]*self.font_size  # (image file name, h_in_rows)
			try:
				image = ui.Image.named(opts['image'][0]).with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			except:
				image = ui.Image.named('emj:Question_Mark_1').with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			wi,hi = image.size
			del image
			wimg = wi * himg/hi
		else:
			himg =  0
			wimg = 0
			
		l = ui.TextView()
		self.set_content_inset(l)
		l.font = ft
		l.text = tv.data_source.items[row]['title']
		l.number_of_lines = 0
		if himg == 0:
			l.frame = (0,0,self.width - x - 4,ft[1])
			l.size_to_fit()
			ho = l.height
		else:
			pos = opts['image'][2]
			if pos == 'left':
				l.frame = (wimg,0,self.width - x - 4 - wimg,ft[1])				
				l.size_to_fit()
				ho = max(himg,l.height)
			elif pos == 'right':
				l.frame = (0,0,self.width - x - 4 - wimg,ft[1])				
				l.size_to_fit()
				ho = max(himg,l.height)
			elif pos == 'top':
				l.frame = (0,0,self.width - x - 4,ft[1])				
				l.size_to_fit()
				ho = himg + l.height
			elif pos == 'bottom':
				l.frame = (0,0,self.width - x - 4,ft[1])				
				l.size_to_fit()
				ho = himg + l.height
		del l

		#print('tableview_height_for_section_row', self.width,ho)
		return ho
		'''
		undo = tv before action
		action
		
		undo:
			redo = tv after action
			tv = undo
		redo:
			tv = redo
		'''	
	def button_undo_action(self,sender):
		mytrace(inspect.stack())
		return # protection ============================================
		if self.undo_multiples_index > 0:
			self.undo_multiples_index -= 1
			items = []
			for item in self.undo_multiples[self.undo_multiples_index][1]:
				items.append(item.copy())
			self.tv.data_source.items = items
			if self.undo_multiples_index > 0:
				self.button_undo_enable(True, self.undo_multiples[self.undo_multiples_index][0])
			else:
				self.button_undo_enable(False, '')
		else:
			self.button_undo_enable(False, '')
		self.modif = True
		self.tv.reload_data()
		if self.undo_multiples_index < (len(self.undo_multiples)-1):
			self.button_redo_enable(True,self.undo_multiples[self.undo_multiples_index+1][0])
				
	def button_redo_action(self,sender):
		mytrace(inspect.stack())
		return # protection ============================================
		if self.undo_multiples_index < (len(self.undo_multiples)-1):
			items = []
			self.undo_multiples_index += 1
			for item in self.undo_multiples[self.undo_multiples_index][1]:
				items.append(item.copy())
			self.tv.data_source.items = items
			if self.undo_multiples_index < (len(self.undo_multiples)-1):
				self.button_redo_enable(True, self.undo_multiples[self.undo_multiples_index][0])
			else:
				self.button_redo_enable(False, '')
		else:
			self.button_redo_enable(False, '')
		self.modif = True
		self.tv.reload_data()	
		if self.undo_multiples_index > 0:
			self.button_undo_enable(True,self.undo_multiples[self.undo_multiples_index][0])	
		
	def undo_save(self,action):
		mytrace(inspect.stack())
		self.undo_multiples.append((action,[]))	# for V01.04 bug correction
		return # protection ============================================
		# new action forces delete of all saved undo after index
		if self.undo_multiples_index < (len(self.undo_multiples)-1):
			del self.undo_multiples[self.undo_multiples_index+1:]
		items = []
		for item in self.tv.data_source.items:
			items.append(item.copy())
		self.undo_multiples.append((action,items))
		#print('undo_save',action,self.undo_multiples)
		del items
		self.undo_multiples_index += 1
		#print('undo_save: size of self.undo_multiples =', sys.getsizeof(self.undo_multiples), 'len=',len(self.undo_multiples))
		self.button_undo_enable(self.undo_multiples_index>0,action)
		
	def button_undo_enable(self,enabled,text):
		mytrace(inspect.stack())
		#print('button_undo_enable', enabled, text)
		b = self['undo_button']
		b.image = ui.Image.named('iob:ios7_undo_outline_32')
		b.enabled = enabled
		if enabled:
			with ui.ImageContext(b.width,b.height) as ctx:
				b.image.draw(0,0)
				#print('text=|'+text+'|')
				ui.draw_string(text, rect=(0,b.height-16,b.width,14), font=('<system>', 12), color='red')
				b.image = ctx.get_image().with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)			
			
	def button_redo_enable(self,enabled,text):
		mytrace(inspect.stack())
		#print('button_redo_enable', enabled, text)
		b = self['redo_button']
		b.image = ui.Image.named('iob:ios7_redo_outline_32')
		b.enabled = enabled
		if enabled:
			with ui.ImageContext(b.width,b.height) as ctx:
				b.image.draw(0,0)
				#print('text=|'+text+'|')
				ui.draw_string(text, rect=(0,b.height-16,b.width,14), font=('<system>', 12), color='red')
				b.image = ctx.get_image().with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			
	def button_search_action(self,sender, simul_find=None):
		mytrace(inspect.stack())
		x = sender.x +sender.width/2
		y = sender.y + sender.height
		tf = ui.TextField(name='search')
		tfo = ObjCInstance(tf).textField()
		tfo.backgroundColor = ObjCClass('UIColor').colorWithRed_green_blue_alpha_(1, 1, 0, 1)
		tf.background_color = 'yellow'
		tf.font = ('Menlo',18)
		tf.frame = (x,y,400,20)
		tf.placeholder = 'type text to be searched'
		tf.delegate = self
		if simul_find:
			tf.text = self.search_text_in_files
		else:
			tf.text = ''
		self.present_popover(tf, 'popover',popover_location=(x,y),hide_title_bar=True, force=True)
		if simul_find:
			ui.delay(partial(self.textfield_did_change,tf), 0.2)

	def textfield_did_change(self, textfield):
		mytrace(inspect.stack())
		#print('textfield_did_change:', textfield.name, textfield.text)
		if textfield.name == 'search':
			txt = textfield.text
			txt = normalize('NFKD', txt).encode('ASCII', 'ignore')
			txt = str(txt,'utf-8').upper()
			#........... not yet for invisible and hidden	
			row = 0
			for item in self.tv.data_source.items:
				title = self.tv.data_source.items[row]['title']
				t = normalize('NFKD', title).encode('ASCII', 'ignore')
				t = str(t,'utf-8').upper()			
				vals,n,opts = self.tv.data_source.items[row]['content']
				opts['hidden'] = (t.find(txt) < 0)
				self.tv.data_source.items[row]['content'] = (vals,n,opts)
				row += 1
			self.tv.reload_data()
			ui.delay(textfield.begin_editing,0.1)
		elif textfield.name == 'image_size':			
			ns = int('0'+textfield.text)
			v = textfield.superview
			ss = v['size_segments']
			idx = -1
			for i in range(len(ss.dims)):
				if ss.dims[i] == ns:
					idx = i
					break
			ss.selected_index = idx
								
	def button_settings_action(self,sender):
		mytrace(inspect.stack())
		sections = []
		fields = []
		accessible = [True] + [self.device_model=='iPad']
		fields.append({'title':'popup menu orientation', 'type':'text', 'value':self.popup_menu_orientation, 'key':'segmented1', 'segments':['vertical', 'horizontal'], 'accessible':accessible})
		fields.append({'title':'show original area', 'type':'text', 'value':self.show_original_area, 'key':'segmented4', 'segments':['yes', 'no']})
		fields.append({'title':'log active', 'type':'text', 'value':self.log, 'key':'segmented5', 'segments':['yes', 'no']})
		fields.append({'title':'font size of hidden outlines', 'type':'number', 'pad':pad_integer, 'value':str(self.font_hidden_size)})
		fields.append({'title':'show lines separator', 'type':'text', 'value':self.show_lines_separator, 'key':'segmented6', 'segments':['yes', 'no']})
		fields.append({'title':'checkboxes', 'type':'text', 'value':self.checkboxes, 'key':'segmented7', 'segments':['yes', 'no']})
		auto_save = 'auto-save'
		if self.save_duration:
			auto_save += ' [' + self.save_duration + ']'
		fields.append({'title':auto_save, 'type':'text', 'value':self.auto_save, 'key':'segmented8', 'segments':['no','each char','each line']})
		
		fields.append({'title':'delete option in red', 'type':'text', 'value':self.red_delete, 'key':'segmented10', 'segments':['yes', 'no']})
		
		fields.append({'title':'tap for popup', 'type':'text', 'value':self.tap_for_popup, 'key':'segmented11', 'segments':['single', 'double']})
		
		fields.append({'title':'autocapitalize type', 'type':'text', 'value':self.autocapitalize_type, 'key':'segmented12', 'segments':['none', 'words', 'sentences', 'all']})
		
		fields.append({'title':'dates format', 'type':'text', 'value':str(self.dates_format)})

		v = 'yes' if self.external_combinations else 'no' 	
		fields.append({'title':'external keyboard combinations', 'type':'text', 'value':v, 'key':'segmented13', 'segments':['no', 'yes']})

		sections.append((self.current_path,fields))	
		f = my_form_dialog('settings', sections=sections, hd=600, kbd_button=True)			
		#f = my_form_dialog('settings', fields=fields, hd=600)		
		#print(f)
		if not f:
			# canceled
			return
		if f == 'kbd':
			# keyboard button pressed
			self.set_external_keyboard_keys_combinations()							
			return
			
		self.popup_menu_orientation = f['popup menu orientation']
		self.prms['popup menu orientation'] = self.popup_menu_orientation
		
		self.show_original_area = f['show original area']
		self.prms['show original area'] = self.show_original_area
		
		self.log = f['log active']
		self.prms['log active'] = self.log
		
		n = int('0'+f['font size of hidden outlines'])
		self.prms['font_hidden'] = n
		self.set_font(font_hidden_size=n)
		
		self.show_lines_separator = f['show lines separator']
		self.prms['show lines separator'] = self.show_lines_separator
		
		self.checkboxes = f['checkboxes']
		self.prms['checkboxes'] = self.checkboxes
		
		self.auto_save = f[auto_save]
		self.prms['auto-save'] = self.auto_save
				
		self.red_delete = f['delete option in red']
		self.prms['delete option in red'] = self.red_delete
		
		self.tap_for_popup = f['tap for popup']
		self.prms['tap for popup'] = self.tap_for_popup
		
		self.autocapitalize_type = f['autocapitalize type']
		self.prms['autocapitalize type'] = self.autocapitalize_type
		
		self.dates_format = f['dates format']
		self.prms['dates format'] = self.dates_format

		v = f['external keyboard combinations']
		if v == 'no':
			self.external_combinations = {}			
		
		self.tv.reload_data()
		
	def button_select_action(self,sender):	
		mytrace(inspect.stack())
		self.select = True
		self.selected_rows_for_cut = []
		x = self.width/2
		y = self.height/2
		sub_menu = ['delete', 'copy', 'cut', 'cancel']
		tv = ui.TableView(name='select')
		tv.background_color = 'yellow'
		tv.row_height = 35
		h = tv.row_height*len(sub_menu)		
		tv.frame = (0,0,250,h)
		lds = ui.ListDataSource(items=sub_menu)
		lds.tableview = tv 	# my own attribute needed in tableview_did_select
		lds.delete_enabled = False
		tv.data_source = lds
		tv.data_source.tableview_cell_for_row = self.select_cell_for_row
		tv.delegate = self
		tv.data_source.selected_row = -1
		tv.allows_multiple_selection = False
		self.present_popover(tv, 'popover',popover_location=(x,y),hide_title_bar=True, force=True, shield_height=True)
			
	def select_cell_for_row(self, tableview, section, row):
		mytrace(inspect.stack())
		cell = ui.TableViewCell()
		cell.text_label.text = tableview.data_source.items[row]
		cell.bg_color = 'yellow'
		return cell		
		
	def select_action(self, act):
		mytrace(inspect.stack())
		#print('select_action', act)
		self.select = False
		if len(self.selected_rows_for_cut) == 0:
			return
		if act in ['copy', 'cut']:
			# copy selected rows to clipboard
			items = []
			clipboard_str = ''
			for row in self.selected_rows_for_cut:
				item_orig = self.tv.data_source.items[row]
				item = item_orig.copy()
				vals,n,opts = item['content']
				if 'eventid' in opts:
					del opts['eventid']	# not copy calendar event id
				if 'hidden' in opts:
					del opts['hidden']	# not copy hidden flag
				item['content'] = (vals,n,opts)
				items.append(item)
				clipboard_str += item['outline'] + ' ' + item['title'] + '\n'
			# tested with clipboard but program hangs......
			#clipboard.set(clipboard_str)
			UIPasteboard = ObjCClass('UIPasteboard').generalPasteboard()
			UIPasteboard.setString_(clipboard_str)
			clipboard_str = str(items)
			with open('outline.clipboard', mode='wt') as fil:
				fil.write(clipboard_str)			
			del items
			del item
			del clipboard_str
		if act in ['delete', 'cut']:
			self.undo_save(act[:3])
			items = []
			for row in range(len(self.tv.data_source.items)):
				if row not in self.selected_rows_for_cut:
					# keep unselected
					item = self.tv.data_source.items[row]
					items_copy = item.copy()
					items.append(items_copy)
				else:
					# delete selected
					vals,n,opts = self.tv.data_source.items[row]['content']
					if 'eventid' in opts:
						id = opts['eventid']
						self.set_due_date(None, delete=id, feedback=False)
			self.tv.data_source.items = items	
			# renumbering 
			self.renumbering('all',None,None, None)
			self.modif = True
			self.check_auto_save('line')
			self.tv.reload_data()
			
	def set_external_keyboard_keys_combinations(self):
		mytrace(inspect.stack())
		v = ui.View(name='external_keyboard_keys_combinations')
		v.background_color = 'yellow'
		v.frame = (0,0,300,300)

		y = 4	
		l1 = ui.Label()
		l1.frame = (2,y,140,20)
		l1.text = '   action'
		v.add_subview(l1)
		l2 = ui.Label()
		l2.frame = (l1.x+l1.width+4,y,80,20)
		l2.text = '   modifier'
		v.add_subview(l2)
		l3 = ui.Label()
		l3.frame = (l2.x+l2.width+4,y,115,20)
		l3.text = '   key'
		v.add_subview(l3)
		
		sub_menu = self.external_actions.keys()
		tv1 = ui.TableView(name='keys_combinations')
		tv1.row_height = 35

		y = l1.y + l1.height + 4
		h = tv1.row_height*len(sub_menu)		
		tv1.content_size = (l1.width,h)
		tv1.frame = (4,y,l1.width,h)
		tv1.corner_radius = 5
		lds1 = ui.ListDataSource(items=sub_menu)
		lds1.tableview = tv1 	# my own attribute needed in tableview_did_select
		#lds1.delete_enabled = False
		lds1.tableview_delete = self.tableview_delete
		lds1.tableview_can_delete = self.tableview_can_delete
		tv1.data_source = lds1
		tv1.data_source.tableview_cell_for_row = self.combination_cell_for_row
		tv1.delegate = self
		tv1.selected_row = 0
		tv1.allows_multiple_selection = False
		v.add_subview(tv1)

		sub_menu = self.external_modifiers.keys()
		tv2 = ui.TableView(name='modifiers')
		tv2.row_height = 35
		h = tv2.row_height*len(sub_menu)		
		tv2.content_size = (l2.width,h)
		tv2.frame = (tv1.x+tv1.width+4,y,l2.width,h)
		tv2.corner_radius = 5
		lds2 = ui.ListDataSource(items=sub_menu)
		lds2.tableview = tv2 	# my own attribute needed in tableview_did_select
		lds2.delete_enabled = False
		tv2.data_source = lds2
		tv2.data_source.tableview_cell_for_row = self.combination_cell_for_row
		tv2.delegate = self
		tv2.selected_row = -1
		tv2.allows_multiple_selection = False
		v.add_subview(tv2)
		
		sub_menu = self.external_keys.keys()
		tv3 = ui.TableView(name='keys')
		tv3.row_height = 35
		h = tv3.row_height*len(sub_menu)		
		tv3.content_size = (l3.width,h)
		tv3.frame = (tv2.x+tv2.width+4,y,l3.width,h)
		tv3.corner_radius = 5
		lds3 = ui.ListDataSource(items=sub_menu)
		lds3.tableview = tv3 	# my own attribute needed in tableview_did_select
		lds3.delete_enabled = False
		tv3.data_source = lds3
		tv3.data_source.tableview_cell_for_row = self.combination_cell_for_row
		tv3.delegate = self
		tv3.selected_row = -1
		tv3.allows_multiple_selection = False
		v.add_subview(tv3)
		
		v.width = tv3.x+tv3.width+4
		h1 = tv1.row_height*len(tv1.data_source.items)
		h2 = tv2.row_height*len(tv2.data_source.items)
		h3 = tv3.row_height*len(tv3.data_source.items)
		v.height = min(self.height*0.8, tv1.y + max(h1,h2,h3)+4)
		hmax = v.height-4-tv1.y
		tv1.height = min(hmax, h1)
		tv2.height = min(hmax, h2)
		tv3.height = min(hmax, h3)
		x = (self.width  - v.width)/2
		y = (self.height - v.height)/2
		
		self.present_popover(v, 'popover',popover_location=(x,y),hide_title_bar=True, force=True)
		
		self.tableview_did_select(tv1,0,0)

	def combination_cell_for_row(self, tableview, section, row):
		mytrace(inspect.stack())
		cell = ui.TableViewCell()
		cell.text_label.text = tableview.data_source.items[row]
		if tableview.name == 'keys_combinations':
			for action in self.external_combinations.keys():
				if action == cell.text_label.text:
					cell.bg_color = 'lightgray'
					l = ui.Label()
					l.text_color = 'blue'
					l.text = self.external_combinations[action][0] + '/' + self.external_combinations[action][1]
					l.font = ('Menlo',8)
					w,h = ui.measure_string(l.text,font=l.font)
					wc,hc = tableview.width, tableview.row_height
					l.frame = (wc-w-2,hc-h-2,w,h)
					cell.content_view.add_subview(l)
					break
		selected_cell = ui.View()
		selected_cell.corner_radius = 5
		selected_cell.bg_color = 'cornflowerblue'
		cell.selected_background_view = selected_cell
		return cell
		
	def searchedfiles_cell_for_row(self, tableview, section, row):
		mytrace(inspect.stack())
		cell = ui.TableViewCell()
		cell.text_label.text = tableview.data_source.items[row]
		cell.bg_color = 'white'
		return cell
				
	def button_filter_action(self,sender):
		mytrace(inspect.stack())
		fields = []
		fields.append({'title':'filter type', 'type':'text', 'value':self.filter[0], 'key':'segmented1', 'segments':['<', '=', '>']})
		fields.append({'title':'filter level', 'type':'number', 'pad':pad_integer, 'value':str(self.filter[1])})
		
		f = my_form_dialog('show only if level', fields=fields, hd=600)		
		#print(f)
		if not f:
			# canceled
			return			
		self.filter = (f['filter type'], int(f['filter level']))
		self.tv.reload_data()		
						
	def button_font_action(self,sender):
		mytrace(inspect.stack())
		root = self

		conf = UIFontPickerViewControllerConfiguration.alloc().init()
		picker = UIFontPickerViewController.alloc().initWithConfiguration_(conf)

		delegate = PickerDelegate.alloc().init()
		picker.setDelegate_(delegate)
		
		vc = SUIViewController.viewControllerForView_(root.objc_instance)
		vc.presentModalViewController_animated_(picker, True)
		
	def button_fsize_action(self,sender):
		mytrace(inspect.stack())
		x = sender.x +sender.width/2
		y = sender.y + sender.height
		tf = ui.TextField(name='font_size')
		tf.frame = (x,y,200,24)
		tf.placeholder = 'type font size in pixels'
		tf.delegate = self
		SetTextFieldPad(tf, pad_integer)
		tf.text = str(self.font_size)
		self.present_popover(tf, 'popover',popover_location=(x,y),hide_title_bar=True)
		#tf.present('popover', popover_location=(x,y),hide_title_bar=True)
		#tf.begin_editing()
		#tf.wait_modal()	
		if self.device_model == 'iPad':
			n = int(tf.text)
			self.set_font(font_size=n)
		
	def set_font(self,font_type=None,font_size=None,font_hidden_size=None, set=True):
		mytrace(inspect.stack())
		global font, font_hidden
		if font_type:
			self.font = font_type
		if font_hidden_size != None:
			self.font_hidden_size = font_hidden_size
		if font_size != None:
			self.font_size = font_size
		#font = UIFont.fontWithName_size_(self.font, self.font_size)
		font = UIFont.fontWithName_size_traits_(self.font, self.font_size,2)
		if self.font_hidden_size > 0:
			font_hidden = UIFont.fontWithName_size_(self.font, self.font_hidden_size)
		else:
			font_hidden = UIFont.fontWithName_size_(self.font, 0.01)
		self.text_attributes = {NSForegroundColorAttributeName:self.text_color, NSFontAttributeName:font}
		self.text_attributes_hidden = {NSForegroundColorAttributeName:self.text_color, NSFontAttributeName:font_hidden}		
		self.outline_attributes = {NSForegroundColorAttributeName:self.outline_color, NSFontAttributeName:font}
		self.outline_attributes_hidden = {NSForegroundColorAttributeName:self.outline_color, NSFontAttributeName:font_hidden}
		
		self.tv.font = (self.font, self.font_size)
		
		if not set:
			return
			
		self.tv.reload_data()
		
	def present_popover(self, view, mode, popover_location=None, hide_title_bar=False,  color=False, force =False, shield_height=False):
		mytrace(inspect.stack())
		self.force = force
		if self.device_model == 'iPad' and not force:
			sleep(0.5) # let time to previous view to close
			view.present(mode, popover_location=popover_location,hide_title_bar=hide_title_bar)
			if isinstance(view, ui.TextField):
				view.begin_editing()
			view.wait_modal()
		else:
			try:
				self.shield.hidden = False
			except:
				self.shield = ui.Button()
				self.shield.frame = (0,0,self.width, self.height)
				if view.name == 'search':
					self.shield.background_color = (1,1,1, 0.3)
				else:
					self.shield.background_color = (0.8, 0.8, 0.8, 0.8)
				self.shield.hidden = False
				self.shield.action = self.shield_tapped
				self.add_subview(self.shield)
			if shield_height:
				self.shield.height = self['sep'].y
			else:
				self.shield.height = self.height
			self.shield.shield_height = self.shield.height
			self.shield.view = view
			self.shield.bring_to_front()
			view.x, view.y = popover_location
			view.x = min(view.x, self.width - view.width - 2)
			view.y = min(view.y, self.height - view.height - 2)
			view.border_width = 1
			view.border_color = 'blue'
			view.corner_radius = 5
			self.add_subview(view)
			view.bring_to_front()
			if isinstance(view, ui.TextField):
				view.begin_editing()			
			
	def shield_tapped(self, sender):
		mytrace(inspect.stack())
		# tap outside the popover view
		sender.hidden = True
		try:
			self.remove_subview(sender.view)
			if 'due date' in sender.view.name:
				self.set_due_date(sender.view)
			elif sender.view.name == 'select':				
				self.select_action('cancel')		
			elif sender.view.name == 'external_keyboard_keys_combinations':
				self.set_key_event_handlers()	
		except:
			pass
		self.selected_row = None

	@ui.in_background		
	def tableview_did_select(self, tableview, section, row):
		mytrace(inspect.stack())
		#print('tableview_did_select', tableview.name)
		self.selected_row = (section,row)
		if tableview.name == 'select':					
			# all devices: no present modal, no shield
			sel_format = tableview.data_source.items[self.selected_row[1]]
			self.shield.hidden = True
			self.remove_subview(tableview)
			del tableview
			self.select_action(sel_format)		
		elif tableview.name == 'searched_files_list':					
			# all devices: no present modal, no shield
			sel_file = tableview.data_source.items[self.selected_row[1]]
			self.shield.hidden = True
			self.remove_subview(tableview.superview)
			del tableview
			self.prms['path'] = self.current_path
			self.prms['file'] = sel_file
			self.files_action('Open','Open', simul_find=True)
		elif tableview.name == 'keys_combinations':	
			# all devices: no present modal
			v = tableview.superview
			tv2 = v['modifiers']
			tv3 = v['keys']
			action = tableview.data_source.items[row]
			if action in self.external_combinations:
				modifier,key = self.external_combinations[action] 
				tv2.selected_row = tv2.data_source.items.index(modifier)
				tv3.selected_row = tv3.data_source.items.index(key)
			else:
				tv2.selected_row = -1
				tv3.selected_row = -1
		elif tableview.name == 'keys':	
			v = tableview.superview
			tv1 = v['keys_combinations']
			tv2 = v['modifiers']
			iaction = tv1.selected_row[1]
			action = tv1.data_source.items[iaction]
			if tv2.selected_row[1] <= 0:
				tv2.selected_row = 0 # modifier = none
			tup = (tv2.data_source.items[tv2.selected_row[1]], tableview.data_source.items[row])
			# check if same combination not already used
			for a in self.external_combinations:
				if a != action and tup == self.external_combinations[a]:
					# same combination exists for other action
					tableview.selected_row = -1
					return
			self.external_combinations[action] = tup
			tv1.reload_data()
			tv1.selected_row = iaction
		elif tableview.name == 'modifiers':	
			v = tableview.superview
			tv1 = v['keys_combinations']
			tv3 = v['keys']
			iaction = tv1.selected_row[1]
			action = tv1.data_source.items[tv1.selected_row[1]]
			tup = (tableview.data_source.items[row], tv3.data_source.items[tv3.selected_row[1]])
			# check if same combination not already used
			for a in self.external_combinations:
				if a != action and tup == self.external_combinations[a]:
					# same combination exists for other action
					tableview.selected_row = -1
					return
			self.external_combinations[action] = tup
			tv1.reload_data()
			tv1.selected_row = iaction
		elif tableview.name != 'outliner':
			# any of the popover tableviews
			if self.device_model == 'iPad':
				# real popover with wait modal
				tableview.close()
			else:
				# simulated popover with shield
				if tableview.name == 'files':
					act = tableview.data_source.items[self.selected_row[1]]
					self.remove_subview(tableview)
					del tableview
					self.shield.hidden = True
					self.files_action(None, act) # no need to pass waited sender
				elif tableview.name == 'formats':					
					loc_format = tableview.data_source.items[self.selected_row[1]]['title']
					self.switch = tableview['1st level has outline'].value
					self.remove_subview(tableview)
					del tableview
					self.shield.hidden = True
					self.format_action(loc_format)		
				elif tableview.name.startswith('for outline'):										
					row = tableview.outline_row
					act = tableview.data_source.items[self.selected_row[1]]
					self.remove_subview(tableview)
					del tableview
					self.shield.hidden = True
					self.popup_menu_action(act, row=row)
				elif tableview.name == 'show':					
					act = tableview.data_source.items[self.selected_row[1]]
					self.selected_date = tableview['dates_segmentedcontrol'].selected_index 
					self.remove_subview(tableview)
					del tableview
					self.shield.hidden = True
					self.show_action(act)	
					
	def tableview_can_delete(self, tableview, section, row):
		mytrace(inspect.stack())
		# Return True if the user should be able to delete the given row.
		if tableview.name == 'keys_combinations':	
			action = tableview.data_source.items[row]
			if action not in self.external_combinations:
				return False
			return True

					
	def tableview_title_for_delete_button(self, tableview, section, row):
		mytrace(inspect.stack())
		if tableview.name == 'keys_combinations':	
			# not real delete, but remove from configured combinations
			return 'disable'
					
	def tableview_delete(self,tableview,section,row):
		mytrace(inspect.stack())
		if tableview.name == 'keys_combinations':	
			# not real delete, but remove from configured combinations
			action = tableview.data_source.items[row]
			del self.external_combinations[action]
			tableview.reload_data()		

	def textfield_should_return(self, textfield):
		mytrace(inspect.stack())
		#print('textfield_should_return:', textfield.name)
		textfield.end_editing()
		if self.device_model == 'iPad' and not self.force:
			textfield.close()  
		else: 
			if textfield.name == 'search':
				textfield.text = ''
				self.textfield_did_change(textfield)
				self.tv.reload_data()
			elif textfield.name == 'font_size':						
				n = int(textfield.text)
				self.set_font(font_size=n)
			elif textfield.name == 'image_size':			
				return	
			elif textfield.name == 'search_files':
				ui.delay(partial(self.search_files, textfield.text),0.1)		
			self.remove_subview(textfield)
			del textfield
			self.shield.hidden = True
		
	def textfield_did_end_editing(self,textfield):
		mytrace(inspect.stack())
		#print('textfield_did_end_editing:', textfield.name)
		if textfield.name in ['font_size', 'search', 'image_size']:
			if _getframe(1).f_code.co_name == 'key_pressed':
				# return key pressed in SetTextFieldPad
				if self.device_model == 'iPad' and not self.force:
					textfield.close()
				else: 
					if textfield.name == 'search':
						textfield.text = ''
						self.textfield_did_change(textfield)
						self.tv.reload_data()
					elif textfield.name == 'font_size':						
						n = int(textfield.text)
						self.set_font(font_size=n)
					elif textfield.name == 'image_size':					
						return	
					self.remove_subview(textfield)
					del textfield
					self.shield.hidden = True
			else:
				# tap outside popover
				if self.device_model == 'iPad':
					pass
				else: 
					self.shield_tapped(self.shield)

	def button_files_action(self,sender):	
		mytrace(inspect.stack())
		if not isinstance(sender, ui.Button):
			act = sender
			self.files_action(sender, act)
		else:
			x = sender.x + sender.width/2
			y = sender.y + sender.height
			sub_menu = ['Set current path', 'New', 'Open','Save', 'Rename']
			if self.log == 'yes':
				sub_menu.append('Play log')
			#sub_menu.append('Recover if incoherent text and content')
			sub_menu.append('Send text to app')
			sub_menu.append('Search')
			tv = ui.TableView(name='files')
			tv.row_height = 30
			h = tv.row_height*len(sub_menu)
			tv.frame = (0,0,330,h)
			tv.data_source = ui.ListDataSource(items=sub_menu)
			tv.allows_multiple_selection = False
			tv.delegate = self
			self.selected_row = None
			self.present_popover(tv, 'popover',popover_location=(x,y),hide_title_bar=True)
			#tv.present('popover',popover_location=(x,y),hide_title_bar=True)
			#tv.wait_modal()
			if self.device_model == 'iPad':
				if not self.selected_row:
					return
				act = sub_menu[self.selected_row[1]]
				self.files_action(sender, act)

	def files_action(self, sender, act, simul_find=None):
		mytrace(inspect.stack())
		if act in ['New', 'Open']:
			if self.file:
				# current file loaded
				if self.modif:
					# current file modified
					b = console.alert('⚠️ File has been modified', 'save before loading another?', 'yes', 'no', hide_cancel_button=True)
					if b == 1:
						self.file_save()
		if act == 'New':
			self['title'].text = '?'
			self.tv.text = ''
			self.outline_format = 'decimal'
			self.set_font(font_type='Menlo', set=False)		
			self.set_font(font_size=18, set=False)	
			# simulate tab pressed
			self.open_log()
			vals = [0]
			outline = self.OutlineFromLevelValue(vals)
			n = len(outline)
			opts = {}
			item = {'title':'','outline':outline, 'content':(vals,n,opts)}
			self.tv.data_source.items = [item]
			self.modif = True
			self.cursor = (0,0)
			self.auto_save = 'no'
			self.file = None
			self.undo_multiples = []
			self.undo_multiples_index = -1
			self.undo_save('')
			if self.show_mode == 'View dates':
				# reset normal view
				self.tv.y = self.ht
				self['dates_title'].hidden = True
			self.show_mode = 'Expand all'
			self.tv.reload_data
			self.last_save_datetime = ''
		elif act == 'Open':
			if sender == 'Open':
				self.path = self.prms['path']
				self.file = self.prms['file']
				if 'font' in self.prms:
					self.set_font(font_type=self.prms['font'])		
				if 'font_size' in self.prms:
					self.set_font(font_size=self.prms['font_size'])	
				if 'font_hidden' in self.prms:
					self.set_font(font_hidden_size=self.prms['font_hidden'])	
				self.pick_open_callback(None, simul_find=simul_find)		
			else:
				f = self.pick_file('from where to open the file', uti=['public.item'], callback=self.pick_open_callback, ask=False, init=self.current_path)
				if not f:
					console.hud_alert('no file has been picked', 'error', 3)
					return
				if f == 'delayed':
					# Files app via UIDocumentPickerViewController needs delay
					return
				# immediate return for Files_Picker use for local Pythonista files
				simul = 'file://' + f
				self.pick_open_callback(simul)		
		elif act == 'Save':
			self.path = self.current_path
			if not self.file:				
				while True:
					f = console.input_alert('Name of new file', hide_cancel_button=True)
					if not f:
						b = console.alert('❌ No file name has been entered','','retry','cancel',hide_cancel_button=True)
						if b == 2:
							return
						else:
							continue
					if f.endswith('.'):
						b = console.alert('❌ file name may not end with a "."','','retry','cancel',hide_cancel_button=True)
						if b == 2:
							return
						else:
							continue
					if f.lower().endswith('.outline'):
						b = console.alert('❌ file name may end with ".outline"', '','retry','cancel',hide_cancel_button=True)
						if b == 2:
							return
						else:
							continue
					if os.path.exists(self.path+f+'.outline'):
						b = console.alert('❌ '+f+' .outline file already exists','in selected folder','retry', 'cancel', hide_cancel_button=True)
						if b == 2:
							return
						else:
							continue
					break
				self.file = f
			self['title'].text = self.file
			self.file_save()
				
		elif act == 'Rename':
			# check if open/new files exist
			# ask new name
			f = console.input_alert('Name of new file', hide_cancel_button=True)
			if not f:
				console.hud_alert('no file name has been entered','error', 3)
				return
			if f.endswith('.'):
				console.hud_alert('file name may not end with "."','error', 3)
				return
			if f.lower().endswith('.outline'):
				console.hud_alert('file name may not end with ".outline"','error', 3)
				return
			oldnam = self.file + self.last_save_datetime + '.outline'
			newnam = f + self.last_save_datetime + '.outline'
			if os.path.exists(self.path+newnam):
				console.hud_alert('new name already exists','error', 3)
				return
			# rename
			os.rename(self.path+oldnam, self.path+newnam)
			# activate new file
			self.file = f
			self['title'].text = self.file
		elif act == 'Play log':
			if not self.file:
				console.hud_alert('no file is active','error', 3)
				return
				
			f = self.pick_file('from where to open the log', uti=['public.item'], callback=self.pick_log_callback, ask=False, init=self.current_path)
			if not f:
				console.hud_alert('no log has been picked','error', 3)
				return
			if f == 'delayed':
				# Files app via UIDocumentPickerViewController needs delay
				return
			# immediate return for Files_Picker use for local Pythonista files
			simul = 'file://' + f
			self.pick_log_callback(simul)		
		elif act == 'Set current path':
			f = self.pick_file('from where to save', uti=['public.folder'], callback=self.pick_folder_callback)
			if not f:
				console.hud_alert('no folder has been picked','error', 3)
				return
			if f == 'delayed':
				# Files app via UIDocumentPickerViewController needs delay
				return
			# immediate return for Files_Picker use for local Pythonista files
			simul = 'file://' + f
			self.pick_folder_callback(simul)				
		elif act == 'Recover if incoherent text and content':
			err = False
			row = 0
			for item in self.tv.data_source.items:
				vals,n,opts = item['content']
				txt = item['outline'] + item['title']
				outline = self.OutlineFromLevelValue(vals)
				nn = len(outline)
				if nn != n:
					# real outline is bigger, thus text more little
					self.tv.data_source.items[row]['outline'] = outline		
					self.tv.data_source.items[row]['content'] = (vals,nn,opts)			
					self.tv.data_source.items[row]['title'] = txt[nn:]
					err = True
				row += 1	
			if err:
				console.hud_alert('content has been modified', 'error', 3)
				self.modif = True
				self.tv.reload_data()
		elif act == 'Search':
			x = sender.x +sender.width/2
			y = sender.y + sender.height
			tf = ui.TextField(name='search_files')
			# textfield background color does not work
			tfo = ObjCInstance(tf).textField()
			tfo.backgroundColor = ObjCClass('UIColor').colorWithRed_green_blue_alpha_(1, 1, 0, 1)
			tf.background_color = 'yellow'
			tf.font = ('Menlo',18)
			tf.frame = (x,y,400,20)
			tf.placeholder = 'type text to be searched'
			tf.delegate = self
			tf.text = ''
			self.present_popover(tf, 'popover',popover_location=(x,y),hide_title_bar=True, force=True)

		elif act == 'Send text to app':
			if not self.file:
				console.hud_alert('no active file','error',3)
				return
			b = console.alert('Share as','', '.txt','.pdf', 'cancel', hide_cancel_button=True)
			if b == 3:# cancel
				return
			path = argv[0]
			i = path.rfind('/')
			path = path[:i+1] + 'outline.'
			if b == 1:
				path += 'txt'
			elif b == 2:
				path += 'pdf'
				# A4 = 210 x 297mm
				# margins: left=15 top,bottom,right=5
				# h = nlines_per_page * font
				# width of text line
				wt = self.width
				# 15mm for left margin and 5mm for right margin on the 210mm paper width
				w = wt * 210 / (210 - 15 - 5)
				# 5mm for top and bottom margins on the 297mm paper height
				h = w * 297/210 
				ht = h * (297 - 5 - 5) / 297
				# height on one line is font size + 2
				dy = self.font_size + 2
				x0 = w * 15/210
				y0 = h * 5/297
				out = PdfFileMerger()
				row = 0
				while 1 == 1:
					with ui.ImageContext(w,h) as ctx:
						pth= ui.Path.rect(0,0,w,h)
						ui.set_color('white')
						pth.fill()
						x = x0
						y = y0
						while row < len(self.tv.data_source.items):
							item = self.tv.data_source.items[row]
							vals,n,opts = item['content']
							hrow = self.tableview_height_for_section_row(self.tv,0,row, nosort=True)
							if (y+hrow) > h:
								# no room enough on current page for row
								break	# do not process it on this page
							txt = item['title']
							outline = item['outline']
							wo,ho = ui.measure_string(outline, font=(self.font, self.font_size))
							ui.draw_string(outline, rect=(x, y, wo, ho), font=(self.font, self.font_size), color=self.outline_rgb, alignment=ui.ALIGN_LEFT)			
							xa = x+wo
							if 'image' in opts:
								img = opts['image']
								ui_image = ui.Image.named(img[0]).with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
								himg = img[1]*self.font_size
								wi,hi = ui_image.size
								wimg = himg * wi/hi
								pos = img[2]
								if pos == 'left':
									img_frame = (xa,y,wimg,himg)				
									txt_frame = (xa+wimg+4,y,self.width - xa - 4 - wimg, hrow)
									htxt = hrow
								elif pos == 'right':
									img_frame = (self.width-wimg,y,wimg,himg)				
									txt_frame = (xa,y,self.width - xa - 4 - wimg, hrow)			
									htxt = hrow	
								elif pos == 'top':
									htxt = hrow - himg	
									txt_frame = (xa,y+himg,self.width-xa-4,htxt)
									img_frame = (xa,y,wimg,himg)
								elif pos == 'bottom':
									htxt = hrow - himg	
									txt_frame = (xa,y,self.width-xa-4,htxt)			
									img_frame = (xa,y+htxt,wimg,himg)			
								xd,yd,wd,hd = img_frame
								ui_image.draw(xd,yd,wd,hd)
								del ui_image
							else:
								himg = 0
								wimg = 0	
								htxt = hrow
								txt_frame = (xa,y,self.width - xa - 4, hrow)			
							xd,yd,wd,hd = txt_frame		

							# set attributes for general text
							attrText = NSMutableAttributedString.alloc().initWithString_(txt)

							font = UIFont.fontWithName_size_traits_(self.font, self.font_size,0)
							attributes = {NSForegroundColorAttributeName:self.text_color, NSFontAttributeName:font}													
							attrText.setAttributes_range_(attributes, NSRange(0,len(txt)))		
							
							# test attributes: bold, italic, underline, strikethrough
							attribs = opts.get('attribs', None)
							if attribs:
								# opts['attribs'] = [(s,e,'biusohcqg'),(s,e,'B'),...]
								for attrib in attribs:
									sa,ea,biusohcqg = attrib
									attributes = self.get_attributes(biusohcqg)
									attrText.setAttributes_range_(attributes, NSRange(sa,ea-sa))

							rect = CGRect(CGPoint(xd,yd), CGSize(wd,hd))
							attrText.drawInRect_(rect)
			
							y += hrow
							row += 1
						# end of rows of the same page
						ui_image = ctx.get_image()
					# process page
					pil_image = Image.open(BytesIO(ui_image.to_png()))
					del ui_image
					if pil_image.mode == "RGBA":
						pil_image = pil_image.convert("RGB")
					pil_image.save(path,"PDF",resolution=100.0)		
					del pil_image
					out.append(open(path, 'rb'))
					os.remove(path)
					if row >= len(self.tv.data_source.items):
						break
				# end of loop on pages
				with open(path, "wb") as fout:
					out.write(fout)
				self.open_in(path)
				return

			with open(path, mode='wt', encoding='utf-8', errors="surrogateescape") as fil:
				t = ''
				for item in self.tv.data_source.items:
					ls = item['title'].split(lf)
					outline = item['outline']
					first = True
					for l in ls:
						if first:
							t += outline          + l + lf #1.1_Word 1
							first = False
						else: 
							t += ' '*len(outline) + l + lf #    Word 2
				fil.write(t)
				del t
			self.open_in(path)
			# code does not wait, thus no remove
			#os.remove(path)			
		else:
			console.hud_alert('content has not been modified', 'success', 3)
			
	def search_files(self, search_text):
		mytrace(inspect.stack())
		txt = normalize('NFKD', search_text).encode('ASCII', 'ignore')
		txt = str(txt,'utf-8').upper()
		files = os.listdir(path=self.current_path)
		sub_menu = []
		for f in files:
			if f.endswith('.outline'):
				with open(self.current_path+f, mode='rt', encoding='utf-8', errors="surrogateescape") as fil:
					c = fil.read()
					c_prms = c.split(lf)
					c = c_prms[0]
					cs = literal_eval(c)
					del c
					del c_prms
					for c in cs:
						vals,outline,opts,dict_text = c
						t = dict_text['text']					
						t = normalize('NFKD', t).encode('ASCII', 'ignore')
						t = str(t,'utf-8').upper()
						if txt in t:
							sub_menu.append(f)
							break
					del t
					del cs
					
		v = ui.View(name='searched_files')
		v.background_color = 'yellow'
		v.frame = (0,0,300,300)

		y = 4	
		l1 = ui.Label()
		l1.frame = (4,y,140,20)
		l1.text = 'files containing'
		w = ui.measure_string(l1.text, font=l1.font)[0] + 20
		l1.width = w
		v.add_subview(l1)
		l2 = ui.Label()
		l2.text_color = 'blue'
		x = l1.x+l1.width+4
		l2.frame = (x,y,v.width-x-4,20)
		l2.text = search_text
		self.search_text_in_files = search_text
		v.add_subview(l2)

		y += l1.height + 4		
		tv = ui.TableView(name='searched_files_list')
		tv.corner_radius = 5
		tv.row_height = 35
		h = tv.row_height*len(sub_menu)		
		tv.frame = (4,y,v.width-8,h)
		lds = ui.ListDataSource(items=sub_menu)
		lds.tableview = tv 	# my own attribute needed in tableview_did_select
		lds.delete_enabled = False
		tv.data_source = lds
		tv.data_source.tableview_cell_for_row = self.searchedfiles_cell_for_row
		tv.delegate = self
		tv.data_source.selected_row = -1
		tv.allows_multiple_selection = False
		wmax = 0
		for f in tv.data_source.items:
			w = ui.measure_string(f, font=('Menlo',16))[0]
			wmax = max(wmax,w)
		wmax += 20
		v.width = min(self.width*0.8,wmax+8)
		tv.width = v.width - 8

		v.add_subview(tv)

		v.height = min(self.height*0.8, tv.y + h + 4)
		hmax = v.height-4-tv.y
		tv.height = min(hmax, h)
				
		x = self['b_files'].x + self['b_files'].width/2
		y = self['b_files'].y + self['b_files'].height
		self.present_popover(v, 'popover',popover_location=(x,y),hide_title_bar=True, force=True)
					
					
	@on_main_thread
	def open_in(self, path):
		mytrace(inspect.stack())
		vo = ObjCInstance(self)
		SUIViewController = ObjCClass('SUIViewController')
		root_vc = SUIViewController.viewControllerForView_(vo)
		main_view=root_vc.view()
		
		url = nsurl(path)		
		url_array = [url]
		
		UIActivityViewController = ObjCClass('UIActivityViewController').alloc().initWithActivityItems_applicationActivities_(url_array,None)
				
		UIActivityViewController.setCompletionHandler_(None)

		if self.device_model == 'iPad':		
			UIActivityViewController.popoverPresentationController().sourceView = main_view
			UIActivityViewController.popoverPresentationController().sourceRect = CGRect(CGPoint(100, -120), CGSize(200,200))
		
		r = root_vc.presentViewController_animated_completion_(UIActivityViewController, True, None)
			
	def pick_open_callback(self,param, simul_find=None):
		mytrace(inspect.stack())
		#print('pick_open_callback:',param)
		if param == 'canceled':
			console.hud_alert('no file has been picked','error', 3)
			return
		if param:
			# param = None if open at stat without passing by open files option
			f = str(param)[7:]  # remove file://
			if not f.lower().endswith('.outline'):
				console.hud_alert('file has to be a ".outline"','error', 3)
				return
			i = f.rfind('/')
			self.path = f[:i+1]
			self.file = f[i+1:]
		else:
			# self.path and .file already known
			pass
		if '/private/var/mobile/Library/Mobile Documents/' in self.path:
			# icloud file
			# force download
			url = nsurl('file://' + (self.path+self.file).replace(' ','%20'))
			NSFileManager = ObjCClass('NSFileManager').defaultManager()
			ret = NSFileManager.startDownloadingUbiquitousItemAtURL_error_(url, None)
			#print(url,'downloaded',ret)	# True if ok		
		if not os.path.exists(self.path+self.file):
			#print('❌ '+self.file_content+' does not exist')
			if '/private/var/mobile/Library/Mobile Documents/' in self.path:
				console.hud_alert('file does not (yet) exist, retry', 'error', 3)
			else:
				console.hud_alert('file does not exist', 'error', 3)
			return
		# check if file name in new style xxxxx_yyyymmdd_hhmmss
		i = self.file.rfind('.')
		if i < 0:
			i = len(self.file) 
		nam = self.file[:i]
		num = nam[-16:]
		try:
			dt = datetime.strptime(num,'_%Y%m%d_%H%M%S') # datetime	
			self.last_save_datetime = num
			self.file = nam[:-16]
		except Exception as e:
			#print(e)
			console.hud_alert('file not xxx_yyyymmdd_hhmmss.outline', 'error', 3)
			return
		self['title'].text = self.file
		with open(self.path+self.file+self.last_save_datetime+'.outline',mode='rt', encoding='utf-8', errors="surrogateescape") as filc:
			c = filc.read()
		c_prms = c.split(lf)
		c = c_prms[0]
		prms = c_prms[1]
		cs = literal_eval(c)
		del c
		del c_prms

		items = []
		#print(cs)
		#print(lines)
		for c in cs:
			#print(c,t)
			# new style: c = (vals,outline, {opts},{'text':text})
			vals,outline,opts,dict_text = c
			n = len(outline)
			item = {}
			item['title'] = dict_text['text']
			item['content'] = (vals,n,opts)
			item['outline'] = outline
			items.append(item)
			
		del cs
	
		if prms.startswith('{'):
			prms = literal_eval(prms)
			self.outline_format = prms['format']
			if '1st level has outline' in prms:
				self.first_level_has_outline = prms['1st level has outline']
			else:
				self.first_level_has_outline = True
			self.set_font(font_type=prms['font'], set=False)		
			self.set_font(font_size=prms['font_size'], set=False)	
		else:
			self.outline_format = prms
			self.first_level_has_outline = True
						
		#self.set_outline_attributes()
		self.prms_save()
		self.open_log()
		self.cursor = (0,0)
		self.edited_row = None
		self.undo_multiples = []
		self.undo_multiples_index = -1
		self.undo_save('')
		if self.show_mode == 'View dates':
			# reset normal view
			self.tv.y = self.ht
			self['dates_title'].hidden = True
		self.show_mode = 'Expand all'
		
		self.tv.data_source.items = items
		del items
		
		if simul_find:
			self.button_search_action(self['b_search'], simul_find=simul_find)

	def pick_folder_callback(self,param):
		mytrace(inspect.stack())
		#print('pick_folder_callback:',param)
		if param == 'canceled':
			console.hud_alert('no folder has been picked','error', 3)
			return
		fil = str(param)[7:]  # remove file://				
		if fil[-1] != '/':
			fil += '/'
		self.current_path = fil
		self.prms['current path'] = self.current_path
				
	def pick_log_callback(self,param):
		mytrace(inspect.stack())
		#print('pick_log_callback:',param)
		if param == 'canceled':
			console.hud_alert('no log has been picked','error', 3)
			return
		f = str(param)[7:]  # remove file://
		self.tv.text = ''
		i = f.rfind('/')
		path = f[:i+1]
		log  = f[i+1:]
		with open(path+log, mode='rt', encoding='utf-8', errors="surrogateescape") as fil:
			recs = fil.read().split(lf)
			for rec in recs[:-1]:
				fs = rec.split(',')
				if fs[0] == 'drop':
					found,fm,tm = (int(fs[1]), int(fs[2]), int(fs[3]))
					if len(fs) > 4:
						tgx = int(fs[4])
					else:
						tgx = 0
					self.drop(found, fm, tm, tgx, play=True)
				else:
					row = int(fs[0])
					rge = (int(fs[1]), int(fs[2]))
					rep = fs[3]
					replacement = rep.replace('lf',lf).replace('backtab','\x02').replace('tab','\x01')
					self.textview_should_change(row, rge, replacement, play=True)

	def pick_file(self, title, ext=None, uti=['public.item'], callback=None, ask=True, init=None):
		mytrace(inspect.stack())
		path = os.path.expanduser('~/')
		img = uti == ['public.image']
		if ask:
			# ask user from where
			if img:
				try:
					b = console.alert(title,'','Local Pythonista', 'Files app', 'Photos', hide_cancel_button=False)
				except:
					return None
			else:
				try:
					b = console.alert(title,'','Local Pythonista', 'Files app', hide_cancel_button=False)
				except:
					return None
		else:
			# use current_path to know from where
			if path in self.current_path:
				b = 1
			else:
				b = 2
			path = self.current_path
		if b == 1:
			if ext:
				fil = File_Picker.file_picker_dialog('Pick a text file', root_dir=path, file_pattern=r'^.*\{}$'.format(ext), only=True)	
			elif uti == ['public.folder']:
				fil = File_Picker.file_picker_dialog('Select a folder where to create the new', root_dir=path, select_dirs=True, only=True)
			else:			
				fil = File_Picker.file_picker_dialog(title, root_dir=path)

			#print(fil)
			return fil
		elif b == 2:	
			sleep(0.2)	# to be sure previous uiview closed
			self.picked_file = None
			#ui.delay(partial(self.pick,uti), 0.0)
			UIDocumentPickerViewController = self.MyPickDocument(600,500, callback=callback, UTIarray=uti, init=init)
			return 'delayed'
		elif b == 3:	
			# photos
			assets = get_assets(media_type='image')
			asset = pick_asset(assets, title='pick a photo')
			if asset:
				# not canceled
				filename = str(ObjCInstance(asset).filename())
				fil = self.current_path + filename
				pil = asset.get_image(original=False)
				pil.save(fil, quality=95)
				del pil
				return fil
								
	@on_main_thread	
	def MyPickDocument(self, w, h, callback=None, UTIarray=['public.item'], PickerMode=1, init=None):
		mytrace(inspect.stack())		
		# view needed for picker
		uiview = ui.View()
		uiview.frame = (0,0,w,h)
		uiview.present('sheet',hide_title_bar=True)
		
		UIDocumentPickerMode = PickerMode
															# 1 = UIDocumentPickerMode.open
															#   this mode allows a search field
															#   and url in delegate is the original one
															# 0 = UIDocumentPickerMode.import
															#   url is url of a copy
															# 2 = UIDocumentPickerModeExportToService (copy)
															# 3 = UIDocumentPickerModeMoveToService   (move)⚠️
		UIDocumentPickerViewController = ObjCClass('UIDocumentPickerViewController').alloc().initWithDocumentTypes_inMode_(UTIarray,UIDocumentPickerMode)
		#print(dir(UIDocumentPickerViewController))
	
		objc_uiview = ObjCInstance(uiview)
		SUIViewController = ObjCClass('SUIViewController')
		vc = SUIViewController.viewControllerForView_(objc_uiview)	
				
		UIDocumentPickerViewController.setModalPresentationStyle_(3) #currentContext
		
		# Use new delegate class:
		delegate = MyUIDocumentPickerViewControllerDelegate.alloc().init()
		UIDocumentPickerViewController.delegate = delegate	
		UIDocumentPickerViewController.callback = callback	# used by delegate
		UIDocumentPickerViewController.uiview   = uiview  		# used by delegate
		UIDocumentPickerViewController.done = False
		UIDocumentPickerViewController.allowsMultipleSelection = False
		if init:
			UIDocumentPickerViewController.setDirectoryURL_(nsurl(init))
		vc.presentViewController_animated_completion_(UIDocumentPickerViewController, True, None)#handler_block)
		
		return UIDocumentPickerViewController
			
	def open_log(self):	
		mytrace(inspect.stack())		
		if self.log == 'yes':
			try:
				self.log_fil.close()
			except:
				pass
			self.log_fil = open(self.log_file, mode='wt', encoding='utf-8', errors="surrogateescape")
					
	def button_version_action(self,sender):
		mytrace(inspect.stack())
		x = sender.x + sender.width/2
		y = sender.y + sender.height
		tv = ui.TextView(name='versions')
		tv.editable = False
		w,h = self.get_screen_size()
		w -= 100
		h -= 200
		tv.frame = (0,0,w-10,h-10)
		tv.font = ('Menlo',14)
		tv.text = Versions
		tv.name = 'Versions'
		tv.present('popover',popover_location=(x,y),hide_title_bar=False)
		
		# Coloring versions numbers in TextView
		tvo = ObjCInstance(tv)
		tvo.setAllowsEditingTextAttributes_(True)
		txto = ObjCClass('NSMutableAttributedString').alloc().initWithString_(tv.text)
		color = ObjCClass('UIColor').redColor()
		attribs = {NSForegroundColorAttributeName:color, NSFontAttributeName:font}
		vers = finditer('Version V', tv.text)
		for ver in vers:
			st,end = ver.span()
			txto.setAttributes_range_(attribs, NSRange(st,end-st+5)) # + 5 due to Vnn.nn
		@on_main_thread
		def th():
			mytrace(inspect.stack())
			tvo.setAttributedText_(txto)
		th()
		
		#tv.wait_modal()
		
	def button_format_action(self,sender):
		mytrace(inspect.stack())
		x = sender.x +sender.width/2
		y = sender.y + sender.height
		sub_menu = []
		i = 0
		for format in self.outline_formats.keys():
			if 'with title' not in format:
				menu = {'title':format, 'accessory_type':'detail_button'}
				if format == self.outline_format:
					idx = (0,i)
				sub_menu.append(menu)
				i += 1
		tv = ui.TableView(name='formats')
		tv.row_height = 35
		h = tv.row_height*len(sub_menu)
		sw = ui.Switch(name='1st level has outline')
		ws,hs = sw.width,sw.height
		sw.frame = (250-ws-2,h+2,ws,hs)
		sw.value = self.first_level_has_outline
		tv.add_subview(sw)
		sl = ui.Label()
		sl.frame = (12,h+2,sw.x-14,hs)	
		sl.text = '1st level has outline'	
		tv.add_subview(sl)
		h += hs + 4
		
		tv.frame = (0,0,250,h)
		lds = ui.ListDataSource(items=sub_menu)
		lds.tableview = tv 	# my own attribute needed in action
		lds.delete_enabled = False
		lds.tableview = tv # used in format selection
		tv.data_source = lds
		tv.data_source.selected_row = idx
		tv.allows_multiple_selection = False
		tv.delegate = self
		tv.data_source.tableview_cell_for_row = self.format_cell_for_row
		lds.accessory_action = self.accessory_action

		self.selected_row = None
		self.switch = self.first_level_has_outline
		self.present_popover(tv, 'popover',popover_location=(x,y),hide_title_bar=True)
		if self.device_model == 'iPad':
			if not self.selected_row:
				return
			loc_format = sub_menu[self.selected_row[1]]['title']
			self.switch = tv['1st level has outline'].value
			self.format_action(loc_format)		
			
	def format_cell_for_row(self, tableview, section, row):
		mytrace(inspect.stack())
		cell = ui.TableViewCell()
		cell.text_label.text = tableview.data_source.items[row]['title']
		if tableview.data_source.selected_row == (section,row):
			cell.bg_color = 'lightgray'
		return cell
		
	def format_action(self, loc_format):
		mytrace(inspect.stack())
		#print('format_action')
		#print(loc_format, self.outline_format, self.switch, self.first_level_has_outline)
		if loc_format != self.outline_format or self.switch != self.first_level_has_outline:
			save_format = self.outline_format	# save in case of error
			save_switch = self.first_level_has_outline
			self.outline_format = loc_format
			self.first_level_has_outline = self.switch
			# 1) check if format accepts high levels
			for item in self.tv.data_source.items:
				vals,n,opts = item['content']
				t_out = self.OutlineFromLevelValue(vals)
				if not t_out:
					# too high level
					console.hud_alert('too high outline level for this outline format','error', 3)
					self.outline_format = save_format	# reset
					self.first_level_has_outline = save_switch
					return
			# 2) replace outlines
			row = 0
			for item in self.tv.data_source.items:
				vals,n,opts = item['content']
				t_out = self.OutlineFromLevelValue(vals)
				n = len(t_out)
				self.tv.data_source.items[row]['content'] =(vals,n,opts)
				self.tv.data_source.items[row]['outline'] = t_out
				row += 1
			self.modif = True
			self.tv.reload_data()
			
	def accessory_action(self,sender):
		mytrace(inspect.stack())
		#print('accessory_action',sender.tapped_accessory_row)
		#sender.tableview.close()
		ft = sender.items[sender.tapped_accessory_row]['title']
		outline_types = self.outline_formats[ft][0]
		blanks = self.outline_formats[ft][1]
		a = []
		for l,outline_type in enumerate(outline_types):
			a.append(' '*blanks*l + outline_type)
		tv = ui.TableView(name='accessory')
		tv.allows_selection = False
		lds = ui.ListDataSource(items=a)
		lds.delete_enabled = False
		tv.data_source = lds
		tv.row_height = 30
		h = tv.row_height*len(outline_types)
		tv.frame = (0,0,180,h)
		tv.name = ft
		x = sender.tableview.width/4
		y = (1+sender.tapped_accessory_row) * sender.tableview.row_height
		self.present_popover(tv, 'popover',popover_location=(x,y),hide_title_bar=True)
		#tv.present('popover',popover_location=(x,y),hide_title_bar=True)
		tv.wait_modal()		
					
	def button_color_action(self,sender):				
		mytrace(inspect.stack())
		rgb = OMColorPickerViewController(title='choose outline color', rgb=self.outline_rgb)
		if not rgb:
			return
		self.outline_rgb = rgb
		self.outline_color = UIColor.colorWithRed_green_blue_alpha_(self.outline_rgb[0], self.outline_rgb[1], self.outline_rgb[2], 1)
		self.outline_attributes = {NSForegroundColorAttributeName:self.outline_color, NSFontAttributeName:font}
		
		self.tv.reload_data()
		
	def tableview_number_of_rows(self, tableview, section):
		mytrace(inspect.stack())
		# Return the number of rows in the section
		return len(tableview.data_source.items)
			
	@on_main_thread
	def set_content_inset(self,bb):
		mytrace(inspect.stack())
		# Standard TextView has a top positive inset by default
		ObjCInstance(bb).textContainerInset = UIEdgeInsets(0,0,0,0)

	def tableview_cell_for_row(self, tableview, section, rowin):
		mytrace(inspect.stack())
		#print('tableview_cell_for_row',rowin)
		if self.show_mode == 'View dates':
			# sort rows
			dtnow = datetime.now() # to be sure all items have same date
			rows_with_dates = []
			ir = 0
			for item in self.tv.data_source.items:
				vals,n,opts = item['content']
				dates = opts.get('dates',None)
				dt = None
				if dates:
					dt =  dates[self.selected_date]
				if dt:
					dt = datetime.strptime(dt,'%Y-%m-%d %H:%M:%S') # datetime	
				else:
					dt = dtnow
				rows_with_dates.append((ir,dt))
				ir += 1
			# sort f(self.dates_sort_mode): 0=normal 1=descending 2=ascending
			if self.dates_sort_mode == 0:
				pass # no sort
			elif self.dates_sort_mode == 1:
				rows_with_dates.sort(key=lambda x:x[1], reverse=True) # sort descending
			elif self.dates_sort_mode == 2:
				rows_with_dates.sort(key=lambda x:x[1]) # sort ascending
			# get sorted row
			row = rows_with_dates[rowin][0]
		elif 'completed checkboxes' in self.show_mode:
			# sort rows on completed checkbox
			rows_with_chk = []
			ir = 0
			for item in self.tv.data_source.items:
				vals,n,opts = item['content']
				checkmark = opts.get('checkmark',None)
				chk = 1 if checkmark == 'yes' else 0
				rows_with_chk.append((ir,chk))
				ir += 1
			if 'sort at beginning' in self.show_mode:
				rows_with_chk.sort(key=lambda x:x[1], reverse=True) # sort descending
			elif 'sort at end' in self.show_mode:
				rows_with_chk.sort(key=lambda x:x[1]) # sort ascending
			# get sorted row
			row = rows_with_chk[rowin][0]	
		else:
			row = rowin
		# Create and return a cell for the given section/row
		cell = ui.TableViewCell()
		#print('tableview_height_for_section_row called by tableview_cell_for_row',row)
		hrow = self.tableview_height_for_section_row(tableview,section,row, nosort=True)
		#print(rowin,row,hrow)
		self.cells[row] = cell
		item = tableview.data_source.items[row]
		# build cell from left to right
		vals,n,opts = item['content']
		#print('tableview_cell_for_row',opts)
		outline = item['outline']
		bg_color = None
		if self.show_original_area == 'yes':		
			# show original area in TextView
			if self.orig_area:
				fr,to =self.orig_area
				if fr <= row <= to:
					bg_color = 'pink'
		hidden = False		
		ft = (self.font, self.font_size)	
		#cell.text_label.text = item['title']
		#cell.text_label.font = ft
		cell.text_label.number_of_lines = 0	# multi-lines
		#cell.text_label.hidden = True
		h = self.font_size
		if 'hidden' in opts:
			if opts['hidden']:
				hidden = True
		img = opts.get('image', None)
		if self.filter:
			if self.filter[0] == '<':
				if len(vals) >= self.filter[1]:
					hidden = True
			elif self.filter[0] == '=':
				if len(vals) != self.filter[1]:
					hidden = True
			elif self.filter[0] == '>':
				if len(vals) <= self.filter[1]:
					hidden = True
		if hidden:
			ft = (self.font, self.font_hidden_size)
			h = self.font_hidden_size
			x = self.font_size
		if not hidden:
			if self.select:
				sel = ui.Button(name='select')
				sel.row = row
				d = 2
				sel.frame = (d,d,h-2*d,h-2*d)
				sel.background_color = 'red' if row in self.selected_rows_for_cut else 'yellow'
				sel.border_width = 1
				sel.border_color = 'black'
				sel.corner_radius = (h-2*d)/2
				sel.action = self.select_outline
				cell.content_view.add_subview(sel)			
			elif self.checkboxes == 'yes' and self.show_mode != 'View dates':	
				# 1) checkbox				
				chk = ui.Button(name='checkbox')
				d = 2
				chk.frame = (d,d,h-2*d,h-2*d)
				chk.border_width = 1
				chk.border_color = 'black'
				chk.corner_radius = 4
				chk.font = ('<System>',10)#h-2*d)
				chk.action = self.checkbox_button_action
				chk.row = row
				chk.checkmark = False
				if 'checkmark' in opts:
					chk.checkmark = True
					if opts['checkmark'] == 'yes':
						chk.checkmark = True
						chk.image = self.checkmark_ui_image
						chk.border_width = 0
					elif opts['checkmark'] == 'hidden':
						chk.hidden = True
				cell.content_view.add_subview(chk)			
				if bg_color:
					# moving area
					chk.background_color =  bg_color
				if not chk.checkmark:
					dates = opts.get('dates',None)
					if dates:
						due_date = dates[2]
						if due_date:
							chk.image = ui.Image.named('iob:ios7_clock_outline_32')
					
		# 1) outline it-self
		x = 2 * self.font_size	# after checkbox, let a place for hide/show button
		if self.show_mode == 'View dates':
			fsd = int(self.font_size*0.8)
			x = 1 * self.font_size	# no checkbox, let a place for hide/show button
			x += 10+ui.measure_string('0000-00-00', font=(self.font,fsd))[0]
			if not hidden:
				dates = opts.get('dates',None)
				if dates:
					dt = dates[self.selected_date]
					if dt:
						# 2021-08-02 22:08:51
						dl = ui.Label()
						dl.font = (self.font,fsd)
						dl.text_color = 'gray'
						# date stored in file as format '%Y-%m-%d %H:%M:%S'
						dt = datetime.strptime(dt,'%Y-%m-%d %H:%M:%S') # datetime						
						dl.text = f"{dt:{self.dates_format}}"
						dl.frame = (10,0,x,self.font_size)
						cell.content_view.add_subview(dl)				
		else:	
			x = 2 * self.font_size	# after checkbox, let a place for hide/show button
		bb = ui.Label(name='outline')
		bb.row = row
		bb.text = outline
		bb.text_color = self.outline_rgb
		bb.font = ft
		wo,ho = ui.measure_string(outline, font=ft)
		bb.frame = (x,0,wo,ho)
		#bb.border_width = 1
		if not self.select:
			if self.tap_for_popup == 'single':
				tap(bb,self.single_or_double_tap_handler)
			else:
				doubletap(bb,self.single_or_double_tap_handler)
			long_press(bb,self.long_press_handler)
		cell.content_view.add_subview(bb)
		if bg_color:
			bb.background_color = bg_color
		xaftout = x + wo
			
		if not hidden:
			
			# 2) hide/show button
			j = len(outline) - len(outline.lstrip())	# length of front blanks
			wo,ho = ui.measure_string(' '*j, font=ft)
			x = x - self.font_size + wo
			b = ui.Button(name='hide_show_'+str(row))
			# check of children hidden
			vals = self.tv.data_source.items[row]['content'][0]
			row1 = row + 1
			b.image = ui.Image.named('iob:ios7_circle_filled_32')
			hide = False
			if row1 < len(self.tv.data_source.items):
				# row has nexts
				nvals = self.tv.data_source.items[row1]['content'][0]
				if len(nvals) > len(vals):
					# next is child
					opts1 = self.tv.data_source.items[row1]['content'][2]
					b.image = ui.Image.named('iob:arrow_down_b_32')
					if 'hidden' in opts1:
						if opts1['hidden']:
							b.image = ui.Image.named('iob:arrow_right_b_32')
							hide = True
			b.frame = (x,0,h,h)
			if not self.select:
				b.action = self.hide_children_via_button
			b.data = (row,len(vals)-1,hide)
			cell.content_view.add_subview(b)
			if bg_color:
				b.background_color = bg_color

		x = xaftout
		bb = ui.TextView(name='text')				
		#bb.border_width = 1
		if img and not hidden:	
			# image
			himg = img[1]*self.font_size
			iv = ui.Button()
			iv.row = row
			iv.frame = (x,0,self.width-x-4,hrow)
			iv.content_mode = ui.CONTENT_SCALE_ASPECT_FIT
			try:
				iv.image = ui.Image.named(img[0]).with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			except:
				with ui.ImageContext(32,32) as ctx:
					path = ui.Path.rect(0,0,32,32)
					ui.set_color('yellow')
					path.fill()
					ui.draw_string('open\nerror',rect=(0,0,32,32),color='red')
					iv.image= ctx.get_image().with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)

			if not self.select:
				iv.action = self.image_size_action
			wi,hi = iv.image.size
			wimg = wi * himg/hi
			iv.width = wimg
			cell.content_view.add_subview(iv)
			
			pos = img[2]
			if pos == 'left':
				iv.frame = (x,0,wimg,himg)				
				bb.frame = (x+wimg+4,0,self.width - x - 4 - wimg, hrow)
				htxt = hrow
			elif pos == 'right':
				iv.frame = (self.width-wimg,0,wimg,himg)				
				bb.frame = (x,0,self.width - x - 4 - wimg, hrow)			
				htxt = hrow	
			elif pos == 'top':
				htxt = hrow - himg	
				bb.frame = (x,himg,self.width-x-4,htxt)
				iv.frame = (x,0,wimg,himg)
			elif pos == 'bottom':
				htxt = hrow - himg	
				bb.frame = (x,0,self.width-x-4,htxt)			
				iv.frame = (x,htxt,wimg,himg)			
		else:
			himg = 0
			wimg = 0	
			htxt = hrow
			bb.frame = (x,0,self.width - x - 4, hrow)					
			
		# text it-self
		txt = item['title']
		#print(txt)
		if self.autocapitalize_type == 'none':
			bb.autocapitalization_type = ui.AUTOCAPITALIZE_NONE
		elif self.autocapitalize_type == 'words':
			bb.autocapitalization_type = ui.AUTOCAPITALIZE_WORDS
		elif self.autocapitalize_type == 'sentences':
			bb.autocapitalization_type = ui.AUTOCAPITALIZE_SENTENCES
		elif self.autocapitalize_type == 'all':
			bb.autocapitalization_type = ui.AUTOCAPITALIZE_ALL
		bb.delegate = self
		self.set_content_inset(bb)
		bb.row = row
		mytrace("function='in tableview_cell_for_row: before ObjCInstance(bb).tv = bb'")
		ObjCInstance(bb).tv = bb
		bb.text = txt
		bb.text_color = 'blue'
		#bb.border_width = 1
		bb.font = ft
		bb.number_of_lines = 0
		#bb.frame = (x,0,self.width-x-4,ft[1])
		w = bb.width
		bb.size_to_fit()
		ho = bb.height
		bb.frame = (bb.x,bb.y,w,ho)
		#print('bb:',self.font_size,ho)
		if self.select:
			bb.touch_enabled = False
		else:
			mytrace("function='in tableview_cell_for_row: before swipe1'") 
			swipe(bb, self.swipe_left_handler,direction=LEFT)
			mytrace("function='in tableview_cell_for_row: before swipe2'") 
			swipe(bb, self.swipe_right_handler,direction=RIGHT)

		#bb.border_width = 1
		cell.content_view.add_subview(bb)
		
		if not hidden:	
			# separation line
			if self.show_lines_separator == 'yes':					
				sep = ui.Label()
				sep.frame = (0,hrow-1,self.tv.width,1)
				sep.border_width = 1
				sep.border_color = 'lightgray'
				cell.content_view.add_subview(sep)	
			mytrace("function='in tableview_cell_for_row: before self.redraw_textview_attributes(bb,opts)'")
			self.redraw_textview_attributes(bb,opts)
	
		# a lot of segmentation errors when we scroll (which set_cursor)	
		# does only if last action = add row
		if row == self.cursor[0] and len(self.undo_multiples) > 0:
			if self.undo_multiples[-1][0] in  ['CR','tab','back']:# or (row == 0 and txt == ''):
				mytrace("function='in tableview_cell_for_row: before bb.begin_editing()'") 
				bb.begin_editing()
				mytrace("function='in tableview_cell_for_row: before ui.delay(partial'")
				ui.delay(partial(self.textview_did_begin_editing,bb),0.1)
				c = self.cursor[1]
				if c >= len(bb.text):
					c = max(0,len(bb.text))
				#bb.selected_range = (c,c)
				# Pythonista does not allow to set c = len(text) to put cursor at end
				range = NSRange(c,c)
				mytrace("function='in tableview_cell_for_row: before ObjCInstance(bb).setSelectedRange_(range)'")
				ObjCInstance(bb).setSelectedRange_(range)
		
		if bg_color:
			bb.background_color = bg_color

		if not hidden:			
			# create ui.View for InputAccessoryView above keyboard
			mytrace("function='in tableview_cell_for_row: before v = MyInputAccessoryView(row)'")
			v = MyInputAccessoryView(row)
			vo = ObjCInstance(v)									# get ObjectiveC object of v
			mytrace("function='in tableview_cell_for_row: before retain_global(v)'")
			retain_global(v) # see https://forum.omz-software.com/topic/4653/button-action-not-called-when-view-is-added-to-native-view
			bbo = ObjCInstance(bb)
			mytrace("function='in tableview_cell_for_row: before bbo.inputAccessoryView = vo'")
			#rowstr = str(row)
			#bbo.setName_(rowstr)
			bbo.inputAccessoryView = vo	# attach accessory to textview
			#  remove undo/redo/paste BarButtons above standard keyboard
			#bbo.inputAssistantItem().setLeadingBarButtonGroups(None)
			#bbo.inputAssistantItem().setTrailingBarButtonGroups(None)

		return cell
		
	def redraw_textview_attributes(self,bb,opts):	
		mytrace(inspect.stack())
		# weblinks
		txt = bb.text
		t = txt.lower()
		# set attributes for general text
		font = UIFont.fontWithName_size_traits_(self.font, self.font_size,0)
		attrText = NSMutableAttributedString.alloc().initWithString_(txt)
		attributes = {NSForegroundColorAttributeName:self.text_color, NSFontAttributeName:font}								
		attrText.setAttributes_range_(attributes, NSRange(0,len(txt)))

		# test attributes: bold, italic, underline, strikethrough
		attribs = opts.get('attribs', None)
		#print(bb.text,attribs)
		if attribs:
			# opts['attribs'] = [(s,e,'biusohcqg'),(s,e,'B'),...]
			for attrib in attribs:
				sa,ea,biusohcqg = attrib
				attributes = self.get_attributes(biusohcqg)
				attrText.setAttributes_range_(attributes, NSRange(sa,ea-sa))

		# eventual weblinks 					
		li = 0
		while li < len(t):	
			lk = t.find('http://',li)
			if lk < 0:
				lk = t.find('https://',li)
			if lk < 0:
				break
			lj = t.find(' ',lk)
			if lj < 0:
				lj = len(t)
			link = txt[lk:lj]
			self.link_attributes = {NSForegroundColorAttributeName:self.link_color, NSFontAttributeName:font, NSLinkAttributeName:link, NSUnderlineStyleAttributeName:1}
			attrText.setAttributes_range_(self.link_attributes, NSRange(lk,lj-lk))	
			li = lj
		self.set_attributed_text(ObjCInstance(bb), attrText)	
		
	def get_attributes(self, biusohcqg, font_size=None):
		mytrace(inspect.stack())
		if not font_size:
			font_size = self.font_size
		traits = 0
		if 'b' in biusohcqg:
			traits = traits | 1 << 1
		if 'i' in biusohcqg:
			traits = traits | 1 << 0
		font = UIFont.fontWithName_size_traits_(self.font, font_size,traits)
		attributes = {NSFontAttributeName:font}								
		if 'u' in biusohcqg:
			attributes[NSUnderlineStyleAttributeName] = 1
		if 's' in biusohcqg:
			attributes[NSStrikethroughStyleAttributeName] = 1
			#attributes[NSStrikethroughColorAttributeName] = ObjCClass('UIColor').redColor()
		if 'c' in biusohcqg:
			# c(r,g,b)
			k = biusohcqg.find('c')
			i = biusohcqg.find('(',k)
			j = biusohcqg.find(')',i)
			rgb = biusohcqg[i+1:j]
			r,g,b = rgb.split(',')
			r,g,b = float(r),float(g),float(b)
			attributes[NSForegroundColorAttributeName] = UIColor.colorWithRed_green_blue_alpha_(r, g, b, 1)
		else:
			attributes[NSForegroundColorAttributeName] = self.text_color
		if 'o' in biusohcqg:
			# outline
			# if strokewidth > 0: foreground color = stroke
			# if strokewidth < 0: foreground color = fill    
			#											strokecolor = 2nd color
			if 'o(' in biusohcqg:
				# support 2nd color for filling outline o(r,g,b)
				# o(r,g,b)
				k = biusohcqg.find('c')
				i = biusohcqg.find('(',k)
				j = biusohcqg.find(')',i)
				rgb = biusohcqg[i+1:j]
				r,g,b = rgb.split(',')
				r,g,b = float(r),float(g),float(b)
				attributes[NSStrokeWidthAttributeName] = -3.0 
				attributes[NSStrokeColorAttributeName] = attributes[NSForegroundColorAttributeName]
				attributes[NSForegroundColorAttributeName] = UIColor.colorWithRed_green_blue_alpha_(r,g,b, 1)
			else:
				# support only one color for outline stroke
				attributes[NSStrokeWidthAttributeName] = +3.0 
		if 'h' in biusohcqg:
			shadow = NSShadow.alloc().init()
			shadow.setShadowOffset_((2,2))
			shadow.setShadowColor_(attributes[NSForegroundColorAttributeName])
			shadow.setShadowBlurRadius_(3.0)
			attributes[NSShadowAttributeName] = shadow
		if 'q' in biusohcqg:
			attributes[NSObliquenessAttributeName] = -0.25
		if 'g' in biusohcqg:
			# g(r,g,b)
			k = biusohcqg.find('g')
			i = biusohcqg.find('(',k)
			j = biusohcqg.find(')',i)
			rgb = biusohcqg[i+1:j]
			r,g,b = rgb.split(',')
			r,g,b = float(r),float(g),float(b)
			attributes[NSBackgroundColorAttributeName] = UIColor.colorWithRed_green_blue_alpha_(r,g,b, 1)
		
		# not yet supported
		if 'x' in biusohcqg:
			# exponent
			font = UIFont.fontWithName_size_traits_(self.font, font_size/2,traits)
			attributes[NSFontAttributeName] = font							
			attributes[NSBaselineOffsetAttributeName] = font_size/4
		if 'y' in biusohcqg:
			# indice
			font = UIFont.fontWithName_size_traits_(self.font, font_size/2,traits)
			attributes[NSFontAttributeName] = font								
	
		return attributes
		
	def keyboard_frame_did_change(self, frame):
		mytrace(inspect.stack())
		# Called when the on-screen keyboard appears/disappears
		# Note: The frame is in screen coordinates.
		#print('keyboard_frame_did_change', frame)
		try:
			self.keyboard_y = max(frame[1],self.keyboard_y)
			self.tv.content_inset = (0,0,frame[3],0) # bottom
		except:
			pass
		
	def textview_did_begin_editing(self, textview):
		mytrace(inspect.stack())
		#print('textview_did_begin_editing', textview.row)
		self.edited_textview = textview
		# see corrected bug of new outline in V00.65
		if textview.row == 0 and self.tv.content_offset[1] == 1:
			return
		#print('before',self.tv.content_offset[1])
		h = textview.height
		# yp = y bottom of row in screen coordinates		
		NSIndexPath = ObjCClass("NSIndexPath")
		nsindex = NSIndexPath.indexPathForRow_inSection_(textview.row,0)
		rect = self.tvo.rectForRowAtIndexPath_(nsindex)
		yp = rect.origin.y + rect.size.height - self.tv.content_offset[1] + self.tv.y + 1
		# don't ask me why but without this line, on iPhone in portrait mode only, 
		#   editing the last line of a file bigger than a screen implies that
		#   the keyboard appears and hides this last line
		yp += 1
		#print(yp,self.keyboard_y,'content_offset y=',self.tv.content_offset[1])
		if yp > self.keyboard_y:
			#print('row hidden:', textview.row, yp, self.keyboard_y)
			# scroll so bottom of edited line is just above keyboard
			y = self.tv.content_offset[1] + (yp - self.keyboard_y) + 1
			self.tv.content_offset = (0,y)
			
	#def scrollview_did_scroll(self, scrollview):
	#	mytrace(inspect.stack())
	#	print('scrollview_did_scroll', scrollview.content_offset[1])
		
	def textview_did_end_editing(self, textview):
		mytrace(inspect.stack())
		self.edited_textview = None
		# if did_end_editing active,
		#    - dismissing keyboard or editing other row, shows new weblink
		#    - crash at lf at end of a row
		#print('textview_did_end_editing', textview.row)
	#	self.tableview_reload_one_row(textview.row)
	#	pass
				
	def textview_should_change(self, textview, range_c, replacement, play=False, key=False):
		mytrace(inspect.stack())
		#print('textview_should_change', range_c,'|'+replacement+'|')
		# problem occurs when replacement is a predictive (non typed) text
		# textview_should_change is called by itself, what forces either crash,
		# either unwanted additional characters

		if len(stack()) > 1:
			if stack()[1][3] == 'textview_should_change':
				return False
		# may be called by
		#   swipe left/right on text
		#   tab/backtab in double tap  popup menu
		#   swipe in long n outline
		#   tab/backtab keys
		#   simulated tab in new file
		#   simulated drop by playlog
		if textview == None:
			# for actions outside the textview of the row: popup menu, swipes, ...
			# range_c = (row,row)
			row = range_c[0]
		elif isinstance(textview, int):
			# from play log
			row = textview
			if replacement in [lf, '\x01', '\x02']:
				rep = {lf:'lf', '\x01':'tab', '\x02':'backtab'}[replacement]
			else:
				rep = replacement
			try:
				l = str(len(self.tv.data_source.items[row]['title']))
			except:
				l = 'len of row, row outside limits'
			#print(rep, row, range_c, l)
		else:
			# real textview of the row for text or special keys
			row = textview.row
		#print('before:',textview.text)
			
		# eventual log
		if self.log == 'yes' and not play:
			rec = f"{row},{range_c[0]},{range_c[0]},"
			rep = replacement.replace(lf,'lf').replace('\x02','backtab').replace('\x01','tab')
			rec += rep
			rec += lf
			try:
				self.log_fil.write(rec)
			except:
				console.hud_alert('You did activate the log on an open file','error',3)
				self.log = 'no'
		processed = False
		vals_before = None
		if replacement == '\x01':
			# next level outline
			# ==================
			vals,n,opts = self.tv.data_source.items[row]['content']
			if vals == [0]:
				console.hud_alert('increase first level not allowed','error', 3)
				return False	# not allowed		
			vals_before = vals.copy()				
			# previous line exists because vals not = [0]
			pvals = self.tv.data_source.items[row-1]['content'][0]

			# check if not increase level of more than 1: begin ====
			if len(pvals) > len(vals):
				a = pvals[len(vals)] + 1
			else:
				a = 0
			nvals = pvals[:len(vals)] + [a] # add one level
			if len(nvals) > (len(pvals)+1):
				console.hud_alert('increase level two consecutive times not allowed','error', 3)
				return False	# not allowed	
			if nvals == vals:
				console.hud_alert('no change','error',3)
				return False	# not allowed	
			# check if not increase level of more than 1: end ========
			outline = self.OutlineFromLevelValue(nvals)
			if not outline:
				# too high level
				console.hud_alert('too high outline level','error',3)
				return False	# not allowed		
			# remove old outline

			self.undo_save('tab')	

			n = len(outline)
			self.tv.data_source.items[row]['content']	= (nvals,n,opts)
			self.tv.data_source.items[row]['outline']	= outline

			if len(nvals) > 1:			
				# automatic outlines renumbering of next lines 		
				self.renumbering('tab', row, vals_before, nvals)		
				self.renumbering('all',None,None, None)		

			self.tv.reload_data()
			if key:
				# tab key pressed, set cursor at end
				self.setCursor(row,len(self.tv.data_source.items[row]['title']))
			else:
				# swipe, popup menu
				self.setCursor(row,0)	
			self.modif = True
			self.check_auto_save('line')
			return False	# no replacement to process				
			
		#elif replacement == lf and range_c[0] == len(textview.text):
		elif replacement == lf and range_c[0] == len(self.tv.data_source.items[row]['title']):
			# line feed at end of line
			# ========================
			self.undo_save('CR')		
			# we will add a new row after all children of row, with sale level, value + 1
			self.add_row_after(row)
			self.check_auto_save('line')
			return False	# no replacement to process				
		elif replacement == '\x02':
			# back level outline
			# ==================
			vals,n,opts = self.tv.data_source.items[row]['content']
			if len(vals) == 1:
				console.hud_alert('no outline level to decrease','error', 3)
				return False	# not allowed		
			vals_before = vals.copy()
			# replace old outline by a new one with one level less					
			# remove old outline
			self.undo_save('back')			
			nvals = vals[:-1]
			if len(nvals) > 0:
				nvals = nvals[:-1] + [nvals[-1]+1]
			outline = self.OutlineFromLevelValue(nvals)
			n = len(outline)
			self.tv.data_source.items[row]['content']	= (nvals,n,opts)
			self.tv.data_source.items[row]['outline']	= outline			
			if len(nvals) >= 1:			
				# automatic outlines renumbering of next lines 		
				self.renumbering('backtab', row, vals_before, nvals)		
				self.renumbering('all',None,None, None)		
				
			self.tv.reload_data()
			if key:
				# tab key pressed, set cursor at end
				self.setCursor(row,len(self.tv.data_source.items[row]['title']))
			else:
				# swipe, popup menu
				self.setCursor(row,0)	

			self.modif = True
			self.check_auto_save('line')
			return False	# no replacement to process				
			
		elif replacement == '\x03':	
			# delete row and its children
			# ===========================	
			self.undo_save('del')		
			self.delete_row_and_children(row)			
			self.modif = True
			self.check_auto_save('line')
			return False	# no replacement to process				
			
		else:
			# normal character, tab, del, cut to remove, lf in text
			# =====================================================
			self.button_undo_enable(False,'')
			t = self.tv.data_source.items[row]['title']
			if lf in t[range_c[0]:range_c[1]]:
				# delete lf, textview will be less high but if return is True,
				# let some time before reload this row
				ui.delay(partial(self.tableview_reload_one_row, row), 0.1)
			l_bef = len(t)
			t = t[:range_c[0]] + replacement + t[range_c[1]:]
			l_aft = len(t)
			self.tv.data_source.items[row]['title'] = t
			
			vals,n,opts = self.tv.data_source.items[row]['content']			
			dt = datetime.now()
			today_date = f'{dt:%Y-%m-%d %H:%M:%S}'
			if 'dates' in opts:
				creation_date,update_date,due_date,complete_date = opts['dates']
				opts['dates'] = (creation_date,today_date,due_date,complete_date)
			else:
				opts['dates'] = (today_date,today_date,None,None)
				
			# in case of insert or delete characters, rebuild new attribs
			attribs = None
			attribs_old = opts.get('attribs',None)
			if attribs_old:
				# transform all attribs of line into array of '' or biusohcqg
				arr = [''] * len(t)
				for attrib in attribs_old:
					s,e,biusohcqg = attrib
					arr = arr[:s] + [biusohcqg]*(e-s) + arr[e:]
				# insert/delete with arr like with text
				arr = arr[:range_c[0]] + ['']*len(replacement) + arr[range_c[1]:] 
				# rebuild attribs
				attribs = []
				prev_biusohcqg = ''
				i = 0
				for biusohcqg in arr:
					if biusohcqg:
						if prev_biusohcqg:
							if biusohcqg != prev_biusohcqg:
								# terminates previous attrib
								e = i
								attrib = (s,e,prev_biusohcqg)
								attribs.append(attrib)
								# start of new attrib
								s = i
							else:
								# continue previous attrib
								pass
						else:
							# first of new attrib
							s = i
					else:
						if prev_biusohcqg:
							# terminates previous attrib
							e = i
							attrib = (s,e,prev_biusohcqg)
							attribs.append(attrib)
						else:
							# nothing
							pass									
					prev_biusohcqg = biusohcqg
					i += 1
				# eventual terminates previous attrib
				if prev_biusohcqg:
					# terminates previous attrib
					e = i
					attrib = (s,e,prev_biusohcqg)
					attribs.append(attrib)				
				opts['attribs'] = attribs
								
			self.tv.data_source.items[row]['content'] = (vals,n,opts)
			if self.show_mode == 'View dates' and self.selected_date == 1:
				# update dates view active
				ui.delay(partial(self.tableview_reload_one_row, row), 0.1)
	
			self.undo_save("...")		
						
			# if we reach the right side of the cell, a soft lf will be generated
			# and the TextView would need to be resized
			ft = (self.font, self.font_size)
			# before
			l = ui.TextView()
			l.font = ft
			l.number_of_lines = 0
			w = self.cells[row].content_view['text'].width
			l.frame = (0,0,w, ft[1])
			l.text = textview.text
			l.size_to_fit()
			ho_before = l.height
			#print(ho_before,l.text)
			del l
			# after
			l = ui.TextView()
			l.font = ft
			l.number_of_lines = 0
			l.frame = (0,0,w, ft[1])
			l.text = t
			l.size_to_fit()
			ho_after = l.height
			#print(ho_after,l.text)
			del l
									
			self.modif = True
			self.cursor = (row,range_c[0]) # not needed else if reload done
			#if lf in replacement:
			if ho_after != ho_before:
				# lf not at end, textview will be higher but if return is True,
				# let some time before reload this row
				ui.delay(partial(self.tableview_reload_one_row, row), 0.1)
			elif attribs:
				ui.delay(partial(self.redraw_textview_attributes, self.cells[row].content_view['text'], opts), 0.1)
				#ui.delay(partial(self.tableview_reload_one_row, row), 0.1)
			self.check_auto_save('char')
			return True # no replacement to process				
			
	#def textview_did_change(self, textview):
	#	mytrace(inspect.stack())
	# print('textview_did_change')
	#	pass

	@on_main_thread
	def tableview_reload_one_row(self, row):
		mytrace(inspect.stack())
		self.cursor = (row,0) # not needed else if reload done
		#print('tableview_reload_one_row',row)
		try:
			NSIndexPath = ObjCClass("NSIndexPath")
			nsindex = NSIndexPath.indexPathForRow_inSection_(row,0)
			UITableViewRowAnimationNone = 5
			#self.tvo.beginUpdates()
			self.tvo.reloadRowsAtIndexPaths_withRowAnimation_([nsindex], UITableViewRowAnimationNone)
			#self.tvo.endUpdates()
		except Exception as e:
			print(f"tableview_reload_one_row: {row}, error={e}")		

		cell = self.cells[row]
		tv = cell.content_view['text']
		tvo = ObjCInstance(tv)
		# for automatic lf in long lines, keyboard sometimes disappeared
		# and cursor was not visible. 
		# added next line seems to correct that
		tvo.becomeFirstResponder()
		i = len(self.tv.data_source.items[row]['title'])
		p1 = tvo.positionFromPosition_offset_(tvo.beginningOfDocument(), i)
		p2 = p1
		tvo.selectedTextRange = tvo.textRangeFromPosition_toPosition_(p1, p2)
			
	def renumbering(self, typ, fr, vals_before, vals_after):		
		mytrace(inspect.stack())
		if typ == 'all':
			# automatic renumbering of all (no parameters needed)
			row = 0
			pre_vals = []
			while row < len(self.tv.data_source.items):
				vals,n,opts = self.tv.data_source.items[row]['content']
				if len(vals) > len(pre_vals):
					nvals = pre_vals + vals[len(pre_vals):len(vals)-1] + [0]
				elif len(vals) == len(pre_vals):
					nvals = pre_vals[:-1] + [pre_vals[-1]+1]
				else:
					nvals = pre_vals[:len(vals)-1] + [pre_vals[len(vals)-1]+1]
				outline = self.OutlineFromLevelValue(nvals)
				n = len(outline)
				self.tv.data_source.items[row]['outline'] = outline
				self.tv.data_source.items[row]['content'] = (nvals,n,opts)
				row += 1
				pre_vals = nvals
			return
		# automatic outlines renumbering of next lines 
		row = fr + 1
		while row < len(self.tv.data_source.items):
			vals,n,opts = self.tv.data_source.items[row]['content']
			nvals = None
			if typ == 'lf':
				# not called with this parameter, old code
				if len(vals) >= len(vals_after):			
					fr_level = len(vals_after) - 1
					nvals = vals[:fr_level] + [vals[fr_level]+1] + vals[fr_level+1:]
			elif typ == 'tab':
				# tapped outline level already increased
				if vals[:len(vals_before)] == vals_before:
					# child of tabbed outline
					nvals = vals_after + vals[len(vals_before):]
				elif len(vals) >= len(vals_before):					
					fr_level = len(vals_before) - 1
					nvals = vals[:fr_level] + [vals[fr_level]-1] + vals[fr_level+1:]
			elif typ == 'backtab':
				# tapped outline level already decreased
				if vals[:len(vals_before)] == vals_before:
					# child of tabbed outline
					nvals = vals_after + vals[len(vals_before):]
				elif len(vals) >= len(vals_after):					
					fr_level = len(vals_after) - 1
					nvals = vals[:fr_level] + [vals[fr_level]+1] + vals[fr_level+1:]
			elif typ == 'del':
				# not called with this parameter, old code, not tested
				if len(vals) >= len(vals_before):			
					fr_level = len(vals_before) - 1
					nvals = vals[:fr_level] + [vals[fr_level]-1] + vals[fr_level+1:]
			
			if nvals:
				outline = self.OutlineFromLevelValue(nvals)
				n = len(outline)
				self.tv.data_source.items[row]['outline'] = outline
				self.tv.data_source.items[row]['content'] = (nvals,n,opts)
			row += 1
												
	def long_press_handler(self,data):
		mytrace(inspect.stack())
		global line1,xp1,found
		xp,yp = data.location
		v = data.view
		xp,yp = ui.convert_point(point=(xp,yp), from_view=v, to_view=self.tv)
		#print('long_press_handler',xp,yp,'state=',data.state)
		# get outline
		if data.state == 1:
			# start long_press
			row = v.row
			xp = v.width/2
			yp = v.height/2
			xp,yp = ui.convert_point(point=(xp,yp), from_view=v, to_view=self.tv)
			self.tvm = None
			self.target = None
			line1 = row
			xp1 = xp
			self.drag_children(row,xp,yp)
		elif data.state >= 2:
			# move
			if self.tvm:
				self.tvm.x = xp+100
				self.tvm.y = yp
				#--------- show a red line where moving text would be inserted: begin ----
				if yp >= 0:
					indexpath = self.tvo.indexPathForRowAtPoint_(CGPoint(xp,yp))
					#print(indexpath)
					if not indexpath:
						found = len(self.tv.data_source.items) - 1
					else:
						found = indexpath.row()
					#print('found=',found)
					#print('state 2: found=',self.found_redline)					
					cell = self.cells[found]
					v = cell.content_view['text']
					y = v.height
					x,y = ui.convert_point(point=(0,y), from_view=v, to_view=self.tv)
					try:
						self.target.y = y		
					except:
						self.target = ui.Label()
						self.target.frame = (0,y,self.tv.width-4,1)
						self.target.background_color = 'red'
						self.tv.add_subview(self.target)
					# under outline or under text?
					w = v.x
					if (xp-100) > w:
						self.target.x = w
					else:
						self.target.x = 0
				else:
					# before first row
					found = -1
					y = 0
					self.target.x = 0					
					self.target.y = y		
				self.found_redline = found

				# tried but locks					
				#self.auto_scroll(found, even=True)
				#--------- show a red line where moving text would be inserted: end ------
		if data.state == 3:
			# end
			#print('state 3: found=',self.found_redline)					
			if self.tvm:
				tgx = 0
				self.tv.remove_subview(self.tvm)
				del self.tvm
				if self.target:
					tgx = self.target.x
					self.tv.remove_subview(self.target)
					del self.target

				if self.orig_area:
					# blank original area in TextView
					fr,k1 = self.orig_area
					# search visible rows
					visible_rows ={}
					for indexpath in self.tvo.indexPathsForVisibleRows():
						visible_rows[indexpath.row()] = indexpath
		
					for row in range(fr,k1+1):			
						# if we reload, the long press is cancelled (state 4)
						# thus we need to change the background by another way			
						if row in visible_rows:
							# row is visible	
							cell = self.cells[row]
							for sv in cell.content_view.subviews:
								sv.background_color = 'white'
					self.orig_area = None

				found = self.found_redline
				fm,tm = self.drag_range
				if found >= 0:
					if found == line1:
						cell = self.cells[found]
						tv = cell.content_view['text']
						if xp > xp1:
							# move left to right => simulate tab
							self.textview_should_change(None,[found,found],'\x01')					
						else:
							# move right to left => simulate back tab
							self.textview_should_change(None,[found,found],'\x02')				
						return
					if fm <= found <= tm:
						console.hud_alert('Drop into the moving lines not allowed', 'error', 3)	
						return
					# drop
				self.drop(self.found_redline,fm,tm,tgx)
							
	def drag_children(self,fr,xp,yp):
		mytrace(inspect.stack())
		# prepare text to drag
		bvals = self.tv.data_source.items[fr]['content'][0]
		k1 = fr
		row = fr + 1
		while row < len(self.tv.data_source.items):
			vals = self.tv.data_source.items[row]['content'][0]
			if (len(vals)-1) > (len(bvals)-1):						
				# level higher that from level, set as selected
				k1 = row
			else:
				# level too high, end of select
				break
			row += 1
		#print(fr,k1)
		
		self.drag_range = (fr,k1)
		try:
			self.remove_subview(self['tvm'])
		except:
			pass
		tvm = ui.View(name='tvm')
		# text in moving box: begin
		y = 0
		wmax = 0
		for row in range(fr,k1+1):
			# 1) outline
			x = 0
			ft = (self.font, self.font_size)	
			bg_color = (0.9,0.9,0.9,0.5)
			o = ui.Label()
			txt = self.tv.data_source.items[row]['outline']
			o.text = txt
			o.text_color = self.outline_rgb
			o.background_color = bg_color
			o.font = ft
			wo,ho = ui.measure_string(txt, font=ft)
			o.frame = (x,y,wo,ho)
			tvm.add_subview(o)
			x += wo
			# 2) text it-self
			t = ui.TextView()
			txt = self.tv.data_source.items[row]['title']
			t.text = txt
			self.set_content_inset(t)
			t.text_color = 'black'
			t.background_color = bg_color
			t.font = ft
			wo,ho = ui.measure_string(txt, font=ft)
			wo += 20
			t.frame = (x,y,wo,ho)
			y += ho
			tvm.add_subview(t)
			wmax = max(wmax, x+wo)
		# text in moving box: end
		h = y
		xdrag = xp + 100 # only to not hide the moving box by the finger
		ydrag = yp 
		tvm.frame = (xdrag,ydrag,wmax,h)
		tvm.border_width = 1
		r = 10
		tvm.corner_radius = r/2
		tvm.background_color = (0.9,0.9,0.9,0.5)
		self.tvm = tvm
		self.tv.add_subview(tvm)

		if self.show_original_area == 'yes':		
			# show original area in TextView
			self.orig_area = (fr,k1)
			# search visible rows
			visible_rows ={}
			for indexpath in self.tvo.indexPathsForVisibleRows():
				visible_rows[indexpath.row()] = indexpath

			for row in range(fr,k1+1):			
				# if we reload, the long press is cancelled (state 4)
				# thus we need to change the background by another way			
				if row in visible_rows:
					# row is visible	
					cell = self.cells[row]
					for sv in cell.content_view.subviews:
						sv.background_color = 'pink'
		
	def drop(self,found, fm, tm, tgx, play=False):
		mytrace(inspect.stack())
		#print('drop:', found, fm,tm, len(self.tv.data_source.items))
		self.undo_save('move')
		
		# eventual log
		if self.log == 'yes' and not play:
			rec = f"drop,{found},{fm},{tm},{tgx}"
			rec += lf
			self.log_fil.write(rec)
		
		under_outline = (tgx == 0)

		if found >= 0:
			pre_vals = self.tv.data_source.items[found]['content'][0]	# vals of prev row
		else:
			pre_vals = [-1]
		# process dropped lines
		first = True
		row = fm
		moved_items = []
		while row <= tm:
			vals,n,opts = self.tv.data_source.items[row]['content']
			if first:
				vals1 = vals.copy()
				if under_outline:
					# drop under outline
					# same level as previous
					nvals = pre_vals[:-1] + [pre_vals[-1]+1]
				else:
					# drop under text
					# next level vs previous
					nvals = pre_vals + [0]
				nvals1 = nvals.copy()
				first = False
			else:
				ndiff = len(vals) - len(vals1) 
				nvals = nvals1 + vals[-ndiff:]  
			outline = self.OutlineFromLevelValue(nvals)
			n = len(outline)
			item ={}
			item['title'] = self.tv.data_source.items[row]['title']
			item['outline'] = outline
			item['content'] = (nvals,n,opts)
			moved_items.append(item)
			row += 1
		self.tv.data_source.items = self.tv.data_source.items[:found+1] + moved_items + self.tv.data_source.items[found+1:]
		
		# remove original
		nbr_added_rows = tm - fm + 1
		if tm > found:
			# deleted part after insertion, thus increase indexes
			fm += nbr_added_rows
			tm += nbr_added_rows
		# if copy instead of move, comment this line: begin ========
		self.tv.data_source.items = self.tv.data_source.items[:fm] + self.tv.data_source.items[tm+1:]
		# if copy instead of move, comment this line: end  ==========
		
		# renumbering after old removed
		self.renumbering('all',None,None, None)		
		
		self.tv.reload_data()
		c = found + 1
		if tm < found:
			c -= nbr_added_rows
		self.setCursor(c,0)	
		self.modif = True
		self.check_auto_save('line')		
		return
		
	def paste(self, found):
		mytrace(inspect.stack())
		#print('paste:', found)
		self.undo_save('past')
				
		under_outline = True # .......

		if found >= 0:
			pre_vals = self.tv.data_source.items[found]['content'][0]	# vals of prev row
		else:
			pre_vals = [-1]
		# process pasted lines
		first = True				
		row = 0
		pasted_items = []
		while row <= (len(self.paste_items)-1):
			vals,n,opts = self.paste_items[row]['content']
			if first:
				vals1 = vals.copy()
				if under_outline:
					# drop under outline
					# same level as previous
					nvals = pre_vals[:-1] + [pre_vals[-1]+1]
				else:
					# drop under text
					# next level vs previous
					nvals = pre_vals + [0]
				nvals1 = nvals.copy()
				first = False
			else:
				ndiff = len(vals) - len(vals1) 
				nvals = nvals1[:-ndiff] + vals[-ndiff:]  
				#nvals = nvals1 # should be better, bug free
			outline = self.OutlineFromLevelValue(nvals)
			n = len(outline)
			item = {}
			item['title'] = self.paste_items[row]['title']
			item['outline'] = outline
			if 'dates' in opts:
				dc,du,dd,de = opts['dates']			
				if dd:
					# due date exists
					dd = None 	# reset due date
					opts['dates'] = (dc,du,dd,de)					
			item['content'] = (nvals,n,opts)
			pasted_items.append(item)
			row += 1
		self.tv.data_source.items = self.tv.data_source.items[:found+1] + pasted_items + self.tv.data_source.items[found+1:]
		self.renumbering('all',None,None, None)						
		self.tv.reload_data()
		self.modif = True
		self.check_auto_save('line')		
		return
			
	@on_main_thread
	def set_attributed_text(self,tvo,t):
		mytrace(inspect.stack())
		tvo.setAttributedText_(t)

	def setCursor(self,row,index):
		mytrace(inspect.stack())
		#print('setCursor')
		rowc = row
		indexc = index
		while rowc < len(self.tv.data_source.items):
			opts = self.tv.data_source.items[rowc]['content'][2]
			hidden = False
			if 'hidden' in opts:
				if opts['hidden']:
					hidden = True
			if not hidden:
				self.cursor = (rowc,indexc)
				self.auto_scroll(rowc)
				return
			rowc += 1
			indexc = 0
		rowc = min(row,len(self.tv.data_source.items)-1)
		while rowc >= 0:
			#print(rowc)
			opts = self.tv.data_source.items[rowc]['content'][2]
			hidden = False
			if 'hidden' in opts:
				if opts['hidden']:
					hidden = True
			if not hidden:
				self.cursor = (rowc,indexc)
				self.auto_scroll(rowc)
				return
			rowc += -1
			indexc = 0
			
	def auto_scroll(self,row, even=False, UITableViewScrollPosition=1):
		mytrace(inspect.stack())
		#print('auto_scroll', row, 'even=',even)
		# search which rows are visible
		if not even:
			for indexpath in self.tvo.indexPathsForVisibleRows():
				if indexpath.row() == row:
					# row is visible, no scroll needed
					return
		# automatic scroll to row
		#print('scroll')
		NSIndexPath = ObjCClass("NSIndexPath")
		nsindex = NSIndexPath.indexPathForRow_inSection_(row,0	)
		# UITableViewScrollPosition = 0 None
		#															1 Top
		#															2 Middle
		#															3 Bottom
		self.tvo.scrollToRowAtIndexPath_atScrollPosition_animated_(nsindex, UITableViewScrollPosition, True)
			
	def checkbox_button_action(self,sender):
		mytrace(inspect.stack())
		reshow_all = False
		row = sender.row
		vals,n,opts = self.tv.data_source.items[row]['content']
		if len(vals) == 1 and not self.first_level_has_outline:
			b = console.alert('What do you want to do?', '', 'tap checkbox', 'open popup menu', hide_cancel_button=True)
			if b == 2:
				data = Data() # class from gestures
				data.location = (0,0)
				data.view = self.cells[row].content_view['outline']
				self.single_or_double_tap_handler(data)
				return
		force_save = False
		if sender.checkmark:
			opts['checkmark'] = 'no'
			if 'dates' in opts:
				creation_date,update_date,due_date,complete_date = opts['dates']
				opts['dates'] = (creation_date,update_date,due_date,None)
			sender.image = None			
			sender.border_width = 1
			if self.show_mode == 'Show checked only':
				opts['hidden'] = True
				reshow_all = True
		else:
			opts['checkmark'] = 'yes'
			dt = datetime.now()
			today_date = f'{dt:%Y-%m-%d %H:%M:%S}'
			if 'dates' in opts:
				creation_date,update_date,due_date,complete_date = opts['dates']
				opts['dates'] = (creation_date,update_date,due_date,today_date)
			else:
				opts['dates'] = (today_date,today_date,None,today_date)
				
			# as the outline is complete, remove its due date event
			if 'eventid' in opts:
				id = opts['eventid']
				self.set_due_date(None, delete=id)
				del opts['eventid']
				# force save to be sure file is coherent with calendar
			force_save = True

			sender.image = self.checkmark_ui_image
			sender.border_width = 0
			if self.show_mode == 'Hide checked':
				opts['hidden'] = True
				reshow_all = True
		sender.checkmark = not sender.checkmark
		self.tv.data_source.items[row]['content'] = (vals,n,opts)
		self.modif = True
		if force_save:
			self.file_save()
		if reshow_all:
			self.tv.reload_data()
		
	def popup_menu_action(self,actin, row=None):
		mytrace(inspect.stack())
		#print('popup_menu_action',row,actin)
		act = actin.replace('\n',' ')
		vals,n,opts = self.tv.data_source.items[row]['content']
		if act == 'hide children':
			self.hide_children(row,len(vals)-1,hide=True)
		elif act == 'show children':
			self.hide_children(row,len(vals)-1,hide=False)
		elif act == '⏭':			
			self.textview_should_change(None,[row,row],'\x01')				
		elif act == '⏮':			
			self.textview_should_change(None,[row,row],'\x02')			
		elif act == '✅':	
			self.check_children(row,len(vals)-1,check='yes')	
		elif act == '⬜️':		
			self.check_children(row,len(vals)-1,check='no')			
		elif act == 'no box':	
			vals,n,opts = self.tv.data_source.items[row]['content']
			opts['checkmark'] = 'hidden'
			self.tv.data_source.items[row]['content'] = vals,n,opts
			self.modif = True	
			#self.tableview_reload_one_row(row)
			self.tv.reload_data()
		elif act == 'delete with children':
			self.textview_should_change(None,[row,row],'\x03')			
		elif act == '🖼':	
			self.image_row = row
			f = self.pick_file('from where to open the image', uti=['public.image'], callback=self.pick_image_callback)
			if not f:
				console.hud_alert('No image has been picked','error', 3)
				return
			if f == 'delayed':
				# Files app via UIDocumentPickerViewController needs delay
				return
			# immediate return for Files_Picker use for local Pythonista files
			simul = 'file://' + f
			self.pick_image_callback(simul)
		elif act == 'due date':	
			cv = self.cells[row].content_view
			x = cv.x + cv['text'].x
			y = cv.y + cv.height/2
			v = ui.View()
			v.frame = (0,0,330,300)
			v.background_color = 'white'
			v.name = 'due date of ' + self.tv.data_source.items[row]['outline']
			v.row = row
			dp = ui.DatePicker(name='datepicker')
			dp.background_color = 'white'
			dp.frame = (0,30,300,300)
			v.add_subview(dp)
			
			bunset = ui.Button(name='unset')
			bunset.frame = (v.width-60,4,56,22)
			bunset.border_width = 1
			bunset.border_color = 'blue'
			bunset.corner_radius = 5
			bunset.tint_color = 'blue'
			bunset.title = 'unset'
			def bunset_action(sender):
				mytrace(inspect.stack())
				self.shield.hidden = True
				self.remove_subview(sender.superview)
				self.set_due_date(sender.superview, unset=True)
			bunset.action = bunset_action
			v.add_subview(bunset)
			
			details = ui.Button(name='details')
			details.frame = (bunset.x-60,4,56,22)
			details.border_width = 1
			details.border_color = 'blue'
			details.corner_radius = 5
			details.tint_color = 'blue'
			details.title = 'details'
			def details_action(sender):
				mytrace(inspect.stack())
				self.shield.hidden = True
				self.remove_subview(sender.superview)
				self.set_due_date(sender.superview, details=True)
			details.action = details_action
			v.add_subview(details)
				
			l = ui.Label()
			l.frame = (4,4,bunset.x-8,22)
			l.text = v.name
			l.text_color = 'blue'
			v.add_subview(l)
			if 'dates' not in opts:
				dt = datetime.now()
				dc = f'{dt:%Y-%m-%d %H:%M:%S}'
				opts['dates'] = (dc,dc,None,None)				
				self.tv.data_source.items[row]['content'] = (vals,n,opts)
			dc,du,dd,de = opts['dates']
			if dd:
				dt = datetime.strptime(dd,'%Y-%m-%d %H:%M:%S') # datetime		
				dp.date = dt				
			x,y = ui.convert_point(point=(x,y), from_view=cv, to_view=None)
			self.present_popover(v, 'popover',popover_location=(x,y),hide_title_bar=True, force=True)
			return
		elif act == 'bold ...':	
			self.selected_text_attributes(row)					
		elif 'paste' in act:	
			self.paste(row)
		elif act == 'add before':
			self.undo_save('CR')		
			self.add_row_before(row)
			self.check_auto_save('line')
								
	def set_due_date(self, view, unset=False, delete=None, details=False, feedback=True):
		mytrace(inspect.stack())
		# this function is called 
		# - for deleting an event (its opts['dates'] due date is reset in calling code)
		# - by tapping outside the datepicker to close the view
		# - by tapping the unset button of the datepicker view
		# - by tapping the details button of the datepicker view
		if delete:
			# outline has been marked as complete, thus its due date event is removed
			id = delete
			event = self.store.eventWithIdentifier_(ns(id))
			if event:
				# remove from calendar, all future occurences
				ret = self.store.removeEvent_span_error_(event,1,None) 
				if not feedback:
					return
				if ret:
					console.hud_alert('due date event has been removed','success',3)
				else:
					console.hud_alert('ERROR: due date event has not been removed','error',3)
			return
			
		# actions in datepicker view
		row = view.row
		vals,n,opts = self.tv.data_source.items[row]['content']
		dc,du,dd_old,de = opts['dates']
				
		if unset:
			if 'eventid' in opts:
				id = opts['eventid']
				event = self.store.eventWithIdentifier_(ns(id))
				if event:
				# remove from calendar, all future occurences
					ret = self.store.removeEvent_span_error_(event,1,None)
					if ret:
						console.hud_alert('due date event has been removed','success',3)
					else:
						console.hud_alert('ERROR: due date event has not been removed','error',3)
				del opts['eventid']
			dd = None
			opts['dates'] = (dc,du,dd,de)					
		else:
			# tap outside datepicker or details button
			# get date set by datepicker, even if details button
			datepicker = view['datepicker']
			dt = datepicker.date
			dd = f'{dt:%Y-%m-%d %H:%M:%S}'	
			title = self.tv.data_source.items[row]['title']			
			opts['dates'] = (dc,du,dd,de)
								
			if details:
				self.eventEditViewControllerAction = None
				v = ui.View()
				vc = ObjCInstance(v)
	
				EventEditViewController = EKEventEditViewController.new().autorelease()
				#print(dir(EventEditViewController))
				EventEditViewController.editViewDelegate = MyEventEditViewDelegate.alloc().init()
				EventEditViewController.eventStore = self.store
				event = None
				if 'eventid' in opts:
					id = opts['eventid']
					event = self.store.eventWithIdentifier_(ns(id))
					#print('event with evenid of opts',event)
				if not event:
					event = ObjCClass('EKEvent').eventWithEventStore_(self.store)
					a = ObjCClass('EKAlarm').alarmWithRelativeOffset_(0)
					event.addAlarm_(a)
				# init event known fields
				event.title = f"{self.file} : {title[:20]}"
				dateFormat = ObjCClass('NSDateFormatter').alloc().init()
				dateFormat.setDateFormat_('yyyyMMdd HH:mm')
				dattim_str = dt.strftime('%Y%m%d %H:%M')
				event.startDate = dateFormat.dateFromString_(dattim_str)
				event.endDate = dateFormat.dateFromString_(dattim_str)	
				event.setCalendar_(self.cal)		
				event.notes = f"pythonista3://outline.py?action=run&args={self.file}\n\n{title}"
				EventEditViewController.event = event
				clview = EventEditViewController.view()
				self.eventEditViewControllerUIView = v	# for delegate
				w,h = ui.get_screen_size()
				v.frame = (0,0,w,h)
				vc.addSubview_(clview)
				v.present('fullscreen', hide_title_bar=True)
				v.wait_modal()	
				# action = 0=canceled 1=saved 2=deleted		
				#print('action=',self.eventEditViewControllerAction)
				if self.eventEditViewControllerAction == 0:
					# canceled
					console.hud_alert('due date event has been canceled','success',3)
					return # no action
				elif self.eventEditViewControllerAction == 1:
					# saved (added or updated)
					strdt = event.startDate()
					dateFormat = ObjCClass('NSDateFormatter').alloc().init()
					dateFormat.setDateFormat_('yyyy-MM-dd HH:mm')
					dd = str(dateFormat.stringFromDate_(strdt)) + ':00'
					opts['dates'] = (dc,du,dd,de)					
					id = str(event.eventIdentifier())
					opts['eventid'] = id
					dd = None # to skip next process
					console.hud_alert('due date event has been added/updated','success',3)
				elif self.eventEditViewControllerAction == 2:
					# deleted
					# same as if unset tapped
					console.hud_alert('due date event has been removed','success',3)
					del opts['eventid']
					dd = None
					opts['dates'] = (dc,du,dd,de)					

		if dd:
			# not unset, not delete event in EKEventEditViewController
			if self.cal:
				add = True
				if dd_old:
					if 'eventid' in opts:
						id = opts['eventid']
						event = self.store.eventWithIdentifier_(ns(id))
						if event:
							add = False
				if add:
					event = ObjCClass('EKEvent').eventWithEventStore_(self.store)
				dateFormat = ObjCClass('NSDateFormatter').alloc().init()
				dateFormat.setDateFormat_('yyyyMMdd HH:mm')
				a = ObjCClass('EKAlarm').alarmWithRelativeOffset_(0)
				event.addAlarm_(a)
				event.title = f"{self.file} : {title[:20]}"
				event.notes = f"pythonista3://outline.py?action=run&args={self.file}\n\n{title}"
				dattim_str = dt.strftime('%Y%m%d %H:%M')
				event.startDate = dateFormat.dateFromString_(dattim_str)
				event.endDate = dateFormat.dateFromString_(dattim_str)	
				event.setCalendar_(self.cal)
				span = 0 # no recurrence
				ret = self.store.saveEvent_span_error_(event, span, None)
				if feedback:
					if add:
						if ret:
							console.hud_alert('due date event has been added','success',3)
						else:
							console.hud_alert('ERROR: due date event has not been added',error,3)
					else:
						if ret:
							console.hud_alert('due date event has been updated','success',3)
						else:
							console.hud_alert('ERROR: due date event has not been updated',error,3)
				id = str(event.eventIdentifier())
				opts['eventid'] = id
			else:
				console.hud_alert('Outline calendar does not exist','error', 3)				
				
		self.tv.data_source.items[row]['content'] = (vals,n,opts)
		self.modif = True	
		# force save to be coherent with calendar
		self.file_save()			
		
		if self.show_mode == 'View dates' and self.selected_date == 2:
			# due dates view active
			self.tableview_reload_one_row(row)
			
	def pick_image_callback(self,param):
		mytrace(inspect.stack())
		#print('pick_image_callback:',param)
		if param == 'canceled':
			console.hud_alert('no image has been picked','error', 3)
			return
		f = str(param)[7:]  # remove file://
		row = self.image_row
		self.undo_save('img')	
		vals,n,opts = self.tv.data_source.items[row]['content']
		opts['image'] = (f,4,'left')
		self.tv.data_source.items[row]['content'] = vals,n,opts
		self.modif = True	
		self.check_auto_save('line')
		self.tv.reload_data()	
		self.image_size_action(row)			
		
	def image_size_action(self,sender):
		mytrace(inspect.stack())
		if isinstance(sender, int):
			row = sender
		else:
			row = sender.row
		vals,n,opts = self.tv.data_source.items[row]['content']
		pos = opts['image'][2] # ex: 'left'
		x = self.width/10
		y = self.height/10
		v = ui.View()
		v.background_color = 'lightgray'
		v.frame = (0,0, self.width*8/10, self.height*8/10)
		v.row = row
		b_del = ui.Button()
		b_del.background_color = 'red'
		b_del.title = 'delete'
		b_del.tint_color = 'white'
		b_del.frame = (5,5,50,30)
		b_del.corner_radius = 5
		b_del.action = self.delete_image
		v.add_subview(b_del)
		b_ok = ui.Button()
		b_ok.background_color = 'blue'
		b_ok.title = 'ok'
		b_ok.tint_color = 'white'
		b_ok.frame = (v.width-5-30,5,30,30)
		b_ok.corner_radius = 5
		b_ok.action = self.ok_image
		v.add_subview(b_ok)
		l_tit = ui.Label()
		xl = b_del.x+b_del.width+5
		l_tit.frame = (xl,5,b_ok.x-xl-5,30)
		l_tit.text = 'height and position for ' + self.tv.data_source.items[row]['outline']
		l_tit.alignment = ui.ALIGN_CENTER
		v.add_subview(l_tit)
		ls = ui.Label()
		ls.frame = (5,40,65,20)
		ls.text = 'height'
		v.add_subview(ls)
		ss = ui.SegmentedControl(name='size_segments')
		ss.action = self.size_segment_tap
		ss.segments = ['small', 'medium', 'large']
		ss.dims     = [ 2     ,  4      ,  6     ]
		ss.selected_index = -1
		xl = ls.x+ls.width+5
		ss.frame = (xl,ls.y,min(v.width-xl,250),20)
		vo = ObjCInstance(ss)
		for sv in vo.segmentedControl().subviews():
			sv.label().adjustsFontSizeToFitWidth = True # auto resize font to fit
		v.add_subview(ss)
		tf = ui.TextField(name='image_size')
		tf.frame = (ss.x,65,50,ss.height)
		SetTextFieldPad(tf, pad_integer, textfield_did_change=self.textfield_did_change)
		ns = opts['image'][1] 
		tf.text = str(ns)
		idx = -1
		for i in range(len(ss.dims)):
			if ss.dims[i] == ns:
				idx = i
				break
		ss.selected_index = idx				
		tf.text_color = 'green'
		v.add_subview(tf)
		ln = ui.Label()
		ln.frame = (tf.x+tf.width+5,tf.y,50,tf.height)
		ln.text = 'lines'
		ln.text_color = 'gray'
		v.add_subview(ln)
		lp = ui.Label()
		lp.frame = (ls.x,90,ls.width,ls.height)
		lp.text = 'position'
		v.add_subview(lp)
		sp = ui.SegmentedControl(name='position_segments')
		sp.segments = ['left','right','top','bottom']
		sp.selected_index = sp.segments.index(pos)
		sp.frame = (ss.x,lp.y,ss.width,ss.height)
		vo = ObjCInstance(sp)
		for sv in vo.segmentedControl().subviews():
			sv.label().adjustsFontSizeToFitWidth = True # auto resize font to fit
		v.add_subview(sp)
		im = ui.ImageView()
		y = sp.y+sp.height+5
		im.frame = (0,y,v.width,v.height-y)
		im.content_mode = ui.CONTENT_SCALE_ASPECT_FIT
		im.image = ui.Image.named(opts['image'][0]).with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		v.add_subview(im)
		self.present_popover(v, 'popover',popover_location=(x,y),hide_title_bar=True, force=True)
		
	def size_segment_tap(self,sender):
		mytrace(inspect.stack())
		idx = sender.selected_index
		n = sender.dims[idx]
		v = sender.superview
		v['image_size'].text = str(n)
	
	def ok_image(self,sender):
		mytrace(inspect.stack())
		v = sender.superview
		row = v.row	
		n = int('0'+v['image_size'].text)				
		pos = v['position_segments'].segments[v['position_segments'].selected_index]
		self.set_image_size(row, n, pos)
		self.remove_subview(v)
		for sv in v.subviews:
			del sv
		del v	
		self.shield.hidden = True	
			
	def delete_image(self, sender):
		mytrace(inspect.stack())
		v = sender.superview
		row = v.row	
		self.set_image_size(row,0,'delete')
		self.remove_subview(v)
		for sv in v.subviews:
			del sv
		del v
		self.shield.hidden = True
			
	def set_image_size(self,row, ns, pos):
		mytrace(inspect.stack())
		#print('set_image_size',row,ns,pos)
		vals,n,opts = self.tv.data_source.items[row]['content']
		if pos == 'delete':
			self.undo_save('dimg')	
			del opts['image']
		else:
			f,s,posn = opts['image']
			opts['image'] = (f,ns,pos)
		self.tv.data_source.items[row]['content'] = (vals,n,opts)
		self.modif = True
		self.check_auto_save('line')
		self.tv.reload_data()
			
	def add_row_after(self,rowin):
		mytrace(inspect.stack())
		# search row of last children of rowin
		self.undo_save('CR')
		valsin = self.tv.data_source.items[rowin]['content'][0]
		row = rowin + 1
		while row < len(self.tv.data_source.items):
			vals = self.tv.data_source.items[row]['content'][0]		
			if len(vals) <= len(valsin):
				break
			row += 1	
		row -= 1
		vals = self.tv.data_source.items[rowin]['content'][0]			
		nvals = vals[:-1] + [vals[-1]+1]
		outline = self.OutlineFromLevelValue(nvals)
		dt = datetime.now()
		creation_date = f'{dt:%Y-%m-%d %H:%M:%S}'
		opts = {}
		opts['dates'] = (creation_date,None,None,None)
		n = len(outline)
		item = {}
		item['title'] = ''
		item['outline'] = outline
		item['content'] = (nvals,n,opts)
		#self.tv.data_source.items.insert(row+1,item)
		self.tv.data_source.items = self.tv.data_source.items[:row+1] + [item] + self.tv.data_source.items[row+1:]
		#if len(nvals) >= 1:			
		#	# automatic outlines renumbering of next lines 		
		#	fr = range_c[0]+1
		#	self.renumbering('lf', row+1, None, nvals)		
		self.renumbering('all',None,None, None)		
		self.tv.reload_data()
		self.modif = True
		self.setCursor(row+1,0)
		
	def add_row_before(self,row):
		mytrace(inspect.stack())
		self.undo_save('CR')
		# generate same outline as row
		vals = self.tv.data_source.items[row]['content'][0]			
		outline = self.OutlineFromLevelValue(vals)
		dt = datetime.now()
		creation_date = f'{dt:%Y-%m-%d %H:%M:%S}'
		opts = {}
		opts['dates'] = (creation_date,None,None,None)
		n = len(outline)
		item = {}
		item['title'] = ''
		item['outline'] = outline
		item['content'] = (vals,n,opts)
		self.tv.data_source.items = self.tv.data_source.items[:row] + [item] + self.tv.data_source.items[row:]
		#	self.renumbering('lf', row+1, None, nvals)		
		self.renumbering('all',None,None, None)		
		self.tv.reload_data()
		self.modif = True
		self.setCursor(row,0)
			
	def delete_row_and_children(self,row):
		mytrace(inspect.stack())
		# delete row 
		self.undo_save('dele')
		vals,n,opts = self.tv.data_source.items[row]['content']
		if 'eventid' in opts:
			id = opts['eventid']
			self.set_due_date(None, delete=id, feedback=False)
		#self.tvo.beginUpdates()	# @jonB advice gives crsh
		del self.tv.data_source.items[row]
		# delete children
		# row1 does not change because continuous delete row until break
		row1 = row
		while row1 < len(self.tv.data_source.items):
			dvals,dn,dopts = self.tv.data_source.items[row1]['content']	
			if len(dvals) > len(vals):
				# child
				if 'eventid' in dopts:
					id = dopts['eventid']
					self.set_due_date(None, delete=id, feedback=False)
				del self.tv.data_source.items[row1]				
			else:
				break
			# no increment row1 because previous row deleted, so index stays the same
		if len(self.tv.data_source.items) == 0:
			# no more row, add first like a new file
			vals = [0]
			outline = self.OutlineFromLevelValue(vals)
			n = len(outline)
			opts = {}
			item = {'title':'','outline':outline, 'content':(vals,n,opts)}
			self.tv.data_source.items = [item]
			self.setCursor(0,0)
		else:
			self.setCursor(max(0,row-1),0)

		# renumbering 
		self.renumbering('all',None,None, None)
		self.modif = True
		self.check_auto_save('line')
		self.tv.reload_data()
		#self.tvo.endUpdates()	# @jonB advice fives crash
			
	def swipe_left_handler(self,data):
		mytrace(inspect.stack())
		v = data.view
		row = v.row
		self.textview_should_change(None,[row,row],'\x02')				
		
	def swipe_right_handler(self,data):
		mytrace(inspect.stack())
		v = data.view
		row = v.row
		self.textview_should_change(None,[row,row],'\x01')				
		
	def tableview_title_for_header(self, tv, section):
		mytrace(inspect.stack())
		return tv.name
				
	def single_or_double_tap_handler(self,data):
		mytrace(inspect.stack())
		#print('single_or_double_tap_handler_handler',data)
		xp,yp = data.location
		v = data.view
		row = v.row
		#ui.delay(self.cells[row].content_view['text'].end_editing,0.1)
		#v.border_width = 1
		# popover at right of outline
		#print(xp,yp,data.state)
		xp = v.width/2
		yp = v.height/2
		xp,yp = ui.convert_point(point=(xp,yp), from_view=v, to_view=None)
		vals,n,opts = self.tv.data_source.items[row]['content']
		t = self.tv.data_source.items[row]['outline']
		sub_menu = ['hide children', 'show children', 'delete with children', '⏭', '⏮', '🖼','bold ...', 'add before']
		sub_menu.append('due date')
		if self.checkboxes == 'yes':
			sub_menu = sub_menu +  ['⬜️', '✅', 'no box']
			
		# check if paste would be proposed
		ok = True
		try:
			with open('outline.clipboard', mode='rt', encoding='utf-8', errors="surrogateescape") as fil:
				clipboard_str = fil.read()			
			#clipboard_str = clipboard.get()
			#print(clipboard_str)
			self.paste_items = literal_eval(clipboard_str)
			del clipboard_str
			if not isinstance(self.paste_items[0], dict):
				ok = False
			else:
				item = self.paste_items[0]
				t = item['title']
		except:
			ok = False
		if ok:
			sub_menu.append('paste '+t+'...')

		if self.popup_menu_orientation == 'vertical':
			#=== vertical: popup menu
			tv = ui.TableView('grouped')
			ft = ('Menlo',16)
			wmax = 0
			for act in sub_menu:
				w = ui.measure_string(act,font=ft)[0]
				wmax = max(w,wmax)
			tv.name = 'for outline ' + self.tv.data_source.items[row]['outline']
			tblo = ObjCInstance(tv)
			hh = 30
			tblo.sectionHeaderHeight = hh
			tv.outline_row = row
			tv.row_height = hh
			h = tv.row_height*len(sub_menu)
			tv.frame = (0,0,wmax+40,h+hh)
			tv.data_source = ui.ListDataSource(items=sub_menu)
			tv.data_source.tableview_title_for_header = self.tableview_title_for_header
			tv.data_source.font = ft
			tv.allows_multiple_selection = False
			tv.delegate = self
			self.selected_row = None
			self.present_popover(tv, 'popover',popover_location=(xp,yp),hide_title_bar=True)
			#tv.present('popover',popover_location=(xp,yp),hide_title_bar=False)
			#tv.wait_modal()
			if self.device_model == 'iPad':
				if not self.selected_row:
					return
				act = sub_menu[self.selected_row[1]]
				self.popup_menu_action(act, row=row)
		else:
			#=== horizontal popup menu **** not available on iPhone ****
			popup = ui.ScrollView(name='popup')
			h = 40
			x = 0
			ft = ('Menlo',14)	
			t = self.tv.data_source.items[row]['outline'].strip()
			for act in [t] + sub_menu:
				b = ui.Button()
				b.title = act
				ib = b.title.find(' ')
				if ib >= 0:
					# split title in two lines
					b.title = b.title[:ib] + '\n' + b.title[ib+1:] # 1st blank only
					for sv in ObjCInstance(b).subviews(): 
						if hasattr(sv,'titleLabel'):
							tl = sv.titleLabel()
							tl.numberOfLines = 0
				w = ui.measure_string(b.title,font=ft)[0] + 10
				x += 8
				b.frame = (x,0,w,h)
				if self.red_delete == 'yes':
					if 'delete' in act:
						b.background_color = 'red'
				x += w
				b.font = ft
				if act == t:
					b.tint_color = 'yellow'
				else:
					b.tint_color = 'white'
					b.row = row
					b.action = self.set_popup_menu_tapped
				popup.add_subview(b)
				l = ui.Label()	
				x += 10		
				l.frame = (x,0,1,h)			
				l.background_color = (0.5,0.5,0.5,0.8)
				popup.add_subview(l)	
			popup.frame = (0,0,x-2,h) # don't show last vertical line
			popup.content_size = (popup.width,popup.height)
			# "bg" is the color you want to set the popover view to
			popup.background_color = 'black'

			self.popup_menu_tapped = None			
			self.present_popover(popup, 'popover',popover_location=(xp,yp),hide_title_bar=True)
			#print(self.popup_menu_tapped)
			if self.popup_menu_tapped:
				self.popup_menu_action(self.popup_menu_tapped, row=row)
			
	def set_popup_menu_tapped(self,sender):
		mytrace(inspect.stack())
		self.popup_menu_tapped = sender.title
		sender.superview.close()

	@ui.in_background
	def console_alert(self):
		mytrace(inspect.stack())
		console.alert(self.alert_title, self.alert_msg, 'ok', hide_cancel_button=True)
		
	def select_outline(self,sender):
		mytrace(inspect.stack())
		row = sender.row
		if row not in self.selected_rows_for_cut:
			self.selected_rows_for_cut.append(row)
			sender.background_color = 'red'
			# select automatically eventual children
		else:
			idx = self.selected_rows_for_cut.index(row)
			del self.selected_rows_for_cut[idx]
			sender.background_color = 'yellow'
		sel_level = len(self.tv.data_source.items[row]['content'][0]) - 1
		row = row + 1	# start after row of selected button
		while row < len(self.tv.data_source.items):
			vals,n,opts = self.tv.data_source.items[row]['content']
			if (len(vals)-1) > sel_level:						
				# level higher that from level, set as (un)hidden
				if row not in self.selected_rows_for_cut:
					self.selected_rows_for_cut.append(row)
				else:
					idx = self.selected_rows_for_cut.index(row)
					del self.selected_rows_for_cut[idx]
			else:
				# level too high, end of (un)selecting
				break
			row += 1
		self.tv.reload_data()

	def hide_children_via_button(self,sender):
		mytrace(inspect.stack())
		#print('hide_children_via_button',sender.data)
		row, fr_level, hide = sender.data
		hide = not hide
		self.hide_children(row, fr_level, hide=hide)
		
	def hide_children(self,fr, fr_level, hide=True):
		mytrace(inspect.stack())
		#print('hide_children:',fr,fr_level,hide)
		row = fr + 1	# start after row of tapped button
		while row < len(self.tv.data_source.items):
			vals,n,opts = self.tv.data_source.items[row]['content']
			if (len(vals)-1) > fr_level:						
				# level higher that from level, set as (un)hidden
				opts['hidden'] = hide
				self.tv.data_source.items[row]['content'] = vals,n,opts
				self.modif = True
			else:
				# level too high, end of (un)hiding
				break
			row += 1
		self.tv.reload_data()
		
	def check_children(self,fr, fr_level, check='yes'):
		mytrace(inspect.stack())
		#print('check_children:',fr,fr_level, check)
		row = fr # start from row of tapped button
		while row < len(self.tv.data_source.items):
			vals,n,opts = self.tv.data_source.items[row]['content']
			if row == fr or (len(vals)-1) > fr_level:						
				# tapped row or level higher that from level, set as (un)checked
				opts['checkmark'] = check
				self.tv.data_source.items[row]['content'] = vals,n,opts
				self.modif = True
			else:
				# level too high, end of (un)hiding
				break
			row += 1
		self.tv.reload_data()
			
	def button_show_action(self,sender):
		mytrace(inspect.stack())
		x = sender.x + sender.width/2
		y = sender.y + sender.height
		sub_menu = ['Collapse all', 'Expand all', 'Hide checked', 'Show checked only', 'View dates', 'completed checkboxes: sort at beginning', 'completed checkboxes:  sort at end', 'completed checkboxes: reset']
		tv = ui.TableView(name='show')
		tv.row_height = 30
		h = tv.row_height*len(sub_menu)
		tv.frame = (0,0,350,h)
		tv.data_source = ui.ListDataSource(items=sub_menu)
		sc = ui.SegmentedControl(name='dates_segmentedcontrol')
		sc.frame = (105,5+4*tv.row_height,240,20)
		sc.segments = ['create','update','due','ended']
		sc.selected_index = 0
		self.selected_date = 0
		tv.add_subview(sc)
		tv.allows_multiple_selection = False
		tv.delegate = self
		self.selected_row = None
		self.present_popover(tv, 'popover',popover_location=(x,y),hide_title_bar=True)
		if self.device_model == 'iPad':
			if not self.selected_row:
				return
			self.selected_date = tv['dates_segmentedcontrol'].selected_index
			act = sub_menu[self.selected_row[1]]
			
			self.show_action(act)
			
	def show_action(self,act):
		mytrace(inspect.stack())
		
		if self.show_mode == 'View dates':
			# reset normal view
			ws = self.get_screen_size()[0]	
			ws = ws - self.safeAreaInsets.left - self.safeAreaInsets.right
			self.tv.frame = (self.safeAreaInsets.left,self.ht,ws-2, self.height - self.ht - self.safeAreaInsets.bottom)		
			self['dates_title'].hidden = True
		self.show_mode = act
		if self.show_mode == 'completed checkboxes: reset':
			self.show_mode = 'Expand all'
		if self.show_mode == 'View dates':
			# dates view
			self.dates_sort_mode = 0 	# set before reload because tableview_cell_for_row
																# uses it
			ws = self.get_screen_size()[0]	
			ws = ws - self.safeAreaInsets.left - self.safeAreaInsets.right
			self.tv.frame = (self.safeAreaInsets.left,self.ht,ws-2, self.height - self.ht - self.safeAreaInsets.bottom)
			self.tv.y += self['dates_title'].height
			self.tv.height -= self['dates_title'].height
			self.tv.reload_data()
			dtt = self['dates_title']
			fsd = int(self.font_size*0.8)
			dtt.text = ['creation','update','due','complete'][self.selected_date] + ' date ' + '🔢'
			dtt.hidden = False
			return
		for row, item in enumerate(self.tv.data_source.items):
			vals,n,opts = item['content']			
			if act == 'Collapse all':	
				if len(vals) > 1:
					opts['hidden'] = True
				else:
					opts['hidden'] = False
			elif act == 'Expand all':	
				opts['hidden'] = False
			elif act == 'Hide checked':	
				if 'checkmark' not in opts:
					opts['hidden'] = False				
				elif opts['checkmark'] == 'yes':
					opts['hidden'] = True
				elif opts['checkmark'] == 'no':
					opts['hidden'] = False
				elif opts['checkmark'] == 'hidden':
					opts['hidden'] = False
			elif act == 'Show checked only':	
				if 'checkmark' not in opts:
					opts['hidden'] = True			
				elif opts['checkmark'] == 'yes':
					opts['hidden'] = False
				elif opts['checkmark'] == 'no':
					opts['hidden'] = True
				elif opts['checkmark'] == 'hidden':
					opts['hidden'] = True
			self.tv.data_source.items[row]['content'] = vals,n,opts	
		self.tv.reload_data()
		
	def dates_sort(self,data):
		mytrace(inspect.stack())
		#print('dates_sort')
		if self.show_mode == 'View dates':
			l = '🔢🔽🔼'
			self.dates_sort_mode += 1
			if self.dates_sort_mode == len(l):
				self.dates_sort_mode = 0
			self['dates_title'].text = self['dates_title'].text[:-1] + l[self.dates_sort_mode]
			self.tv.reload_data()
		
	def selected_text_attributes(self,row):
		mytrace(inspect.stack())
		#print('selected_text_attributes',row)
		tv = self.cells[row].content_view['text']
		tvo = ObjCInstance(tv)
		s,e = tv.selected_range
		#print(s,e)
		if s >= len(tv.text):
			# cursor at end of text
			return
		if s == e:
			# no selection
			return
		p1 = tvo.positionFromPosition_offset_(tvo.beginningOfDocument(), s)
		p2 = tvo.positionFromPosition_offset_(tvo.beginningOfDocument(), e)
		rge = tvo.textRangeFromPosition_toPosition_(p1,p2)
		rect = tvo.firstRectForRange_(rge)	# CGRect
		x,y = rect.origin.x,rect.origin.y
		w,h = rect.size.width,rect.size.height
		x = x + w/2
		v = ui.ScrollView(name='attributes')
		w,h = 240,238
		v.frame = (0,0,w,h)
		v.background_color = 'white'
		b = ui.Button()
		b.frame = (w-30,2,28,28)
		b.border_width = 1
		b.border_color = 'lightgray'
		b.corner_radius = 16
		b.title = 'ok'
		def b_action(sender):
			self.undo_save('Aa')	
			v = sender.superview
			self.shield.hidden = True
			self.remove_subview(sender.superview)
			vals,n,opts = self.tv.data_source.items[row]['content']
			attribs = opts.get('attribs',[])			
			# check if new attrib overlaps with old ones 
			biusohcqg = v.biusohcqg
			attrib = (s,e,biusohcqg)			
			upd = False
			attribs_new = []
			#print('before:',attribs)
			for attrib_old in attribs:
				s_old,e_old,biusohcqg_old = attrib_old
				if s <= s_old and e_old <= e:
					# new overlaps entirely old, remove old
					continue	# do not keep old
				elif s_old <= s and e <= e_old:
					# new inner to old, split old in 2 
					if s_old < s:
						attrib_old1 = (s_old,s,biusohcqg_old)
						attribs_new.append(attrib_old1)
					if e < e_old:
						attrib_old2 = (e,e_old,biusohcqg_old)
						attribs_new.append(attrib_old2)
				elif s < s_old and e > s_old:
					# new overlaps left part of old
					attrib_old1 = (e,e_old,biusohcqg_old)
					attribs_new.append(attrib_old1)					
				elif s < e_old and e > e_old:
					# new overlaps right part of old
					attrib_old1 = (s_old,s,biusohcqg_old)
					attribs_new.append(attrib_old1)			
				else:
					# previous does not overlap with new one, keep old
					attribs_new.append(attrib_old)
			if biusohcqg != '':	
				attribs_new.append(attrib)
			#print('after:',attribs_new)
			opts['attribs'] = attribs_new
			self.tv.data_source.items[row]['content'] = (vals,n,opts)
			self.modif = True
			#ui.delay(partial(self.tableview_reload_one_row, row), 0.1)
			tv = self.cells[row].content_view['text']
			self.redraw_textview_attributes(tv,opts)
		b.action = b_action
		v.add_subview(b)
		l = ui.Label(name='text')
		l.frame = (2,4,b.x-4,28)
		l.alignment = ui.ALIGN_LEFT
		l.text_color = 'blue'
		l.text = tv.text[s:e]
		v.add_subview(l)
		sep = ui.Label()
		sep.frame = (0,32,v.width,1)
		sep.border_color = 'lightgray'
		sep.border_width = 1
		v.add_subview(sep)
		lb = ui.Label()
		lb.frame = (10,34,110,32)
		lb.text = 'bold'
		v.add_subview(lb)
		sb = ui.Switch(name='b')
		sb.frame = (144,34,32,32)
		v.add_subview(sb)
		li = ui.Label()
		li.frame = (10,68,110,32)
		li.text = 'italic'
		v.add_subview(li)
		si = ui.Switch(name='i')
		si.frame = (144,68,32,32)
		v.add_subview(si)
		lu = ui.Label()
		lu.frame = (10,102,110,32)
		lu.text = 'underline'
		v.add_subview(lu)
		su = ui.Switch(name='u')
		su.frame = (144,102,32,32)
		v.add_subview(su)
		ls = ui.Label()
		ls.frame = (10,136,110,32)
		ls.text = 'strikethrough'
		v.add_subview(ls)
		ss = ui.Switch(name='s')
		ss.frame = (144,136,32,32)
		v.add_subview(ss)
		lo = ui.Label()
		lo.frame = (10,170,110,32)
		lo.text = 'outline'
		v.add_subview(lo)
		so = ui.Switch(name='o')
		so.frame = (144,170,32,32)
		v.add_subview(so)
		#===========
		co = ui.Button(name='o(')
		co.frame = (w-34,170,30,30)
		co.border_width = 1
		co.border_color = 'lightgray'
		co.corner_radius = 16
		co.font = (self.font,24)
		co.background_color = 'white'
		#v.add_subview(co)		
		#===========
		lh = ui.Label()
		lh.frame = (10,204,110,32)
		lh.text = 'shadow'
		v.add_subview(lh)
		sh = ui.Switch(name='h')
		sh.frame = (144,204,32,32)
		v.add_subview(sh)	
		lq = ui.Label()
		lq.frame = (10,238,110,32)
		lq.text = 'oblique'
		v.add_subview(lq)
		sq = ui.Switch(name='q')
		sq.frame = (144,238,32,32)
		v.add_subview(sq)
	
		lc = ui.Label()
		lc.frame = (10,272,110,32)
		lc.text = 'color'
		v.add_subview(lc)
		sc = ui.Button(name='c')
		sc.frame = (144,272,30,30)
		sc.border_width = 1
		sc.border_color = 'lightgray'
		sc.corner_radius = 16
		sc.font = (self.font,24)
		sc.title = 'a'
		sc.tint_color = 'blue'
		v.add_subview(sc)
		lg = ui.Label()
		lg.frame = (10,306,110,32)
		lg.text = 'background'
		v.add_subview(lg)
		sg = ui.Button(name='g')
		sg.frame = (144,306,30,30)
		sg.border_width = 1
		sg.border_color = 'lightgray'
		sg.corner_radius = 16
		sg.font = (self.font,24)
		sg.background_color = 'white'
		v.add_subview(sg)

		def color_action(sender):
			mytrace(inspect.stack())
			rgb = OMColorPickerViewController(title='choose color')
			if not rgb:
				return
			r,g,b = rgb
			if sender.name == 'c':
				sender.tint_color = rgb
			elif sender.name == 'g':
				sender.background_color = rgb
			elif sender.name == 'o(':
				sender.background_color = rgb
			v = sender.superview
			if sender.name in v.biusohcqg:
				# c(r,g,b) or g(r,g,b) or o(r,g,b)
				k = v.biusohcqg.find(sender.name)
				i = v.biusohcqg.find('(',k)
				j = v.biusohcqg.find(')',i)
				v.biusohcqg = v.biusohcqg[:i-1] + v.biusohcqg[j+1:]
			#....... for o, switch needs also to by on
			v.biusohcqg += sender.name[0] + '('+str(r)+','+str(g)+','+str(b)+')'
			#print(v.biusohcqg)
			attrText = NSMutableAttributedString.alloc().initWithString_(l.text)
			attributes = self.get_attributes(v.biusohcqg, font_size=24)
			attrText.setAttributes_range_(attributes, NSRange(0,len(l.text)))
			self.set_attributed_text(ObjCInstance(l), attrText)	
			switch_image(sb)
			switch_image(si)
			switch_image(su)
			switch_image(ss)
			switch_image(so)
			switch_image(sh)
			switch_image(sq)
			
		sc.action = color_action
		sg.action = color_action
		#co.action = color_action
		
		h = sg.y + sh.height + 4
		v.height = h
		v.content_size = (v.width,h)
				
		def switch_image(sender):
			mytrace(inspect.stack())
			t = sender.name
			for sv in ObjCInstance(sender).subviews():
				if sv._get_objc_classname().startswith(b'UISwitch'):
					with ui.ImageContext(32,32) as ctx:
						pth = ui.Path.rect(0,0,32,32)
						ui.set_color('white')
						pth.fill()
						attrText = NSMutableAttributedString.alloc().initWithString_(' a')
						attributes = self.get_attributes(t, font_size=24)
						attrText.setAttributes_range_(attributes, NSRange(0,2))
						rect = CGRect(CGPoint(0,0), CGSize(32,32))
						attrText.drawInRect_(rect)							
						img = ctx.get_image()
					sv.setThumbTintColor_(UIColor.colorWithPatternImage_(ObjCInstance(img)))
					
		switch_image(sb)
		switch_image(si)
		switch_image(su)
		switch_image(ss)
		switch_image(so)
		switch_image(sh)
		switch_image(sq)

		def sw_action(sender):
			mytrace(inspect.stack())
			# switch action: redraw text, attributes in label of v
			v = sender.superview
			a = sender.name # b or i or u or s or h or q or c
			v.biusohcqg = v.biusohcqg.replace(a,'')
			if sender.value:
				v.biusohcqg += a
			l = v['text']
			attrText = NSMutableAttributedString.alloc().initWithString_(l.text)
			attributes = self.get_attributes(v.biusohcqg, font_size=24)
			attrText.setAttributes_range_(attributes, NSRange(0,len(l.text)))
			self.set_attributed_text(ObjCInstance(l), attrText)	
			
		sb.action = sw_action
		si.action = sw_action
		su.action = sw_action
		ss.action = sw_action
		so.action = sw_action
		sh.action = sw_action
		sq.action = sw_action
		
		v.biusohcqg = ''
		opts = self.tv.data_source.items[row]['content'][2]
		attribs = opts.get('attribs',None)
		if attribs:
			# opts['attribs'] = [(s,e,'biusohcqg'),(s,e,'B'),...]
			for attrib in attribs:
				sa,ea,biusohcqg = attrib
				if sa <= s and e <= ea:
					# selected text entirely in a portion already with attributes
					v.biusohcqg = biusohcqg
					sb.value = 'b' in biusohcqg
					si.value = 'i' in biusohcqg
					su.value = 'u' in biusohcqg
					ss.value = 's' in biusohcqg
					so.value = 'o' in biusohcqg
					if 'c' in biusohcqg:
						k = biusohcqg.find('c')
						i = biusohcqg.find('(',k)
						j = biusohcqg.find(')',i)
						rgb = biusohcqg[i+1:j]
						r,g,b = rgb.split(',')
						r,g,b = float(r),float(g),float(b)
						sc.tint_color = (r,g,b)
					if 'g' in biusohcqg:
						k = biusohcqg.find('g')
						i = biusohcqg.find('(',k)
						j = biusohcqg.find(')',i)
						rgb = biusohcqg[i+1:j]
						r,g,b = rgb.split(',')
						r,g,b = float(r),float(g),float(b)
						sg.background_color = (r,g,b)
					if 'o(' in biusohcqg:
						k = biusohcqg.find('o(')
						i = biusohcqg.find('(',k)
						j = biusohcqg.find(')',i)
						rgb = biusohcqg[i+1:j]
						r,g,b = rgb.split(',')
						r,g,b = float(r),float(g),float(b)
						co.background_color = (r,g,b)
					else:
						co.background_color = (1,1,1)						

					attrText = NSMutableAttributedString.alloc().initWithString_(l.text)
					attributes = self.get_attributes(biusohcqg, font_size=24)
					attrText.setAttributes_range_(attributes, NSRange(0,len(l.text)))
					self.set_attributed_text(ObjCInstance(l), attrText)	
					break	
					
		x,y = ui.convert_point(point=(x,y), from_view=tv, to_view=None)
		self.present_popover(v, 'popover',popover_location=(x,y),hide_title_bar=False, force=True)	
		v.height = min(v.content_size[1],self.height - 40)
		v.y = (self.height - v.height) / 2
		
	def int_to_roman(self,n):
		mytrace(inspect.stack())
		if n >= 0 and n <= 1000:
			d = [{'0':'','1':'M'}, {'0':'','1':'C','2':'CC','3':'CCC','4':'DC','5':'D', '6':'DC','7':'DCC','8':'DCCC','9':'MC'},{'0':'','1':'X','2':'XX','3':'XXX','4':'XL','5':'L', '6':'LX','7':'LXX','8':'LXXX','9':'CX'},{'0':'','1':'I','2':'II','3':'III','4':'IV','5':'V', '6':'VI','7':'VII','8':'VIII','9':'IX'}]
			x = str('0000' + str(n))[-4:]
			r = ''
			for i in range(4):
				r = r + d[i][x[i]]
			return r
			
	def int_to_alpha(self,n):
		mytrace(inspect.stack())
		r = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[n-1]
		return r
		
	def OutlineFromLevelValue(self,vals):
		mytrace(inspect.stack())
		'''
		Decimal format
		1.0 Item
		2.0 Item
		  2.1 Child
		  2.2 Child
			  2.2.1 Child at next level
		Alphanumeric format
		I.  Highest level
		   A. Child node
		   B. Second Child node
		II. Second level.
		   A. Child node
		   B. 2nd child
		      i. Next level
		     ii. etc.
		       a. etc.
		Traditional format
		1.  Highest level
		   A. Child node
		   B. Second Child node
		2. Second level.
		   A. Child node
		   B. 2nd child
		      i. Next level
		     ii. etc.
		       a. etc.
		'''
		# vals parameter is an array of level+1 values
		k = self.outline_format
		if not self.first_level_has_outline:
			k += ' with title'
		outline_types = self.outline_formats[k][0]
		# check if level not too high
		if len(vals) > len(outline_types):
			return None
		blanks = self.outline_formats[self.outline_format][1]
		level = len(vals)-1
		outline_type = outline_types[level] + ' '	# temporary _ will be blank later
		
		v = vals[-1]
		if 'v' in outline_type:
			for v in vals:
				outline_type = outline_type.replace('v',str(v+1),1)
		elif 'w' in outline_type:
			for v in vals[1:]:
				outline_type = outline_type.replace('w',str(v+1),1)
		elif 'I' in outline_type:
			outline_type = outline_type.replace('I', self.int_to_roman(v+1), 1)
		elif 'A' in outline_type:
			outline_type = outline_type.replace('A', self.int_to_alpha(v+1), 1)
		elif 'i' in outline_type:
			outline_type = outline_type.replace('i', self.int_to_roman(v+1), 1).lower()
		elif 'a' in outline_type:
			outline_type = outline_type.replace('a', self.int_to_alpha(v+1), 1).lower()
		elif '1' in outline_type:
			outline_type = outline_type.replace('1', str(v+1), 1)
			
		outline_type = ' ' * blanks * level + outline_type
		#print(vals,outline_type)
		return outline_type	
		
	def check_auto_save(self,modif):
		mytrace(inspect.stack())
		#print('check_auto_save: modif=',modif,'self.auto_save=', self.auto_save)
		if not self.file:
			return
		if self.auto_save == 'no':
			return
		elif self.auto_save == 'each char':		
			self.file_save()
		elif self.auto_save == 'each line':		
			if modif != 'char':
				self.file_save()
		
	def file_save(self, save_prm=True):
		mytrace(inspect.stack())
		
		c = []
		notes = ''
		for item in self.tv.data_source.items:
			outline = item['outline']
			vals,n,opts = item['content']
			c.append((vals,outline,opts,{'text':item['title']}))	# (vals,outline, {options},{'text':xxx})
			chk = opts.get('checkmark','')
			if chk == 'yes':
				chk = '✅'
			elif chk == 'hidden':
				chk = '▫️'
			else:
				chk = '⬜️'
				dates = opts.get('dates',None)
				if dates:
					due_date = dates[2]
					if due_date:
						chk = '🕦'
			if chk == '▫️':
				l = len(outline) - len(outline.lstrip())	# blanks at left of outline
				b = ' '*l
				outline = outline[l:]
				notes += b + chk + outline + ' ' + item['title'] + '\n' # event notes for Apple Watch
			else:
				notes += chk + outline + ' ' + item['title'] + '\n' # event notes for Apple Watch
		
		# store outline text as event at 01/01/2022 01:01
		# search if event with same title exists 
		#  no use of eventIdentifier because not same cross devices
		# Convert string yyyymmdd to NSdate
		dateFormat = ObjCClass('NSDateFormatter').alloc().init()
		dateFormat.setDateFormat_('yyyyMMdd HH:mm:ss')	
		date1 = dateFormat.dateFromString_('20220101 01:01:00') 
		date2 = dateFormat.dateFromString_('20220101 01:01:01') 	
		calendars_array = [self.cal]
		predicate = self.store.predicateForEventsWithStartDate_endDate_calendars_(date1, date2, calendars_array)
		events = self.store.eventsMatchingPredicate_(predicate)
		event = None
		for evt in events:
			if str(evt.title())	== self.file:
				event = evt
				break
		if not event:	
			event = ObjCClass('EKEvent').eventWithEventStore_(self.store)
		dateFormat = ObjCClass('NSDateFormatter').alloc().init()
		dateFormat.setDateFormat_('yyyyMMdd HH:mm')
		event.title = self.file
		event.notes = notes
		del notes
		dattim_str = '20220101 01:01'
		event.startDate = dateFormat.dateFromString_(dattim_str)
		event.endDate = dateFormat.dateFromString_(dattim_str)	
		event.setCalendar_(self.cal)
		span = 0 # no recurrence
		ret = self.store.saveEvent_span_error_(event, span, None)
						
		#print('file_save')
		t1 = datetime.now()
		dt = f'{t1:_%Y%m%d_%H%M%S}'
		if self.last_save_datetime:
			while dt == self.last_save_datetime:
				sleep(0.1)				
				t1 = datetime.now()
				dt = f'{t1:_%Y%m%d_%H%M%S}'
		# save current
		new_filename = self.file + dt
		old_filename = self.file + self.last_save_datetime

		with open(self.path + new_filename + '.outline', mode='wt', encoding='utf-8', errors="surrogateescape") as fil:
			prms = {}
			prms['format'] = self.outline_format
			prms['1st level has outline'] = self.first_level_has_outline
			prms['font'] = self.font
			prms['font_size'] = self.font_size			
			t = str(c) + lf + str(prms)
			fil.write(t)
			del t
			del c
		
		# delete .old version
		if os.path.exists(self.path + old_filename + '.outline'):
			os.remove(self.path + old_filename + '.outline')
		self.modif = False
		self.prms['path'] = self.path
		self.prms['file'] = new_filename + '.outline'
		t2 = datetime.now()
		self.save_duration = str(t2-t1)
		self.last_save_datetime = dt

		if save_prm:		
			self.prms_save()

	def prms_save(self):	
		mytrace(inspect.stack())
		self.prms['font'] = self.font
		self.prms['font_size'] = self.font_size
		self.prms['font_hidden'] = self.font_hidden_size
		with open(self.prm_file, mode='wt', encoding='utf-8', errors="surrogateescape") as fil:
			x = str(self.prms)
			fil.write(x)
					
	def close_action(self, sender):
		mytrace(inspect.stack())
		if self.log == 'yes':
			try:
				self.log_fil.close()
			except:
				pass
		if self.modif:
			b = console.alert('⚠️ File has been modified', 'save before leaving?', 'yes', 'no', hide_cancel_button=True)
			if b == 1:
				self.button_files_action('Save')
		self.prms_save()

		# unregister Blackmamba key_event_handlers
		if self._handlers:
			unregister_key_event_handlers(self._handlers)

		self.close()

def main():
	global mv
	mytrace(inspect.stack())

	quiet_add_line = False	
	if appex.is_running_extension():
		if len(argv) > 1:
			# suppose appex mode to add a shared text at end of file in arg 
			quiet_add_line = True
	else:
		if len(argv) == 3 and argv[-1] == 'CLIPBOARD':
			# suppose started by a shortcut with arguments outline_name CLIPBOARD
			quiet_add_line = True
	if quiet_add_line:
		# get current_path in .prm
		path = argv[0]
		i = path.rfind('.')
		prm_file = path[:i] + '.prm'
		with open(prm_file, mode='rt', encoding='utf-8', errors="surrogateescape") as fil:
			x = fil.read()
			prms = literal_eval(x)
		path = prms['current path']
		type = None
		if appex.is_running_extension():
			txt = appex.get_text() # str
		else:
			txt = clipboard.get()
		if not txt:
			if appex.is_running_extension():
				url = appex.get_url()
			else:
				url = None
			if not url:
				if appex.is_running_extension():
					img_b = appex.get_image_data()
				else:
					img_b = False
				if not img_b:
					console.hud_alert('No text, url, image passed', 'error',3)
					if appex.is_running_extension():
						appex.finish()
					else:
						webbrowser.open('shortcuts://')
					return
				else:
					t1 = datetime.now()
					imgnam = f'IMG_paste_{t1:%Y%m%d_%H%M%S}.JPG'
					with open(path+imgnam, mode='wb') as fil:
						fil.write(img_b)
					type = 'image'
					txt = ''
			else:
				i = url.find('?')
				if i >= 0:
					urli = url[:i]
				else:
					urli = url
				i = urli.rfind('.')
				if urli.lower()[i+1:] in ('jpg', 'jpeg', 'png', 'heic'):
					img_b = requests.get(url).content
					t1 = datetime.now()
					imgnam = f'IMG_paste_{t1:%Y%m%d_%H%M%S}.JPG'
					with open(path+imgnam, mode='wb') as fil:
						fil.write(img_b)
					type = 'image'
					txt = ''
				else:
					txt = url # str
					type = 'url'
		else:
			type = 'text'
		# get file passed as arg1
		file = argv[1]
		files = os.listdir(path=path)
		fnd = file			
		for f in files:
			if f.startswith(file+'_20') and f.endswith('.outline'):
				if f > fnd:
					# keep newest
					fnd = f
		file = fnd
		if not os.path.exists(path+file):
			console.hud_alert('file argument does not exist','error', 3)
			if appex.is_running_extension():
				appex.finish()
			else:
				webbrowser.open('shortcuts://')
			return	
		# read file
		with open(path+file,mode='rt', encoding='utf-8', errors="surrogateescape") as filc:
			c = filc.read()
		c_prms = c.split(lf)
		c = c_prms[0]
		prms_out = c_prms[1]
		items = literal_eval(c)
		prms_out = literal_eval(prms_out)
		n = 0
		for item in items:
			vals,outline,opts,dict_text = item
			n = vals[0]
		# append an outline row of 1st level
		n += 1	
		vals = [n]
		mv = Outliner(only_formats=True)	
		mv.first_level_has_outline = prms_out['1st level has outline']		
		mv.outline_format = prms_out['format']
		# generate outline from level and flag first_level_has_outline
		outline = mv.OutlineFromLevelValue(vals)
		del mv
		opts = {}
		dt = datetime.now()
		creation_date = f'{dt:%Y-%m-%d %H:%M:%S}'
		opts['dates'] = (creation_date,None,None,None)
		dict_text = {'text':txt}
		if type == 'image':
			opts['image'] = (path + imgnam, 4 , 'left')
		items.append((vals,outline,opts,dict_text))
		# write new file with generated date-time
		t1 = datetime.now()
		dt = f'{t1:_%Y%m%d_%H%M%S}'
		# save current
		i = file.find('_20')
		new_filename = file[:i] + dt + '.outline'
		with open(path + new_filename, mode='wt', encoding='utf-8', errors="surrogateescape") as fil:
			t = str(items) + lf + str(prms_out)
			fil.write(t)	
		os.remove(path + file)	
		# save new filename in .prm
		prms['path'] = prms['current path']
		prms['file'] = new_filename
		with open(prm_file, mode='wt', encoding='utf-8', errors="surrogateescape") as fil:
			x = str(prms)
			fil.write(x)	
		console.hud_alert(type+' pasted in '+new_filename,'success', 3)
		if appex.is_running_extension():
			appex.finish()
		else:
			webbrowser.open('shortcuts://')
		return
		#=======================================				
	if appex.is_running_extension():
		# runs in appex mode, only used to get path of "on my device"
		path = appex.get_file_path()
		if not path:
			console.alert('❌ No path passed', '', 'ok', hide_cancel_button=True)
			appex.finish()
			return	
		# /private/var/mobile/Containers/Shared/AppGroup/EF3F9065-AD98-4DE3-B5DB-21170E88B77F/File Provider Storage/.....
		t1 = '/private/var/mobile/Containers/Shared/AppGroup/'
		t2 = '/File Provider Storage/'
		device_model = str(ObjCClass('UIDevice').currentDevice().model())			
		if t1 not in path or t2 not in path:
			console.alert('❌ No share of file from', 'On my ' + device_model, 'ok', hide_cancel_button=True)
			appex.finish()
			return				
		i = path.find(t2)
		i += len(t2)
		path_onmy = path[:i]
		path = argv[0]
		i = path.rfind('.')
		prm_file = path[:i] + '.prm'
		if not os.path.exists(prm_file):
			console.alert('❌ .prm file has to exist', '', 'ok', hide_cancel_button=True)
			appex.finish()
			return				
		with open(prm_file, mode='rt', encoding='utf-8', errors="surrogateescape") as fil:
			x = fil.read()
			prms = literal_eval(x)
		prms['on_my_path'] = path_onmy
		with open(prm_file, mode='wt', encoding='utf-8', errors="surrogateescape") as fil:
			x = str(prms)
			fil.write(x)
		appex.finish()
		return				
	# normal mode
	if len(argv) == 2:
		if argv[1] == 'grant_access_to_calendar':
			# Once Pythonista has been authorized, this code does not need to be executed

			# EKEventStore = calendar database
			store = ObjCClass('EKEventStore').alloc().init()

			access_granted = Event()
			def completion(_self, granted, _error):
				mytrace(inspect.stack())
				access_granted.set()
			completion_block = ObjCBlock(completion, argtypes=[c_void_p, c_bool, c_void_p])
			store.requestAccessToEntityType_completion_(0, completion_block)
			access_granted.wait()
			
			print('access to calendar should be granted')
			print('see IOS Settings/Pythonista')
				
			return

	mv = Outliner()
	mv.present('fullscreen', hide_title_bar=True)
	
if __name__ == '__main__':
	main()
