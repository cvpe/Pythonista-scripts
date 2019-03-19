# code needs to install xhtml2pdf in site-packages
# via stash/pip install xhtml2pdf
import editor
import os
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name
from xhtml2pdf import pisa
from objc_util import *

def GetConsoleText():
	win = ObjCClass('UIApplication').sharedApplication().keyWindow()
	main_view = win.rootViewController().view()	
	ret = '' 
	def analyze(v):
		ret = None
		for sv in v.subviews():
			if 'textview' in str(sv._get_objc_classname()).lower():
				if 'OMTextEditorView' not in str(sv.superview()._get_objc_classname()):	# not TextView of script
					return str(sv.text())
			ret = analyze(sv)
			if ret:
				return ret
	ret = analyze(main_view)
	return ret

# Syntax-highlight code
# from omz code at https://forum.omz-software.com/topic/1950/syntax-highlight-python-code-on-screen-while-running
code = editor.get_text() + '\n' + GetConsoleText()
html_formatter = HtmlFormatter(style='colorful')
highlighted_code = highlight(code, PythonLexer(), html_formatter)
styles = html_formatter.get_style_defs()
html = '<html><head><style>%s</style></head><body>%s</body></html>' % (styles, highlighted_code)

# html -> pdf
file_name = os.path.splitext(editor.get_path())[0] + '.pdf'
with open(file_name, 'wb') as fil:
	pisa.CreatePDF(html,fil)
