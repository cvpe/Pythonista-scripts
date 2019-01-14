import ui
import objc_util
import sys

def VersionInStatusBar(version=False):	
	# called at begin of a script with version=text
	#           end                    version=False
	root, ext = os.path.splitext(sys.argv[0])  # script path without .py
	script_name = os.path.basename(root)  # script name without the path
	app = objc_util.UIApplication.sharedApplication()
	w = objc_util.ObjCClass('UIApplication').sharedApplication().keyWindow()
	main_view = w.rootViewController().view()
	bar = app.statusBar()
	b = bar.bounds()
	sv = bar.subviews()
	for v in sv:
		if v._get_objc_classname().startswith(b'SUILabel_PY3'):
			v.removeFromSuperview()
			del v
			if not version:		# remove version label 
				return
	lbl = ui.Label()
	lbl.frame = (200,2,23,16)
	lbl.text_color = 'blue'
	lbl.border_width = 1
	lbl.border_color = 'blue'
	lbl.font = ('Courier-Bold',12)
	lbl.text = script_name+': version='+version
	lbl.width = ui.measure_string(lbl.text,font=lbl.font)[0]
	lbl = lbl
	bar.addSubview_(lbl)
	
#VersionInStatusBar(version='test')
#VersionInStatusBar(version=False)
