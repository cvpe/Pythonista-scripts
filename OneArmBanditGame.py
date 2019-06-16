# Version V0.1
# - bug: view title was "diring" instead of "during"
# - mod:random selection, 
#		instead of showing (selecting) row between 1th and n-th,
#   show (select) row between n + 1 and n + n to avoid blank rows at top
# - mod: disable manual spin
# - mod: inverse rotation sense, like real one-arm bandit games
# - mod: always turn in same sense
# - mod: reuse identic view per component
# Version V0.0
# - original posted on forum 
#   forum.omz-software.com/topic/5680/see-your-photos-in-an-uipickerview

from objc_util import create_objc_class, ObjCClass, ObjCInstance
import photos
from random import randint
import ui

#assets = photos.get_assets()
assets ='🏈🍿🍏🍎🥝🥕🍔🍟🧁🍺🍷🚗🍌🍉🍓🍒🍍🌽🧀🍇🍋🍊🥥🗝🧸🎁' 
# choose only emoji with ONE character, use this code to check it
#for i in range(0,len(assets)):
#	print(i,assets[i])
view_of_row = {}																										# add V0.1
# simulate infinite to avoid changing rotation sense								# add V0.1
max_rows = int(100000/len(assets))*len(assets)											# add V0.1

#===================== delegate of UIPickerView: begin =====================
def pickerView_numberOfRowsInComponent_(self, cmd, picker_view, component):
    return max_rows 																								# add V0.1
    #return len(assets)

def numberOfComponentsInPickerView_(self, cmd, picker_view):
    return 3

def rowSize_forComponent_(self, cmd, picker_view, component):
    return ObjCInstance(picker_view).myRowWidth

def pickerView_rowHeightForComponent_(self, cmd, picker_view, component):
    return ObjCInstance(picker_view).myRowHeight

def pickerView_didSelectRow_inComponent_(self, cmd, picker_view, row, component):
    #print(cmd,row)
    return

def pickerView_viewForRow_forComponent_reusingView_(self, cmd, picker_view, row, component,view_ptr):
    idx = row % len(assets)
    if (idx,component) in view_of_row:															# add V0.1
       #print('reuse',component,row,idx)					# test						# add V0.1
       view = view_of_row[(idx,component)]				# reuse view			# add V0.1
       view.setHidden_(False)											# not sure needed	# add V0.1
       return view.ptr																							# add V0.1
    UIPickerView = ObjCInstance(picker_view)
    if view_ptr == None:
      #print(row, component)
      view = ObjCClass('UILabel').alloc().init()
      #view.text = str(row)+','+str(component)			# test only			# add V0.1
      iv = ui.ImageView()
      iv.frame = (0,0, UIPickerView.myRowWidth, UIPickerView.myRowHeight)
      iv.content_mode = ui.CONTENT_SCALE_ASPECT_FIT
      if type(assets) is str:
          iv.image = emoji_to_image(assets[idx],w=iv.width,h=iv.height)
      else:
          iv.image = assets[idx].get_ui_image(size=(iv.width,iv.height))
      view.addSubview_(ObjCInstance(iv))
      view_of_row[(idx,component)] = view 													# add V0.1
    else:
      view = ObjCInstance(view_ptr)
    return view.ptr

methods = [
	numberOfComponentsInPickerView_, pickerView_numberOfRowsInComponent_, rowSize_forComponent_, pickerView_rowHeightForComponent_, pickerView_didSelectRow_inComponent_, pickerView_viewForRow_forComponent_reusingView_]

protocols = ['UIPickerViewDataSource', 'UIPickerViewDelegate']

UIPickerViewDataSourceAndDelegate = create_objc_class(
    'UIPickerViewDataSourceAndDelegate', methods=methods, protocols=protocols)
#===================== delegate of UIPickerView: end =======================

class MyUIPickerView(ui.View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        UIPickerView = ObjCClass('UIPickerView')
        self._picker_view = UIPickerView.alloc().initWithFrame_(ObjCInstance(self).bounds()).autorelease()
        ObjCInstance(self).addSubview_(self._picker_view)
        self.delegate_and_datasource = UIPickerViewDataSourceAndDelegate.alloc().init().autorelease()
        self._picker_view.delegate = self.delegate_and_datasource
        self._picker_view.dataSource = self.delegate_and_datasource
        
        self._picker_view.myRowWidth = self.width/3
        self._picker_view.myRowHeight = int(self.height/5)
        #self._picker_view.setUserInteractionEnabled_(False)					# add V0.1
        #print(dir(self._picker_view))
        
    def layout(self):
        self._picker_view.frame = ObjCInstance(self).bounds()
        
# @phuket2 code
# https://forum.omz-software.com/topic/3232/share-code-emoji-to-ui-image-or-png-file
def emoji_to_image(emoji_char, w =32, h=32, font_name = 'Arial Rounded MT Bold'):
    font_size = min(w,h) - 8
    r = ui.Rect(0, 0, w, h)
    with ui.ImageContext(r.width, r.height) as ctx:
        # just draw the string
        ui.draw_string(emoji_char, rect=r,
        font=(font_name, font_size), color='black',
        alignment=ui.ALIGN_CENTER,
        line_break_mode=ui.LB_TRUNCATE_TAIL)
        img = ctx.get_image()
        return img

def main():
    mv = ui.View()
    mv.frame = (0,0,600,500)
    mv.name = 'One-arm Bandit Game'
    d = 60
    arm_btn = ui.Button(name='arm')
    arm_btn.frame = (mv.width-d-10,(mv.height-d)/2,d,d)
    #arm_btn.title = ''
    arm_btn.background_image = emoji_to_image('',w=d,h=d)
    w = arm_btn.x
    h = mv.height
    def go(sender):
        mv.right_button_items[0].title = ''
        l = []
        for i in range(0,3):
            r = randint(0,len(assets)-1)
            l.append(r)
            # force roll always in same direction
            s = mv['pv']._picker_view.selectedRowInComponent_(i)
            r = (max(1,int(s/len(assets))-1))*len(assets) + r				# mod V0.1
            l.append(r)															# test only			# add V0.1
            mv['pv']._picker_view.selectRow_inComponent_animated_(r,i,True)
        if sender == 'init':
           return
        #mv.name = 'during tests: ' + str(l)				# test only			# add V0.1
        if len(set(l)) == 1:
            mv.right_button_items[0].title = '🍾    '
    arm_btn.action = go
    mv.add_subview(arm_btn)
    win_btn = ui.ButtonItem()
    win_btn.title = ''
    mv.right_button_items = (win_btn,)
    pv = MyUIPickerView(frame= (0,0,w,h),name='pv')
    pv.background_color = 'lightgray'
    # start from last rows to inverse rotation sense								# add V0.1
    for i in range(0,3):																						# add V0.1
        r = (int(max_rows/len(assets))-1)*len(assets) 							# add V0.1
        pv._picker_view.selectRow_inComponent_animated_(r,i,True)		# add V0.1
    mv.add_subview(pv)
    mv.present('sheet')
    go('init')																											# add V0.1

if __name__ == '__main__':
    main()

