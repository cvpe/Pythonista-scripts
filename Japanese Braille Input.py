# https://forum.omz-software.com/topic/5584/braille-application
#
# Version 1.3
# - new: buttons up,ok, down in conversion list will have as variable title
#				 a sentence as example of the kanji which would be generated if
#			 	 pressed 
# Version 1.2
# - bug: left delete during tableview does not hide scroll and ok 3 buttons
# - new: buttons title instead of image, so VoiceOver may speach it
#        	- title in Japanese
# 				- background_image instead of image so visible even if long title
# - new: buttons up,ok, down in conversion list will have as variable title
#				 the kanji which would be generated if pressed 
# Version 1.1
# - bug: dot 5 prefix does not work since dot-5 point
#				 temporary remove dot 5 point
# Version 1.0
# - new: use ObjectiveC AVSpeechSynthesizer instead of Pythonista speech
#				 because speech does not work on iPad mini 4 and iPhone XS Max
# Version 0.9
# - new: support some punctuation with 2 characters: —
# - new: speech selected Kanji sent to TextField
# - mod: bigger font and rowheight of Kanji's conversion list
# - new: kanji's tableview scroll and select via buttons
#				 - current element is red, if you tap ✅, it will be sent to Textfield
#				 - bug: I can't actually put this current element at first visible
#								row because content_offset does not work like I think
#								wait and see
# Version 0.8
# - new: support Yō-on, displayed as Katakana
#	- new: support arab digits with special process:
#				 prefix is valable until next char is not a digit 
#          or an hyphen which is not displayed.
#				 But the following process has to be done by user:
#         "Words immediately follow numbers, unless they begin with a vowel or 
#          with r-. 
#          Because the syllables a i u e o and ra ri ru re ro are homographic
#          with the digits 0–9, an hyphen is inserted to separate them.
#          Thus 6人 "six people" (6 nin) is written w/o hyphen'' ⠼⠋⠇⠴ ⟨6nin)
#          but 6円 "six yen" (6 en) is written with a hyphen, ⠼⠋⠤⠋⠴ ⟨6-en⟩,
#          because ⠼⠋⠋⠴ would be read as ⟨66n⟩."
# - new: support Japanese punctuation of one single dots set: -。？！、・
# Version 0.7
# - bug corrected: sqlite3 operationalerror accessing HiraganaToKanji.db
#                  was not intercepted
# - new: cursor left and right move buttons
# - new: support Hirgana with one/dot prefix for (han)dakuten
# Version 0.6
# - bug corrected: right column of vertical dots had inverted n°s
# Version 0.5
# - new: if conversion doesn't give any Kanji, send Hirgana's to TextField
#        without passing via the TextView
# Version 0.4
# - new: add Hirgana's as 1st element in Kanji's list, in green color
# - new: supports Braille dots buttons 
#				 - vertically  : default or argument v
#				 - horizontally: argument h
# - new: delete button deletes temporary dots character if in progress
# - bug corrected: delete button during Kanji selection did not hide
#									 the Kanji's list TableView
# Version 0.3
# - new: use keychain to save and restore Braille dots positions
#        service=Braille account=Portrait or Landscape
#        password = '{'dot n°':(x,y),...}'
# - bug corrected: if dots not tapped together, some ones can be lost 
#                  due to reuse by system of same touch_id 
# Version 0.2
# - bug corrected: back after close (x), gray hirgana was not cleared
# - bug corrected: TextField not visible on iPhone
# - bug corrected: automatic buttons dimensions and positions for
#	                 ipad/iphone portrait/landscape Pythonista/custom keyboard
# Version 0.1
# - bug corrected: delete when cursor in TextField shows old Hirganas
# - bug corrected: tap ourside buttons was processed as invalid Braille dots
# - bug corrected: conversion button disappears if conversion gives no Kanji
# - bug corrected: hide conversion buttons if all hirganas deleted
# - bug corrected: back after close (x), closed conversion db error
# - bug corrected: back after close (x), hirganas were not cleared
# - bug corrected: ok button was even if dots combination was invalid
# - new: delete button deletes in textfield if no Hirgana in progress
# Version 0.0
# - initial draft version 
#
# still todo
# ==========
# - new: conversion list elements, sentence
#					- button? try another sentence
# - bug: content_offset not ok for tableview
# - bug: dot 5 point implies dot 5 prefix does not work
# - new: support ponctuation char used as start and end like (...)
# - left delete should delete also the prefix if exists, wait bug?
# - questions: do you want to 
#		- do you prefer conversion list as a grid of buttons instead tableview?
#		- how to differentiate dot5 point and dot5 prefix?
#		- generate a blank, if yes, how?
#		- titles of buttons could have transparent color, so we see icon?
#		- foresee a way to move the dots buttons and store their positions?
import ast
import console
from   datetime import datetime
import keychain
import Image, ImageDraw		
import io
from   objc_util import *
import os
import plistlib
import speech
import sqlite3
import sys
import ui

AVSpeechUtterance=ObjCClass('AVSpeechUtterance')
AVSpeechSynthesizer=ObjCClass('AVSpeechSynthesizer')
AVSpeechSynthesisVoice=ObjCClass('AVSpeechSynthesisVoice')
voices=AVSpeechSynthesisVoice.speechVoices()
synthesizer=AVSpeechSynthesizer.new()
for i in range(0,len(voices)):
	#print(i,voices[i],voices[i].description())
	if 'ja-JP' in str(voices[i].description()):
		voice_jp = i
		break

