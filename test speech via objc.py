import ui
from objc_util import *
import time

AVSpeechUtterance=ObjCClass('AVSpeechUtterance')
AVSpeechSynthesizer=ObjCClass('AVSpeechSynthesizer')
AVSpeechSynthesisVoice=ObjCClass('AVSpeechSynthesisVoice')

voices=AVSpeechSynthesisVoice.speechVoices()
#for i in range(0,len(voices)):
#	print(i,voices[i].language(),voices[i].identifier())

flags_c_codes = []
# Regional indicator of flags are encoded in the range 
# from U+1F1E6 🇦 REGIONAL INDICATOR SYMBOL LETTER A (127462;)
# to   U+1F1FF 🇿 REGIONAL INDICATOR SYMBOL LETTER Z (127487)

for i in range(127462,127488):
	flags_c_codes.append(chr(i).encode('utf-8'))
	
synthesizer=AVSpeechSynthesizer.new()

# some emoji like flags count as 2 for len but as 4 for selected_range
def IndexToPos(tv):
    tvo = ObjCInstance(tv)
    # build array index -> position in range
    idxtopos = []
    pre_x = -1
    #print(tv.text)
    p = 0
    i = 0
    pre_c_code = ''
    for c in tv.text:  	
      # nbr characters used e=1 é=1 😂=1 🇯🇵=2 👨‍👨‍👧‍👧=7
      # some emoji generate more than one sub-character, 
      # separated by U+200D = zero-width joiner = b'\xe2\x80\x8d'
      # sometimes counted for more than one in range
      # 1,2,3->1  4->2
      # flag emoji = 2 chars but not separated by zero-width joiner
      c_code = c.encode('utf-8')
      nb = 1 + int(len(c_code)/4)
      #print(c,c_code)
      for j in range(0,nb):
        p1 = tvo.positionFromPosition_offset_(tvo.beginningOfDocument(), p)
        p2 = p1
        rge = tvo.textRangeFromPosition_toPosition_(p1, p2)
        rect = tvo.firstRectForRange_(rge)	# CGRect
        if c_code == b'\xe2\x80\x8d':
          pass				# zero-width joiner, keep same x
        elif c_code == b'\xef\xb8\x8f':
          pass				# variation selector 16, keep same x
        elif pre_c_code == b'\xe2\x80\x8d':
          pass				# previous is zero-width joiner, keep same x
        elif (c_code in flags_c_codes) and (pre_c_code in flags_c_codes):
        	pass				# 2nd char of flag emoji, keep same x
        elif j == 0:
          x = rect.origin.x
        else:
          pass				# not first position of one char, keep same x
        #print(c,'len=',len(c_code),'nb=',nb,'p=',p,'x=',x)
        if x == float('inf') or x == pre_x:
          # same x as previous one, composed character
          pass
        else:
          pre_x = x
        if j == 0:
          idxtopos.append((i,x))						# start position of c
        else:
          idxtopos.append((-i,x))						# start position of c
        #print(c,'j=',j,'/',nb,'i=',i,'p=',p,'x=',x)
        p = p + 1
      i = i + 1
      pre_c_code = c_code
    idxtopos.append((i,x+1))					# end position of last c
    #print(idxtopos)
    return idxtopos

v = ui.View()
v.frame = (0,0,500,400)
v.name = 'Test Objective-C Speech'
v.background_color = 'white'

tl = ui.Label()
tl.frame = (10,10,160,32)
tl.text = 'text'
v.add_subview(tl)
tv = ui.TextView('tv')
tv.frame =(tl.x*2+tl.width,10,v.width-tl.x*3-tl.width,32)
tv.font = ('Arial Rounded MT Bold',24)
tv.text = 'a😢🇯🇵z👩‍🎨'
v.add_subview(tv)

vl = ui.Label()
vl.frame = (10,50,tl.width,32)
vl.text = 'voice'
v.add_subview(vl)
vc = ui.SegmentedControl()
vc.frame =(tl.x*2+tl.width,50,v.width-tl.x*3-tl.width,32)
s = []
for i_voice in range(0,len(voices)):
	voice = voices[i_voice]
	vi = str(voice.identifier())
	if 'com.apple.ttsbundle.' in vi:
		vi = vi[len('com.apple.ttsbundle.'):]
	else:
		vi = vi[len('com.apple.'):]
	s.append(str(voice.language())+':'+vi)
