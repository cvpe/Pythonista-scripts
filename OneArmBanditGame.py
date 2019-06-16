# todo
# - always turn in the same direction
# - several spins before end
# - simulate swipe has better animation

from objc_util import create_objc_class, ObjCClass, ObjCInstance
import photos
from random import randint
import ui

#assets = photos.get_assets()
assets ='🏈🍿🍏🍎🥝🥕🍔🍟🧁🍺🍷🚗🍌🍉🍓🍒🍍🌽🧀🍇🍋🍊🥥🗝🧸🎁' 
# choose only emoji with ONE character, use this code to check it
#for i in range(0,len(assets)):
#	print(i,assets[i])

#===================== delegate of UIPickerView: begin =====================
def pickerView_numberOfRowsInComponent_(self, cmd, picker_view, component):
    return 10000				# simulate infinite 
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
    UIPickerView = ObjCInstance(picker_view)
    if view_ptr == None:
      idx = row % len(assets)
      view = ObjCClass('UILabel').alloc().init()
      iv = ui.ImageView()
      iv.frame = (0,0, UIPickerView.myRowWidth, UIPickerView.myRowHeight)
      iv.content_mode = ui.CONTENT_SCALE_ASPECT_FIT
      if type(assets) is str:
          iv.image = emoji_to_image(assets[idx],w=iv.width,h=iv.height)
      else:
          iv.image = assets[idx].get_ui_image(size=(iv.width,iv.height))
      view.addSubview_(ObjCInstance(iv))
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
        #self._picker_view.setUserInteractionEnabled_(False)
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
            #s = mv['pv']._picker_view.selectedRowInComponent_(i)
            #r = (1+int(s/len(assets)))*len(assets) + r
            mv['pv']._picker_view.selectRow_inComponent_animated_(r,i,True)
        if sender == 'init':
           return
        mv.name = 'diring tests: ' + str(l)
        if len(set(l)) == 1:
            mv.right_button_items[0].title = '🍾    '
    arm_btn.action = go
    mv.add_subview(arm_btn)
    win_btn = ui.ButtonItem()
    win_btn.title = ''
    mv.right_button_items = (win_btn,)
    pv = MyUIPickerView(frame= (0,0,w,h),name='pv')
    pv.background_color = 'lightgray'
    mv.add_subview(pv)
    go('init')
    mv.present('sheet')

if __name__ == '__main__':
    main()

