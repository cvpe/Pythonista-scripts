# code needs to install xhtml2pdf in site-packages
# via stash/pip install xhtml2pdf
import editor
import os
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name
from xhtml2pdf import pisa

# Syntax-highlight code
# from omz code at https://forum.omz-software.com/topic/1950/syntax-highlight-python-code-on-screen-while-running
code = editor.get_text()
html_formatter = HtmlFormatter(style='colorful')
highlighted_code = highlight(code, PythonLexer(), html_formatter)
styles = html_formatter.get_style_defs()
html = '<html><head><style>%s</style></head><body>%s</body></html>' % (styles, highlighted_code)

# html -> pdf
file_name = os.path.basename(os.path.splitext(editor.get_path())[0]) + '.pdf'
with open(file_name, 'wb') as fil:
	pisa.CreatePDF(html,fil)
