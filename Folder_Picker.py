# coding: utf-8
# Select folder
# based on omz script at https://gist.github.com/omz/e3433ebba20c92b63111
import ui
import os
import console
from objc_util import ObjCInstance, ObjCClass

class TreeNode (object):
	def __init__(self):
		self.expanded = False
		self.children = None
		self.title = ''
		self.level = 0

	def expand_children(self):
		self.expanded = True
		self.children = []

	def collapse_children(self):
		self.expanded = False

class FileTreeNode (TreeNode):
	def __init__(self, path):
		TreeNode.__init__(self)
		self.path = path
		self.title = os.path.split(path)[1]
		self.enabled = True

	def expand_children(self):
		if self.children is not None:
			self.expanded = True
			return
		files = os.listdir(self.path)
		children = []
		for filename in sorted(files):
			if filename.startswith('.'):
				continue
			full_path = os.path.join(self.path, filename)
			# As I have allowed show all folders of Pythonista3, not only
			# Documents (to allow selection of Documents),
			# I have to discard Library, etc... from children
			i = full_path.find('Pythonista3/') # always present
			w = full_path[i+len('Pythonista3/'):]
			if not('/' in w) and (w[:] != 'Documents'):
				# other root folder than Documents, skip process
				continue
			if not os.path.isdir(full_path):
				# not a folder, skip process
				continue
			node = FileTreeNode(full_path)
			node.level = self.level + 1
			children.append(node)
		self.expanded = True
		self.children = children

class TreeDialogController (object):
	def __init__(self, root_node):
		self.selected_entries = None
		self.table_view = ui.TableView()
		self.table_view.frame = (0, 0, 500, 500)
		self.table_view.data_source = self
		self.table_view.delegate = self
		self.table_view.flex = 'WH'
		self.table_view.allows_multiple_selection = False
		self.table_view.tint_color = 'gray'
		self.view = ui.View(frame=self.table_view.frame)
		self.view.add_subview(self.table_view)
		self.view.name = root_node.title
		self.root_node = root_node
		self.entries = []
		self.flat_entries = []
		self.expand_root()

	def expand_root(self):
		self.root_node.expand_children()
		self.entries = self.root_node.children
		self.flat_entries = self.entries
		self.table_view.reload()
	
	def flatten_entries(self, entries, dest=None):
		if dest is None:
			dest = []
		for entry in entries:
			dest.append(entry)
			if entry.expanded:
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
		image_view = ui.ImageView(frame=(44 + 20*level, 5, 34, 34)) # + image
		image_view.image = ui.Image.named('Folder')									# + image
		cell.content_view.add_subview(image_view)										# + image
		label_x = 44+34+8+20*level																	# + image
		#label_x = 44+8+20*level																		# - image
		label_w = cell.content_view.bounds.w - label_x - 8
		label_frame = (label_x, 0, label_w, 44)
		label = ui.Label(frame=label_frame)
		label.font = ('<System>', 18)
		label.text = entry.title
		label.flex = 'W'
		cell.content_view.add_subview(label)

		has_children = entry.expanded
		btn = ui.Button(image=ui.Image.named('CollapseFolder' if has_children else 'ExpandFolder'))
		btn.frame = (20*level, 0, 44, 44)
		btn.action = self.expand_dir_action
		cell.content_view.add_subview(btn)
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
			self.do_expand(entry, row)
				
	def do_expand(self, entry, row):
		entry.expand_children()
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
		if selected:
			self.done_action(None)

	def done_action(self, sender):
		self.selected_entries = [self.flat_entries[i[1]] for i in self.table_view.selected_rows if self.flat_entries[i[1]].enabled]
		self.view.close()

def folder_picker_dialog(title=None,root_dir=None):
	if not root_dir:
		root_dir = os.path.expanduser('~/')
	if title is None:
		title = os.path.split(root_dir)[1]
	root_node = FileTreeNode(root_dir) #os.path.expanduser('~/'))
	root_node.title = title or ''
	picker = TreeDialogController(root_node)
	picker.view.present('sheet')
	picker.view.wait_modal()
	if picker.selected_entries is None:
		return None
	paths = [e.path for e in picker.selected_entries]
	return paths[0]

def main():
	py_dir = folder_picker_dialog('Select a folder')
	if py_dir != None:
		print('Selected dir from ~/Documents:'+py_dir)
	
if __name__ == '__main__':
	main()
