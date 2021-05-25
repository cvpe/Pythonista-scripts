# coding: utf-8
import editor
import functools
from   objc_util import *
from   operator import attrgetter
import os
import sys
import threading
import time
import ui

# for GoogleDrive
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import webbrowser

class my_thread(threading.Thread):
	def __init__(self):
		global local_filename
		threading.Thread.__init__(self)
		self.last_modification_time = os.path.getmtime(local_filename)
	def run(self):
		global main_view, edit_tab, EditedGoogleFile
		while True:
			time.sleep(1)

			# check if tab has been closed			
			win = UIApplication.sharedApplication().keyWindow()
			root_vc = win.rootViewController()
			tabs = []
			if root_vc.isKindOfClass_(ObjCClass('PASlidingContainerViewController')):
				tabs_vc = root_vc.detailViewController()
				for tab in tabs_vc.tabViewControllers():
					if tab.isKindOfClass_(ObjCClass('PA2UniversalTextEditorViewController')):
						tabs.append(tab)
			if edit_tab not in tabs:
				# tab has been closed
				self.save()
				time.sleep(0.2)
				os.remove(local_filename)
				break
						
			# if modif, save
			last_modification_time = os.path.getmtime(local_filename)
			if last_modification_time != self.last_modification_time:
				# save on GoogleDrive
				self.last_modification_time = last_modification_time
				self.save()
			
	def save(self):
		global EditedGoogleFile, local_filename
		EditedGoogleFile.SetContentFile(local_filename)
		EditedGoogleFile.Upload()

class TreeNode (object):
	def __init__(self):
		self.expanded = False
		self.children = None
		self.leaf = True
		self.title = ''
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
	def __init__(self, GoogleFile):
		TreeNode.__init__(self)
		self.GoogleFile = GoogleFile
		self.title = GoogleFile['title']
		self.id = GoogleFile['id']
		is_dir = GoogleFile['mimeType'] == 'application/vnd.google-apps.folder'
		self.leaf = not is_dir
		i = GoogleFile['title'].rfind('.')
		ext = GoogleFile['title'][i+1:].lower()
		if is_dir:
			self.icon_name = 'Folder'
		elif ext == 'map':
			self.icon_name = 'iob:map_32'
		elif ext == ['txt']:
			self.icon_name = 'iob:ios7_compose_outline_32'
		elif ext == 'py':
			self.icon_name = 'FilePY'
		elif ext == 'pyui':
			self.icon_name = 'FileUI'
		elif ext in ['png','jpg','jpeg','bmp','gif','tif','tiff']:
			self.icon_name = 'iob:image_32'
		elif ext in ['mp4','mov','avi','mkv','m4v']:
			self.icon_name = 'iob:ios7_film_outline_32'
		elif ext in ['zip','rar']:
			self.icon_name = 'iob:archive_32'
		elif ext in ['mp3','wav']:
			self.icon_name = 'iob:ios7_musical_notes_32'
		else:
			self.icon_name = 'FileOther'
		if is_dir:
			self.enabled = False
		else:
			filename = GoogleFile['title']
			self.enabled = ext in ['py', 'txt', 'html']

	@property
	def cmp_title(self):
		return self.title.lower()

	def expand_children(self):
		global drive
		if self.children is not None:
			self.expanded = True
			return

		files = drive.ListFile({'q': "'%s' in parents and trashed=false" % (self.id)}).GetList()
		children = []
		for GoogleFile in files:
			#print(type(GoogleFile))
			#print('mimeType: %s, title: %s, id: %s' % (GoogleFile['mimeType'], GoogleFile['title'], GoogleFile['id']))
			node = FileTreeNode(GoogleFile)
			node.level = self.level + 1
			children.append(node)
		self.expanded = True
		self.children = sorted(children, key=attrgetter('leaf', 'cmp_title'))

class TreeDialogController (object):
	def __init__(self, root_node, allow_multi=False, async_mode=False):
		self.async_mode = async_mode
		self.allow_multi = allow_multi
		self.selected_entries = None
		self.table_view = ui.TableView()
		self.table_view.frame = (0, 0, 700,800)
		self.table_view.data_source = self
		self.table_view.delegate = self
		self.table_view.flex = 'WH'
		self.table_view.allows_multiple_selection = True
		self.table_view.tint_color = 'gray'
		self.view = ui.View(frame=self.table_view.frame)
		self.view.add_subview(self.table_view)
		self.view.name = 'My Google Drive'
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
		label_frame = (label_x, 0, label_w, 44)
		label = ui.Label(frame=label_frame)
		label.font = ('<System>', 18)
		label.text = entry.title
		label.flex = 'W'
		cell.content_view.add_subview(label)
		if entry.leaf and not entry.enabled:
			label.text_color = '#999'
		cell.content_view.add_subview(image_view)
		if not entry.leaf:
			has_children = entry.expanded
			btn = ui.Button(image=ui.Image.named('CollapseFolder' if has_children else 'ExpandFolder'))
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
			sender.image = ui.Image.named('ExpandFolder')
		else:
			sender.image = ui.Image.named('CollapseFolder')
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
		self.view.close()

def main():
	global drive, edit_tab, EditedGoogleFile, local_filename
	
	google_drive_auth_path = os.path.expanduser('~/Documents/MesTools/settings.yaml')
	gauth = GoogleAuth(google_drive_auth_path)
	drive = GoogleDrive(gauth)
	# Create local webserver and auto handles authentication.
	if not hasattr(webbrowser,'_open'):
		webbrowser._open=webbrowser.open
	def wbopen(url, *args,**kwargs):
		return webbrowser._open(url)
	webbrowser.open=wbopen
	
	GoogleFile = {}
	GoogleFile['title'] = 'drive'
	GoogleFile['id']    = 'root'
	GoogleFile['mimeType'] = 'application/vnd.google-apps.folder'

	root_node = FileTreeNode(GoogleFile)			
		
	picker = TreeDialogController(root_node)
	picker.view.present('sheet')
	picker.view.wait_modal()
	if picker.selected_entries:
		e = picker.selected_entries[0]
		EditedGoogleFile = e.GoogleFile
		filename = EditedGoogleFile['title']
		
		# create local file for editing
		path = sys.argv[0]
		i = path.rfind('/')
		path = path[:i+1]
		i = filename.rfind('.')
		ext = filename[i+1:]
		local_filename = path + filename[:i] + ' [on GoogleDrive].' + ext
		# get Google Drive file as a local file
		EditedGoogleFile.GetContentFile(local_filename)
		
		time.sleep(0.2)
		
		# edit local file in same tab, so keyboard is still active
		editor.open_file(local_filename, new_tab=False)
		
		# add a save key to Pythonista keyboard
		edit_tab = editor._get_editor_tab()

		th = my_thread()
		th.start()
	
if __name__ == '__main__':
	main()
