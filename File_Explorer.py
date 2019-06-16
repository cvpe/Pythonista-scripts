# coding: utf-8
# from omz FilePicker

import ui
import os
import sys
from objc_util import ObjCInstance, ObjCClass
from operator import attrgetter
import time
import unicodedata
import threading
import functools
import re
import datetime
import dialogs
import console
import ast
import editor
import ImageFont
import zipfile
import tarfile
import sqlite3

# replace ui._bind_action by mine because loading .pyui files generates
# warnings "could not bind action" due to missing actions code because
# the viewer only displays a view and does not need actions... 
def my_bind_action(v, action_str, f_globals, f_locals, attr_name='action'):
	if action_str:
		try:
			action = eval(action_str, f_globals, f_locals)
			if callable(action):
				setattr(v, attr_name, action)
			else:
				pass
				#sys.stderr.write('Warning: Could not bind action: Not callable\n')
		except Exception as e:
			pass
			#sys.stderr.write('Warning: Could not bind action: %s\n' % (e,))
			
ui._bind_action = my_bind_action

def my_hud_alert(my_back,msg,type,duration=1,keep_same_width=False):

	my_ui_view = my_back
	#if type == 'warning':
	#	my_back['msg_label'].text_color = 'black'	
	#	img = '⚠️'
	#elif type == 'success':
	#	my_back['msg_label'].text_color = 'green'	
	#	img = '✅'
	#elif type == 'error':
	#	my_back['msg_label'].text_color = 'red'	
	#	img = '❌'
	#elif type == 'ok':
	#	my_back['msg_label'].text_color = 'black'	
	#	img = '✅'
	#else:
	#	my_back['msg_label'].text_color = 'blue'	
	#	img = 'ℹ'
	alert_types = {'warning': ('black', '⚠️'),
               'success': ('green', '✅'),
               'error': ('red', '❌'),
               'ok': ('black', '✅')}
	(my_back['msg_label'].text_color, img) = alert_types.get(type, ('blue', 'ℹ'))
		
	my_back['msg_label'].text = msg+' '+img+' '
	my_back['msg_label'].line_break_mode = ui.LB_WORD_WRAP
	my_back['msg_label'].number_of_lines = 0
	
	font = ImageFont.truetype('Courier-Bold',20)
	lines = my_back['msg_label'].text.split('\n')
	h_txt = 0
	w_txt = 0
	for line in lines:
		w_line,h_line = font.getsize(line)
		if w_line > w_txt:
			w_txt = w_line
		h_txt = h_txt + 32
	if w_txt > (my_back.width-20):
		w_txt = my_back.width-20

	if not keep_same_width:		
		my_back['msg_label'].width = w_txt + 8
	my_back['msg_label'].height = h_txt + 8
	my_back['msg_label'].x = (my_back.width  - my_back['msg_label'].width )/2
	my_back['msg_label'].y = (my_back.height - my_back['msg_label'].height)/2

	my_back['msg_label'].border_width = 2
	my_back['msg_label'].border_color = my_back['msg_label'].text_color

	#my_back['msg_label'].corner_radius = my_back['msg_label'].height/2
	my_back['msg_label'].hidden = False
	my_back['msg_label'].bring_to_front()	
	
	if duration == 0:
		return							# let msg displayed
	
	time.sleep(duration)	
	my_back['msg_label'].hidden = True	

class my_thread_scan(threading.Thread):
	global picker,files,folders,folder_nodes
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		picker.view['progress_bar'].hidden = False
		self.loc_dirs('Documents/')
		picker.view['progress_bar'].hidden = True
		picker.view.name = 'File Explorer ['+str(len(files)) + ' folders/files]'
		picker.view.right_button_items[0].enabled = True		# search
		picker.table_view.reload()
		# If we expand a folder during the scan thread, the values size/number
		# could be incorrect, because the scan was not yet ended.
		# Thats's why we memorize the TreeNodes of the folders during their
		# creation, so now, after the scan, we can set their sub-titles with
		# correct values.
		for folder_node in folder_nodes:
			# Folder is a Folder TreeNode
			path = folder_node.path
			i = path.find('Documents/')
			if i == -1:									# path = ......./Documents
				folder = 'Documents'
			else:
				folder = path[i:]
			folder = unicodedata.normalize('NFC', folder)
			if folder[-1] != '/':
				folder = folder + '/'
			if folder in folders:
				folder_node.subtitle = human_size(folders[folder][1]) + ' [' +  str(folders[folder][0]) + ' files, ' + str(folders[folder][2]) + ' folders]'

	#@ui.in_background		
	def loc_dirs(self,path_in):
		try:
			path = unicodedata.normalize('NFC', path_in)
			folders[path] = [0,0,0]
			file_path = os.path.expanduser('~/'+path)
			os.chdir(file_path)
			filelist = os.listdir(file_path)
			for file in filelist:
				f_full = file_path + file
				#print(path,file)
				if os.path.isdir(f_full):
					self.loc_dirs(path+file+'/') # explore it
				else:					
					loc_size = os.path.getsize(f_full)
					loc_mtime = os.path.getmtime(f_full)
					i = f_full.index('Documents')
					f = f_full[i:]
					f = unicodedata.normalize('NFC', f)
					files[f] = [loc_size,loc_mtime]
					n,s,nf = folders[path]
					n += 1
					s += loc_size
					folders[path] = [n,s,nf]
					if len(files) % 100 == 0:
						picker.view['progress_bar'].width = picker.view.width * len(files)/26000
		except Exception as e:
			print('exception: ',e)
		os.chdir(os.path.pardir)				# parent directory = '.' in IOS
		path_up = os.getcwd()						# current directory
		i = path_up.find('Documents/')
		if i == -1:									 # path = ......./Documents
			if path == 'Documents/':
				# if we don't return, n-s-nf of Documents would be doubled
				return
			#print(path,path_up)
			path_up = 'Documents/'
		else:
			path_up = path_up[i:] + '/'
		path_up = unicodedata.normalize('NFC', path_up)
		if path_up not in folders:
			folders[path_up] = [0,0,0]
		nt,st,nft = folders[path_up]
		n,s,nf = folders[path]
		nt += n
		st += s
		nft += nf + 1
		folders[path_up] = [nt,st,nft]
		return
	
