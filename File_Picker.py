# coding: utf-8
# from omz
import ui
import os
from objc_util import ObjCInstance, ObjCClass
from operator import attrgetter
import time
import threading
import functools
import ftplib
import re
import appex		# added by cvp for displaying other images of appex mode
# http://stackoverflow.com/a/6547474
def human_size(size_bytes):
	'''Helper function for formatting human-readable file sizes'''
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
		self.enabled = True

	def expand_children(self):
		self.expanded = True
		self.children = []

	def collapse_children(self):
		self.expanded = False

	def __repr__(self):
		return '<TreeNode: "%s"%s>' % (self.title, ' (expanded)' if self.expanded else '')

class FileTreeNode (TreeNode):
	def __init__(self, path, show_size=True, select_dirs=True,   
               file_pattern=None,only=False):
		global folders
		TreeNode.__init__(self)
		self.path = path
		if path in folders:
			self.title = folders[path] #{path:name}
		else:
			self.title = os.path.split(path)[1]
		self.select_dirs = select_dirs
		self.file_pattern = file_pattern
		self.only = only
		is_dir = os.path.isdir(path)
		self.leaf = not is_dir
		ext = os.path.splitext(path)[1].lower()
		if is_dir:
			self.icon_name = 'Folder'
		elif ext == '.py':
			self.icon_name = 'FilePY'
		elif ext == '.pyui':
			self.icon_name = 'FileUI'
		elif ext in ['.png','.jpg','.jpeg','.bmp','.gif','.tif','.tiff']:
			self.icon_name = path	#'FileImage'
		else:
			self.icon_name = 'FileOther'
		self.show_size = show_size
		if not is_dir and show_size:
			self.subtitle = human_size((os.stat(self.path).st_size))
		if is_dir and not select_dirs:
			self.enabled = False
		elif not is_dir:
			filename = os.path.split(path)[1]
			self.enabled = not file_pattern or re.match(file_pattern, filename)

	@property
	def cmp_title(self):
		return self.title.lower()

	def expand_children(self):
		global folders, common
		if self.children is not None:
			self.expanded = True
			return
		if self.path == common:
			files = []
			for k in folders.keys():
				files.append(k[0])
			files =  [k[0] for k in sorted(folders.items(), key=lambda x:x[1].lower(), reverse=True)]	
		else:
			files = os.listdir(self.path)
		children = []
		for filename in files:
			if filename.startswith('.'):
				continue
			full_path = os.path.join(self.path, filename)
			if self.select_dirs and self.only and not os.path.isdir(full_path):
				# select only dirs and this is not a folder, skip
				continue
			if self.only:
				if (not os.path.isdir(full_path)) and not (not self.file_pattern or re.match(self.file_pattern, filename)):
					continue
			node = FileTreeNode(full_path, self.show_size, self.select_dirs, self.file_pattern,self.only)
			node.level = self.level + 1
			children.append(node)
		self.expanded = True
		if self.path == common:
			self.children = children
		else:
			self.children = sorted(children, key=attrgetter('leaf', 'cmp_title'))

# Just a simple demo of a custom TreeNode class... The TreeDialogController should be initialized with async_mode=True when using this class.
class FTPTreeNode (TreeNode):
	def __init__(self, host, path=None, level=0):
		TreeNode.__init__(self)
		self.host = host
		self.path = path
		self.level = level
		if path:
			self.title = os.path.split(path)[1]
		else:
			self.title = self.host
		self.leaf = path and len(os.path.splitext(path)[1]) > 0
		self.icon_name = 'FileOther' if self.leaf else 'Folder'

	def expand_children(self):
		ftp = ftplib.FTP(self.host, timeout=10)
		ftp.login('anonymous')
		names = ftp.nlst(self.path or '')
		ftp.quit()
		self.children = [FTPTreeNode(self.host, name, self.level+1) for name in names]
		self.expanded = True

