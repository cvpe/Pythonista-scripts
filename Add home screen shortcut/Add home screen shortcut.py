# from http://www.editorial-workflows.com/workflow/5872060161064960/e831ijSVsok
# converted for python3 which uses bytes ipo strings
import dialogs
import http.server
import webbrowser
import base64
import os
import ui
import sys
import dialogs
import requests
import console
from objc_util import *
import photos
from PIL import Image
import math
import io
import time
from File_Picker import *
from MyPickDocument import MyPickDocument

page_template = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
	<head>
		<meta charset="utf-8">
		<title>
			{{TITLE}}
		</title>
		<link rel="apple-touch-icon" sizes="{{ICON_SIZE}}" href="{{ICON_B64}}">
		<meta name="apple-mobile-web-app-capable" content="yes">
		<meta name="apple-mobile-web-app-status-bar-style" content="black">
		<meta name="viewport" content="initial-scale=1 maximum-scale=1 user-scalable=no">
		<style type="text/css">
		body {
			background-color: #023a4e;
			-webkit-text-size-adjust: 100%;
			-webkit-user-select: none;
		}
		#help {
			display: none;
			color: white;
			font-family: "Avenir Next", helvetica, sans-serif;
			padding: 40px;
		}
		.help-step {
			border-radius: 8px;
			background-color: #047ea9;
			color: white;
			font-size: 20px;
			padding: 20px;
			margin-bottom: 20px;
		}
		.icon {
			background-image: url({{ICON_B64}});
			width: 76px;
			height: 76px;
			background-size: 76px 76px;
			border-radius: 15px;
			margin: 0 auto;
		}
		.share-icon {
			width: 32px;
			height: 27px;
			display: inline-block;
			background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAAA2CAQAAADdG1eJAAAAyElEQVRYw+3YvQrCMBSG4a/SKxC8M6dOnQShk9BJKAi9OcFLKrwuaamDRRtMLHxnCBySch7yR6i07aCjy1seyEbgxhhd3vI5CKH8ddamJNAD0EoAEm1SQijfSCNAoklGoAcG6pAFgMQpCYELMFBN+QSQqBmA828BBx4cZ/kMIFFxZ5/2NLwA1sQu92VuQHZAubTB3vcVRfz4/5+BZfnnY5cPqjehAQYYYIABBhhQxn3+zYPFS2CAAQYYYIABBqx6kMT+htzADDwBk2GVUD9m13YAAAAASUVORK5CYII=');
			background-size: 32px 27px;
			vertical-align: -4px;
		}
		.icon-title {
			font-family: "Helvetica Neue", helvetica, sans-serif;
			text-align: center;
			font-size: 16px;
			margin-top: 10px;
			margin-bottom: 30px;
		}
		@media only screen and (max-width: 767px) {
			#help {
				padding: 30px 0px 10px 0px;
			}
			.help-step {
				padding: 10px;
			}
		}
		</style>
	</head>
	<body>
		<div id="help">
			<div class="icon"></div>
			<div class="icon-title">
				{{ICON_B64}}
			<div class="icon-title">
				{{TITLE}}
			<div class="icon-title">
				{{SHORTCUT_URL}}
			</div>
			<div class="help-step">
				<strong>1.</strong> Tap the
				<div class="share-icon"></div>button in the toolbar
			</div>
			<div class="help-step">
				<strong>2.</strong> Select "Add to Home Screen"
			</div>
			<div class="help-step">
				<strong>3.</strong> Tap "Add"
			</div>
		</div><script type="text/javascript">
if (navigator.standalone) {
		  window.location = "{{SHORTCUT_URL}}";
		} else {
		  var helpDiv = document.getElementById("help");
		  helpDiv.style.display = "block";
		}
		</script>
	</body>
</html>
'''

redirect_template = '''<!doctype html>
<html>
	<head>
		<meta charset="utf-8">
		<title>Loading...</title>
	</head>
	<body>
	<script>
	window.location = "data:text/html;base64,{{DATA}}";	  
	</script>
	</body>
