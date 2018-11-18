# coding: utf-8
#
# Functionalities
# - the script uses a function, geocodeAddressString, for converting an
#		address string into a localization (latitude,longitude).
#		If you want to use it in different scripts, you could store it in
#		site-packages folder
#	- a button (satellite) allows to switch between the standard, satellite and 
#		hybrid views of the map
#	- you can zoom and move the map by pinching and swiping
# - a button (pin) allows to switch between a pin or a photo for contact
#		if a contact does not have a photo, a pin is always shown
#	- tapping a pin or a photo shows a view with the name(s) of the contact(s)
#		at this location, and the address
# - if several contacts have the same address, the script cumulates them
# 	on an unique pin, by horizontally juxtaposing their photos into a wide one
#		the script also tries to cumulate the contacts full names by identifying
#		the identic last words as a family name. Not sure it's always ok
#		ex: Fred Astaire and Mary Astaire give a title of Fred, Mary Astaire
#		Normally a long title is shorten by ...
# 	The script shows a small view under the title with one line per group
#		of persons with different last names.
# -	a button (address) allows to type a manual address. At enter, the script
#		will try to get its location. If successful, a green pin is displayed 
#		and the map is automatically centered and zoomed on it.
#		If unsuccessful, the address is set in red and no pin is shown
# - there is a simulation mode (main(simulation=True)) where a namedtuple
#		simulates contacts. Photo can be any internal or external image
#		and their names need to be given in the 'simul = namedtuple...' line
# - sometimes, geocodeAddressString returns None. Either the address string
#		is invalid, but somerimes, a retry gives a correct gps localization.
#		Perhaps due to a big number of calls in a short time.
#		In this case, the script display a button 'nn not (yet) localized' and 
#		starts a thread which will retry (maximum 100 times) all not yet localized
#		contacts. The delay between two retries increase at each retry.
#		The button title is green if the thread runs and red if not.
#		Tapping this button gives the list of these contacts with their retries
#		number
#	- The close button forces the thrad to be stopped.
# - the script has been tested with 250 contacts and sometimes, after several #		runs, it crashs, perhaps due to memory problems. In this case, remove
#		the app from memory and restart.

import ui
import os
import console
import sys
import time
import contacts
from objc_util import *
from geocodeAddressString import geocodeAddressString
import threading
import ImageFont
from collections import namedtuple

class CLLocationCoordinate2D (Structure):
	_fields_ = [('latitude', c_double), ('longitude', c_double)]
class MKCoordinateSpan (Structure):
	_fields_ = [('d_lat', c_double), ('d_lon', c_double)]
class MKCoordinateRegion (Structure):
	_fields_ = [('center', CLLocationCoordinate2D), ('span', MKCoordinateSpan)]
	
MKPointAnnotation = ObjCClass('MKPointAnnotation')
MKPinAnnotationView = ObjCClass('MKPinAnnotationView')
MKAnnotationView = ObjCClass('MKAnnotationView')
UIColor = ObjCClass('UIColor') # used to set pin color
		
