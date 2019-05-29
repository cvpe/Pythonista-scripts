# webview and its scrollview, download image, javascript
import clipboard
import console
from   objc_util import *
import requests
import ui
class MyView(ui.View):
	def __init__(self,w,h):
		self.width = w
		self.height = h
		
		webview = ui.WebView()
		webview.frame = self.frame
		webview.delegate = self
		self.add_subview(webview)

		t = 'https://forum.omz-software.com/topic/'
		url = clipboard.get()	
		if url:
			if url[:len(t)] != t:
				url = None
		if not url:
			url = 'https://forum.omz-software.com/topic/3317/introduction'
		webview.load_url(url)
		# get scrollview of webview via its ObjectiveC object
		self.scrollview = ObjCInstance(webview).subviews()[0].scrollView()

		# print html source file during tests
		#r = requests.get(url)
		#source =r.text
		#print(source)
		
		c = ui.Button(name='close')
		c.frame = (10,20,32,32)
		c.background_image = ui.Image.named('iob:ios7_close_outline_32')
		c.tint_color = 'red'
		c.action = self.close_button
		self.add_subview(c)
					
		b = ui.Button(name='avatar')
		d = 64
		b.frame = (10,10,d,d)
		b.font =('Menlo',d/2)
		b.background_color = 'cyan'
		b.corner_radius = d/2
		b.border_color ='blue'
		b.border_width = 1
		b.hidden = True
		self.add_subview(b)

		self.top = 0
		
	def close_button(self,sender):
		self.close()
		
	def webview_did_finish_load(self, webview):
		# search posts, users, profile images
		"""
		<div class="clearfix">
			<div class="icon pull-left">
				<a href="/user/xxxxxx">
					<img src="yyyyyyyyyyyyy  align="left" itemprop="image" />			
				</a>
		"""
		t_img = '<img src="'
		t_usr = '<a href="/user/'
		self.users = {}
		self.posts = {}
		# number of elements of class "icon pull-left"	
		n_posts = int(webview.evaluate_javascript('document.getElementsByClassName("icon pull-left").length'))
		for i in range(0,n_posts):
			webview.evaluate_javascript('ele=document.getElementsByClassName("icon pull-left")['+str(i)+'];')
			html = webview.evaluate_javascript('ele.innerHTML')
			#print(html)
			i = html.find(t_usr)
			j = html.find('"',i+len(t_usr))
			usr = html[i+len(t_usr):j]
			#print(usr)
			if usr not in self.users:
				i = html.find(t_img)
				j = html.find('"',i+len(t_img))
				url = html[i+len(t_img):j]
				#print(url)
				if url[0] == '/':
					url = 'https://forum.omz-software.com' + url
				r = requests.get(url)
				image_data = r.content
				self.users[usr] = image_data
			o = int(webview.evaluate_javascript('ele.getBoundingClientRect().top'))
			self.posts[o] = usr
			
		self.update_interval = 1/60
		
	def update(self):
		self.top = self.top + 1
		self.scrollview.setContentOffset_(CGPoint(0,self.top))
		if self.top in self.posts:
			usr = self.posts[self.top]
			#print(self.top,usr)
			if self.users[usr]:
				self['avatar'].title = ''				
				self['avatar'].background_image = ui.Image.from_data(self.users[usr])
			else:
				self['avatar'].title = usr
				siz = self['avatar'].width/2
				while True:
					w,h = ui.measure_string(usr,font=('Menlo',siz))
					#print(usr,siz,w,self['avatar'].width)
					if w < self['avatar'].width:
						self['avatar'].font = ('Menlo',siz)
						break
					siz = siz - 1
				self['avatar'].background_image = None
			self['avatar'].hidden = False
			self['avatar'].y = 100

def main():
	console.clear()
	w, h = ui.get_screen_size()
	disp = 'full_screen'
	back = MyView(w,h)
	back.background_color='white'
	back.present(disp, hide_title_bar=True)		
	
if __name__ == '__main__':
	main()
