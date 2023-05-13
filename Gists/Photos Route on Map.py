# todo
# - settîngs pin's visible or not
# - settings route color/width
# coding: utf-8
#
# MKMapView part initially copied from OMZ MapView demo
#		 https://gist.github.com/omz/451a6685fddcf8ccdfc5
# then "cleaned" to keep the easiest code as possible
#
# For use of objc_util calls and crashes trace, more than help received from
#   @dgelssus and @JonB in Pythonista forum
#		https://forum.omz-software.com/topic/3507/need-help-for-calling-an-objective_c-function
#
# Display MKPolyline in Mapkit from Robert Kerr
#   http://blog.robkerr.com/adding-a-mkpolyline-overlay-using-swift-to-an-ios-mapkit-map/
#
import console
from objc_util import *
import ctypes
import ui
from PIL import Image
import photos			

class CLLocationCoordinate2D (Structure):
	_fields_ = [('latitude', c_double), ('longitude', c_double)]
class MKCoordinateSpan (Structure):
	_fields_ = [('d_lat', c_double), ('d_lon', c_double)]
class MKCoordinateRegion (Structure):
	_fields_ = [('center', CLLocationCoordinate2D), ('span', MKCoordinateSpan)]

MKPolyline = ObjCClass('MKPolyline')
MKPolylineRenderer = ObjCClass('MKPolylineRenderer')
MKPointAnnotation = ObjCClass('MKPointAnnotation')
MKAnnotationView = ObjCClass('MKAnnotationView')

map_pin_size = 80

def mapView_viewForAnnotation_(self,cmd,mk_mapview,mk_annotation):
	global route_points
	try:
		# not specially called in the same sequence as pins created
		# should have one MK(Pin)AnnotationView by type (ex: pin color)
		annotation = ObjCInstance(mk_annotation)
		mapView = ObjCInstance(mk_mapview)
		if annotation.isKindOfClass_(MKPointAnnotation):
			tit = str(annotation.title())	
			subtit = str(annotation.subtitle())	
			id = subtit
			pinView = mapView.dequeueReusableAnnotationViewWithIdentifier_(id)		
			if not pinView:
				# Modify pin image: use MKAnnotationView
				pinView = MKAnnotationView.alloc().initWithAnnotation_reuseIdentifier_(annotation,id)
				ui_image = route_points[int(subtit)][3]
				pinView.setImage_(ui_image.objc_instance)
				pinView.canShowCallout = True
			else:
				pinView.annotation = annotation
			return pinView.ptr
		return None
	except Exception as e:
		print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

def mapView_rendererForOverlay_(self,cmd,mk_mapview,mk_overlay):
	try:
		overlay = ObjCInstance(mk_overlay)
		mapView = ObjCInstance(mk_mapview)
		if overlay.isKindOfClass_(MKPolyline):
			pr = MKPolylineRenderer.alloc().initWithPolyline(overlay);
			pr.strokeColor = UIColor.blueColor().colorWithAlphaComponent(0.5);
			pr.lineWidth = 2;
			return pr.ptr
			pass
		return None
	except Exception as e:
		print('exception: ',e)
	
# Build method of MKMapView Delegate
methods = [mapView_rendererForOverlay_, mapView_viewForAnnotation_]
protocols = ['MKMapViewDelegate']
try:
	MyMapViewDelegate = ObjCClass('MyMapViewDelegate')
except:
	MyMapViewDelegate = create_objc_class('MyMapViewDelegate', NSObject, methods=methods, protocols=protocols)