def mapView_viewForAnnotation_(self,cmd,mk_mapview,mk_annotation):
	global map_pin_type, map_pin_color, map_addr_color, map_pin_size, map_pin_radius, map_pin_borderwidth, map_pin_bordercolor, contacts_photos
	try:
		# not specially called in the same sequence as pins created
		# should have one MK(Pin)AnnotationView by type (ex: pin color)
		annotation = ObjCInstance(mk_annotation)
		mapView = ObjCInstance(mk_mapview)
		if annotation.isKindOfClass_(MKPointAnnotation):
			tit = str(annotation.title())
			subtit = str(annotation.subtitle())
			#print('subtit',subtit)
			if tit != 'address':
				id = 'photo=' + str(map_pin_type) + str(map_pin_color) + tit
			else:
				id = 'address'
			#print('id',id)
			pinView = mapView.dequeueReusableAnnotationViewWithIdentifier_(id)
			
			if not pinView:
				# Modify pin color: use MKPinAnnotationView
				# Modify pin image: use MKAnnotationView
				if 'photo' in id:
					# photo
					if map_pin_type == 0 or contacts_photos[tit] == None:
						# pin type = pin
						pinView = MKPinAnnotationView.alloc().initWithAnnotation_reuseIdentifier_(annotation,id)
						pinView.canShowCallout = True  	# tap-> show title
						pinView.animatesDrop   = False  # Animated pin falls like a drop
						pinView.pinColor = map_pin_color # 0=red 1=green 2=purple
					else:
						# pin type = photo
						pinView = MKAnnotationView.alloc().initWithAnnotation_reuseIdentifier_(annotation,id)
						img = contacts_photos[tit]
						pinView.setImage_(img.objc_instance)
						pinView.canShowCallout = True
						if tit.find(' & ') >= 0:
							l_title = ui.Label()
							l_title.text = '- '+tit.replace(' & ','\n- ')+'\n'+subtit
							l_title.font = ('Arial',12)
							lo = ObjCInstance(l_title)
							lo.setNumberOfLines_(0)
							pinView.setDetailCalloutAccessoryView_(lo)
						pinView.layer().setBorderWidth_(map_pin_borderwidth)
						# layer bordercolor as a CGColor
						pinView.layer().setBorderColor_(UIColor.color( red=map_pin_bordercolor[0], green=map_pin_bordercolor[1],  blue=map_pin_bordercolor[2], alpha=1.0).CGColor())
						pinView.layer().setCornerRadius_(map_pin_radius)
				else:
					# address
					pinView = MKPinAnnotationView.alloc().initWithAnnotation_reuseIdentifier_(annotation,id)
					pinView.canShowCallout = True  	# tap-> show title
					pinView.animatesDrop   = True   # Animated pin falls like a drop
					pinView.pinColor = map_addr_color # 0=red 1=green 2=purple
			else:
				pinView.annotation = annotation
			return pinView.ptr
		return None
	except Exception as e:
		print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
		
# Build method of MKMapView Delegate
methods = [mapView_viewForAnnotation_]
protocols = ['MKMapViewDelegate']
try:
	MyMapViewDelegate = ObjCClass('MyMapViewDelegate')
except:
	MyMapViewDelegate = create_objc_class('MyMapViewDelegate', methods=methods, protocols=protocols)	
	#MyMapViewDelegate = create_objc_class('MyMapViewDelegate', NSObject, methods=methods, protocols=protocols)	

@on_main_thread	
def build_mapview(superview,frame):
	MKMapView = ObjCClass('MKMapView')
	my_map_view = MKMapView.alloc().initWithFrame_(frame)
	flex_width, flex_height = (1<<1), (1<<4)
	my_map_view.setAutoresizingMask_(flex_width|flex_height)
	# Type of map: 0=standard  1=satellite  2=hybrid
	my_map_view.mapType = 0
	#my_map_view.hidden = True
	self_objc = ObjCInstance(superview)
	self_objc.addSubview_(my_map_view)
	my_map_view.release()

	# Set Delegate of mk_map_view
	map_delegate = MyMapViewDelegate.alloc().init()#.autorelease()
	my_map_view.setDelegate_(map_delegate)
		
	return my_map_view
	
@on_main_thread
def remove_one_pin(mk_map_view,annot):
	'''Remove all annotations (pins) from the map'''
	mk_map_view.removeAnnotation_(annot)
	
#@on_main_thread
def remove_all_pins(mk_map_view):
	'''Remove all annotations (pins) from the map'''
	mk_map_view.removeAnnotations_(mk_map_view.annotations())	

@on_main_thread
def add_pin(mk_map_view,lat, lon, title, subtitle,select=False):
	'''Add a pin annotation to the map'''
	MKPointAnnotation = ObjCClass('MKPointAnnotation')
	coord = CLLocationCoordinate2D(lat, lon)
	annotation = MKPointAnnotation.alloc().init()#.autorelease()
	# if no title, tap pin does not show the title/subtitle buble
	annotation.setTitle_(str(title))
	annotation.setSubtitle_(str(subtitle))
	#print('add pin',subtitle)
	annotation.setCoordinate_(coord, restype=None, argtypes=[CLLocationCoordinate2D])
	mk_map_view.addAnnotation_(annotation)
	# if I comment next line, pin is not visible without an action on map (zoom fi)
	if select:
		mk_map_view.selectAnnotation_animated_(annotation, True)
	return annotation
	
