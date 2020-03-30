import swizzle
from objc_util import *

def initWithURL_(_self,_sel, _url):
	from objc_util import ObjCInstance
	import os
	from pygments import highlight
	from pygments.lexers import PythonLexer
	from pygments.formatters import HtmlFormatter
	from pygments.styles import get_style_by_name
	import re
	global search_term
	self = ObjCInstance(_self) # PA2QuickHelpContentViewController
	url = ObjCInstance(_url)
	if 'myfile://' in str(url):
		t = str(url)
		i = t.find('myfile://')
		t = t[i+2:]
		url = nsurl(t)	# file:///...
		tx = '/Pythonista3/Documents/'
		i = t.find(tx) + len(tx)
		j = t.find('#')
		path = t[i:j]
		path = path.replace('~',' ')
		self.setTitle_(path)
					
		fpath = os.path.expanduser('~/Documents/' + path)
		
		with open(fpath, mode='rt', encoding='utf-8', errors='ignore') as fil:
			code = fil.read()
					
		# Syntax-highlight code
		# from omz code at https://forum.omz-software.com/topic/1950/syntax-highlight-python-code-on-screen-while-running
		html_formatter = HtmlFormatter(style='colorful')
		l = PythonLexer()
		l.add_filter('whitespace', tabs=' ', tabsize=2)
		highlighted_code = highlight(code, l, html_formatter)
		styles = html_formatter.get_style_defs()
		
		# change html code to highlight searched term with yellow background
		styles = styles + '\n' + '.search { background-color: #ffff00 } /* search term */'
		highlighted_code = highlighted_code.replace(search_term, '</span><span class="search">' + search_term + '</span>')
		
		# add class to searched term independantly of case
		src_str  = re.compile('('+search_term+')', re.IGNORECASE) 
		# @Olaf: use \1 to refer to matched text grouped by () in the regex
		highlighted_code = src_str.sub(r'</span><span class="search">\1</span>', highlighted_code)
		
		# meta tag UTF-8 is needed to display emojis if present in a script 		
		html = '<html><head><meta charset="UTF-8"><style>%s</style></head><body> %s </body></html>' % (styles, highlighted_code)

		fpath = os.path.expanduser('~/Documents/find_in_files_via_help.html') 
		# segmentation error crash if write file in text mode
		#with open(fpath, mode='wb') as fil:
		#	fil.write(html.encode())
		with open(fpath, mode='wt',encoding='utf8') as fil:
			fil.write(html)
		url = nsurl('file://'+fpath)
	rtnval = self.originalinitWithURL_(url) 
	return rtnval.ptr

def setSearchResults_(_self,_sel,_search_results):
	from objc_util import ObjCInstance, ns
	import os
	global search_term
	self=ObjCInstance(_self)	# PA2QuickHelpViewController
	#print(dir(self))
	search_term = str(self.searchTerm())
	search_results = ObjCInstance(_search_results)
	#print(search_results)
	new_search_results = []
	
	# if Pythonista help also needed
	for elem in search_results:
		new_search_results.append(ns(elem))

	path = os.path.expanduser('~/Documents')
	tx = '/Pythonista3/Documents/'
	se = search_term.lower()

	# search all .py. Tests show that os.scandir is quicker than os.walk
	def scantree(path):
		"""Recursively yield DirEntry objects for given directory."""
		for entry in os.scandir(path):
			if entry.is_dir(follow_symlinks=False):
				scantree(entry.path)
			else:
				fpath = entry.path
				if os.path.splitext(entry.path)[-1].lower() != ".py":
					continue
	#for root, dirs, files in os.walk(path):
	#	for f in files:
	#		fpath = os.path.join(root, f)
	#		if os.path.splitext(fpath)[-1].lower() in [".py"]:	
				with open(fpath, mode='rt', encoding='utf-8', errors='ignore') as fil:
					content = fil.read().lower()
					if se not in content:
						continue
				# segmentation error crash if url or title contains a blank,
				# even if contains %20 instead of blank
				# thus replace blank by ~ (allowed character in url)
				# url is zip:///...myfile:///...#title
				my_path = 'myfile://' + fpath.replace(' ','~') # temporary
				i = fpath.find(tx) + len(tx)
				t = fpath[i:]
				t = t.replace(' ','~')
				typ = 'mod' # mod,exception,attribute,method,class,function,data
				new_search_results.append(ns({'path':my_path, 'rank':10, 'title':t, 'type':typ}))		
	scantree(path)	
	
	#print('search:',self.searchTerm(),'results=',new_search_results)
	self.originalsetSearchResults_(new_search_results)
	
cls=ObjCClass('PA2QuickHelpContentViewController')
swizzle.swizzle(cls,'initWithURL:',initWithURL_)

cls2 = ObjCClass('PA2QuickHelpViewController')		
swizzle.swizzle(cls2,'setSearchResults:',setSearchResults_)