</html>
'''

def ui2pil(ui_img):
	return Image.open(io.BytesIO(ui_img.to_png()))
	
def pil2ui(imgIn):
	with io.BytesIO() as bIO:
		imgIn.save(bIO, 'PNG')
		imgOut = ui.Image.from_data(bIO.getvalue())
	del bIO
	return imgOut

class MyView(ui.View):
	def __init__(self,w,h):
		self.width = w
		self.height = h
		
		b_ok = ui.ButtonItem()
		b_ok.title = 'ok'
		b_ok.action = self.ok
		self.right_button_items = (b_ok,)
		
		# get device info
		device = ObjCClass('UIDevice').currentDevice()
		self.device_model = str(device.model())
		#print(device.name())
		UIScreen = ObjCClass('UIScreen').mainScreen()
		#print(dir(UIScreen))
		self.screen_scale = UIScreen.nativeScale()
		#print(UIScreen.nativeScale())
		self.screen_width  = UIScreen.bounds().size.width
		self.screen_height = UIScreen.bounds().size.height
		if self.screen_scale > 1:
			self.device_model = self.device_model + ' retina'
		if self.screen_scale > 2:
			self.device_model = self.device_model + 'HD'
		if self.screen_width > 1024 or self.screen_height > 1024:
			self.device_model = self.device_model + ' pro'
		#print(UIScreen.bounds().size.height)
		#print(self.device_model)
		if 'ipad' in self.device_model.lower():
			if 'pro' in self.device_model.lower():
				# ipad pro
				self.icon_size_pts = 83.5
			else:
				# ipad, ipad mini
				self.icon_size_pts = 76
		else:
			# iphone, ipod
			self.icon_size_pts = 60
		self.icon_size = int(self.icon_size_pts * self.screen_scale)
		#print(self.icon_size)
		self.name = 'Add home screen shortcut: ' + self.device_model + ' [icon=' + str(self.icon_size) + 'pixels]' 
						
	def process(self):
		fields = []
		field = {'title':'title','type':'text','value':''}
		fields.append(field)
		field = {'title':'url','type':'text','value':''}
		fields.append(field)
		field = {'title':'icloud','type':'switch','value':False}
		fields.append(field)
		field = {'title':'script','type':'text','value':''}
		fields.append(field)
		field = {'title':'arguments','type':'text', 'value':''}
		fields.append(field)
		field = {'title':'icon', 'type':'text', 'value':'', 'key':'segmented', 'segments':['photo','local','icloud','url']}
		fields.append(field)
		f = myform_dialog(title='Home Screen Shortcut', done_button_title='ok',fields=fields, sections=None)
		#print(f)
		if f == None:
			# Close/cancel pressed
			return
		url = f['url']
		if url == '':
			script = f['script']
			#print(script)
			if 'Mobile Documents/iCloud' in script:
				icloud = True
			else:
				icloud = False
			t = 'Pythonista3/Documents/'
			i = script.find(t)
			script = script[i+len(t):-3]# remove path and .py
			arguments = f['arguments']
			self.shortcut_url = 'pythonista3://' + script + '?action=run'
			if icloud:
				self.shortcut_url = self.shortcut_url + '&root=icloud'
			if arguments != '':
				self.shortcut_url = self.shortcut_url + '&argv=' + arguments
		else:
			self.shortcut_url = url
		self.title = f['title']
		self.image_data = f['icon']

		# I got errors when Gestures view os an ImageView			
		im = ui.ImageView(name='imageview')
		#self.touch_enabled = False
		#im.touch_enabled = True
		im.image = ui.Image.from_data(self.image_data)

		wi = self.width
		hi = self.height
		w,h = im.image.size
		# not so easy, depends on ratio wi*hi vs w/h
		ri = wi/hi
		r  = w/h
		if ri < r:
			hi = wi * h/w
			side = hi
		else:
			wi = hi * w/h
			side = wi
		side = side*0.9	# temporary=======================
		im.frame = ((self.width-wi)/2,(self.height-hi)/2,wi,hi)
		self.add_subview(im)
		
		l = ui.Label(name='square')
		l.frame = ((wi-side)/2,(hi-side)/2,side,side)
		l.border_color = 'blue'
		l.border_width = 2
		# icon is not really a square with circular corners (it is a squircle)
		# but to simulate how will mask our square, use corner radius = side/6.4
		l.corner_radius = side/6.4 
		im.add_subview(l)
		self.square = l
			
	def ok(self,sender):
		global page_template,redirect_template,redirect_page

		w = self['imageview'].width
		h = self['imageview'].height
		side = int(self['imageview']['square'].width)
		x = int(self['imageview']['square'].x)
		y = int(self['imageview']['square'].y)
		#print(w,h,x,y,side)
		with ui.ImageContext(side,side) as ctx:
			try:
				# sometimes image.draw says None does not have draw method
				# although image is shown, allow user to retry
				self['imageview'].image.draw(-x,-y,w,h)
			except Exception as e:
				console.hud_alert('error:'+str(e)+', retry','error',2)
				return
			ui_image = ctx.get_image()
		pil_image = ui2pil(ui_image)
		pil_icon = pil_image.resize((self.icon_size,self.icon_size))	
		ui_icon = pil2ui(pil_icon)
		self.image_data = ui_icon.to_png()

		# prepare html page for Safari
		icon_b64 = 'data:image/jpeg;charset=utf-8;base64,' + str(base64.b64encode(self.image_data),'utf-8')

		t = str(self.icon_size)+'x'+str(self.icon_size)
	
		page = page_template.replace('{{ICON_SIZE}}', t).replace('{{TITLE}}', self.title).replace('{{SHORTCUT_URL}}', self.shortcut_url).replace('{{ICON_B64}}', icon_b64)
		page_b64 = str(base64.b64encode(page.encode()),'utf-8')
		redirect_page = redirect_template.replace('{{DATA}}', page_b64).encode()
	
		httpd = http.server.HTTPServer(('', 0), MyHandler)
		port = str(httpd.socket.getsockname()[1])
		webbrowser.open('safari-http://localhost:' + port)
		httpd.handle_request()
		
		self.close()
		
	def touch_began(self,touch):
		#print('touch_began',touch.location)
		self.pan_on_image(1,touch)

	def touch_moved(self,touch):
		#print('touch_moved',touch.location)
		self.pan_on_image(2,touch)

	def pan_on_image(self,state,touch):
		x,y = touch.location
		im = self['imageview']
		if x < im.x or y < im.y or x > (im.x+im.width) or y > (im.y+im.height):
			return
		x = x - im.x
		y = y - im.y
		if state == 1:
			# begin	
			# search nearst corner and set it as fixed
			# Check if on corner on inside square
			# check if touch in imageview
			# use ((x-x1)**2 + (y-y1)**2) < d**2 quicker than sqrt
			d = self.square.corner_radius*self.square.corner_radius
			if (math.pow(x-(self.square.x),2)+math.pow(y-(self.square.y),2)) < d:
				self.touch_type = 'size_top_left'
			elif (math.pow(x-(self.square.x+self.square.width),2)+math.pow(y-(self.square.y),2)) < d:
				self.touch_type = 'size_top_right'
			elif (math.pow(x-(self.square.x),2)+math.pow(y-(self.square.y+self.square.height),2)) < d:
				self.touch_type = 'size_bottom_left'
			elif (math.pow(x-(self.square.x+self.square.width),2)+math.pow(y-(self.square.y+self.square.height),2)) < d:
				# touch near bottom/right corner, thus resize wanted
				self.touch_type = 'size_bottom_right'
			else:
				if x>= self.square.x and x<=(self.square.x+self.square.width) and y>=self.square.y and y<=(self.square.y+self.square.height):
					# Touch inside square
					self.touch_type = 'move'
				else:
					# Touch outside square
					self.touch_type = None
			return
		# move
		# compute translation versus previous position
		dx = x - (touch.prev_location.x - im.x)
		dy = y - (touch.prev_location.y - im.y)
		if self.touch_type == None:
			return			
		wi = im.width
		hi = im.height
		if self.touch_type == 'move':
			# check if move would not place square outside
			xn = self.square.x + dx
			yn = self.square.y + dy
			if xn<0 or (xn+self.square.width)>wi or yn<0 or (yn+self.square.height)>hi:
				return
			self.square.x = xn
			self.square.y = yn
		elif 'size' in self.touch_type:
			dy = dx	# force keeping square
			if self.touch_type == 'size_top_left':
				# right and bottom stay unchanged
				xn = self.square.x + dx
				yn = self.square.y + dy
				wn  = self.square.width  - dx
				hn = self.square.height - dy
			elif self.touch_type == 'size_top_right':
				# left and bottom stay unchanged
				xn = self.square.x
				yn = self.square.y - dy
				wn  = self.square.width  + dx
				hn = self.square.height + dy
			elif self.touch_type == 'size_bottom_left':
				# right and top stay unchanged
				xn = self.square.x + dx
				yn = self.square.y
				wn  = self.square.width  - dx
				hn = self.square.height - dy
			elif self.touch_type == 'size_bottom_right':
				# left and top stay unchanged
				xn = self.square.x
				yn = self.square.y
				wn  = self.square.width  + dx
				hn = self.square.height + dy
			if xn < 0 or (xn+wn) > wi or yn < 0 or (yn+hn) > hi:
				return
			self.square.x      = xn
			self.square.y      = yn
			self.square.width  = wn
			self.square.height = hn
			self.square.corner_radius = self.square.width/6.4
			#self.set_needs_display()	
	
	def will_close(self):
		if 'from_launcher' in sys.argv:
			# Back to home screen
			#os._exit(0)
			webbrowser.open('launcher://crash')
		
class MyHandler (http.server.BaseHTTPRequestHandler):
	def do_GET(s):
		global redirect_page
		s.send_response(200)
		s.send_header('Content-Type', 'text/html')
		s.end_headers()
		s.wfile.write(redirect_page)
	def log_message(self, format, *args):
		pass

class MyTextFieldDelegate (object):
	global c
		
	def textfield_should_begin_editing(self, textfield):
		#print('should_begin_editing',textfield.name)
		c.textfield_active = textfield
		if textfield.name == 'script':
			icloud = c.values['icloud']
			def callback(textfield):
				# for esthetics, remove initial part of full path
				# if done 'in line' after modal dialog, textfield not modified,
				# obviously, threads problem
				t = c.values['script']
				ts = 'Pythonista3/'
				i = t.find(ts)
				textfield.text = t[i+len(ts):]
			file_picker_dialog('Select script', multiple=False, select_dirs=False,file_pattern=r'^.*\.py$',from_dialog=[c,textfield], root_dir=os.path.expanduser('~/Documents/'), icloud=icloud,only=True,callback=callback)
			textfield.end_editing()
		elif textfield.name == 'url':	
			c.container_view['webview_view'].hidden = False
			c.container_view['shield'].hidden = False
			c.container_view['webview_view']['copy_url'].hidden = False
			c.container_view['webview_view']['copy_url'].field = textfield
			c.container_view['webview_view']['webview'].load_url('http://www.google.com')
		return True
		
	def textfield_did_begin_editing(self, textfield):
		#print('did_begin_editing',textfield.name,textfield.text)
		c.error_message.text = ''		
		if textfield.name == 'icon url':	
			textfield.text = ''	
		
	def webview_did_finish_load(self, webview):
		url = webview.evaluate_javascript('window.location.href') 
		c.container_view['webview_view']['address'].text = url
		
	def textfield_did_change(self, textfield):
		#print('did_change',textfield.name)
		c.values[textfield.name] = textfield.text
		if textfield.name == 'icon url':
			c.container_view['webview_view'].hidden = True
			c.container_view['icon url'].hidden = True
			c.container_view['shield'].hidden = True
			self.disp_icon(c.container_view['icon url'])
			textfield.text = ''

	def textfield_did_end_editing(self, textfield):
		#print('did_end_editing',textfield.name,textfield.text)
		if textfield.name == 'address':
			url = textfield.text
			if not (url.startswith('http://') or url.startswith('https://')):
				url = 'http://' + url
			c.container_view['webview_view']['webview'].load_url(url)
		elif textfield.name == 'url':
			c.values[textfield.name] = textfield.text
		c.textfield_active = None
			
	def switch_action(self,sender):
		if sender.name == 'icloud':
			if sender.value != c.values[sender.name]:
				# swich modified, reset script textfield
				c.values['script'] = ''
				c.textfield_script.text = ''
				self.textfield_did_change(c.textfield_script)
		c.values[sender.name] = sender.value
		if c.textfield_active:
			c.textfield_active.end_editing()

	def segmented_action(self,sender):
		if c.textfield_active:
			c.textfield_active.end_editing()
		c.icon_origin_segmentedcontrol = sender
		icon_origin = sender.segments[sender.selected_index]			
		sender.selected_index = -1	# reset for other image, if any		
		c.container_view['icon url'].icon_origin = icon_origin
		if icon_origin == 'local':
			def picked_local(tf):
				self.disp_icon(c.container_view['icon url'])
			file_picker_dialog('Select icon', multiple=False, select_dirs=False,file_pattern=r'^.*\.(jpg$|png$)', from_dialog=[c,c.container_view['icon url']], root_dir=os.path.expanduser('~/Documents/'), icloud=False, only=True, callback=picked_local)
			# c.values and textfield.text filled in file_picker_dialog
			# cancel => callback not called
		elif icon_origin == 'photo':
			photo_asset = photos.pick_asset(assets=photos.get_assets(media_type='photo'))
			if not photo_asset:
				return
			c.values['icon url'] = photo_asset
			self.disp_icon(c.container_view['icon url'])
		elif icon_origin == 'icloud':
			def picked_icloud(param):
				if param == 'canceled':
					return
				c.values['icon url'] = str(param[7:]) # remove file://
				self.disp_icon(c.container_view['icon url'])
			MyPickDocument(500,500,title='test',UTIarray=['public.image'], PickerMode=0, callback=picked_icloud)
		elif icon_origin == 'url':
			c.container_view['shield'].hidden = False
			c.container_view['icon url'].enabled = True
			c.container_view['icon url'].text = 'drag & drop image here'			
			c.container_view['icon url'].hidden = False
			c.container_view['webview_view']['webview'].load_url('http://www.google.com')
			c.container_view['webview_view'].hidden = False
			
	def disp_icon(self,textfield):
		icon_origin = c.container_view['icon url'].icon_origin
		if icon_origin == 'photo':
			image_data = c.values['icon url'].get_image_data().getvalue()
		elif icon_origin == 'local':
			with open(c.values['icon url'],mode='rb') as fil:
				image_data = fil.read()
		elif icon_origin == 'icloud':
			with open(c.values['icon url'],mode='rb') as fil:
				image_data = fil.read()
		elif icon_origin == 'url':
			url = textfield.text	
			#print(url)
			# sometimes Google shows an image by pointing to another url
			t = 'imgurl=http'
			i = url.find(t)
			if i >= 0:
				url = url[i+7:]
			#print(url)
			# sometimes Google imbeds an image as base64 string
			t = 'data:image/'	
			if url[:len(t)] == t and 'base64' in url:
				# encoded data image url
				NSData = ObjCClass('NSData').alloc().initWithContentsOfURL_(nsurl(url))
				image_data = nsdata_to_bytes(ObjCInstance(NSData))
			else:
				# assumed url of an image to be downloade
				try:
					r = requests.get(url)
					image_data = r.content
				except Exception as e:
					c.error_message.text = 'download error for url='+url		
					print(url)	
					return		
		c.container_view['icon'].image = ui.Image.from_data(image_data)
		c.container_view['icon'].hidden = False
		c.values['icon'] = image_data
		
		# indicate which origin
		# we can't let a segment as selected because, in this case,
		# we could not select the same segment to, for instance pick another photo
		sender = c.icon_origin_segmentedcontrol
		idx = sender.segments.index(icon_origin)
		l = sender['indicator']
		if not l:
			l = ui.Label()
			l.name = 'indicator'
			sender.add_subview(l)
		w = sender.width/4
		x = idx * w
		l.frame = (x,0,w,sender.height)
		l.background_color = (1,0,0,0.1)

def myform_dialog(title='', fields=None,sections=None, done_button_title='ok'):
	global c

	sections = [('', fields)]
	c = dialogs._FormDialogController(title, sections, done_button_title=done_button_title)
	c.container_view.frame = (0,0,600,800)
		
	def my_done_action(sender):
		# check if needed fields are filled
		#print('my_done_action',c.values)
		c.error_message.text = ''		
		if c.values['title'].strip() == '':
			c.error_message.text = 'title has to be defined'
			return
		if c.values['script'].strip() == '' and c.values['url'].strip() == '':
			c.error_message.text = 'script or url has to be defined'
			return
		if c.values['url'].strip() != '' and c.values['arguments'].strip() != '':
			c.error_message.text = 'arguments not allowed if url'
			return
		if 'icon' not in c.values:
			c.error_message.text = 'icon not defined'
			return		
		if c.shield_view:
			c.dismiss_datepicker(None)
		else:
			ui.end_editing()
			c.was_canceled = False
			c.container_view.close()

	# set my own "ok" button to check fields before leaving dialog		
	c.container_view.right_button_items[0].action = my_done_action
	
	y0 = 35
	y = y0
	for s in c.cells:
		for cell in s:
			y = y + cell.height
	w = c.container_view.width
	h = c.container_view.height - y
	x = 0
	icon = ui.ImageView(frame=(x,y,w,h))
	icon.name = 'icon'
	icon.content_mode = ui.CONTENT_SCALE_ASPECT_FIT
	icon.hidden = True
	c.container_view.add_subview(icon)	
	
	shield = ui.View()
	shield.name = 'shield'
	shield.frame = (0,y0,w,y-y0)
	shield.background_color = (1,1,1,0.8)
	shield.hidden = True
	c.container_view.add_subview(shield)		
	
	for i in range(0,len(c.cells[0])):			# loop on rows of section 0
		cell = c.cells[0][i]									# ui.TableViewCell of row i
		# some fields types are subviews of the cell:
		#   text,number,url,email,password,switch
		#  but check, date and time are not set as subviews of cell.content_view
		if len(cell.content_view.subviews) > 0:
			tf = cell.content_view.subviews[0] 		# ui.TextField of value in row
			# attention: tf.name not set for date fields
			if tf.name in ['title','url','script','arguments']:			# No check for switch
				tf.delegate = MyTextFieldDelegate()	# delegate to check while typing
				if tf.name == 'script':
					c.textfield_script = tf
			elif 'ui.Switch' in str(type(tf)):
				tf.action = MyTextFieldDelegate().switch_action
			elif tf.name == 'segmented': # key='segmented', title='icon'
				item = c.sections[0][1][i]	# section 0, 1=items, row i
				segmented = ui.SegmentedControl()
				segmented.name = cell.text_label.text
				segmented.action = MyTextFieldDelegate().segmented_action
				segmented.frame = tf.frame
				segmented.segments = item['segments']
				absolute_y = y0 + i * cell.height
				cell.content_view.remove_subview(tf)
				del tf
				cell.content_view.add_subview(segmented)
				
				textfield_icon = ui.TextField()
				textfield_icon.name = 'icon url'
				x = segmented.x+segmented.width+10
				hs = segmented.height
				textfield_icon.frame = (x, absolute_y-5*hs, w-x-10, 5*hs)
				textfield_icon.corner_radius = hs/2
				textfield_icon.border_width = 2
				textfield_icon.border_color = 'red'
				textfield_icon.text_color = 'red'
				textfield_icon.font = ('<System-Bold>',20)
				textfield_icon.alignment = ui.ALIGN_CENTER
				textfield_icon.delegate = MyTextFieldDelegate()	# to intercept if typing in textfield
				textfield_icon.hidden = True
				c.container_view.add_subview(textfield_icon) # not cell for animation
				
	c.error_message = ui.Label(frame=(10,5,580,20))
	c.error_message.text_color = 'red'
	c.error_message.text = ''
	c.container_view.add_subview(c.error_message)	
	
	def go_back(sender):
		c.container_view['webview_view']['webview'].go_back()
		
	def go_forward(sender):
		c.container_view['webview_view']['webview'].go_forward()	
		
	def go_close(sender):
		c.container_view['webview_view']['copy_url'].hidden = True
		c.container_view['webview_view'].hidden = True
		c.container_view['icon url'].hidden = True
		c.container_view['shield'].hidden = True

	def go_copy(sender):	
		#print('go_copy')
		sender.field.text = c.container_view['webview_view']['address'].text
		sender.field.end_editing()
		go_close('simulated')

	# ui.View for url, nack, forward, webview
	v = ui.View()	
	v.name = 'webview_view'	
	v.background_color ='lightgray'
	v.frame = icon.frame
	v.hidden = True	
	c.container_view.add_subview(v)		
	wv = ui.WebView()
	wv.name = 'webview'
	d = 40
	wv.frame = (0,d,v.width,v.height-d)
	wv.delegate = MyTextFieldDelegate()
	v.add_subview(wv)	
	bi_forward = ui.Button(image=ui.Image.named('iob:ios7_arrow_forward_32'))
	bi_forward.frame = (v.width-d-10,0,d,d)
	bi_forward.action = go_forward
	v.add_subview(bi_forward)
	bi_back = ui.Button(image=ui.Image.named('iob:ios7_arrow_back_32'))
	bi_back.frame = (bi_forward.x-d-10,0,d,d)
	v.add_subview(bi_back)
	bi_back.action = go_back
	bi_copy = ui.Button(image=ui.Image.named('iob:ios7_copy_outline_32'))
	bi_copy.name = 'copy_url'
	bi_copy.frame = (bi_back.x-d-10,0,d,d)
	v.add_subview(bi_copy)
	bi_copy.action = go_copy
	bi_copy.hidden = True
	bi_close = ui.Button(image=ui.Image.named('iob:ios7_close_outline_32'))
	bi_close.frame = (10,0,d,d)
	bi_close.action = go_close
	v.add_subview(bi_close)
	tf = ui.TextField()
	tf.name = 'address'
	tf.clear_button_mode = 'while_editing'
	tf.keyboard_type = ui.KEYBOARD_URL
	x = bi_close.x + bi_close.width + 10
	tf.frame = (x,0,bi_copy.x-x-2*10,d)
	tf.delegate = MyTextFieldDelegate()
	v.add_subview(tf)

	c.textfield_active  = None	
	c.container_view.present('sheet')
	c.container_view.wait_modal()
	# Get rid of the view to avoid a retain cycle:
	c.container_view = None
	if c.was_canceled:
		return None

	return c.values
	
def main():
	console.clear()
	
	# Hide script
	w, h = ui.get_screen_size()
	disp = 'full_screen'
	back = MyView(w, h)
	back.background_color='white'
	back.present(disp, hide_title_bar=False)
	back.process()

# Protect against import	
if __name__ == '__main__':
	main()