@on_main_thread
def set_center_coordinate(mk_map_view, lat, lon, animated=False):
	'''Set latitude/longitude without changing the zoom level'''
	coordinate = CLLocationCoordinate2D(lat, lon)
	mk_map_view.setCenterCoordinate_animated_(coordinate, animated, restype=None, argtypes=[CLLocationCoordinate2D, c_bool])
		
#@on_main_thread
def set_region(mk_map_view,lat, lon, d_lat, d_lon, animated=False):
	'''Set latitude/longitude of the view's center and the zoom level (specified implicitly as a latitude/longitude delta)'''
	region = MKCoordinateRegion(CLLocationCoordinate2D(lat, lon), MKCoordinateSpan(d_lat, d_lon))
	mk_map_view.setRegion_animated_(region, animated, restype=None, argtypes=[MKCoordinateRegion, c_bool])
	
#@on_main_thread
def set_world_region(mk_map_view, animated=False):
	'''Set latitude/longitude of the view's center and the zoom level (specified implicitly as a latitude/longitude delta)'''
	region = MKCoordinateRegion(CLLocationCoordinate2D(0.0, 0.02), MKCoordinateSpan(180, 360))
	mk_map_view.setRegion_animated_(region, animated, restype=None, argtypes=[MKCoordinateRegion, c_bool])
	
def my_list_popover(elements,val=None,x=None,y=None,color='white',title=None):
	class my_list(ui.View):
		def __init__(self,selected):

			# ListDataSource for clients TableView
			elements_lst = ui.ListDataSource(items=lst)
			# ListDataSource has no attribute "name"
			elements_lst.delete_enabled = False
			elements_lst.move_enabled = False
			elements_txt = ui.TableView(name='elements_txt')
			elements_txt.allows_multiple_selection = False
			elements_txt.text_color = 'black'
			elements_txt.font= ('Courier',16)
			elements_txt.row_height = elements_txt.font[1] * 2
			h = len(lst) *	elements_txt.row_height
			font = ImageFont.truetype('Courier',16)
			w = 0
			for ele in lst:
				if type(ele) is list:
					data = ele[0]
				else:
					data = ele
				w_ele,h_ele = font.getsize(data)
				if w_ele > w:
					w = w_ele
			w = w + 32
			elements_txt.content_size = (w,h)
			h_max = h_screen/2
			if h > h_max:
				h = h_max
			w_max = w_screen - 20
			if w > w_max:
				w = w_max
			elements_txt.frame = (4,4,w,h)	
			#elements_txt.border_color = 'blue'
			#elements_txt.border_width = 3
			elements_txt.data_source = elements_lst
			elements_txt.data_source.tableview_cell_for_row = self.tableview_cell_for_row
			if selected >= 0:
				elements_txt.selected_row = (0,selected)

						
			elements_txt.delegate  = self
			self.add_subview(elements_txt)	
			self.width = elements_txt.width   + 8
			self.height = elements_txt.height + 8
			#elements_txt.corner_radius = 5
			#self.corner_radius = 5
			#self.border_color = 'blue'
			#self.border_width = 2
			self.background_color = color
			if title:#and multiple:
				# title bar displayed in multiple
				self.name = title
				
		def tableview_did_select(self, tableview, section, row):
			# Called when a row was selected
			data = tableview.data_source.items[row]
			if type(data) is list:
				if not data[1]:
					return
			lst.append(lst[row])
			v.close()
			
		def tableview_cell_for_row(self, tableview, section, row):
			cell = ui.TableViewCell()

			data = tableview.data_source.items[row]
			if type(data) is list:
				txt = data[0]					# [text,flag]
				cell.selectable = data[1]
			else:
				txt = data						# text
			cell.text_label.text = txt
			cell.text_label.alignment = ui.ALIGN_LEFT
			cell.bg_color = color
			if cell.selectable:
				cell.text_label.text_color = 'black'
				selected_cell = ui.View()
				selected_cell.border_color = 'black'
				selected_cell.border_width = 2
				selected_cell.corner_radius = 10
				selected_cell.bg_color = 'cornflowerblue'
				cell.selected_background_view = selected_cell
			else:
				cell.text_label.text_color = 'lightgray'
			return cell		
	
	lst = []
	i = 0
	selected = -1
	if type(elements) is dict:
		elements_list = sorted(elements.keys())
	elif type(elements) is list:
		elements_list = elements
	for element in elements_list:
		lst.append(element)
		if element == val:
			selected = i
		i = i + 1
	w_screen,h_screen = ui.get_screen_size()
	if not x:
		x = int(w_screen/2)
	if not y:
		y = int(h_screen/2)
	v = my_list(selected)
	# lst already copied into elements_lst, thus we can change lst
	# to contain iniital value in case of tap outside
	if selected == -1:
		lst.append('')
	else:
		lst.append(lst[selected])
	if title:
		v.present('popover',popover_location=(x,y),hide_title_bar=False)
	else:
		v.present('popover',popover_location=(x,y),hide_title_bar=True)
	v.wait_modal()
	return lst[len(lst)-1]	# return last
	
