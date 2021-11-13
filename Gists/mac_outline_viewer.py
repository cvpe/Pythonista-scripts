#!/usr/bin/env python3
# coding: utf-8
'''
Versions
  V0.04
    - use a dropdown selector to choose which dates to show
  V0.03
    - show if item is unchecked, checked, completed or without checkbox
  V0.02
    - runs on Mac and in Pythonista on iPad/iPhone
    - generates a web page (without images, font attributes, links...)
    - opens a new tab in Safari to display the html
  V0.01
    - optional path of outline file passed as argument
  V0.00
    - base version
    
todo

- 
'''

from __future__ import print_function, absolute_import
from   ast      import literal_eval
import os
import platform
import sys
machine = platform.machine().lower()
ios = 'ipad' in machine or 'iphone' in machine
if ios:
	import dialogs	
	import http.server
	import webbrowser
	class MyHandler (http.server.BaseHTTPRequestHandler):
		def do_GET(s):
			global redirect_page
			s.send_response(200)
			s.send_header('Content-Type', 'text/html')
			s.end_headers()
			s.wfile.write(redirect_page)
		def log_message(self, format, *args):
			pass	
else:
	from   tkinter  import *
	from   tkinter.filedialog import askopenfilename
	root = Tk()
	root.withdraw()

valid_types = [("Outline files", "*.outline")]

RED = '\033[91m'
BLUE = '\033[94m'

def clear():
	os.system('clear')

def main():
	if len(sys.argv) == 1:
		if ios:
			file_path = dialogs.pick_document()
		else:
			default_path = os.path.expanduser('~/Desktop/Users/Christian/Pythonista/Backup/Outline')
			file_path = askopenfilename(initialdir=default_path,
                                 message="Choose one outline file",
                                 multiple=False,
                                 title="Outline Selector",
                                 filetypes=valid_types)
	else:
		file_path = sys.argv[1]
	if not file_path:
		sys.exit("User cancelled")
	clear()
	#print(file_path, end='\n')
	with open(file_path, mode='rt', encoding='utf-8', errors="surrogateescape") as fil:
		body = ''
		c = fil.read()
		c_prms = c.split('\n')
		c = c_prms[0]
		cs = literal_eval(c)
		del c
		del c_prms
		for c in cs:
			vals,outline,opts,dict_text = c
			chk = opts.get('checkmark','')
			dates = opts.get('dates',None)
			if chk == 'yes':
				chk = '✅'
			elif chk == 'hidden':
				chk = '  '
			else:
				chk = '⬜️'
				if dates:
					due_date = dates[2]
					if due_date:
						chk = '🕦'
			text = dict_text['text']	
			if not dates:
				dates = [None,None,None,None]
			crea = dates[0][:10] if dates[0] else '&nbsp&nbsp'*10
			upda = dates[1][:10] if dates[1] else '&nbsp&nbsp'*10
			dued = dates[2][:10] if dates[2] else '&nbsp&nbsp'*10
			endd = dates[3][:10] if dates[3] else '&nbsp&nbsp'*10
			body += f"<p ><span name='crea'; style='display:none';>{crea} </span><span name='upda'; style='display:none';>{upda} </span><span name='dued'; style='display:none';>{dued} </span><span name='endd'; style='display:none';>{endd} </span><span class='outline'>{chk} {outline}</span> <span class='text'>{text}</span></p><hr>"
			#print(f"{RED}{outline} {BLUE}{text}")
		del text
		del cs
	html = '''
		<html>
			<meta charset="UTF-8">
			<head>
				<style>
					* {max-width: 100%;}
					p {  margin-top: 0em; margin-bottom: 0em; }
					.outline 
						{color: red; font-family: menlo; white-space: pre; }
					.text    
						{color: blue; font-family: menlo; white-space: pre; 
						overflow-wrap:break-word; }
				</style>
				<title>
					FNAME
				</title>
			</head>
			<body {font-family:monospace;}>	
				<p>If you want to display a date, select it:</p>
				<p>
					<select id = "select_date" onchange="toggle()">
						<option value = "none" selected>none</option>
						<option value = "crea">creation date</option>
						<option value = "upda">update date</option>
						<option value = "dued">due date</option>
						<option value = "endd">completed date</option>
					</select>
				</p><br>
				BODY	
			</body>
			<script>
				function toggle() {
					var d = document.getElementById("select_date").value;
					var types = ['crea','upda','dued','endd']
					for (i = 0; i < types.length; i++) { 					
						type = types[i]
						var conts = document.getElementsByName(type);
						for (j = 0; j < conts.length; j++) { 
							cont = conts[j]
							if (type == d) {
								cont.style.display = 'inline';
							} else {
								cont.style.display = 'none';																
							}
						}
					}
				}
			</script>
		</html> ​
'''
	fname = 'mac_outline_viewer.html'
	i = file_path.rfind('/')
	outline_name = file_path[i+1:]
	html = html.replace('FNAME', outline_name)
	html = html.replace('BODY', body)
	#print(html)
	with open(fname,mode='wt',encoding='utf-8') as fil:
		fil.write(html)		
	if ios:
		global redirect_page
		redirect_page = html.encode()
		httpd = http.server.HTTPServer(('', 0), MyHandler)
		port = str(httpd.socket.getsockname()[1])
		webbrowser.open('safari-http://localhost:' + port)
		httpd.handle_request()
	else:
		os.system("open /Applications/Safari.app file:///"+os.getcwd()+"/"+fname)	

if __name__ == '__main__':
	sys.exit(main())