#vc.segments = s
#vc.selected_index = 0
#v.add_subview(vc) 

class MyTableViewDelegate(object):
	def tableview_did_select(self, tableview, section, row):
		if not tableview.expanded:
			tv.end_editing()
			tableview.height = int((tableview.superview.height - tableview.y - 10)/tableview.row_height)*tableview.row_height
		else:
			tableview.height = 32
			tableview.content_offset = (0,row*tableview.row_height)
		tableview.expanded = not tableview.expanded
	def tableview_cell_for_row(self,tableview, section, row):
		data = tableview.data_source.items[row]
		cell = ui.TableViewCell()
		cell.text_label.text = data
		cell.bg_color = 'white'
		tableview.bring_to_front()
		return cell

vt = ui.TableView()
vt.frame =(tl.x*2+tl.width,50,v.width-tl.x*3-tl.width,32)
vt.border_width = 1
vt.row_height = 32
vt.data_source = ui.ListDataSource(items=s)
vt.delegate = MyTableViewDelegate()
vt.data_source.tableview_cell_for_row = MyTableViewDelegate().tableview_cell_for_row
vt.expanded = False
v.add_subview(vt)
	
rl = ui.Label()
rl.frame = (10,90,tl.width,32)
rl.text = ''
v.add_subview(rl)
rs = ui.Slider()
rs.frame = (tl.x*2+tl.width,90,v.width-tl.x*3-tl.width,32)
rs.value = 0.5
def rs_action(sender):
	rl.text = 'voice rate = '+str(int(100*sender.value)/100)
rs.action = rs_action
rs_action(rs)
v.add_subview(rs)

dl = ui.Label()
dl.frame = (10,130,tl.width,32)
dl.text = ''
v.add_subview(dl)
ds = ui.Slider()
ds.frame = (tl.x*2+tl.width,130,v.width-tl.x*3-tl.width,32)
ds.value = 0.2
def ds_action(sender):
	dl.text = 'spell delay = '+str(int(10*sender.value)/10)+' sec'
ds.action = ds_action
ds_action(ds)
v.add_subview(ds)

def speak_or_spell(action,cc):
	#print(cc)
	utterance=AVSpeechUtterance.speechUtteranceWithString_(cc)
	# the value that sounds good apparantly depends on ios version
	utterance.rate = rs.value
	utterance.voice = voices[vt.selected_row[1]]
	utterance.useCompactVoice=False 
	synthesizer.speakUtterance_(utterance)
	if action == 'spell':
		time.sleep(ds.value)

def b_speak_or_spell(sender):
	#print(tv.text)
	#print('len(tv.text)=',len(tv.text))
	#print('selected_range[0]=',tv.selected_range[0])
	idxtopos = IndexToPos(tv)
	#print(idxtopos,len(idxtopos))
	x_prev = -1
	cc = ''
	for p in range(0,len(idxtopos)):
		i,x = idxtopos[p]
		if p == (len(idxtopos)-1):
			c = ''				# not used
		elif i >= 0:
			c = tv.text[i]
		else:
			c = ''				# not 1st encode of a char
		#print(p,i,c,x,x_prev,cc)
		if (sender.title == 'speak') or (x == x_prev):
			cc = cc + c
			if p < (len(idxtopos)-1):
				continue
		else:
			if ('spell' in sender.title) and (cc != ''):
				speak_or_spell('spell',cc)
			cc = c
		x_prev = x
	if sender.title == 'speak':
		speak_or_spell('speak',cc)

b_speak =ui.Button()
b_speak.frame = (10,170,60,32)
b_speak.title ='speak'
b_speak.border_width = 1
b_speak.border_color ='blue'
b_speak.corner_radius = 5
b_speak.action = b_speak_or_spell
v.add_subview(b_speak)

b_spell =ui.Button()
b_spell.frame = (80,170,60,32)
b_spell.title ='spell'
b_spell.border_width = 1
b_spell.border_color ='blue'
b_spell.corner_radius = 5
b_spell.action = b_speak_or_spell
v.add_subview(b_spell)

v.present('sheet')
tv.begin_editing()