class my_thread(threading.Thread):
	global main_view
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		try:
			while main_view.run:
				names = []
				for name in main_view.not_yet_localized.keys():
					names.append(name)
				nmaxtries = 0
				for n in names:
					name = n
					ad_string,ntries = main_view.not_yet_localized[name]
					if ntries == 0 or ntries >= 100:
						# no address or alreadh maximum tries. skip
						nmaxtries = nmaxtries + 1
						continue
					lat,lon = geocodeAddressString(ad_string)
					if (lat,lon) != (None,None):
						k = (lat,lon)
						if k not in main_view.points:
							main_view.points[k] = (name,ad_string,None)
						else:
							old_name,old_ad_string,annot = main_view.points[k]
							# remove old annotation
							remove_one_pin(main_view.mk_map_view_plan,annot)
							join_photos(old_name,name)
							name = join_names(old_name,name)
							# no del contacts_photos[old_name] because could be used
							# for other gps if a contact has several addresses
						del main_view.not_yet_localized[n]
						main_view.right_button_items[1].title = str(len(main_view.not_yet_localized)) + ' not (yet) localized'
						subtitle = ad_string
						annot = add_pin(main_view.mk_map_view_plan,lat,lon, name, subtitle, select=False)		
						main_view.points[k] = (name,ad_string,annot)
					else:
						ntries = ntries + 1
						main_view.not_yet_localized[name] = (ad_string,ntries)
						time.sleep(0.1*ntries)

				# end of loop on not_yet_localized			
				if nmaxtries == len(main_view.not_yet_localized):
					main_view.run = False			
				if main_view.not_yet_localized == {}:
					main_view.run = False

			# end of while => no more to be localized	or enough tries
			if main_view.not_yet_localized == {}:		
				main_view.right_button_items[1].title = ''	# no more to be localized
			else:
				main_view.right_button_items[1].tint_color = 'red'
		except Exception as e:
			#print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
			pass
			
def join_names(name1,name2):
	w2 = name2.split()
	n1 = name1.split(' & ')				# already several names?
	found = False
	nn = ''
	for n in n1:
		if nn != '':
			nn = nn + ' & '
		w1 = n.split()
		# check if some last parts are identic, assumed to be same last name
		li_min = 0
		for li in range(1,min(len(w1),len(w2))):
			if w1[-li] == w2[-li]:
				li_min = li
			else:
				break
		if li_min > 0:
			nn1 = ''
			for i in range(0,len(w1)-li_min):
				if nn1 != '':
					nn1 = nn1 + ' '
				nn1 = nn1 + w1[i]
			nn2 = ''
			for i in range(0,len(w2)-li_min):
				if nn2 != '':
					nn2 = nn2 + ' '
				nn2 = nn2 + ' ' + w2[i]
			nn = nn + nn1 + ',' + nn2
			for li in range(li_min,0,-1):
				nn = nn + ' ' + w1[-li]
			found = True
		else:
			nn = nn + n 
	if not found:
		name = name1 + ' & ' + name2	
	else:
		name = nn
	return name
			
def join_photos(name1,name2):
	global  contacts_photos
	img1 = contacts_photos[name1] 
	img2 = contacts_photos[name2]
	new_name = join_names(name1,name2)
	if img2 == None:
		img_new = img1
	elif img1 == None:
		img_new = img2
	else:
		# join horizontally the two images because they have same height
		w1,h1 = img1.size
		w2,h2 = img2.size
		with ui.ImageContext(w1+w2,h1) as ctx:
			img1.draw(0,0,w1,h1)
			img2.draw(w1,0,w2,h1)
			img_new = ctx.get_image()				
		contacts_photos[new_name] = img_new