# @ccc code to get Pythonista Version 
# https://github.com/cclauss/Ten-lines-or-less/blob/master/pythonista_version.py
def pythonista_version():  # 2.0.1 (201000)
	plist = plistlib.readPlist(os.path.abspath(os.path.join(sys.executable, '..', 'Info.plist')))
	return '{CFBundleShortVersionString} ({CFBundleVersion})'.format(**plist)
w = pythonista_version()		# ex: 3.3 (330012)
PythonistaVersion = float(w.split(' ')[0])
#print(PythonistaVersion)
if PythonistaVersion >= 3.3:
	import keyboard	
	
class BrailleKeyboardInputAccessoryViewForTextField(ui.View):
	def __init__(self, frame=None,*args, **kwargs):
		super().__init__(self, *args, **kwargs)
		self.background_color = 'white' 
		
		self.multitouch_enabled = True
		self.touch_actives = {}
		self.touch_n = 0
		if frame:
			self.frame=frame

		# sources
		# -------
		# https://fr.wikipedia.org/wiki/Braille_japonais
		# http://web.archive.org/web/20090807085414/http:/www.hi.sfc.keio.ac.jp/access/arc/NetBraille/etc/brttrl.html#3.5
		# https://en.wikipedia.org/wiki/Japanese_Braille		
		
		# basic syllabes
		self.Japanese_Braille = {
		'1':'あ',			# ⠁
		'12':'い',			# ⠃
		'14':'う',			# ⠉
		'124':'え', 		# ⠋
		'24':'お',			# ⠊
		'16':'か',			# ⠡
		'126':'き',		# ⠣
		'146':'く',		# ⠩
		'1246':'け',		# ⠫
		'246':'こ',		# ⠪
		'156':'さ',		# ⠱
		'1256':'し',		# ⠳
		'1456':'す',		# ⠹
		'12456':'せ',	# ⠻
		'2456':'そ',		# ⠺
		'1256':'し',		# ⠳
		'1456':'す',		# ⠹
		'12456':'せ',	# ⠻
		'2456':'そ',		# ⠺
		'135':'た',		# ⠕
		'1235':'ち',		# ⠗
		'1345':'つ',		# ⠝
		'12345':'て',	# ⠟
		'2345':'と',		# ⠞
		'13':'な',			# ⠅
		'123':'に',		# ⠇ 
		'134':'ぬ',		# ⠍
		'1234':'ね',		# ⠏
		'234':'の',		# ⠎
		'136':'は',		# ⠥
		'1236':'ひ',		# ⠧
		'1346':'ふ',		# ⠭
		'12346':'へ',	# ⠯
		'2346':'ほ',		# ⠮
		'1356':'ま',		# ⠵
		'12356':'み',	# ⠷
		'13456':'む',	# ⠽
		'123456':'め',	# ⠿
		'23456':'も',	# ⠾
		'356':'ん',		# ⠴
		'34':'や',			# ⠌
		'346':'ゆ',		# ⠬
		'345':'よ',		# ⠜ 
		'15':'ら',			# ⠑
		'125':'り',		# ⠓
		'145':'る',		# ⠙
		'1245':'れ',		# ⠛
		'245':'ろ'	,		# ⠚
		'3':'わ',			# ⠄
		'23':'ゐ',			# ⠆
		'235':'ゑ',		# ⠖
		'35':'を',			# ⠔
		# dakuten list from http://www.yoihari.com/tenji/tdaku.htm
		'5':'_',			# needs another 2nd character
		'5|16':'',		# ⠐⠡
		'5|126':'',		# 
		'5|146':'',		# 
		'5|1246':'',	# 
		'5|246':'',		# 
		'5|156':'',		# 
		'5|1256':'',	# 
		'5|1456':'',	#
		'5|12456':'',	# 
		'5|2456':'',	# 
		'5|135':'',		# 
		'5|1235':'',	# 
		'5|1345':'',	# 
		'5|12345':'',	# 
		'5|2345':'',	# 
		'5|136':'',		# 
		'5|1236':'',	# 
		'5|1346':'',	#
		'5|12346':'',	# 
		'5|2346':'',	# 
		'6':'_',			# needs another 2nd character
		'6|136':'',		# 
		'6|1236':'',	# 	
		'6|1346':'',	# 	
		'6|12346':'',	#
		'6|2346':'',	# 
		# Yō-on       http://www.yoihari.com/tenji/tyou.htm
		'4':'_',			# needs another 2nd character
		'4|16':'キャ',	#
		'4|146':'キュ',#
		'4|246':'キョ',#
		'4|156':'シャ',#
		'4|1456':'シュ',#
		'4|2456':'ショ',#
		'4|135':'ヂャ',#
		'4|1345':'チュ',#
		'4|2345':'チョ',#
		'4|13':'ニャ',	#
		'4|134':'ニュ',#
		'4|234':'ニョ',#
		'4|136':'ヒャ',#
		'4|1346':'ヒュ',#
		'4|2346':'ヒョ',#
		'4|1356':'ミャ',#
		'4|13456':'ミュ',#
		'4|23456':'ミョ',#
		'4|15':'リャ',	#
		'4|145':'リュ',#
		'4|245':'リョ',#
		'46':'_',			# needs another 2nd character
		'46|136':'ピャ',	#
		'46|1346':'ピュ',#
		'46|2346':'ピョ',#
		'45':'_',			# needs another 2nd character
		'45|16':'ギャ',	#
		'45|146':'ギュ',	#
		'45|246':'ギョ',	#
		'45|156':'ジャ',	#
		'45|1456':'ジュ',#
		'45|2456':'ジョ',#
		'45|135':'ヂャ',	#
		'45|1345':'ヂュ',#
		'45|2345':'ヂョ',#
		'45|136':'ビャ',	#
		'45|1346':'ビュ',#
		'45|2346':'ビョ',#
		# arab digits http://www.yoihari.com/tenji/tsuji.htm
		'3456':'_',			# needs another 2nd character
		'3456|1':'1',		#
		'3456|12':'2',	#
		'3456|14':'3',	#
		'3456|145':'4',	#
		'3456|15':'5',	#
		'3456|124':'6',	#
		'3456|1245':'7',#
		'3456|125':'8',	#
		'3456|24':'9',	#
		'3456|245':'0',	#
		# punctuation http://www.yoihari.com/tenji/tkigo.htm
		# punctuation with 1 character
		'36':'-',				# hyphen: if end of arab digits, not displayed
		'256':'。'	,			# end point
		'26':'？',				#
		'235':'！',			#
		'56':'、',				# comma
		#'5':'・'	,				# inter words point
		# punctuation with 2 characters
		'25':'_',				# needs another 2nd character
		'25|25':'—'
		#'36|36':'~',# comment ne pas confondre avec hyphen?=============
		# punctuation with 3 characters
		#'25|25|134':'→',#
		#'246|25|25':'←',#
		# punctuation with 4 characters
		#'246|25|25|134':'⟷',#
		# punctuation with start and end characters
		#'2356':,'()'		#
		}
		
		# Generate dakuten characters from their prefix/dot and dots	
		for ele in self.Japanese_Braille.keys():
			i = ele.find('|')
			if i >= 0:													# ex: 5|1345			
				prefix = ele[:i]									# ex: 5
				k = ele[i+1:]											# ex:	1345
				ch = self.Japanese_Braille[k]			# ex: つ
				if prefix == '5':
					d = 1														# ex: 5 -> 1  
				elif prefix == '6':
					d = 2
				else:
					continue													# ex: 4
				b = ch.encode('utf-8')						# ex: b'\xe3\x81\x8b'
				n = b[:-1] + bytes([int(b[-1])+d])# ex: b'\xe3\x81\x8c'
				c = str(n,'utf-8')								# ex: か -> が          へ -> ぺ
				self.Japanese_Braille[ele] = c	
		
		self.prefix = ''
		
		# other symbols exist: sokuon, chōon, yōon, handakuten, gōyōon
		# see https://en.wikipedia.org/wiki/Japanese_Braille
		# for their dots combinations
		
		# https://github.com/Doublevil/JmdictFurigana		
		self.conn = sqlite3.connect("HiraganaToKanji.db",check_same_thread=False)
		self.cursor = self.conn.cursor()
		
		# get sentences as examples for Kanjis
		# https://www.manythings.org/anki/
		with open('SentencesEngJpn.dat',encoding='utf-8') as fil:
			l = fil.read()
			self.sentences = l.split('\n')
			del l

		# build dots buttons but bounds not yet known in init, let some delay		
		ui.delay(self.dimensions,0.1)
		
	def dimensions(self):		
		
		wk, hk = self.bounds.size
		#wk,hk = 756,237		# ipad mini 4
		#wk,hk = 320,237	 	# iphone 5S
		d = 48		# size of other buttons (close, delete, ...)
		db = 4
		z = 'v'
		if not self.custom_keyboard:
			if len(sys.argv) > 1:
				z = sys.argv[1]
		if z == 'h':
			diam = int((wk-d-7*db)/6)
			dy = int((hk - d - diam - db)/2)
			dx = int((wk - d - 6*diam)/7)
			x0 = dx + d
			dx = dx + diam
			y0 = d
			x1 = x0 + 3*dx
		else:
			diam = (hk - 4*db)/3
			dx = 0
			dy = diam + db
			x0 = db + d + db	
			y0 = db	
			x1 = wk - x0 - diam
		if wk < hk:
			self.mode = 'Portrait'
		else:
			self.mode = 'Landscape'
		#print(wk,hk,r,d)
		
		# get/set circle positions	
		settings_str = None	
		#settings_str = keychain.get_password('Braille',self.mode)
		if settings_str:
			self.settings = ast.literal_eval(settings_str) # convert str -> dict
		else:	
			self.settings = {}

		x = x0 
		y = y0 
		for i in range(1,7):
			b = ui.Button()
			b.name = str(i)
			b.background_color = (1,0,0,0.5)
			b.tint_color = (1,1,1,0.8)
			b.font = ('Academy Engraved LET',diam/2)
			b.corner_radius = diam/2
			b.title = b.name
			if settings_str:
				x,y = self.settings[b.name]
			else:
				self.settings[str(i)] = (x,y)
			b.frame = (x,y,diam,diam)
			#b.TextField = tf # store tf as key attribute  needed when pressed
			b.touch_enabled = False
			self.add_subview(b)
			x = x + dx
			if i < 3:
				y = y + dy
			if i == 3:
				x = x1
				if z == 'v':
					y = y0
					dy = -dy
			elif i > 3:
				y = y - dy
				
		if not settings_str:
			self.save_settings()
			
		self.buttons_titles = {
			'b_close':'キーボードを閉じる',
			'b_delete':'左削除',
			'b_left':'左に移動',
			'b_right':'右に動く',
			'b_fecision':'点字OK',
			'b_conversion':'漢字',
			'kanjis_up':'漢字アップ',
			'kanjis_ok':'漢字は大丈夫',
			'kanjis_down':'漢字'
		}
		self.select_text = '選択する '
		
		b_close = ui.Button(name='b_close')
		b_close.frame = (2,2,d,d)
		b_close.corner_radius = d/2
		b_close.background_color = (0.8,0,0,0.5)
		b_close.background_image = ui.Image.named('iob:ios7_close_outline_32')
		b_close.action = self.close_button_action
		self.add_subview(b_close)
		
		b_delete = ui.Button(name='b_delete')
		b_delete.frame = (2,hk-d-10,d,d)
		b_delete.corner_radius = 24
		b_delete.background_color = (0.8,0,0,0.5)
		b_delete.background_image = ui.Image.named('typb:Delete')
		b_delete.action = self.delete_button_action
		self.add_subview(b_delete)
		
		b_left = ui.Button(name='b_left')
		b_left.frame = (wk/2-d-10,hk-d-10,d,d)
		b_left.corner_radius = 24
		b_left.background_color = (0.8,0,0,0.5)
		b_left.background_image = ui.Image.named('typb:Left')
		b_left.action = self.left_button_action
		self.add_subview(b_left)
		
		b_right = ui.Button(name='b_right')
		b_right.frame = (wk/2+10,hk-d-10,d,d)
		b_right.corner_radius = 24
		b_right.background_color = (0.8,0,0,0.5)
		b_right.background_image = ui.Image.named('typb:Right')
		b_right.action = self.right_button_action
		self.add_subview(b_right)
					
		b_decision = ui.Button(name='b_decision')
		b_decision.frame = (wk-d-2,hk-d-10,d,d)
		b_decision.corner_radius = 24
		b_decision.background_color = (0.8,0,0,0.5)
		b_decision.background_image = ui.Image.named('iob:ios7_checkmark_outline_32')
		b_decision.action = self.decision_button_action
		b_decision.hidden = True
		self.add_subview(b_decision)
		
		dots = ui.ImageView(name='dots')
		self.dots_e = e = 3
		self.dots_d = d = 9
		self.dots_h = h = 4*e + 3*d
		self.dots_w = wd = 14 + d + e
		dots.frame = (100,0,wd,h)
		dots.hidden = True
		self.add_subview(dots)
		self.dots_xy = [(e,e),(e,e+(d+e)),(e,e+2*(d+e)),(14,e),(14,e+(d+e)),(14,e+2*(d+e))]
		prefix_dots = ui.ImageView(name='prefix_dots')
		prefix_dots.frame = (100,0,wd,h)
		prefix_dots.hidden = True
		self.add_subview(prefix_dots)
		self.dots_xy = [(e,e),(e,e+(d+e)),(e,e+2*(d+e)),(14,e),(14,e+(d+e)),(14,e+2*(d+e))]
		
		hirganas = ui.Label(name='hirganas')
		hirganas.frame = (wk/2,2,0,32)
		hirganas.text = ''
		hirganas.font = ('Menlo',32)
		hirganas.text_color = (0,0,1,1)	
		hirganas.border_color = 'lightgray'
		hirganas.border_width = 1
		self.add_subview(hirganas)
		self.hirganas = []
		
		hirgana = ui.Label(name='hirgana')
		hirgana.frame = (0,0,32,32)
		hirgana.text = ''
		hirgana.font = ('Menlo',32)
		hirgana.text_color = 'gray'	
		hirganas.add_subview(hirgana)
		
		b_conversion = ui.Button(name='b_conversion')
		b_conversion.frame = (0,2,32,32)
		b_conversion.corner_radius = 32/2
		b_conversion.background_color = (0.8,0,0,0.5)
		b_conversion.title = '漢字'
		b_conversion.hidden = True
		#b_conversion.background_image = ui.Image.named('iob:ios7_checkmark_outline_32')
		b_conversion.action = self.conversion_button_action
		self.add_subview(b_conversion)
		
		kanjis = ui.TableView(name='kanjis')
		kanjis.frame = (0,2+32,32,hk-(2+32+2))
		kanjis.allows_multiple_selection = False
		kanjis.border_color = 'lightgray'
		kanjis.border_width = 1
		kanjis.corner_radius = 5
		kanjis.data_source = ui.ListDataSource(items=[])
		kanjis.data_source.font = ('Menlo',64)
		kanjis.row_height = 64
		kanjis.delegate = self
		kanjis.data_source.tableview_cell_for_row = self.tableview_cell_for_row
		kanjis.hidden = True
		self.add_subview(kanjis)	
		
		# up, down play on content_offset of TableView (subclass of ScrollView)
		# y positions so buttons are equidistants
		# x position set later when tableview width is set
		h = kanjis.height
		d_b = 64
		e_b = (h-3*d_b)/4
		b1 = ui.Button(name='kanjis_up')
		b1.background_image = ui.Image.named('iob:arrow_up_c_32')
		b1.background_color = (0,1,0,0.5)
		y = kanjis.y + e_b
		b1.frame =(0,y,d_b,d_b)
		b1.corner_radius = b1.width/2
		b1.hidden = True
		b1.action = self.tableview_up
		self.add_subview(b1)
		
		b2 = ui.Button(name='kanjis_ok')
		b2.background_image = ui.Image.named('iob:checkmark_round_32')
		b2.background_color = (0,1,0,0.5)
		y = y + d_b + e_b
		b2.frame =(0,y,d_b,d_b)
		b2.corner_radius = b2.width/2
		b2.hidden = True
		b2.action = self.tableview_ok
		self.add_subview(b2)
		
		b3 = ui.Button(name='kanjis_down')
		b3.background_image = ui.Image.named('iob:arrow_down_c_32')
		b3.background_color = (0,1,0,0.5)
		y = y + d_b + e_b
		b3.frame =(0,y,d_b,d_b)
		b3.corner_radius = b3.width/2
		b3.hidden = True
		b3.action = self.tableview_down
		self.add_subview(b3)
		
		for sv in self.subviews:
			if type(sv) is ui.Button:
				bn = sv.name
				if bn in self.buttons_titles:
					if self.buttons_titles[bn] != '':
						sv.title = self.buttons_titles[bn]
						sv.image = None
						#sv.background_image = None
		
	def save_settings(self):
		settings_str = str(self.settings) # convert dict -> str
		settings_str = keychain.set_password('Braille',self.mode,settings_str)	

	def left_button_action(self,sender):	
		# move cursor left in textfield
		if self.custom_keyboard:	
			keyboard.move_cursor(-1)
		else:
			cursor = self.tfo.offsetFromPosition_toPosition_(self.tfo.beginningOfDocument(), self.tfo.selectedTextRange().start())
			if cursor <= 0:
				return
			cursor = cursor - 1
			# set cursor
			cursor_position = self.tfo.positionFromPosition_offset_(self.tfo.beginningOfDocument(), cursor)
			self.tfo.selectedTextRange = self.tfo.textRangeFromPosition_toPosition_(cursor_position, cursor_position)	
			
	def right_button_action(self,sender):	
		# move cursor right in textfield
		if self.custom_keyboard:	
			keyboard.move_cursor(+1)
		else:
			cursor = self.tfo.offsetFromPosition_toPosition_(self.tfo.beginningOfDocument(), self.tfo.selectedTextRange().start())
			cursor = cursor + 1
			# set cursor
			cursor_position = self.tfo.positionFromPosition_offset_(self.tfo.beginningOfDocument(), cursor)
			self.tfo.selectedTextRange = self.tfo.textRangeFromPosition_toPosition_(cursor_position, cursor_position)	
		
	def close_button_action(self,sender):
		#self.conn.close()
		if self.touch_actives != {}:
			self.touch_n = 0
			self.touch_actives = {}
		self.prefix = ''
		self['dots'].hidden = True
		self['prefix_dots'].hidden = True
		self['kanjis'].hidden = True
		self['hirganas'].text = ''
		self['hirganas']['hirgana'].text = ''
		self.hirganas =[]
		self['b_conversion'].hidden = True
		self['hirganas'].width = 0
		if not self.custom_keyboard:
			self.tf.end_editing()	
			return
		# we simulate 'dismiss keybord key' pressed
		o = ObjCInstance(sender)	# objectivec button
		while True:
			o = o.superview()
			if 'KeyboardInputView' in str(o._get_objc_classname()):
				KeyboardInputView = o
				break	
		self.b_lowest_right = None
		self.xo = 0
		self.yo = 0
		def analyze(v):	
			for sv in v.subviews():
				if 'uibuttonlabel' in str(sv._get_objc_classname()).lower():
					x = sv.superview().frame().origin.x
					y = sv.superview().frame().origin.y
					if y > self.yo:
						self.b_lowest_right = sv
						self.xo = x
						self.yo = y
					elif y == self.yo:
						if x > self.xo:
							self.b_lowest_right = sv
							self.xo = x
							self.yo = y			
				ret = analyze(sv)
		analyze(KeyboardInputView)

		b = self.b_lowest_right.superview()
		if 'uibutton' in str(b._get_objc_classname()).lower() or 'ckbkeybutton' in str(b._get_objc_classname()).lower():
			# simulate press the button	
			UIControlEventTouchUpInside = 255
			b.sendActionsForControlEvents_(UIControlEventTouchUpInside)
		
	def delete_button_action(self,sender):		
		if self['hirganas']['hirgana'].width > 0:
			# temporary hirgana in progress
			self['hirganas']['hirgana'].width = 0
			self.touch_n = 0
			self.touch_actives = {}
			self['dots'].hidden = True
			self['prefix_dots'].hidden = True
			self['b_decision'].hidden = True			
			self.draw_hirganas()
		elif len(self.hirganas) > 0:
			# Hirhanas in progress
			# process to delete last hirgana
			# one hirganas uses a variable number of characters, thus not easy to remove it at right of a text
			del self.hirganas[-1]
			t = ''
			for ch in self.hirganas:
				t += ch
			self['hirganas'].text = t
			self.draw_hirganas()
			# if Kanji selection was in progress, cancel it
			if not self['kanjis'].hidden:
				self['kanjis'].hidden = True
				self['kanjis_up'].hidden = True
				self['kanjis_ok'].hidden = True
				self['kanjis_down'].hidden = True
		else:		
			# process to delete in textfield
			if self.custom_keyboard:	
				keyboard.backspace(times=1)
			else:
				cursor = self.tfo.offsetFromPosition_toPosition_(self.tfo.beginningOfDocument(), self.tfo.selectedTextRange().start())
				if cursor > 0:
					self.tf.text = self.tf.text[:cursor-1] + self.tf.text[cursor:]
					cursor = cursor - 1
				# set cursor
				cursor_position = self.tfo.positionFromPosition_offset_(self.tfo.beginningOfDocument(), cursor)
				self.tfo.selectedTextRange = self.tfo.textRangeFromPosition_toPosition_(cursor_position, cursor_position)
		
	def decision_button_action(self,sender):	
		if self.touch_actives != {}:
			self.touch_n = 0
			self.touch_actives = {}
			self.key_pressed(self.seq)
			self['dots'].hidden = True
			#self['prefix_dots'].hidden = True
			self['b_decision'].hidden = True
			
	def conversion_button_action(self,sender):
		t = self['hirganas'].text
		items = [t]
		try:		
			self.cursor.execute(
			'select hiragana, kanji from Hiragana_to_Kanji where hiragana = ?',
			(t,))
		except Exception as e:
			console.hud_alert('be sure that HiraganaToKanji.db file is present', 'error', 3)
			
		w_max = 0
		for row in self.cursor:
			t = row[1]
			items.append(t)
		for t in items:
			w,h = ui.measure_string(t, font=self['kanjis'].data_source.font)
			w_max = max(w_max,w+50)
		sender.hidden = True
		self['kanjis'].data_source.items = items
		if len(items) == 1:
			self.tableview_did_select(self['kanjis'], 0, 0)
			return
		# Kanji's exist, display a TableView
		self['kanjis'].x = (self.width - w_max)/2
		self['kanjis'].width = w_max
		self['kanjis'].height = min(self.bounds.size[1]-(2+32+2), len(items)*self['kanjis'].row_height)
		self['kanjis'].hidden = False
		x = self['kanjis'].x + self['kanjis'].width + 10
		self['kanjis_up'].hidden = False
		self['kanjis_up'].x = x
		self['kanjis_ok'].hidden = False
		self['kanjis_ok'].x = x
		self['kanjis_down'].hidden = False
		self['kanjis_down'].x = x
		self['kanjis'].current = 0
		ui.delay(self.tableview_say_current,0.01)
		self['kanjis_ok'].title = self.select_text+self.get_kanji(0)
		self['kanjis_up'].title = self.get_kanji(-1)
		self['kanjis_down'].title = self.get_kanji(+1)
		
	def get_kanji(self,delta):
		i = self['kanjis'].current + delta
		if i < 0 or i == len(self['kanjis'].data_source.items):
			i = self['kanjis'].current
		kanji = self['kanjis'].data_source.items[i]
		for li in self.sentences:
			s = li.split('\t')
			try:
				if kanji not in s[1]:
					continue
				kanji = kanji + '  ' + s[1]
				break
			except Exception as e:
				# some lines are blank
				continue	
		return kanji
		
	def tableview_cell_for_row(self,tableview, section, row):
		cell = ui.TableViewCell()
		data = tableview.data_source.items[row]
		cell.text_label.font = ('Menlo',32)
		#cell.text_label.alignment = ui.ALIGN_LEFT
		if row == tableview.current:
			cell.text_label.text_color = 'red'
			cell.bg_color = 'lightgray'
		elif row == 0:
			cell.text_label.text_color = 'green'
		else:
			cell.text_label.text_color = 'black'
		cell.text_label.text = data
		return cell
		
	def tableview_up(self,sender):
		tableview = self['kanjis']
		if tableview.current > 0:
			tableview.current = tableview.current - 1
			self.table_view_scroll(tableview)
			ui.delay(self.tableview_say_current,0.01)
		self['kanjis_up'].title = self.get_kanji(-1)	# future title to hear
		self['kanjis_ok'].title = self.select_text+self.get_kanji(0)
		self['kanjis_down'].title = self.get_kanji(+1)
		
	def tableview_down(self,sender):
		tableview = self['kanjis']
		#print(dir(ObjCInstance(tableview)))
		if tableview.current < (len(tableview.data_source.items)-1):
			tableview.current = tableview.current + 1
			self.table_view_scroll(tableview)
			ui.delay(self.tableview_say_current,0.01)
		self['kanjis_up'].title = self.get_kanji(-1)	# future title to hear
		self['kanjis_ok'].title = self.select_text+self.get_kanji(0)
		self['kanjis_down'].title = self.get_kanji(+1)

	def table_view_scroll(self,tableview):
		x,y = tableview.content_offset
		y = float(tableview.current*tableview.row_height)
		#print(y)
		tableview.content_offset = (x,y)
		tableview.reload()
		#tableview.selected_row = tableview.current
		
	def tableview_ok(self,sender):
		tableview = self['kanjis']
		row = tableview.current
		self.tableview_did_select(tableview, 0, row)
		
	def tableview_say_current(self):
		return
		t = self['kanjis'].data_source.items[self['kanjis'].current]
		#speech.say(t,'jp-JP')
		utterance = AVSpeechUtterance.speechUtteranceWithString_(t)
		#the value that sounds good apparantly depends on ios version
		utterance.rate = 0.5
		#print(voices[voice_jp].description())
		utterance.voice = voices[voice_jp]
		utterance.useCompactVoice = False 
		synthesizer.speakUtterance_(utterance)
		
	def tableview_did_select(self, tableview, section, row):
		tableview.current = row
		self.tableview_say_current()
		t = tableview.data_source.items[row]
		# insert kanji
		if self.custom_keyboard:	
			keyboard.insert_text(t)	
		else:	
			cursor = self.tfo.offsetFromPosition_toPosition_(self.tfo.beginningOfDocument(), self.tfo.selectedTextRange().start())
			self.tf.text = self.tf.text[:cursor] + t + self.tf.text[cursor:]
			cursor = cursor + len(t)
			# set cursor
			cursor_position = self.tfo.positionFromPosition_offset_(self.tfo.beginningOfDocument(), cursor)
			self.tfo.selectedTextRange = self.tfo.textRangeFromPosition_toPosition_(cursor_position, cursor_position)
		self['kanjis'].hidden = True
		self['kanjis_up'].hidden = True
		self['kanjis_ok'].hidden = True
		self['kanjis_down'].hidden = True
		self['hirganas'].text = ''
		self.hirganas =[]
		self['b_conversion'].hidden = True
		self['hirganas'].width = 0
		
	def touch_began(self,touch):
		#print('touch_began',touch.location)
		bn = self.dot_touched(touch)
		if bn == '':
			return
		x0,y0 = touch.location
		self.touch_actives[touch.touch_id] = ((x0,y0),bn,touch.location)
		self.touch_n += 1
		if len(self.touch_actives) == 6:
			self.six_fingers_touch = datetime.now()
		self.dots_touched()
		
	def touch_moved(self,touch):
		if touch.touch_id not in self.touch_actives:
			return
		bn = self.dot_touched(touch)
		x0,y0 = self.touch_actives[touch.touch_id][0]
		self.touch_actives[touch.touch_id] = ((x0,y0),bn,touch.location)
		self.dots_touched()
		
	def touch_ended(self,touch):
		if touch.touch_id not in self.touch_actives:
			return
		x ,y  = touch.location
		self.touch_n -= 1			# but keep dict of touches
		# change key in self.touch_actives because if a new touch
		# begins, its touch_id could be reused, thus the same
		new_key = 'T'+str(len(self.touch_actives))+str(touch.touch_id)
		self.touch_actives[new_key] = self.touch_actives[touch.touch_id]
		del self.touch_actives[touch.touch_id]
		if self.touch_n > 0:
			# still at least one finger on screen
			return	
		# all fingers removed from screen
		if self.seq == '123456':#len(self.touch_actives) == 6:
			# 6 touches were active
			if (datetime.now() - self.six_fingers_touch).total_seconds() > 3:
				# six fingers stay on the screen at least 3 seconds
				# else, normal process for 6 dots tapped
				l = []
				for touch_id in self.touch_actives.keys():
					x,y = self.touch_actives[touch_id][2]
					l.append((x,y))
				# sort on ascending x
				l = sorted(l,key=lambda x: x[0])
				l_left  = l[0:3]
				# sort the 3 first ones (thus at left) on ascending y
				l_left  = sorted(l_left ,key=lambda x: x[1])			
				l_right = l[3:6]
				# sort the 3 others on ascending y
				l_right = sorted(l_right,key=lambda x: x[1])			
				l = l_left + l_right	
				if self.width < self.height:
					mode = 'portrait'
				else:
					mode = 'landscape'
				n = 0
				for x,y in l:
					n += 1
					bn = str(n)
					r = self[bn].width/2
					self[bn].x = x - r	
					self[bn].y = y - r	
					self.settings[mode][bn]	= (x-r,y-r)
				self.save_settings()
				self.touch_actives = {}
				self.set_needs_display()
				return	
		return #-------------------------- wait decision button pressed ------
			
	def dot_touched(self,touch):
		xt,yt = touch.location
		for b in self.subviews:
			if type(b) is not ui.Button:
				continue
			if b.name[0] == 'b':	# not dots button
				continue
			r = b.width/2
			x = b.x + r
			y = b.y + r
			if ((xt-x)**2+(yt-y)**2) <= r**2:
				return b.name
		return ''
		
	def draw_dots(self,imageview,seq):	
		im = Image.new("RGB", (self.dots_w,self.dots_h), 'white')
		draw = ImageDraw.Draw(im)
		for c in range(1,7):
			x,y = self.dots_xy[c-1]
			draw.ellipse((x,y,x+10,y+10),'lightgray','lightgray')
		for ch in seq:
			c = int(ch)
			x,y = self.dots_xy[c-1]
			draw.ellipse((x,y,x+10,y+10),'red','red')
		del draw
		with io.BytesIO() as fp:
			im.save(fp, 'PNG')
			imageview.image = ui.Image.from_data(fp.getvalue())		
			imageview.hidden = False
		
	def dots_touched(self):
		self.seq = ''
		for touch_id in self.touch_actives.keys():
			bn = self.touch_actives[touch_id][1]
			if bn not in self.seq:
				self.seq += bn
		self.seq = ''.join(sorted(self.seq))
		
		# display touched dots, symbol, Hirgana
		self.draw_dots(self['dots'],self.seq)
		if self.prefix != '':
			self.draw_dots(self['prefix_dots'],self.prefix)			
			prefix_key = self.prefix + '|' + self.seq
			if prefix_key not in self.Japanese_Braille:
				# key could be no more an arab digit, remove prefix
				#self['prefix_dots'].hidden = True
				prefix_key = self.seq
		else:
			prefix_key = self.seq

		if prefix_key not in self.Japanese_Braille:
			temp_hirgana = '?'
		else:
			temp_hirgana = self.Japanese_Braille[prefix_key]
			self['b_decision'].hidden = False
		
		# display not yet confirmed hirgana in hirganas field
		w1,h = ui.measure_string(self['hirganas'].text, font=self['hirganas'].font)
		w2,h = ui.measure_string(temp_hirgana, font=self['hirganas']['hirgana'].font)
		self['hirganas']['hirgana'].text = temp_hirgana
		self['hirganas']['hirgana'].x = w1
		self['hirganas']['hirgana'].width = w2
		self['dots'].x = self['hirganas'].x + self['hirganas']['hirgana'].x 
		self['dots'].y = self['hirganas'].y + self['hirganas'].height
		if self.prefix != '':
			self['prefix_dots'].x = self['dots'].x - self['prefix_dots'].width
			self['prefix_dots'].y = self['dots'].y
		self['hirganas'].width = w1 + w2
		
	def key_pressed(self,key):
		self['hirganas']['hirgana'].width = 0
		if self.prefix == '':
			prefix_key = key
		else:
			prefix_key = self.prefix + '|' + key
			if self.prefix == '3456':
				# arab digits prefix active
				if prefix_key not in self.Japanese_Braille:
					# key is no more an arab digit, remove prefix
					self.prefix = ''
					self['prefix_dots'].hidden = True
					prefix_key = key
					if self.seq == '36':
						# hyphen after arab digits may not be displayed
						prefix_key = 'simulate key not in dictionnary'
		if prefix_key in self.Japanese_Braille:
			ch = self.Japanese_Braille[prefix_key]
			if ch =='_':
				self.prefix = key  		# store dot of dakuten
				self['prefix_dots'].image = self['dots'].image
				self['prefix_dots'].x = self['dots'].x - self['prefix_dots'].width	# move it left
				self['prefix_dots'].y = self['dots'].y
				self['prefix_dots'].hidden = False
				return
			self.hirganas.append(ch)
			self['hirganas'].text += ch
			self.draw_hirganas()
		if self.prefix != '3456':
			# prefix of arab digits must stay active
			self.prefix =''
			self['prefix_dots'].hidden = True
			
	def draw_hirganas(self):
		w,h = ui.measure_string(self['hirganas'].text, font=self['hirganas'].font)
		self['hirganas'].width = w
		self['hirganas'].x = (self.width - w)/2
		self['b_conversion'].x = self['hirganas'].x - self['b_conversion'].width
		self['b_conversion'].hidden = len(self.hirganas) == 0
		
	def layout(self):
		#print(self.bounds.size)
		pass
		