def myform_dialog(title='', fields=None,sections=None, done_button_title='Done',cover=None,delete_button=False,add_button=False):
	global c,cover_file,cover_image,file_content
	sections = [('', fields)]
	c = dialogs._FormDialogController(title, sections, done_button_title=done_button_title)
	
	c.container_view.frame = (0,0,640,620) # standard = 540,620

	if isinstance(cover,str):
		# Add a Quicklook button
		cover_file = cover
		quicklook_button = ui.ButtonItem()
		#quicklook_button.title = 'Quicklook'
		quicklook_button.tint_color = 'blue'
		quicklook_button.image = ui.Image.named('iob:ios7_eye_outline_32')
		quicklook_button.action = quicklook_button_action
		c.container_view.right_button_items = c.container_view.right_button_items + (quicklook_button,)	
		# Add a Open_In button
		open_in_button = ui.ButtonItem()
		#open_in_button.title = 'Open In'
		open_in_button.tint_color = 'blue'
		open_in_button.image = ui.Image.named('iob:ios7_upload_outline_32')
		open_in_button.action = open_in_button_action
		c.container_view.right_button_items += (open_in_button,)			
		
	if delete_button:
		# Add a delete button
		delete_button = ui.ButtonItem()
		delete_button.tint_color = 'red'
		delete_button.image = ui.Image.named('iob:ios7_trash_outline_32')
		delete_button.action = delete_button_action
		# right buttons is a tuple, the way to add an element is "+(element,)"
		c.container_view.right_button_items += (delete_button,)
		
	if add_button:
		# Add a add button
		add_button = ui.ButtonItem()
		add_button.image = ui.Image.named('iob:ios7_plus_outline_32')
		#add_button.tint_color = 'red'
		add_button.action = add_button_action
		# right buttons is a tuple, the way to add an element is "+(element,)"
		c.container_view.right_button_items += (add_button,)

				
	c.was_canceled = True		# set False by done_action in FormDialogController
	c.was_deleted  = False		
	c.was_added    = False	
	
	y = 35
	for s in c.cells:
		y += sum(cell.height for cell in s)
		#for cell in s:
		#	y += cell.height
	if cover != None:

		w = c.container_view.width
		h = c.container_view.height - y
		x = 0
		cover_image = None
		if isinstance(cover,str):
			i = cover.rfind('.')
			ext = cover.lower()[i:]
			if ext in ['.gif','.htm','.html','.webarchive','.pdf','.mov','.mp3','.wav','.m4a','.mp4','.avi','.doc','.docx','.xls','.xlsx','.pps','.ppt','.gmap']:
				cover_image = ui.WebView()
				#cover_image.touch_enabled = False
				cover_image.frame = (x,y,w,h)
				if ext in ['.gif','.htm','.html','.webarchive','.pdf','.mov','.mp3','.wav', '.m4a', '.mp4','.avi','.doc','.docx','.xls','.xlsx','.pps','.ppt']:
					cover_image.load_url(os.path.abspath(cover))
				elif ext in ['.gmap']:
					gmap_rec = ''
					fil = open(cover,'r',encoding='utf-8')
					for rec in fil:
						gmap_rec += rec
					fil.close()
					# {"url": url,"doc_id: doc_id,"email": email,"resource_id": id}	
					gmap_dict = ast.literal_eval(gmap_rec) 	# convert str -> dict
					url = gmap_dict['url']
					cover_image.load_url(url)
			elif ext in ['.txt','.dat','.infos','.py','.md','.zip','.gz','.mht','.mhtml','.vcf','.ics','.db']:
				cover_image = ui.TextView()
				cover_image.frame = (x,y,w,h)
				cover_image.editable = False
				cover_image.scroll_enabled = True
				t = ''
				if ext in ['.txt','.dat','.infos','.py','.md','.vcf','.ics']:
					fil = open(cover,'r',encoding='utf-8')
					for rec in fil:
						t += rec
					fil.close()
					file_content = t
					# add an Edit button
					edit_button = ui.ButtonItem()
					edit_button.tint_color = 'blue'
					edit_button.title = 'Edit'
					edit_button.image = ui.Image.named('iob:ios7_compose_outline_32')
					edit_button.action = edit_button_action
					c.container_view.right_button_items = c.container_view.right_button_items + (edit_button,)
					# Message Label for my_hud_alert
					msg = ui.Label(name='msg_label')
					msg.frame = (x+20,y+(h-32)/2,w-40,32)
					msg.bg_color = 'lightgray'
					msg.border_color = 'red'
					msg.border_width = 2
					msg.alignment = ui.ALIGN_CENTER
					msg.font= ('Courier-Bold',20)
					msg.text_color = 'red'
					msg.hidden = True
					c.container_view.add_subview(msg)
				elif ext in ['.mht','.mhtml']:
					fil = open(cover,'r',encoding='utf-8',errors='replace')
					for rec in fil:
						t += rec
					fil.close()
				elif ext in ['.db']:
					try:
						conn = sqlite3.connect(cover)
						for line in conn.iterdump():
							t += line + '\n'
						conn.close()
					except Exception as e:
						t = str(e)
				elif ext in ['.zip']:
					try:
						zip = zipfile.ZipFile(cover,mode='r')
						# loop on zip members names
						for zip_file in zip.namelist():
							t += zip_file + '\n'
						zip.close()
					except Exception as e:
						t = str(e)
				elif ext in ['.gz']:
					try:
						tar = tarfile.open(cover,mode='r')
						# loop on tar members names
						for tar_file in tar.getnames():
							t += tar_file + '\n'
						tar.close()
					except Exception as e:
						t = str(e)
				cover_image.text = t
				# cover_image is a TextView
				# Add some particular buttons to scroll top/bottom
				# Add a Bottom button
				bot_button = ui.ButtonItem()
				bot_button.title = '⬇️'
				bot_button.tint_color = 'blue'
				bot_button.action = bot_button_action
				c.container_view.right_button_items = c.container_view.right_button_items + (bot_button,)		
				# Add a Top button
				top_button = ui.ButtonItem()
				top_button.title = '⬆️'
				top_button.tint_color = 'blue'
				top_button.action = top_button_action
				c.container_view.right_button_items = c.container_view.right_button_items + (top_button,)		
			elif ext in ['.pyui']:
				cover_image = ui.load_view(cover)
				cover_image.frame = (x,y,w,h)
			elif ext in ['.png','.jpg','.jpeg','.bmp','.tif','.tiff']:
				# to have an image clickable, we need to create a button
				# and to set the image as subview of the button
				# I've tried a button alone but the image as image or background_image
				# was compressed...
				cover_image = ui.Button(frame=(x,y,w,h))
				cover_image.action = quicklook_button_action
				cover_image1 = ui.ImageView(frame=(0,0,w,h))
				cover_image1.content_mode = ui.CONTENT_SCALE_ASPECT_FIT
				cover_image1.image = ui.Image.named(cover)
				cover_image.add_subview(cover_image1)
			else:
				cover_image = ui.Label()
				cover_image.frame = (x,y,w,h)
				cover_image.frame = (x+20,y+(h-32)/2,w-40,32)
				cover_image.alignment = ui.ALIGN_CENTER
				cover_image.font = ('Courier-Bold',20)
				cover_image.text_color = 'red'
				cover_image.text = 'No available viewer'
				
		if cover_image:
			c.container_view.add_subview(cover_image)	

	# we could access textfields as subview cell.content_view['name']		
	for i in range(0,len(c.cells[0])):			# loop on rows of section 0
		cell = c.cells[0][i]									# ui.TableViewCell of row i
		# some fields types are subviews of the cell:
		#   text,number,url,email,password,switch
		if len(cell.content_view.subviews) > 0:
			tf = cell.content_view.subviews[0] 	# ui.TextField of value in row
			if tf.name == 'size':								# tf.name is the key
				tf.enabled = False								# so field can't ne modified
				cell.text_label.text = 'Size'
			elif tf.name == 'ctime':						# tf.name is the key
				tf.enabled = False								# so field can't be modified
				cell.text_label.text = 'Creation'
			elif tf.name == 'mtime':						# tf.name is the key
				tf.enabled = False								# so field can't be modified
				cell.text_label.text = 'Modification'
			elif tf.name == 'folder':						# tf.name is the key
				tf.enabled = False								# so field can't be modified
				cell.text_label.text = 'Folder'
			elif tf.name == 'sub-folder':				# tf.name is the key
				tf.enabled = True									# so field can't be modified
				cell.text_label.text = 'Sub-folder'
			elif tf.name == 'file':							# tf.name is the key
				tf.enabled = True									# so field can't be modified
				cell.text_label.text = 'File'
			elif tf.name == 'file_or_folder':							# tf.name is the key
				tf.enabled = True									# so field can't be modified
			elif tf.name == 'name':							# tf.name is the key
				tf.enabled = True									# so field can't be modified
				cell.text_label.text = 'Name'

	c.container_view.present('sheet')
	c.container_view.wait_modal()
	ui.cancel_delays()						# if we close when msg delay still active
	# Get rid of the view to avoid a retain cycle
	c.container_view = None
	if c.was_canceled:
		return None
	if c.was_deleted:
		return 'delete'
	if c.was_added:
		return 'add'
	return c.values
		