class TreeDialogController (object):
	def __init__(self, root_node, allow_multi=False, async_mode=False):
		self.async_mode = async_mode
		self.allow_multi = allow_multi
		self.selected_entries = None
		self.table_view = ui.TableView()
		self.table_view.frame = (0, 0, 500, 500)
		self.table_view.data_source = self
		self.table_view.delegate = self
		self.table_view.flex = 'WH'
		self.table_view.allows_multiple_selection = True
		self.table_view.tint_color = 'gray'
		self.view = ui.View(frame=self.table_view.frame)
		self.view.add_subview(self.table_view)
		self.view.name = root_node.title
		self.busy_view = ui.View(frame=self.view.bounds, flex='WH', background_color=(0, 0, 0, 0.35))
		hud = ui.View(frame=(self.view.center.x - 50, self.view.center.y - 50, 100, 100))
		hud.background_color = (0, 0, 0, 0.7)
		hud.corner_radius = 8.0
		hud.flex = 'TLRB'
		spinner = ui.ActivityIndicator()
		spinner.style = ui.ACTIVITY_INDICATOR_STYLE_WHITE_LARGE
		spinner.center = (50, 50)
		spinner.start_animating()
		hud.add_subview(spinner)
		self.busy_view.add_subview(hud)
		self.busy_view.alpha = 0.0
		self.view.add_subview(self.busy_view)
		self.done_btn = ui.ButtonItem(title='Done', action=self.done_action)
		if self.allow_multi:
			self.view.right_button_items = [self.done_btn]
		self.done_btn.enabled = False
		self.root_node = root_node
		self.entries = []
		self.flat_entries = []
		if self.async_mode:
			self.set_busy(True)
			t = threading.Thread(target=self.expand_root)
			t.start()
		else:
			self.expand_root()

	def expand_root(self):
		self.root_node.expand_children()
		self.set_busy(False)
		self.entries = self.root_node.children
		self.flat_entries = self.entries
		self.table_view.reload()
	
	def flatten_entries(self, entries, dest=None):
		if dest is None:
			dest = []
		for entry in entries:
			dest.append(entry)
			if not entry.leaf and entry.expanded:
				self.flatten_entries(entry.children, dest)
		return dest
		
	def rebuild_flat_entries(self):
		self.flat_entries = self.flatten_entries(self.entries)

	def tableview_number_of_rows(self, tv, section):
		return len(self.flat_entries)

	def tableview_cell_for_row(self, tv, section, row):
		cell = ui.TableViewCell()
		entry = self.flat_entries[row]
		level = entry.level - 1
		image_view = ui.ImageView(frame=(44 + 20*level, 5, 34, 34))
		label_x = 44+34+8+20*level
		label_w = cell.content_view.bounds.w - label_x - 8
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
		if entry.subtitle:
			label.font = ('<System>', 15)
		else:
			label.font = ('<System>', 18)
		label.text = entry.title
		label.flex = 'W'
		cell.content_view.add_subview(label)
		if entry.leaf and not entry.enabled:
			label.text_color = '#999'
		cell.content_view.add_subview(image_view)
		if not entry.leaf:
			has_children = entry.expanded
			if not appex.is_running_extension():					# added by cvp
				btn = ui.Button(image=ui.Image.named('CollapseFolder' if has_children else 'ExpandFolder'))
			else:																					# added by cvp
				btn = ui.Button(image=ui.Image.named('iob:arrow_down_b_24' if has_children else 'iob:arrow_right_b_24'))		# added by cvp
			btn.frame = (20*level, 0, 44, 44)
			btn.action = self.expand_dir_action
			cell.content_view.add_subview(btn)
		if entry.icon_name:
			image_view.image = ui.Image.named(entry.icon_name)
		else:
			image_view.image = None
		cell.selectable = entry.enabled
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
		if entry.expanded:
			if not appex.is_running_extension():										# added by cvp
				sender.image = ui.Image.named('ExpandFolder')
			else:																										# added by cvp		
				sender.image = ui.Image.named('iob:arrow_right_b_24')	# added by cvp
		else:
			if not appex.is_running_extension():										# added by cvp
				sender.image = ui.Image.named('CollapseFolder')
			else:																										# added by cvp		
				sender.image = ui.Image.named('iob:arrow_down_b_24')	# added by cvp
		self.toggle_dir(row)
		self.update_done_btn()

	def toggle_dir(self, row):
		'''Expand or collapse a folder node'''
		entry = self.flat_entries[row]
		if entry.expanded:
			entry.collapse_children()
			old_len = len(self.flat_entries)
			self.rebuild_flat_entries()
			num_deleted = old_len - len(self.flat_entries)
			deleted_rows = range(row + 1, row + num_deleted + 1)
			self.table_view.delete_rows(deleted_rows)
		else:
			if self.async_mode:
				self.set_busy(True)
				expand = functools.partial(self.do_expand, entry, row)
				t = threading.Thread(target=expand)
				t.start()
			else:
				self.do_expand(entry, row)

	def do_expand(self, entry, row):
		'''Actual folder expansion (called on background thread if async_mode is enabled)'''
		entry.expand_children()
		self.set_busy(False)
		old_len = len(self.flat_entries)
		self.rebuild_flat_entries()
		num_inserted = len(self.flat_entries) - old_len
		inserted_rows = range(row + 1, row + num_inserted + 1)
		self.table_view.insert_rows(inserted_rows)

	def tableview_did_select(self, tv, section, row):
		self.update_done_btn()

	def tableview_did_deselect(self, tv, section, row):
		self.update_done_btn()

	def update_done_btn(self):
		'''Deactivate the done button when nothing is selected'''
		selected = [self.flat_entries[i[1]] for i in self.table_view.selected_rows if self.flat_entries[i[1]].enabled]
		if selected and not self.allow_multi:
			self.done_action(None)
		else:
			self.done_btn.enabled = len(selected) > 0

	def set_busy(self, flag):
		'''Show/hide spinner overlay'''
		def anim():
			self.busy_view.alpha = 1.0 if flag else 0.0
		ui.animate(anim)

	def done_action(self, sender):
		self.selected_entries = [self.flat_entries[i[1]] for i in self.table_view.selected_rows if self.flat_entries[i[1]].enabled]
		if self.from_dialog != None:
			if self.selected_entries != None:
				paths = [e.path for e in self.selected_entries]
				c  = self.from_dialog[0]
				tf = self.from_dialog[1]
				#print('picker',paths[0])
				c.values[tf.name] = paths[0]
				tf.text = paths[0]
				if self.callback != None:
					self.callback(tf)
		self.view.close()

