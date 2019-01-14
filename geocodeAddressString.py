from objc_util import *
import time

def geocodeAddressString(address):
	global handler_done,gps
	handler_done = None
	gps = (None,None)
	# check if contact without address
	def handler(_cmd,obj1_ptr,_error):
		global handler_done,gps
		if not _error and obj1_ptr:
			obj1 = ObjCInstance(obj1_ptr)
			ret = str(obj1)
			#print(ret)
			t = 'center:<'
			i = ret.find(t)
			if i >= 0:
				ret = ret[i+len(t):]
				i = ret.find('>')
				gps = ret[:i]
				try:
					lat, comma, lon = gps.partition(',')
					gps = float(lat), float(lon)
				except Exception as e:
					gps = (None,None)					
		handler_done = True
		return
		
	CLGeocoder = ObjCClass('CLGeocoder').alloc().init()
	#print(dir(CLGeocoder))
	handler_block = ObjCBlock(handler, restype=None, argtypes=[c_void_p, c_void_p, c_void_p])
	CLGeocoder.geocodeAddressString_completionHandler_(ns(address),handler_block)
	#geocodeAddressDictionary_preferredLocale_completionHandler_'
	# wait handler called and finished
	while not handler_done:
		time.sleep(0.01)
	return gps
