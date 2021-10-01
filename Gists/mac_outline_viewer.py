#!/usr/bin/env python3
# coding: utf-8
'''
Versions
  0.00
   - base version
  0.01
   - optional path of outline file passed as argument
'''

from __future__ import print_function, absolute_import
from   ast      import literal_eval
import os
import sys
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
		default_path = os.path.expanduser('~/Desktop/Users/Christian/Pythonista/Backup/Outline')

		file_path = askopenfilename(initialdir=default_path,
                             message="Choose one outline file",
                             multiple=False,
                             title="Outline Selector",
                             filetypes=valid_types)
		if not file_path:
			sys.exit("User cancelled")
	else:
		file_path = sys.argv[1]
	clear()
	#print(file_path, end='\n')
	with open(file_path, mode='rt', encoding='utf-8', errors="surrogateescape") as fil:
		c = fil.read()
		c_prms = c.split('\n')
		c = c_prms[0]
		cs = literal_eval(c)
		del c
		del c_prms
		for c in cs:
			vals,outline,opts,dict_text = c
			text = dict_text['text']					
			print(f"{RED}{outline} {BLUE}{text}")
		del text
		del cs
	#os.system("open /Applications/Safari.app file:///"+os.getcwd()+"/test.html")	

if __name__ == '__main__':
	sys.exit(main())
