# coding: utf-8
from __future__ import absolute_import
from objc_util import *
import ui
from collections import OrderedDict
from six.moves import range
import console

UITableView = ObjCClass('UITableViewController')
UITableViewCell = ObjCClass('UITableViewCell')

class UITableViewStyle(object):
		UITableViewStylePlain = 0
		UITableViewStyleGrouped = 1

def test_data(number):
	data = OrderedDict()
	valueRange = 7
	for i in range(0,number):
		ii = i * valueRange
		key = str(ii)
		value = []
		for j in range(ii,ii+valueRange):
			value.append(str(j))
		data[key] = value
	return data

data = test_data(1)

def tableView_cellForRowAtIndexPath_(self,cmd,tableView,indexPath):
	ip = ObjCInstance(indexPath)
	cell = ObjCInstance(tableView).dequeueReusableCellWithIdentifier_('mycell')
	
	if cell == None:
		cell = UITableViewCell.alloc().initWithStyle_reuseIdentifier_(0,'mycell')
	key = list(data.keys())[ip.section()]
	text = ns(data[key][ip.row()])
	cell.textLabel().setText_(text)

	return cell.ptr

def numberOfSectionsInTableView_(self,cmd,tableView):
	return len(data)

def tableView_numberOfRowsInSection_(self,cmd, tableView,section):
	key = list(data.keys())[section]
	return ns(len(data[key])).integerValue()

def sectionIndexTitlesForTableView_(self,cmd,tableView):
	return ns(list(data.keys())).ptr

def tableView_sectionForSectionIndexTitle_atIndex_(self,cmd,tableView,title,index):
	#I have assumed order and number of list is the same from list and sections
	return index

def tableView_titleForHeaderInSection_(self,cmd,tableView,section):
	return ns('Header for ' + list(data.keys())[section]).ptr

def tableView_viewForHeaderInSection_(self,cmd,tableView,section):
	print('ici')
	return ns('Header for ' + list(data.keys())[section]).pt

def tableView_heightForHeaderInSection_(self,cmd,tableView,section):
	return 50.0

def tableView_titleForFooterInSection_(self,cmd,tableView,section):
	return ns('Footer for ' + list(data.keys())[section]).ptr

def tableView_commitEditingStyle_forRowAtIndexPath_(self,cmd,tableView,editingStyle,indexPath):
	if editingStyle == 1:
		# delete
		section_row = ObjCInstance(indexPath)
		tv = ObjCInstance(tableView)
		row = section_row.row()
		b = console.alert('delete row',str(row), 'confirm', 'cancel', hide_cancel_button=True)
		if b == 1:
			pass
			#tv.beginUpdates()
			#?.removeAtIndex(indexPath.row)
			#tv.deleteRowsAtIndexPaths_withRowAnimation_([section_row],0)
			#tv.endUpdates()			
		

#def tableView_canEditRowAtIndexPath_(self,cmd,tableView,indexPath):
	#pass

#def tableView_canMoveRowAtIndexPath_(self,cmd,tableView,indexPath):
	#pass

#def tableView_moveRowAtIndexPath_toIndexPath_(self,cmd,tableView,fromIndexPath,toIndexPath):
	#pass

methods = [tableView_cellForRowAtIndexPath_,tableView_numberOfRowsInSection_,numberOfSectionsInTableView_,tableView_titleForHeaderInSection_,tableView_sectionForSectionIndexTitle_atIndex_,sectionIndexTitlesForTableView_,tableView_titleForFooterInSection_, tableView_commitEditingStyle_forRowAtIndexPath_]#, tableView_viewForHeaderInSection_, tableView_heightForHeaderInSection_]
protocols = ['UITableViewDataSource']
TVDataSourceAndDelegate = create_objc_class('TVDataSourceAndDelegate', NSObject, methods=methods, protocols=protocols)

#=============== TableView delegate: begin
def tableView_trailingSwipeActionsConfigurationForRowAtIndexPath_(self,cmd, tableView, indexPath):
	global UISwipeActionsConfiguration
	section_row = ObjCInstance(indexPath)
	tv = ObjCInstance(tableView)
	section,row = section_row.section(),section_row.row()
	print(section,row)
	return UISwipeActionsConfiguration.ptr

methods = [tableView_trailingSwipeActionsConfigurationForRowAtIndexPath_]
protocols = ['UITableViewDelegate']
UITableViewDelegate = create_objc_class('UITableViewDelegate', NSObject, methods=methods, protocols=protocols)
#=============== TableView delegate: end

def handler():
	print('handler called')
	return

@on_main_thread
def Main():
		global UISwipeActionsConfiguration
		root_vc = UIApplication.sharedApplication().keyWindow().rootViewController()
		tableviewcontroller = UITableView.alloc().initWithStyle_(UITableViewStyle.UITableViewStylePlain)

		#=============== TableView delegate: begin				
		#set delegate
		tb_ds = TVDataSourceAndDelegate.alloc().init().autorelease()
		tableviewcontroller.tableView().setDataSource_(tb_ds)
		
		tb_dl = UITableViewDelegate.alloc().init().autorelease()
		tableviewcontroller.tableView().setDelegate_(tb_dl)
				
		# set actions if swipe
		UIContextualAction = ObjCClass('UIContextualAction').alloc()
		UIContextualAction.setTitle_("@Ryubai's' action 😅")
		# block does not have parameter nor return, thus we can use a Python def
		UIContextualAction.setHandler_(handler)
		UIContextualAction.setBackgroundColor_(ObjCClass('UIColor').blueColor().colorWithAlphaComponent(0.5))
		
		UISwipeActionsConfiguration = ObjCClass('UISwipeActionsConfiguration').configurationWithActions_([UIContextualAction])
		#=============== TableView delegate: end
		
		root_vc.presentViewController_animated_completion_(tableviewcontroller, True, None)
		
if __name__ == '__main__':
	Main()


