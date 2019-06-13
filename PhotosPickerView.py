# coding: utf-8

from objc_util import create_objc_class, ObjCClass, ObjCInstance
import photos
import ui

#===================== delegate of UIPickerView: begin =====================
def pickerView_numberOfRowsInComponent_(self, cmd, picker_view, component):
    UIPickerView = ObjCInstance(picker_view)
    return(len(UIPickerView.assets))

def numberOfComponentsInPickerView_(self, cmd, picker_view):
    return 1

def rowSize_forComponent_(self, cmd, picker_view, component):
    return ObjCInstance(picker_view).myRowWidth

def pickerView_rowHeightForComponent_(self, cmd, picker_view, component):
    return ObjCInstance(picker_view).myRowHeight

def pickerView_didSelectRow_inComponent_(self, cmd, picker_view, row, component):
    #print(row)
    return

def pickerView_viewForRow_forComponent_reusingView_(self, cmd, picker_view, row, component,view_ptr):
    UIPickerView = ObjCInstance(picker_view)
    if view_ptr == None:
      view = ObjCClass('UILabel').alloc().init()
      #view.setText_('test')
      iv = ui.ImageView()
      iv.frame = (0,0, UIPickerView.myRowWidth, UIPickerView.myRowHeight)
      iv.content_mode = ui.CONTENT_SCALE_ASPECT_FIT
      iv.image = UIPickerView.assets[row].get_ui_image(size=(iv.width,iv.height))
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
        
        self._picker_view.assets = photos.get_assets()
        self._picker_view.myRowWidth = self.width
        self._picker_view.myRowHeight = int(self.height/5)
        
    def layout(self):
        self._picker_view.frame = ObjCInstance(self).bounds()

def main():
    pv = MyUIPickerView(frame=(0,0,400,600))
    pv.background_color = 'lightgray'
    pv.name = 'Photos in PickerView'
    pv.present('sheet')

if __name__ == '__main__':
    main()