def delete_button_action(sender):
	global c
	c.was_canceled = False
	c.was_added    = False
	c.was_deleted  = True
	c.container_view.close()
	
def add_button_action(sender):
	global c
	c.was_canceled = False
	c.was_deleted  = False
	c.was_added    = True
	c.container_view.close()
	
def quicklook_button_action(sender):
	global cover_file
	console.quicklook(cover_file)
	
def open_in_button_action(sender):
	global cover_file
	console.open_in(cover_file)
	
def top_button_action(sender):
	global cover_image
	cover_image.content_offset = (0,0)
		
def bot_button_action(sender):
	global cover_image
	y = max(0, cover_image.content_size[1] - cover_image.height)
	cover_image.content_offset = (0,y)
	
def edit_button_action(sender):
	global c,cover_image,cover_file,file_content
	def hide_msg():
		c.container_view['msg_label'].hidden = True
	def set_msg(msg,duration):
		c.container_view['msg_label'].hidden = False
		c.container_view['msg_label'].text = msg
		c.container_view['msg_label'].bring_to_front()
		ui.delay(hide_msg,duration)
	if sender.title == 'Edit':
		cover_image.editable = True
		cover_image.bring_to_front()
		sender.title = ''
		sender.image = ui.Image.named('iob:log_in_32')
	else:
		if cover_image.text == file_content:
			 set_msg('File unchanged, save canceled',2)
		else:
			# Save file
			file_content = cover_image.text
			fil = open(cover_file,'wt',encoding='utf-8')
			fil.write(file_content)
			fil.close()
			c.was_canceled = False
			c.was_deleted = False
			c.container_view.close()
			
def my_list_popover(elements,val=None,x=None,y=None,color='white',title=None):
	class my_list(ui.View):
		def __init__(self,selected):

			# ListDataSource for clients TableView
			elements_lst = ui.ListDataSource(items=lst)
			# ListDataSource has no attribute "name"
			elements_lst.delete_enabled = False
			elements_lst.move_enabled = False
			elements_txt = ui.TableView(name='elements_txt')
			elements_txt.allows_multiple_selection = False
			elements_txt.text_color = 'black'
			elements_txt.font= ('Courier',16)
			elements_txt.row_height = elements_txt.font[1] * 2
			h = len(lst) *	elements_txt.row_height
			font = ImageFont.truetype('Courier',16)
			w = 0
			for element in lst:
				w_ele,h_ele = font.getsize(element)
				if w_ele > w:
					w = w_ele
			w += 32
			elements_txt.content_size = (w,h)
			h_max = h_screen/2
			if h > h_max:
				h = h_max
			w_max = w_screen - 20
			if w > w_max:
				w = w_max
			elements_txt.frame = (4,4,w,h)	
			#elements_txt.border_color = 'blue'
			#elements_txt.border_width = 3
			elements_txt.data_source = elements_lst
			elements_txt.data_source.tableview_cell_for_row = self.tableview_cell_for_row
			if selected >= 0:
				elements_txt.selected_row = (0,selected)
						
			elements_txt.delegate  = self
			self.add_subview(elements_txt)	
			self.width = elements_txt.width   + 8
			self.height = elements_txt.height + 8
			#self.corner_radius = 20
			#self.border_color = 'blue'
			#self.border_width = 2
			self.background_color = color
			if title:#and multiple:
				# title bar displayed in multiple
				self.name = title
				
		def tableview_did_select(self, tableview, section, row):
			# Called when a row was selected
			lst.append(lst[row])
			v.close()
			
		def tableview_cell_for_row(self, tableview, section, row):
			cell = ui.TableViewCell()
			selected_cell = ui.View()
			selected_cell.border_color = 'black'
			selected_cell.border_width = 2
			selected_cell.corner_radius = 10
			data = tableview.data_source.items[row]
			selected_cell.bg_color = 'cornflowerblue'
			cell.selected_background_view = selected_cell
			cell.text_label.text = data
			cell.text_label.alignment = ui.ALIGN_LEFT
			cell.text_label.text_color = 'black'
			cell.bg_color = color
			return cell		
	
	lst = []
	i = 0
	selected = -1
	if type(elements) is dict:
		elements_list = sorted(elements.keys())
	elif type(elements) is list:
		elements_list = elements
	for element in elements_list:
		lst.append(element)
		if element == val:
			selected = i
		i += 1
	w_screen,h_screen = ui.get_screen_size()
	if not x:
		x = int(w_screen/2)
	if not y:
		y = int(h_screen/2)
	v = my_list(selected)
	# lst already copied into elements_lst, thus we can change lst
	# to contain iniital value in case of tap outside
	if selected == -1:
		lst.append('')
	else:
		lst.append(lst[selected])
	if title:
		v.present('popover',popover_location=(x,y),hide_title_bar=False)
	else:
		v.present('popover',popover_location=(x,y),hide_title_bar=True)
	v.wait_modal()
	return lst[len(lst)-1]	# return last
	
def human_size(size_bytes):
	# Helper function for formatting human-readable file sizes
	# http://stackoverflow.com/a/6547474
	if size_bytes == 1:
		return "1 byte"
	suffixes_table = [('bytes',0),('KB',0),('MB',1),('GB',2),('TB',2), ('PB',2)]
	num = float(size_bytes)
	for suffix, precision in suffixes_table:
		if num < 1024.0:
			break
		num /= 1024.0
	if precision == 0:
		formatted_size = "%d" % num
	else:
		formatted_size = str(round(num, ndigits=precision))
	return "%s %s" % (formatted_size, suffix)

