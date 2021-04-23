from objc_util import *
import ui

def b_action(sender):
	import GoogleDriveBrowser
	GoogleDriveBrowser.main()

@on_main_thread
def main():
	global folder_icon
	win = ObjCClass('UIApplication').sharedApplication().keyWindow()
	main_view = win.rootViewController().view() 
	folder_icon = None
	def analyze(v,indent):
		global folder_icon,__persistent_views
		for sv in v.subviews():
			#print('.'*indent+str(sv._get_objc_classname()))
			if 'UITableViewLabel' in str(sv._get_objc_classname()):
				#print(sv.text())
				if str(sv.text()) == 'com~apple~CloudDocs':
					#print(dir(sv))
					sv.setText_('iCloud Drive')
				elif str(sv.text()) == 'File Provider Storage':
					device = ObjCClass('UIDevice').currentDevice()
					sv.setText_('On my '+str(device.model()))
				elif str(sv.text()) == 'Google Drive.png':
					#print(sv)
					UITableViewCellContentView = sv.superview() 
					cell = UITableViewCellContentView.superview()
					UITableView = cell.superview()
					#print(UITableView)
					for sv2 in UITableView.subviews():
						if 'SUIButton_PY3' in str(sv2._get_objc_classname()):
							sv2.removeFromSuperview()						
					y = cell.frame().origin.y 
					w = cell.frame().size.width
					h = cell.frame().size.height
					b = ui.Button()
					b.background_color = 'white'
					b.frame = (0,y,w,h-1)
					b.action = b_action
					bo = ObjCInstance(b)
					UITableView.addSubview_(bo)
					x = sv.frame().origin.x
					y = sv.frame().origin.y
					w = sv.frame().size.width
					h = sv.frame().size.height
					iv = ui.ImageView()
					x1 = (x-h)/2
					h1 = h - 4
					iv.frame = (x1+2,2,h1,h1)
					iv.image = ui.Image.named('Google Drive.png')
					b.add_subview(iv)
					l = ui.Label()
					l.frame = (x,y,w,h)
					l.background_color = 'white'
					l.text = 'Google Drive'
					b.add_subview(l)
					xi,yi,wi,hi,icon_uiimage = folder_icon
					ic = ui.ImageView()
					ic.frame = (xi,yi,wi,hi)
					with ui.ImageContext(wi,hi) as ctx:
						icon_uiimage.drawAtPoint_(CGPoint(0,0))
						ic.image = ctx.get_image()					
					b.add_subview(ic)	
					retain_global(b)				
			elif '_UITableCellAccessoryButton' in str(sv._get_objc_classname()):
				# just to known its frame and icon for folder
				if not folder_icon:
					x = sv.frame().origin.x
					y = sv.frame().origin.y
					w = sv.frame().size.width
					h = sv.frame().size.height				
					img = sv.backgroundImageForState_(0)
					folder_icon = (x,y,w,h,img)
			ret = analyze(sv,indent+1)
	analyze(main_view,0)	
	
if __name__ == '__main__':
	main()	