def file_picker_dialog(title=None, root_dir=None, multiple=False,
                       select_dirs=False, file_pattern=None, only=False, show_size=True, from_dialog=None, icloud=False, callback=None):
	global folders, common
	folders = {}
	common = ''
	root = root_dir
	if root is None:
		root = os.path.expanduser('~/')
	if title is None:
		title = os.path.split(root)[1]
	if isinstance(root,dict):
		folders = root
		paths = list(folders.keys())
		# Python 3 program to find longest
		# common prefix of given array of words.
		n = len(paths)
		if n == 0:
			root = ''
		elif n == 1:
			root = paths[0]
		else:
			# sort the array of strings
			paths.sort()
			# find the minimum length from
			# first and last string
			end = min(len(paths[0]), len(paths[n - 1])) 
			# find the common prefix between
			# the first and last string
			i = 0
			while (i < end and paths[0][i] == paths[n - 1][i]):
				i += 1
			common = paths[0][0: i]
			root = common 

	if icloud:
		root_node = FileTreeNode('/private/var/mobile/Library/Mobile Documents/iCloud~com~omz-software~Pythonista3/Documents/', show_size, select_dirs, file_pattern,only)			# bug? does not use root_dir
	else:
		root_node = FileTreeNode(root, show_size, select_dirs, file_pattern,only)			# bug? does not use root_dir
		
	root_node.title = title or ''
	picker = TreeDialogController(root_node, allow_multi=multiple)
	picker.from_dialog = from_dialog
	picker.callback = callback
	picker.view.present('sheet')
	if from_dialog == None:
		picker.view.wait_modal()
	else:
		# called by a textfield of form_dialog.
		# if wait_modal, scroll does not function
		# return process performed in done_action, see above
		return

	if picker.selected_entries is None:
		return None
	paths = [e.path for e in picker.selected_entries]
	if multiple:
		return paths
	else:
		return paths[0]

def ftp_dialog(host='mirrors.kernel.org'):
	# This is just a demo of how TreeDialogController is
	# extensible with custom TreeNode subclasses, so there
	# aren't as many options as for the regular file dialog.
	root_node = FTPTreeNode(host)
	picker = TreeDialogController(root_node, async_mode=True)
	picker.view.present('sheet')
	picker.view.wait_modal()
	if picker.selected_entries:
		return picker.selected_entries[0].path

def main():

		
	#py_files = file_picker_dialog('Pick some .py files', multiple=False, select_dirs=True, file_pattern=r'^.*\.py$',only=True)
	#py_files = file_picker_dialog('Pick some .py files', multiple=True, select_dirs=False, file_pattern=r'^.*\.py$')
	#file = file_picker_dialog('On your iDevice', root_dir='/private/var/mobile/Containers/Shared/AppGroup/EF3F9065-AD98-4DE3-B5DB-21170E88B77F/File Provider Storage')
	
	path = os.path.expanduser('~/Documents/')
	i = len('/private/var/mobile/Containers/Shared/AppGroup/')
	j = path.find('/',i)
	# on my ipad does not have same device_id as local Pythonista....
	device_id_local = path[i:j]
	path_on_my = '/private/var/mobile/Containers/Shared/AppGroup/EF3F9065-AD98-4DE3-B5DB-21170E88B77F/File Provider Storage/'
	device_model = str(ObjCClass('UIDevice').currentDevice().model())		
	#files = ['/var/mobile/Containers/Shared/AppGroup/'+device_id_local+'/Pythonista3/Documents/', '/private/var/mobile/Library/Mobile Documents/iCloud~com~omz-software~Pythonista3/Documents/', path_on_my, '/private/var/mobile/Library/Mobile Documents/com~apple~CloudDocs/']
	folders = {
		'/private/var/mobile/Containers/Shared/AppGroup/'+device_id_local+'/Pythonista3/Documents/':'Pythonista local', 
		'/private/var/mobile/Library/Mobile Documents/iCloud~com~omz-software~Pythonista3/Documents/':'Pythonista iCloud',
		path_on_my:'On my ' + device_model,
		'/private/var/mobile/Library/Mobile Documents/com~apple~CloudDocs/':'iCloud Drive'}	
				
	file = file_picker_dialog('On your iDevice', root_dir=folders, select_dirs=True, only=True)
	print('Picked:', file)
	
	#ftp_file = ftp_dialog()
	#print('Picked from FTP server:', ftp_file)
	
if __name__ == '__main__':
	main()