class MyView(ui.View):

	def __init__(self,w,h,simulation):
		global map_pin_type, map_pin_color, map_addr_color, map_pin_size, map_pin_radius, map_pin_borderwidth, map_pin_bordercolor, contacts_photos
		self.width = w
		self.height = h
		self.simulation = simulation
		self.contacts = []
		self.points = {}
		contacts_photos = {}		

		# bouton for address
		address_button = ui.ButtonItem()
		address_button.title = 'address'
		address_button.tint_color = 'green'
		address_button.action = self.address_button_action
		
		# bouton for pin type
		pin_type_button = ui.ButtonItem()
		pin_type_button.title = 'pin'
		pin_type_button.tint_color = 'red'
		pin_type_button.action = self.pin_type_button_action
		
		self.left_button_items = (address_button,pin_type_button)
		
		# bouton for map type
		map_type_button = ui.ButtonItem()
		map_type_button.title = 'satellite'
		map_type_button.action = self.map_type_button_action
		
		# bouton for not yet localized
		not_yet_localized_button = ui.ButtonItem()
		not_yet_localized_button.title = ''
		not_yet_localized_button.action = self.not_yet_localized_button_action	

		self.right_button_items = (map_type_button,not_yet_localized_button)
		
		# global settings		
		map_pin_type = 1								# 0=pin 1=photo 2=carree 3=ronde
		map_pin_size = 80
		map_pin_color = 0 							# 0=red 1=green 2=purple
		map_addr_color = 1 							# 0=red 1=green 2=purple
		map_pin_radius = 5
		map_pin_borderwidth = 2
		map_pin_bordercolor = (255,0,0)	# red
		
		# Message Label
		msg = ui.Label(name='msg_label')
		msg.frame = (w/4,h/2,w/2,28)
		msg.background_color=(0.00, 0.50, 1.00, 0.5)	
		msg.bg_color = 'bisque'		
		msg.border_width = 2
		msg.text_color = 'black'
		msg.border_color = 'black'

		msg.alignment = ui.ALIGN_CENTER
		msg.font= ('Courier-Bold',20)
		msg.hidden = True
		self.add_subview(msg)
		
		# progressbar
		progress_bar = ui.Label(name='progress_bar', flex='') 
		progress_bar.background_color=(0.00, 0.50, 1.00, 0.5)
		progress_bar.bg_color=(0.00, 0.50, 1.00, 0.5)
		progress_bar.hidden = True
		self.add_subview(progress_bar)
		
		# textfield for address
		address_textfield = ui.TextField(name='address_textfield')
		address_textfield.frame = (10,10,self.width-20,32)
		address_textfield.text = ''
		address_textfield.action = self.address_textfield_action
		address_textfield.hidden = True
		self.add_subview(address_textfield)
		
		# MapView for maps
		x = 0	
		y = 0
		w = self.width		
		h = self.height					
		frame = CGRect(CGPoint(x, y), CGSize(w, h))
		self.mk_map_view_plan = build_mapview(self,frame)
		#print(dir(self.mk_map_view_plan))

		self.not_yet_localized = {}		

		ui.delay(self.scan_contacts,0.1)	

	def compute_region_param(self):
		# Compute min and max of latitude and longitude
		# {(lat,lon):(name,addr)}
		l = self.points.keys() # [(lat,lon),(lat,lon),...]
		#print(l)
		min_lat = min(l,key = lambda x:x[0])[0]
		max_lat = max(l,key = lambda x:x[0])[0]
		min_lon = min(l,key = lambda x:x[1])[1]
		max_lon = max(l,key = lambda x:x[1])[1]
		d_lat = 1.2*(max_lat-min_lat)
		d_lon = 1.2*(max_lon-min_lon)
		return min_lat,min_lon,max_lat,max_lon,d_lat,d_lon
		
	def address_button_action(self,sender):
		self['address_textfield'].hidden = False
		self['address_textfield'].bring_to_front()
		self['address_textfield'].begin_editing()

	@ui.in_background		
	def address_textfield_action(self,sender):
		ad_string = sender.text
		if ad_string.strip() == '':
			sender.hidden = True	
			return
		lat,lon = geocodeAddressString(ad_string)
		if (lat,lon) != (None,None):
			self.address = ('address',ad_string,lat,lon)
			sender.text_color = 'black'
			sender.hidden = True	
			ui.delay(self.add_pin_of_address,0.1)
		else:
			sender.text_color = 'red'

	@on_main_thread						
	def add_pin_of_address(self):
		name,subtitle,lat,lon = self.address
		annot = add_pin(self.mk_map_view_plan,lat,lon,name,subtitle,select=False)		
		self.points[(lat,lon)] = (name,subtitle,annot)
		# center map on address
		set_center_coordinate(self.mk_map_view_plan, lat, lon, animated=False)
		# zoom so area of 2 km
		d = 1 / 111		# 1° lat or lon = 111 km
		set_region(self.mk_map_view_plan, lat, lon, d, d, animated=True)	
		
	def pin_type_button_action(self,sender):
		global map_pin_type
		t = ['photo','pin']
		w = t.index(sender.title)
		w = w + 1
		if w > 1:
			w = 0
		sender.title  = t[w]
		sender.tint_color = ['blue','red'][w]
		map_pin_type = w
		self.disp(redraw=True)
		
	def map_type_button_action(self,sender):
		t = ['satellite','hybrid','standard']
		w = t.index(sender.title)
		w = w + 1
		if w > 2:
			w = 0
		sender.title  = t[w]
		self.mk_map_view_plan.mapType = w
	
	def not_yet_localized_button_action(self,sender):
		x = self.width - 100
		y = 50
		menu = []
		for k in sorted(self.not_yet_localized.keys()):
			ad,n = self.not_yet_localized[k]
			menu.append(str(n)+' '+k+':'+ad)
		my_list_popover(menu,x=x,y=y,color='white', title='not (yet) localized contacts')
		
	def callback(self,n): 			
		if self['progress_bar'].hidden:
			self['progress_bar'].x = self['msg_label'].x
			self['progress_bar'].y = self['msg_label'].y
			self['progress_bar'].height = self['msg_label'].height
			self['progress_bar'].hidden = False
			self['progress_bar'].bring_to_front()	

		self['progress_bar'].width = self['msg_label'].width * n/self.ntot
		if n == self.ntot:
			self['msg_label'].hidden = True				# hide msg
			self['progress_bar'].hidden = True	# hide progress bar	
			
	@ui.in_background	# to see the progress bar						
	def scan_contacts(self):	
		global limit_reached	
		if not self.simulation:
			all_people = contacts.get_all_people()
		else:
			simul = namedtuple('simul', ['full_name','address','image_data'])
			all_people = [
				simul('Old Brueghel',[('home',{'Street':'Rue de la Regence 3', 'ZIP':'', 'City':'Bruxelles', 'Country':'Belgium'})], 'test:Lenna'),
				simul('Young Brueghel',[('home',{'Street':'Rue de la Regence 3', 'ZIP':'', 'City':'Bruxelles', 'Country':'Belgium'})], 'test:Peppers'),
				simul('Rene Magritte',[('home',{'Street':'Rue de la Regence 3', 'ZIP':'', 'City':'Bruxelles', 'Country':'Belgium'})], 'test:Sailboat'),
				simul('Auguste Renoir',[('home',{'Street':'Rue d Rivoli', 'ZIP':'','City':'Paris','Country':'France'})], 'test:Mandrill'),
				simul('Vincent Van Gogh',[('home',{'Street':'Museumplein 6', 'ZIP':'', 'City':'Amsterdam', 'Country':'Holland'})], 'test:Boat'),
				simul('Albrecht Durer',[('home',{'Street':'Pariser Platz 4', 'ZIP':'', 'City':'Berlin', 'Country':'Germany'})], 'test:Bridge'),
				simul('example without photo',[('home',{'Street':'', 'ZIP':'', 'City':'Prague', 'Country':'Tchekie'})], None),
				simul('example without address',[('home',{'Street':'', 'ZIP':'', 'City':'', 'Country':''})], None)
				]
		self.ntot = len(all_people)
		self['msg_label'].hidden = False
		self['msg_label'].text = 'Scan Contacts'
		self['msg_label'].bring_to_front()	
		n = 0
		for person in all_people:
			n = n + 1
			self.callback(n)
			#if n==3:		# for quicker test
			#	break			# for quicker test
			ads = person.address
			#[('_$!<Home>!$_', {'Street': 'xxxx', 'ZIP': 'yyy', 'City': 'zzz', 'CountryCode': 'uu', 'State': '', 'Country': 'vv'})]
			try:
				for ad in ads:	# if multiple addresses
					dic = ad[1]		# ('name',dict)
					#print(dic)
					street = dic['Street']
					b = street.lower().find('bte')
					if b >= 0:
						street = street[:b]
					ad_string = street + ',' + dic['ZIP'] + ' ' + dic['City'] + ',' + dic['Country']
					name = person.full_name
					if person.image_data == None:
						contacts_photos[name] = None
					else:
						# store reduced photo to win memory 
						if not self.simulation:
							img = ui.Image.from_data(person.image_data)
						else:
							img = ui.Image.named(person.image_data)
						wh = img.size
						# normal photo 
						h = map_pin_size
						w = int(h * wh[0] / wh[1])
						with ui.ImageContext(w,h) as ctx:
							img.draw(0,0,w,h)
							img = ctx.get_image()				
						contacts_photos[name] = img
					if ad_string.replace(',','').strip() == '':
						# no address
						self.not_yet_localized[name] = ('',0)
						continue
					gps = geocodeAddressString(ad_string)			
					if gps == (None,None):
						self.not_yet_localized[name] = (ad_string,1)
					else:
						k = (gps[0],gps[1])
						if k not in self.points:
							self.points[k] = (name,ad_string,None)
						else:
							old_name,old_ad_string,annot = self.points[k]
							join_photos(old_name,name)
							# no del contacts_photos[old_name] because could be used
							# for other gps if a contact has several addresses
							new_name = join_names(old_name,name)
							self.points[k] = (new_name,old_ad_string,annot)
			except Exception as e:
				print(str(e))
				gps = (None,None)
			self.contacts.append([person,gps])
		self.callback(self.ntot)
		ui.delay(self.disp,0.1)

		if self.not_yet_localized != {}:	
			self.right_button_items[1].title = str(len(self.not_yet_localized)) + ' not (yet) localized'
			self.right_button_items[1].tint_color = 'green'
			self.run = True
			server_thread = my_thread()
			server_thread.start()
		
	@on_main_thread			
	def disp(self,redraw=False):
		# remove all annotations, one by one, because for  little number of
		# annotations, remove_all_pins crashes, no ide :a why
		#remove_all_pins(self.mk_map_view_plan)	
		for k in self.points.keys():
			name,ad_string,annot = self.points[k]
			# remove old annotation
			remove_one_pin(self.mk_map_view_plan,annot)
		if not redraw:
			if self.points != {}:
				min_lat,min_lon,max_lat,max_lon,d_lat,d_lon = self.compute_region_param()
				set_region(self.mk_map_view_plan, (min_lat+max_lat)/2, (min_lon+max_lon)/2,1.2*(max_lat-min_lat), 1.2*(max_lon-min_lon), animated=True)	
			else:	
				set_world_region(self.mk_map_view_plan,animated=True)	
		for k in self.points.keys():
			lat,lon = k
			name,address,annot = self.points[k]
			# add a pin at address
			annot = add_pin(self.mk_map_view_plan,lat,lon,name,address, select=False)	
			self.points[k] = name,address,annot
				
	def will_close(self):
		self.run = False		# to force thread to end
		if 'from_launcher' in sys.argv:
			# Back to home screen
			webbrowser.open('launcher://crash')
		
def main(simulation=False):
	global main_view,contacts_photos
	
	#----- Main process -----
	console.clear()
	
	# Initializations
	w, h = ui.get_screen_size()
	disp_mode = 'full_screen'
		
	# Hide script
	main_view = MyView(w,h,simulation)
	main_view.background_color='white'
	main_view.name = 'Contacts on map'

	main_view.present(disp_mode,hide_title_bar=False)
	
# Protect against import	
if __name__ == '__main__':
	main()#simulation=True)