class TreeNode (object):
	def __init__(self):
		self.expanded = False
		self.children = None
		self.leaf = True
		self.title = ''
		self.subtitle = ''
		self.icon_name = None
		self.level = 0
		self.btn = None

	def expand_children(self):
		self.expanded = True
		self.children = []

	def collapse_children(self):
		self.expanded = False

	def __repr__(self):
		return '<TreeNode: "%s"%s>' % (self.title, ' (expanded)' if self.expanded else '')

class FileTreeNode (TreeNode):
	global files,folders,script_path,folder_nodes
	def __init__(self, path):
		TreeNode.__init__(self)
		# path ......../Documents
		#      ......../Documents/folder/
		#      ......../Documents/folder/file.ext
		#print(path)
		self.path = path
		self.title = os.path.split(path)[1]
		is_dir = os.path.isdir(path)
		self.leaf = not is_dir
		ext = os.path.splitext(path)[1].lower()
		if is_dir:
			self.icon_name = 'Folder'
		elif ext == '.epub':
			self.icon_name = 'emj:Blue_Book'
		elif ext in ('.txt','.dat','.md','.infos'):
			self.icon_name = 'emj:Memo'
		elif ext == '.db':
			self.icon_name = 'icon_sql.png'
		elif ext in ('.mp3','.wav','.m4a'):
			self.icon_name = 'emj:Musical_Note'
		elif ext in ('.avi','.mov','mkv','.mp4','.mpg','.mpeg'):
			self.icon_name = 'icon_movie.png'
		elif ext in ('.zip','.rar','.7z','.gz'):
			self.icon_name = 'icon_zip.png'
		elif ext in ('.htm','.html','.webarchive','.mht','.mhtml'):
			self.icon_name = 'icon_html.png'
		elif ext in ('.odf','.odt','.ods','.odp','.odg','.odc','.odb','.odi','.odm'):
			self.icon_name = 'icon_open_office.png'
		elif ext in ('.xls','.xlsx','.numbers'):
			self.icon_name = 'icon_numbers.png'
		elif ext in ('.pps','.ppt'):
			self.icon_name = 'icon_powerpoint.png'
		elif ext in ('.doc','.docx'):
			self.icon_name = 'icon_word.png'
		elif ext == '.ics':
			self.icon_name = 'icon_calendar.png'
		elif ext == '.vcf':
			self.icon_name = 'icon_contacts.png'
		elif ext == '.pdf':
			self.icon_name = 'icon_pdf.png'
		elif ext == '.psafe3':
			self.icon_name = 'emj:Lock_1'
		elif ext == '.py':
			self.icon_name = 'FilePY'
		elif ext == '.pyui':
			self.icon_name = 'FileUI'
		elif ext == '.gmap':
			self.icon_name = 'icon_gmap.png'
		elif ext in ('.png', '.jpg', '.jpeg', '.gif','.bmp','.tif','.tiff'):
			self.icon_name = 'icon_image.png'
		else:
			self.icon_name = 'FileOther'
		# As a thread runs for scanning local files, current dir is often changed
		# and the icon is not found when displayed
		if self.icon_name[0:5] == 'icon_':
			self.icon_name = script_path + self.icon_name
		if is_dir:
			# Folder
			folder_nodes.append(self)					# store folders TreeNodes
			i = path.find('Documents/')
			if i == -1:									 # path = ......./Documents
				folder = 'Documents'
			else:
				folder = path[i:]
			folder = unicodedata.normalize('NFC', folder)
			if folder[-1] != '/':
				folder += '/'
			#print('FileTreeNode:',folder)
			# folder Documents/
			#        Documents/folder/
			if folder in folders:
				self.subtitle = human_size(folders[folder][1]) + ' [' +  str(folders[folder][0]) + ' files, ' + str(folders[folder][2]) + ' folders]'
			#else:
				#self.subtitle = '... [... files, ... folders]'
		else:
			# File
			self.subtitle = human_size((os.stat(self.path).st_size))
			mt = os.path.getmtime(self.path)
			self.subtitle += '  [' + datetime.datetime.fromtimestamp(mt).strftime('%d/%m/%Y %H:%M:%S') + ']'

	@property
	def cmp_title(self):
		return self.title.lower()
			
	def expand_children(self):
		if self.children is not None:
			self.expanded = True
			return
		files_dir = os.listdir(self.path)
		children = []
		t = 'Pythonista3/'
		for filename in files_dir:
			#print(self.path,filename)
			if filename.startswith('.'):
				continue
			# as we start from ~/, we need to only keep Documents
			if self.path[-len(t):] == t:
				if filename != 'Documents':
					continue
			full_path = os.path.join(self.path, filename)
			node = FileTreeNode(full_path)
			node.level = self.level + 1
			children.append(node)
		self.expanded = True
		self.children = sorted(children, key=attrgetter('leaf', 'cmp_title'))

