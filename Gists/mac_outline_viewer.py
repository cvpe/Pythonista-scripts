#!/usr/bin/env python3
# coding: utf-8
'''
Versions
  V0.05
    - support sort on dates
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
- sort on dates via a second dropdown: none, ascending, descending
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
		body_none = ''
		body_crea_none = ''
		body_crea_asce = ''
		body_crea_desc = ''
		body_upda_none = ''
		body_upda_asce = ''
		body_upda_desc = ''
		body_dued_none = ''
		body_dued_asce = ''
		body_dued_desc = ''
		body_endd_none = ''
		body_endd_asce = ''
		body_endd_desc = ''
		c = fil.read()
		c_prms = c.split('\n')
		c = c_prms[0]
		cs = literal_eval(c)
		del c
		del c_prms
		rows_with_dates = []
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
			rows_with_dates.append((crea,upda,dued,endd,chk,outline,text))
		for i in range(len(rows_with_dates)):
			j = i
			crea,upda,dued,endd,chk,outline,text = rows_with_dates[j]
			body_none += f"<p ><span class='outline'>{chk} {outline}</span> <span class='text'>{text}</span></p><hr>"
			body_crea_none += f"<p ><span>{crea} </span><span class='outline'>{chk} {outline}</span> <span class='text'>{text}</span></p><hr>"
			body_upda_none += f"<p ><span>{upda} </span><span class='outline'>{chk} {outline}</span> <span class='text'>{text}</span></p><hr>"
			body_dued_none += f"<p ><span>{dued} </span><span class='outline'>{chk} {outline}</span> <span class='text'>{text}</span></p><hr>"
			body_endd_none += f"<p ><span>{endd} </span><span class='outline'>{chk} {outline}</span> <span class='text'>{text}</span></p><hr>"
			crea,upda,dued,endd,chk,outline,text = sorted(rows_with_dates,key=lambda x:x[0])[i] # sort ascending
			body_crea_asce += f"<p ><span>{crea} </span><span class='outline'>{chk} {outline}</span> <span class='text'>{text}</span></p><hr>"
			crea,upda,dued,endd,chk,outline,text = sorted(rows_with_dates,key=lambda x:x[0], reverse=True)[i] # sort descending
			body_crea_desc += f"<p ><span>{crea} </span><span class='outline'>{chk} {outline}</span> <span class='text'>{text}</span></p><hr>"
			crea,upda,dued,endd,chk,outline,text = sorted(rows_with_dates,key=lambda x:x[1])[i] # sort ascending
			body_upda_asce += f"<p ><span>{upda} </span><span class='outline'>{chk} {outline}</span> <span class='text'>{text}</span></p><hr>"
			crea,upda,dued,endd,chk,outline,text = sorted(rows_with_dates,key=lambda x:x[1], reverse=True)[i] # sort descending
			body_upda_desc += f"<p ><span>{upda} </span><span class='outline'>{chk} {outline}</span> <span class='text'>{text}</span></p><hr>"	
			crea,upda,dued,endd,chk,outline,text = sorted(rows_with_dates,key=lambda x:x[2])[i] # sort ascending
			body_dued_asce += f"<p ><span>{dued} </span><span class='outline'>{chk} {outline}</span> <span class='text'>{text}</span></p><hr>"
			crea,upda,dued,endd,chk,outline,text = sorted(rows_with_dates,key=lambda x:x[2], reverse=True)[i] # sort descending
			body_dued_desc += f"<p ><span>{dued} </span><span class='outline'>{chk} {outline}</span> <span class='text'>{text}</span></p><hr>"
			crea,upda,dued,endd,chk,outline,text = sorted(rows_with_dates,key=lambda x:x[3])[i] # sort ascending
			body_endd_asce += f"<p ><span>{endd} </span><span class='outline'>{chk} {outline}</span> <span class='text'>{text}</span></p><hr>"
			crea,upda,dued,endd,chk,outline,text = sorted(rows_with_dates,key=lambda x:x[3], reverse=True)[i] # sort descending
			body_endd_desc += f"<p ><span>{endd} </span><span class='outline'>{chk} {outline}</span> <span class='text'>{text}</span></p><hr>"
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
				<p>If you want to sort on dates, select it:</p>
				<p>
					<select id = "select_sort" onchange="toggle()">
						<option value = "_none" selected>none</option>
						<option value = "_asce">ascending dates</option>
						<option value = "_desc">descending dates</option>
					</select>
				</p><br>
				<div id='none'; style='display:block'>BODY_NONE</div>
				<div id='crea_none'; style='display:none'>BODY_CREA_NONE</div>
				<div id='crea_asce'; style='display:none'>BODY_CREA_ASCE</div>
				<div id='crea_desc'; style='display:none'>BODY_CREA_DESC</div>
				<div id='upda_none'; style='display:none'>BODY_UPDA_NONE</div>
				<div id='upda_asce'; style='display:none'>BODY_UPDA_ASCE</div>
				<div id='upda_desc'; style='display:none'>BODY_UPDA_DESC</div>
				<div id='dued_none'; style='display:none'>BODY_DUED_NONE</div>
				<div id='dued_asce'; style='display:none'>BODY_DUED_ASCE</div>
				<div id='dued_desc'; style='display:none'>BODY_DUED_DESC</div>
				<div id='endd_none'; style='display:none'>BODY_ENDD_NONE</div>
				<div id='endd_asce'; style='display:none'>BODY_ENDD_ASCE</div>
				<div id='endd_desc'; style='display:none'>BODY_ENDD_DESC</div>
			</body>
			<script>
				function toggle() {
					var d = document.getElementById("select_date").value;
					if (d == 'none') {
						var s = '';
					} else {
						var s = document.getElementById("select_sort").value;
					}
					var types = ['none', 'crea_none', 'upda_none', 'dued_none', 'endd_none', 'crea_asce', 'upda_asce', 'dued_asce', 'endd_asce', 'crea_desc', 'upda_desc', 'dued_desc', 'endd_desc'];
					for (i = 0; i < types.length; i++) { 					
						var type = types[i];
						var div = document.getElementById(type);
						if (type == (d+s)) {
							div.style.display = 'block';
						} else {
							div.style.display = 'none';														
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
	html = html.replace('BODY_NONE', body_none)
	html = html.replace('BODY_CREA_NONE', body_crea_none)
	html = html.replace('BODY_CREA_ASCE', body_crea_asce)
	html = html.replace('BODY_CREA_DESC', body_crea_desc)
	html = html.replace('BODY_UPDA_NONE', body_upda_none)
	html = html.replace('BODY_UPDA_ASCE', body_upda_asce)
	html = html.replace('BODY_UPDA_DESC', body_upda_desc)
	html = html.replace('BODY_DUED_NONE', body_dued_none)
	html = html.replace('BODY_DUED_ASCE', body_dued_asce)	
	html = html.replace('BODY_DUED_DESC', body_dued_desc)
	html = html.replace('BODY_ENDD_NONE', body_endd_none)
	html = html.replace('BODY_ENDD_ASCE', body_endd_asce)
	html = html.replace('BODY_ENDD_DESC', body_endd_desc)
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