class MapView(ui.View):

	@on_main_thread
	def __init__(self, *args, **kwargs):
		ui.View.__init__(self, *args, **kwargs)
		MKMapView = ObjCClass('MKMapView')
		frame = CGRect(CGPoint(0, 0), CGSize(self.width, self.height))
		self.mk_map_view = MKMapView.alloc().initWithFrame_(frame)
		flex_width, flex_height = (1<<1), (1<<4)
		self.mk_map_view.setAutoresizingMask_(flex_width|flex_height)
		self_objc = ObjCInstance(self)
		self_objc.addSubview_(self.mk_map_view)
		self.mk_map_view.release()
		
		# Set Delegate of mk_map_view
		self.map_delegate = MyMapViewDelegate.alloc().init().autorelease()
		self.mk_map_view.setDelegate_(self.map_delegate)
	
	@on_main_thread
	def add_pin(self, lat, lon, title, subtitle):
		global all_points
		'''Add a pin annotation to the map'''
		coord = CLLocationCoordinate2D(lat, lon)
		all_points.append(coord)			# store all pin's for MKPolyline
		annotation = MKPointAnnotation.alloc().init().autorelease()
		annotation.setTitle_(title)
		annotation.setSubtitle_(str(subtitle))
		annotation.setCoordinate_(coord, restype=None, argtypes=[CLLocationCoordinate2D])
		self.mk_map_view.addAnnotation_(annotation)
		
	@on_main_thread
	def set_region(self, lat, lon, d_lat, d_lon, animated=False):
		'''Set latitude/longitude of the view's center and the zoom level (specified implicitly as a latitude/longitude delta)'''
		region = MKCoordinateRegion(CLLocationCoordinate2D(lat, lon), MKCoordinateSpan(d_lat, d_lon))
		self.mk_map_view.setRegion_animated_(region, animated, restype=None, argtypes=[MKCoordinateRegion, c_bool])
		
	@on_main_thread	
	def addPolyLineToMap(self):
		global all_points
		global all_points_array
		all_points_array = (CLLocationCoordinate2D * len(all_points))(*all_points)
		polyline = ObjCInstance(MKPolyline.polylineWithCoordinates_count_(
    all_points_array,
    len(all_points),
    restype=c_void_p,
    argtypes=[POINTER(CLLocationCoordinate2D), c_ulong],
))
		self.mk_map_view.addOverlay_(polyline)
		
def main():
	global all_points, route_points
	
	#----- Main process -----
	console.clear()
	
	# Hide script
	back = MapView(frame=(0, 0, 540, 620))
	back.background_color='white'
	back.name = 'Display route of localized photos'
	back.present('full_screen', hide_title_bar=False)
	
	# Get a list of all photos
	ps = photos.get_assets(media_type='image')

	# Loop on all photos
	route_points = []
	min_date = min(ps[0].creation_date,ps[1].creation_date).date()
	max_date = max(ps[0].creation_date,ps[1].creation_date).date()
	for p in ps:
		p_date = p.creation_date.date()
		if (len(ps) > 2) or (len(ps) == 2 and p_date >= min_date and p_date <= max_date):
			# Photo belongs to the route period
			if p.location:
				# Photo has GPS tags
				lat = p.location['latitude']
				lon = p.location['longitude']

				# store reduced photo to win memory 
				img = p.get_ui_image()
				wh = img.size
				# normal photo 
				h = map_pin_size
				w = int(h * wh[0] / wh[1])
				with ui.ImageContext(w,h) as ctx:
					img.draw(0,0,w,h)
					img = ctx.get_image()				

				# store latitude, longitude and taken date
				route_points.append((lat,lon,p_date, img))
				
	if len(route_points) < 2:
		console.hud_alert('At least two localized photos neded','error')
		back.close()
		return
	# Sort points by ascending taken date
	route_points = sorted(route_points,key = lambda x: x[2])
	# Compute min and max of latitude and longitude
	min_lat = min(route_points,key = lambda x:x[0])[0]
	max_lat = max(route_points,key = lambda x:x[0])[0]
	min_lon = min(route_points,key = lambda x:x[1])[1]
	max_lon = max(route_points,key = lambda x:x[1])[1]
	# Display map, center and zoom so all points are visible
	back.set_region((min_lat+max_lat)/2,(min_lon+max_lon)/2, 1.2*(max_lat-min_lat), 1.2*(max_lon-min_lon), animated=True)
	# Display pin's
	all_points = []
	idx = 0
	for point in route_points:
		back.add_pin(point[0],point[1],str(point[2]), str(idx))
		idx += 1

	# Display polygon line of sorted locations
	back.addPolyLineToMap()
			
# Protect against import	
if __name__ == '__main__':
	main()