class TreeDialogController (object):
	global files,folders,folder_nodes
	def __init__(self, root_node, allow_multi=False):
		self.allow_multi = allow_multi
		self.selected_entries = None
		
		# TableView for Tree
		self.table_view = ui.TableView()
		# it seems that width,height are not used but the y=2 yes...
		self.table_view.frame = (0,2, 500, 500) # some pixels for progress bar
		self.table_view.data_source = self
		self.table_view.delegate = self
		self.table_view.flex = 'WH'
		#self.table_view.allows_multiple_selection = True
		self.table_view.tint_color = 'gray'
		
		# View for presenting
		self.view = ui.View(frame=self.table_view.frame)
		self.view.background_color = 'white'			# for progress bar 
		self.view.add_subview(self.table_view)
		self.view.name = root_node.title
		self.root_node = root_node
		self.entries = []
		self.flat_entries = []
		
		# ButtonItem for search		
		search_button = ui.ButtonItem()
		#search_button.title = 'Search'
		search_button.tint_color = 'green'
		search_button.image = ui.Image.named('iob:ios7_search_32')
		search_button.action = self.search_button_action
		search_button.enabled = False
		
		self.view.right_button_items = [search_button,]
		
		# TextField for search
		self.screen_width,self.screen_height = ui.get_screen_size()
		search_text = ui.TextField(name='search_text')
		search_text.text = ''
		search_text.width = self.screen_width - 20
		search_text.height = 32
		search_text.x = (self.screen_width - search_text.width)/2
		search_text.y = 10
		search_text.border_color = 'blue'
		search_text.border_width = 1
		search_text.text_color = 'blue'
		search_text.keyboard_type = ui.KEYBOARD_DEFAULT
		search_text.autocapitalization_type = ui.AUTOCAPITALIZE_NONE
		search_text.autocorrection_type = False
		search_text.alignment = ui.ALIGN_LEFT
		search_text.clear_button_mode = 'while_editing'
		search_text.font= ('Helvetica',20)
		search_text.delegate = self
		search_text.hidden = True
		self.view.add_subview(search_text)
		self.search_normalized = ''
		
		# ListDataSource for search TableView
		self.elements_lst = ui.ListDataSource(items=[])
		self.elements_lst.delete_enabled = False
		self.elements_lst.move_enabled = False
		found_files = ui.TableView(name='found_files')
		found_files.allows_multiple_selection = False
		found_files.text_color = 'black'
		found_files.font= ('Courier',12)
		found_files.row_height = 50
		found_files.x = search_text.x
		found_files.y = search_text.y + search_text.height + 10
		found_files.width = search_text.width
		found_files.height = self.screen_height - 130
		found_files.border_color = 'blue'
		found_files.border_width = 3
		found_files.data_source = self.elements_lst
		found_files.delegate = self
		found_files.hidden = True
		self.view.add_subview(found_files)
		
		# Thin Label for progress bar
		progress_bar = ui.Label(name='progress_bar')
		progress_bar.frame = (0,0,0,2)
		progress_bar.background_color = 'blue'
		progress_bar.text = ''	
		progress_bar.hidden = True
		self.view.add_subview(progress_bar)	
		
		# Message Label for my_hud_alert
		msg = ui.Label(name='msg_label')
		msg.background_color=(0.00, 0.50, 1.00, 0.5)	
		msg.bg_color = 'bisque'		
		msg.alignment = ui.ALIGN_CENTER
		msg.font= ('Courier-Bold',20)
		msg.hidden = True
		self.view.add_subview(msg)
		
		self.expand_root()
		
	def search_button_action(self,sender):
		if self.view['search_text'].hidden:	
			self.table_view.y = self.view['search_text'].y + 		self.view['search_text'].height + 2
			self.view['search_text'].hidden = False
			if self.search_normalized != '':
				self.view['found_files'].hidden = False
			self.view['search_text'].begin_editing()
		else:
			self.table_view.y = 2
			self.view['search_text'].hidden = True
			self.view['found_files'].hidden = True
		
	def textfield_did_change(self, field):
		# search text did change, we force tableview to reload because
		# the tableview_cell_for_row code checks the row title bs search text
		txt = field.text
		if txt == '':
			self.view['found_files'].hidden = True
			return
		txt = unicodedata.normalize('NFKD', txt).encode('ASCII', 'ignore')
		self.search_normalized = str(txt,'utf-8').upper()
		lst = []
		for files_key in files.keys():
			file = files_key		#[10:]			 # Remove 'Documents/'
			file_normalized = unicodedata.normalize('NFKD', file).encode('ASCII', 'ignore')
			file_normalized = str(file_normalized,'utf-8').upper()
			if self.search_normalized in file_normalized:
				dict = {'title':file}
				#dict = {'title':file,'image':ui.Image.named('FileOther')}
				lst.append(dict)
		for folder_key in folders.keys():
			folder = folder_key		#[10:]			 # Remove 'Documents/'
			folder_normalized = unicodedata.normalize('NFKD', folder).encode('ASCII', 'ignore')
			folder_normalized = str(folder_normalized,'utf-8').upper()
			if self.search_normalized in folder_normalized:
				#dict = {'title':folder}
				dict = {'title':folder,'image':ui.Image.named('Folder')}
				lst.append(dict)	
		lst = sorted(lst,key=lambda dict:dict['title'])
		self.elements_lst.items = lst
		h_max = self.screen_height - 130
		h = self.view['found_files'].row_height * len(self.elements_lst.items)
		if h > h_max:
			h = h_max
		self.view['found_files'].height = h
		self.view['found_files'].hidden = False
		#self.table_view.reload()

	def expand_root(self):
		self.root_node.expand_children()
		self.entries = self.root_node.children
		self.flat_entries = self.entries
		self.table_view.reload()
	
	def flatten_entries(self, entries, dest=None):
		dest = dest or []
		for entry in entries:
			dest.append(entry)
			if not entry.leaf and entry.expanded:
				self.flatten_entries(entry.children, dest)
		return dest
		
	def rebuild_flat_entries(self):
		self.flat_entries = self.flatten_entries(self.entries)

	def tableview_number_of_rows(self, tv, section):
		if tv == self.view['found_files']:
			return
		return len(self.flat_entries)

	def tableview_cell_for_row(self, tv, section, row):
		if tv == self.view['found_files']:
			return
		cell = ui.TableViewCell()
		entry = self.flat_entries[row]
		level = entry.level - 1
		image_view = ui.ImageView(frame=(44 + 20*level, 5, 34, 34))
		label_x = 44+34+8+20*level
		#label_w = cell.content_view.bounds.width - label_x - 8 
		label_w = ui.get_screen_size()[0] - label_x					# cvp: test
		if not entry.leaf and not entry.subtitle:
			# Folder which has not yet a subtitle with its infos
			folder = entry.path
			i = folder.rfind('Documents/')
			if i == -1:									 # path = ......./Documents
				folder = 'Documents'
			else:
				folder = folder[i:] +'/'
			if folder[-1] != '/':
				folder += '/'
			if folder in folders:
				entry.subtitle = human_size(folders[folder][1]) + ' [' +  str(folders[folder][0]) + ' files, ' + str(folders[folder][2]) + ' folders]'
				self.flat_entries[row] = entry		# store it
		if entry.subtitle:
			label_frame = (label_x, 0, label_w, 26)
			sub_label = ui.Label(frame=(label_x, 26, label_w, 14))
			sub_label.font = ('<System>', 12)
			sub_label.text = entry.subtitle
			sub_label.text_color = '#999'
			cell.content_view.add_subview(sub_label)
		else:
			label_frame = (label_x, 0, label_w, 44)
		label = ui.Label(frame=label_frame)
		label.font = ('<System>', 16) if entry.subtitle else ('<System>', 18)
		label.text = entry.title
		label.flex = 'W'
		label.text_color = 'black'		
		if self.search_normalized != '':		
		#if not self.view['search_text'].hidden and self.search_normalized != '':
			# Search in progress
			tit = unicodedata.normalize('NFKD', label.text).encode('ASCII', 'ignore')
			tit = str(tit,'utf-8').upper()	
			if self.search_normalized in tit:
				label.text_color = 'blue'				
		cell.content_view.add_subview(label)
		#if entry.leaf and not entry.enabled:
			#label.text_color = '#999'
		cell.content_view.add_subview(image_view)
		if not entry.leaf:
			# Folder
			#label.font = ('<System-Bold>',label.font[1])	# folder -> bold
			has_children = entry.expanded
			btn = ui.Button(image=ui.Image.named('CollapseFolder' if has_children else 'ExpandFolder'))
			btn.frame = (20*level, 0, 44, 44)
			btn.action = self.expand_dir_action
			cell.content_view.add_subview(btn)
			entry.btn = btn 										# store button in entry
			self.flat_entries[row] = entry			# store modified entry
			cell.accessory_type = 'detail_button'
		if entry.icon_name:
			path = entry.path
			i = path.rfind('.')
			ext = path.lower()[i:]
			if ext in ['.png','.jpg','.jpeg','.bmp','.gif','.tif','.tiff']:
				image_view.image = ui.Image.named(entry.path)
			else:
				image_view.image = ui.Image.named(entry.icon_name)
		else:
			image_view.image = None
			
		# Only show selected of file, not folder
		selected_cell = ui.View()
		if entry.leaf:
			# File
			selected_cell.bg_color = 'lightgray'
		else:
			# Folder
			selected_cell.bg_color = self.view.background_color
		cell.selected_background_view = selected_cell
		
		cell.selectable = True
		return cell
		
	def row_for_view(self, sender):
		'''Helper to find the row index for an 'expand' button'''
		cell = ObjCInstance(sender)
		while not cell.isKindOfClass_(ObjCClass('UITableViewCell')):
			cell = cell.superview()
		return ObjCInstance(self.table_view).indexPathForCell_(cell).row()

	def expand_dir_action(self, sender):
		'''Invoked by 'expand' button'''
		row = self.row_for_view(sender)
		entry = self.flat_entries[row]
		sender.image = ui.Image.named('ExpandFolder' if entry.expanded else 'CollapseFolder')
		self.toggle_dir(row)

	def toggle_dir(self, row):
		'''Expand or collapse a folder node'''
		# Start thread to scan all local files
		entry = self.flat_entries[row]
		if entry.expanded:
			entry.collapse_children()
			old_len = len(self.flat_entries)
			self.rebuild_flat_entries()
			num_deleted = old_len - len(self.flat_entries)
			deleted_rows = range(row + 1, row + num_deleted + 1)
			self.table_view.delete_rows(deleted_rows)
		else:
			self.do_expand(entry, row)

	def do_expand(self, entry, row):
		#Actual folder expansion
		entry.expand_children()
		old_len = len(self.flat_entries)
		self.rebuild_flat_entries()
		num_inserted = len(self.flat_entries) - old_len
		inserted_rows = range(row + 1, row + num_inserted + 1)
		self.table_view.insert_rows(inserted_rows)

	def tableview_did_select(self, tv, section, tv_row):
		if tv == self.view['found_files']:
			# TableView of found files/folders
			# Simulate search button to force "end of search"
			self.search_button_action('?')
			dict = self.elements_lst.items[tv_row]
			file_folder = dict['title']
			#print('select:',file_folder)
			if file_folder[-1] == '/':
				# folder ex: Mes donnees/Budget/
				folder = file_folder
			else:
				# file ex: Mes donnees/Budget/file.ext
				i = file_folder.rfind('/')
				folder = file_folder[:i+1]									# remove file name
			folder_norm = unicodedata.normalize('NFC', folder)
			#print('select folder:',folder_norm)
			# ex: Mes donnees/Budget/
			i = folder_norm.find('/')
			# expand all folders of tree containing the selected file or folder
			# loop on folders in tree, from top to down
			while i>= 0:
				is_folder_in_node = folder_norm[:i]
				#print(is_folder_in_node)
				node = None
				for folder_node in folder_nodes:
					path_node = folder_node.path
					if unicodedata.normalize('NFC', path_node)[-len(is_folder_in_node):] == is_folder_in_node:
						#print(is_folder_in_node,'in',path_node)
						node = folder_node
						break
				if node:
					# already in nodes
					# check if folder not already expanded
					if not node.expanded:
						# folder not yet expanded
						# find row of this folder, 
						# expand it but without displaying it
						row = self.flat_entries.index(node)
						self.toggle_dir(row)
				else:
					# not yet in nodes, 
					# would not be possible as we begin from top folder
					pass
				i = folder_norm.find('/',i+1)	
			# find row, needed if delete would pressed on the formdialog
			# passed tv_row is the row in the found tableview, not in the
			# nodes tableview
			# if folder, the last node we did find is the node of the folder
			# if file, we still need to search its node
			if file_folder[-1] != '/':
				# file
				file_norm = unicodedata.normalize('NFC', file_folder)
				#print('select file:',file_norm)
			else:
				# folder
				file_norm = folder_norm
			row = 0
			for node in self.flat_entries:
				path_node = node.path
				if not node.leaf:
					# node of a folder, ad a / at end for comparing
					path_node += '/'
				#print(path_node)
				if unicodedata.normalize('NFC', path_node)[-len(file_norm):] == file_norm:
					#print(path_node)
					break
				row += 1
			#print(node.title,row)
			# Force scroll so tje selected row is on screen
			# I don't know why but self.table_view.row_height = 1!!!
			self.table_view.content_offset = (0,row*44)
			# select element
			self.tableview_select(self.table_view,node,row)			
			return
		# TableView of nodes
		row = tv_row
		selected = [self.flat_entries[i[1]] for i in self.table_view.selected_rows]
		e = selected[0]
		if not e.leaf:
			# Folder
			#	Simulate pressed expand/collapse button of selected row	
			self.expand_dir_action(e.btn)		
			return	
		self.tableview_select(tv,e,row)
		
	def tableview_accessory_button_tapped(self, tv, section, row):
		# Called when the accessory (ex: info) tapped
		if tv == self.view['found_files']:
			return
		e = self.flat_entries[row]
		self.tableview_select(tv,e,row)

	# Mandatory else my_formdialog abends
	@ui.in_background			
	def tableview_select(self,tv,e,row):
		# Called by a file select or a folder info tapped
		path = e.path							# ex: ..../Documents
															#     ..../Documents/MesApps
		#print('e.path=',e.path)
		t = 'Documents/'
		i = path.find(t)
		if i < 0:
			# we are in ~/
			folder = 'Documents'		# ex: Documents
		else:
			# we are under Documents/
			folder = path[i:]				# ex: Documents/MesApps
		folder = unicodedata.normalize('NFC', folder)
		file_name = e.title
		fields = []
		t = '_'*13				# string of chars to align values
		
		if not e.leaf:
			# Folder
			title = 'Dossier'
			i = folder.find(file_name)
			folder_up = folder[:i]	# ex: 
															#     Documents/
			#print(folder_up)
			fields.append({'title':t,'key':'folder','type':'text', 'value':folder_up})
			fields.append({'title':t,'key':'sub-folder','type':'text', 'value':file_name})

			f = myform_dialog(title=title, done_button_title='ok',fields=fields, sections=None, cover=None, delete_button=True,add_button=True)	
			if f == None:
				return					# cancel pressed, no action
			elif f == 'delete':
				# Delete pressed
				# Check if folder is empty
				if os.listdir(path) != []:
					my_hud_alert(self.view,'Folder is not empty', 'error', duration=2)
					return
				# Ask confirmation
				b = console.alert('Do you confirm deletion of the folder', folder,'yes','no',hide_cancel_button=True)
				if b == 2:
					return				# confirm = no, no action
				# confirm = yes 				
				# Check scan is finished							
				while not self.view['progress_bar'].hidden:
					my_hud_alert(self.view,'scan still in progrss,\nwait please','warning', duration=1)
				my_hud_alert(self.view,'This folder will be deleted\n'+folder, 'warning',duration=2)
				# Delete local folder
				os.rmdir(path)
				# delete folder in folders list
				del folders[folder+'/']
				# Update folders/nodes if they are in the tree of this path
				self.update_folder_nodes_containing_path(folder,0,0,-1)			
				# Remove file node from children of its folder node
				for folder_node in folder_nodes:
					# Folder is a Folder TreeNode
					if folder_node.children:
						if e in folder_node.children:
							folder_node.children.remove(e)	# Remove e node from childrens
							break
				# Delete the node of the folder
				del e
				# delete the datasource of the tableview row
				del self.flat_entries[row]
				self.rebuild_flat_entries()
				del_rows_range = range(row,row+1)
				self.table_view.delete_rows(del_rows_range)
				tv.reload()
				return
			elif f == 'add':
				# Add pressed
				fields = []
				t = '_'*10				# string of chars to align values
				fields.append({'title':t,'key':'folder','type':'text', 'value':folder})
				fields.append({'title':'File (ON) or folder (OFF)', 'key':'file_or_folder','type':'switch'})
				fields.append({'title':t,'key':'name','type':'text'})
				f = myform_dialog(title='add', done_button_title='ok',fields=fields, sections=None, cover=None, delete_button=False, add_button=False)	
				#print(f)
				if f == None:
					return					# cancel pressed, no action
				added_name = f['name'].strip()
				if added_name == '':
					# name would be empty
					my_hud_alert(self.view,'Name must be defined', 'error',duration=2)
					return
				norm_added_name = ''.join((c for c in unicodedata.normalize('NFD', added_name) if unicodedata.category(c) != 'Mn'))
				if added_name != norm_added_name:
					# name contains accents
					my_hud_alert(self.view,'Name contains accents \n'+file_name,'error',duration=2)
					return
				#print(folder+'/'+added_name)
				if os.path.exists(path+'/'+added_name):
					# Folder already exists 
					my_hud_alert(self.view,'A file or a folder with this name already exists\n'+added_name,'error',duration=2)
					return
				# Ask confirmation
				b = console.alert('Do you confirm the creation of ', added_name+'\nin '+folder, 'yes','no',hide_cancel_button=True)
				if b == 2:
					return
				# Check scan is finished							
				while not self.view['progress_bar'].hidden:
					my_hud_alert(self.view,'scan still in progress,\nwait please','warning', duration=1)
				added_path = path + '/' + added_name	# extended path of new folder
				if f['file_or_folder']:
					# on => file
					# Create local file of 0 bytes
					fil = open(added_path,'wt',encoding='utf-8')
					#fil.write('only for tsting with size non zero')	
					fil.close()
					full_path = path + '/' + added_name
					mt = os.path.getmtime(full_path)
					size = os.path.getsize(full_path)
					# Update files
					path_in = folder + '/' + added_name
					files[path_in] = [size,mt]
					
					# Update folders/nodes if they are in the tree of this path
					self.update_folder_nodes_containing_path(folder,1,size,0)#files,size
				else:
					# off => folder
					# Create local folder
					os.mkdir(added_path)

					# store added folder in array of all folders	
					path_in = folder + '/' + added_name + '/'
					path_in = unicodedata.normalize('NFC', path_in)					
					folders[path_in] = [0,0,0]	# folder is empty
					
					full_path = path + '/' + added_name
						
					# Update folders/nodes if they are in the tree of this path
					self.update_folder_nodes_containing_path(folder,0,0,1) # nbr folders

				# code for file and folder
				# Create a new node for added folder or file		
				node = FileTreeNode(full_path)	# create a new node for added folder
																				#  which automatically append
																				#  the node to folder_nodes array
				node.level = e.level + 1				# under the up folder
				if e.expanded:									# up folder already expanded
					children = e.children					# children of up folder
					children.append(node)					# append new folder as child
					e.children = sorted(children, key=attrgetter('leaf', 'cmp_title'))

				self.do_expand(e, row)					# expand or add new to expanded						
				tv.reload()
				return
				
			# ok pressed
			# Check if folder name would change
			if f['sub-folder'] != file_name:
				# Folder name would change
				file_name_new = f['sub-folder'].strip()
				if file_name_new == '':
					# Folder name would be empty
					my_hud_alert(self.view,'Folder name must ne defined', 'error',duration=2)
					return
				norm_file_name_new = ''.join((c for c in unicodedata.normalize('NFD', file_name_new) if unicodedata.category(c) != 'Mn'))
				if file_name_new != norm_file_name_new:
					# Folder name contains accents
					my_hud_alert(self.view,'Folder name contains accents \n'+file_name_new,'error',duration=2)
					return
				if os.path.exists(folder_up+file_name_new):
					# Folder already exists 
					my_hud_alert(self.view,'A file or a folder with the new name already exists\n'+file_name_new,'error',duration=2)
					return
				# Ask confirmation
				b = console.alert('Do you confirm the rename',file_name+'\n|\nV\n'+ file_name_new,'yes','no',hide_cancel_button=True)
				if b == 2:
					return
				# Check scan is finished							
				while not self.view['progress_bar'].hidden:
					my_hud_alert(self.view,'scan stillin progress,\nwait please','warning', duration=1)
				# Rename folder
				os.rename(folder_up+file_name,folder_up+file_name_new)

				# Rename in folders
				folders[folder_up+file_name_new+'/'] = folders[folder_up+file_name+'/']
				del folders[folder_up+file_name+'/']
				# Update Folder TreeNode
				e.title = file_name_new
				e.path = e.path[:len(e.path)-len(file_name)] + file_name_new
				# Refresh TableView
				tv.reload()				 # reload TableView								
		else:			
			# File
			mt = os.path.getmtime(path)
			mt_str = datetime.datetime.fromtimestamp(mt).strftime('%d/%m/%Y %H:%M:%S')
			NSFileManager = ObjCClass('NSFileManager')
			NSFileCreationDate = 'NSFileCreationDate'
			attrs = NSFileManager.defaultManager().attributesOfItemAtPath_error_(path, None)
			creation_date = attrs[NSFileCreationDate]
			# Creation date-time in UTC zone
			utc_time = '{}'.format(creation_date)		# 2017-08-14 07:50:30 +0000
			utc_time = utc_time[0:19]								# 2017-08-14 07:50:30
			utc_datetime = datetime.datetime.strptime(utc_time, '%Y-%m-%d %H:%M:%S')
			# Delta between UTC-zone and local zone
			now_timestamp = time.time()
			offset = datetime.datetime.fromtimestamp(now_timestamp) - datetime.datetime.utcfromtimestamp(now_timestamp)
			# Creation date-time in local zone
			ct = utc_datetime + offset
			ct_str = datetime.datetime.strftime(ct,'%d/%m/%Y %H:%M:%S')
			cover = None
			title = 'File'
			i = folder.rfind('/')
			folder = folder[:i+1]
			folder = unicodedata.normalize('NFC', folder)
			file_name = unicodedata.normalize('NFC', file_name)
			size = os.path.getsize(path)
			size_str = human_size(size) + ' [' + '{:,}'.format(size).replace(',','.') + ' bytes]'
			fields.append({'title':t,'key':'folder','type':'text','value':folder})
			fields.append({'title':t,'key':'file','type':'text','value':file_name})
			fields.append({'title':t,'key':'size','type':'text','value':size_str})
			fields.append({'title':t,'type':'text','key':'mtime','value':mt_str})	
			fields.append({'title':t,'type':'text','key':'ctime','value':ct_str})	

			f = myform_dialog(title=title, done_button_title='ok',fields=fields, sections=None, cover=path, delete_button=True,add_button=False)	
			if f == None:
				return					# cancel pressed, no action
			elif f == 'delete':
				# Delete pressed
				while not self.view['progress_bar'].hidden:
					my_hud_alert(self.view,'scan still in progress,\nwait please','warning', duration=1)
				b = console.alert('Do you confirm the deletion of the file', folder+file_name,'yes','no',hide_cancel_button=True)
				if b == 2:
					return				# confirm = no, no action
				# confirm = yes 
				# Delete on iPad
				my_hud_alert(self.view,'The file will be deleted\n'+folder+'\n'+file_name, 'warning',duration=2)
				# Delete local file
				os.remove(path)
				# delete file in files list
				del files[folder+file_name]
				# Update folders/nodes if they are in the tree of this path
				self.update_folder_nodes_containing_path(folder,-1,-size,0)			
				# Remove file node from children of its folder node
				for folder_node in folder_nodes:
					# Folder is a Folder TreeNode
					if folder_node.children:
						if e in folder_node.children:
							folder_node.children.remove(e)	# Remove e node from childrens
							break
				# Delete the node of the file
				del e
				# delete the datasource of the tableview row
				del self.flat_entries[row]
				self.rebuild_flat_entries()
				del_rows_range = range(row,row+1)
				self.table_view.delete_rows(del_rows_range)
				tv.reload()
				return
			
			# ok pressed
		
			# Check of file has been modified
			mt_new = os.path.getmtime(path)
			size_new = os.path.getsize(path)
			if mt_new != mt or size_new != size:
				# File has been modified by save button
				while not self.view['progress_bar'].hidden:
					my_hud_alert(self.view,'scan still in progress,\nwait please','warning', duration=1)
				# Update files
				files[folder+file_name] = [size_new,mt_new]
				# Update File TreeNode
				e.subtitle = human_size(size_new) + '  [' + datetime.datetime.fromtimestamp(mt_new).strftime('%d/%m/%Y %H:%M:%S') + ']'
				# Update folders/nodes if they are in the tree of this path
				self.update_folder_nodes_containing_path(folder,0,size_new-size,0)
				# Refresh TableView
				tv.reload()				 # reload TableView
			
			# Check if name would change
			if f['file'] != file_name:
				# File name would change
				file_name_new = f['file'].strip()
				if file_name_new == '':
					# File name would be empty
					my_hud_alert(self.view,'File name must be defined', 'error',duration=2)
					return
				norm_file_name_new = ''.join((c for c in unicodedata.normalize('NFD', file_name_new) if unicodedata.category(c) != 'Mn'))
				if file_name_new != norm_file_name_new:
					# File name contains accents
					my_hud_alert(self.view,'File mame contains accents \n'+file_name_new,'error',duration=2)
					return
				if os.path.exists(folder+file_name_new):
					# File already exists
					my_hud_alert(self.view,'A file with the new name already exists\n'+file_name_new,'error',duration=2)
					return
				# Check of extension would change
				i = file_name.rfind('.')
				file_ext = file_name[i:] if i >= 0 else ''
				i = file_name_new.rfind('.')
				file_ext_new = file_name_new[i:] if i >= 0 else ''
				if file_ext.lower() != file_ext_new.lower():
					# File extension would change
					b = console.alert('Do you confirm the change of extension', file_ext+'\n|\nV\n'+file_ext_new,'yes','no',hide_cancel_button=True)
					if b == 2:
						return
				# Ask confirmation
				b = console.alert('Do you confirm the rename',file_name+'\n|\nV\n'+ file_name_new,'yes','no',hide_cancel_button=True)
				if b == 2:
					return
				# Rename file
				os.chdir(os.path.expanduser('~/'))
				os.rename(folder+file_name,folder+file_name_new)

				# Rename in files
				while not self.view['progress_bar'].hidden:
					my_hud_alert(self.view,'scan still in progress,\nwaot please','warning', duration=1)
				files[folder+file_name_new] = files[folder+file_name]
				del files[folder+file_name]
				# Update File TreeNode
				i = e.path.rfind('/')
				e.path = e.path[:i+1] + file_name_new
				e.title = file_name_new
				# Refresh TableView
				tv.reload()				 # reload TableView			
		
	def update_folder_nodes_containing_path(self,folder_in,dn,ds,df):
		# update size and number of files in tree of folder
		folder = folder_in
		if folder[-1] != '/':
			folder += '/'
		#print('update_folder_nodes_containing_path: folder=',folder)
		for folder_key in folders:
			if folder[:len(folder_key)] == folder_key: 
				n,s,nf = folders[folder_key]
				folders[folder_key] = [n+dn,s+ds,nf+df]
				#print('update_folder_nodes_containing_path:    folder_key=',folder_key)
		# update nodes of files in tree of folder
		for folder_node in folder_nodes:
			# Folder is a Folder TreeNode
			i = folder_node.path.find('Documents/')
			if i == -1:
				node_path = 'Documents/'
			else:
				node_path = folder_node.path[i:] 
			if folder[:len(node_path)] == node_path:
				if node_path[-1] != '/':
					node_path += '/'
				if node_path in folders:
					n,s,nf = folders[node_path]
					folder_node.subtitle = human_size(s) + ' [' +  str(n) + ' files, ' + str(nf) + ' folders]'

	#def tableview_did_deselect(self, tv, section, row):
		#return
	
	def will_close(self):
		pass

def main():
	global script_path,files,folders,picker,folder_nodes
	#----- Main process -----
	console.clear()
	
	# Initializations
	x = sys.argv[0] 				# Script path and name
	i =	x.rfind('/') 				# index last /
	script_path = x[:i+1]			# expanded path of script
	root_dir = os.path.expanduser('~/')#Documents/')
	files = {}
	folders = {}
	folder_nodes = []
	
	title = 'File Explorer'
	root_node = FileTreeNode(root_dir)		
	#root_node = FileTreeNode('/private/var/mobile/Library/Mobile Documents/iCloud~com~omz-software~Pythonista3/Documents/')
	root_node.title = title
	picker = TreeDialogController(root_node, allow_multi=False)
	picker.view.present('full_screen',hide_title_bar=False)
	
	# Start thread to scan all local files
	thread = my_thread_scan()
	thread.start()
	
if __name__ == '__main__':
	main()