def main():
	if PythonistaVersion >= 3.3:
		if keyboard.is_keyboard():
			v = BrailleKeyboardInputAccessoryViewForTextField()
			v.custom_keyboard = True
			keyboard.set_view(v, 'expanded')
			return
	# Before Pythonista supporting keyboard or run in Pythonista app
	w,h = ui.get_screen_size()
	mv = ui.View()
	mv.name = 'Test keyboard in Pythonista'
	mv.background_color = 'white'
	tf = ui.TextField()
	tf.text = ''
	tf.frame = (2,2,w-4,32)
	mv.add_subview(tf)
	tfo = ObjCInstance(tf).textField() # UITextField is subview of ui.TextField
	kv = ui.View()

	kv.frame = (0,0,w,min(363,h*(3/5)))
	unused = ' unused, only to simulate height of custom keyboard with Pythonista 3.3'
	kv.add_subview(ui.Label(frame=(0,0,w,kv.height/7),text=unused))
	kv.background_color = 'lightgray'

	frame = (0,kv.height/7,w,kv.height*5/7)
	v = BrailleKeyboardInputAccessoryViewForTextField(frame=frame)
	v.custom_keyboard = False
	kv.add_subview(v)
	kv.add_subview(ui.Label(frame=(0,v.y+v.height,w,kv.height/7),text=unused))
	
	tfo.setInputView_(ObjCInstance(kv))
	v.tf = tf
	v.tfo = ObjCInstance(tf).textField() # UITextField is subview of ui.TextField
	
	# view of keyboard
	retain_global(v) # see https://forum.omz-software.com/topic/4653/button-action-not-called-when-view-is-added-to-native-view
	
	#  remove undo/redo/paste BarButtons above standard keyboard
	tfo.inputAssistantItem().setLeadingBarButtonGroups(None)
	tfo.inputAssistantItem().setTrailingBarButtonGroups(None)

	mv.present('full_screen')
	tf.begin_editing()
	mv.wait_modal()

if __name__ == '__main__':
	main()
