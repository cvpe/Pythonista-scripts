# todo
# coding: utf-8
import console
import os
import requests
import sys
import ui

try:
	from Folder_Picker import folder_picker_dialog
except ModuleNotFoundError as e:
	folder_picker_dialog = None
		
class MyView(ui.View):
	def __init__(self,w,h):
		self.width = w
		self.height = h
		self.background_color='white'
		self.github_url = 'https://github.com/'
		self.github_raw = 'https://raw.githubusercontent.com/'
		self.github_raw2= 'https://gist.githubusercontent.com/'
		
		bi_forw = ui.ButtonItem(image=ui.Image.named('iob:ios7_arrow_forward_32'))
		bi_forw.action = self.go_forw

		bi_back = ui.ButtonItem(image=ui.Image.named('iob:ios7_arrow_back_32'))	
		bi_back.action = self.go_back
		
		bi_down = ui.ButtonItem(image=ui.Image.named('iob:ios7_cloud_download_outline_32'))	
		bi_down.action = self.go_down
		bi_down.enabled = False
		
		self.right_button_items = (bi_down,bi_forw,bi_back)
		
		tf = ui.TextField(name='url')
		tf.clear_button_mode = 'while_editing'
		tf.keyboard_type = ui.KEYBOARD_URL
		tf.text_color = 'blue'
		tf.frame = (2,2,w-2*2,32)
		tf.delegate = self
		tf.text = 'https://www.google.com/'
		self.add_subview(tf)

		y = tf.y + tf.height + 2
		wv = ui.WebView(name='webview')
		wv.frame = (2,y,w-2*2,h-y-2)
		wv.delegate = self
		wv.border_color = 'blue'
		wv.border_width = 1
		self.add_subview(wv)	
		
		wv.load_url(tf.text)

	def webview_did_finish_load(self, webview):
		self['url'].text = self.url
		# check of github raw
		self.right_button_items[0].enabled = False
		if self.url[:len(self.github_raw)] == self.github_raw or self.url[:len(self.github_raw2)] == self.github_raw2:
			# enable raw button
			self.right_button_items[0].enabled = True				
				
	def webview_should_start_load(self, webview, url, nav_type):
		#print('Will start loading', url)
		self.url = url
		return True

	def webview_did_start_load(self, webview):
		#print('Started loading')
		pass
			
	def textfield_did_end_editing(self, textfield):
		#print('did_end_editing',textfield.name,textfield.text)
		url = textfield.text
		if not url.startswith(('http://', 'https://')):
			url = 'http://' + url
		self['webview'].load_url(url)		
		
	def go_forw(self,sender):
		self['webview'].go_forward()	
		
	def go_back(self,sender):
		self['webview'].go_back()	
		
	def go_down(self,sender):
		# download from the web
		try:
			url = self['url'].text
			data = requests.get(url).content
		except Exception as e:
			console.hud_alert('download error '+str(e),'error',2)
			print('download error for url='+url,str(e))
			return	
		if folder_picker_dialog:
			# select folder where to copy
			dir = folder_picker_dialog('Select where you want to save')	
			#print(dir)
			if dir == None:
				console.hud_alert('folder selection canceled','error',1)
				return
			else:
				t = 'Pythonista3/'
				i = dir.find(t)
				loc = dir[i+len(t):]
				console.hud_alert('File copied on '+loc,'success',2)
		else:
			# Folder_Picker module does not exist
			console.hud_alert('No Folder_Picker, file copied on root','warning',2)
			dir  = os.path.expanduser('~/Documents')	# copy on root
		# copy
		file_name = url.split('/')[-1]
		path = dir + '/' + file_name
		with open(path,mode='wb') as out_file:
			out_file.write(data)

def main():
	console.clear()	
	MyView(*ui.get_screen_size()).present('full_screen')	
	
if __name__ == '__main__':
	main()
