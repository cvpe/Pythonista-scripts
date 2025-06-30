from objc_util import *
import ctypes
import ui
from math import pi
from ImageColor import getrgb
import threading
from random import random
import ast
import photos

load_framework('SceneKit')

SCNView, SCNScene, SCNBox, SCNPyramid, SCNCone, SCNCylinder, SCNSphere, SCNPlane, SCNNode, SCNMaterial, SCNCamera, SCNLight, SCNAction, SCNLookAtConstraint = map(ObjCClass, ['SCNView', 'SCNScene', 'SCNBox', 'SCNPyramid', 'SCNCone', 'SCNCylinder', 'SCNSphere', 'SCNPlane', 'SCNNode', 'SCNMaterial', 'SCNCamera', 'SCNLight', 'SCNAction',  'SCNLookAtConstraint' ])

class CMRotationRate (Structure):
	_fields_ = [('x', c_double), ('y', c_double), ('z', c_double)]
	
SCNTransaction = ObjCClass('SCNTransaction').alloc()

stop_thread = False
	
class my_thread_bt(threading.Thread):
	def __init__(self, geometry_node):
		threading.Thread.__init__(self)
		self.name = 'bt'
		self.geometry_node = geometry_node
	def run(self):
		global stop_thread
		pitch = 0
		yaw   = 0
		roll  = 0
		delta_ang = pi/10
		SCNTransaction = ObjCClass('SCNTransaction').alloc()
		# https://forum.omz-software.com/topic/3030
		CMMotionManager = ObjCClass('CMMotionManager').alloc().init()
		#print(CMMotionManager.isDeviceMotionAvailable())
		CMMotionManager.startGyroUpdates()
		while True:
			# EulerAngles is a SCNVector3
			# The order of components in this vector matches the axes of rotation:
			# Pitch (the x component) is the rotation about the node’s x-axis.
			# Yaw (the y component) is the rotation about the node’s y-axis.
			# Roll (the z component) is the rotation about the node’s z-axis.
			#pitch += (random() - 0.5) * delta_ang
			#yaw   += (random() - 0.5) * delta_ang
			#roll  += (random() - 0.5) * delta_ang
			gyro_data = CMMotionManager.gyroData()
			if not gyro_data:
				#print('data not available (yet?)')
				continue
			# Using the custom struct here:
			rate = gyro_data.rotationRate(argtypes=[], restype=self.CMRotationRate)
			# You can now access the struct's fields as x, y, z:
			roll  = rate.z
			pitch = rate.x
			yaw   = rate.y
			#print(rate.x, rate.y, rate.z)

			# change euler angles but by using animation
			SCNTransaction.begin()
			SCNTransaction.setAnimationDuration(0.3)
			self.geometry_node.setEulerAngles((pitch, yaw, roll))
			SCNTransaction.commit()
			try:
				if stop_thread:
					break
			except:
				break
		CMMotionManager.stopGyroUpdates()
		CMMotionManager.release()

class MyView(ui.View):
 ###@on_main_thread
 def __init__(self,w,h, asset):
  self.width = w
  self.height = h
  self.name = 'SceneKit'
  self.background_color = 'white'
  
  main_view_objc = ObjCInstance(self)
  scene_view = SCNView.alloc().initWithFrame_options_(((0, 0),(self.width,self.height)), None).autorelease()
  scene_view.setAutoresizingMask_(18)
  scene_view.setAllowsCameraControl_(True)
  #scene_view.setDebugOptions_(0xFFFF)
  main_view_objc.addSubview_(scene_view)
  
  scene = SCNScene.scene()
  scene_view.setScene_(scene)
  
  root_node = scene.rootNode()
  
  camera = SCNCamera.camera()
  camera_node = SCNNode.node()
  camera_node.setCamera(camera)
  d = 50
  camera_node.setPosition((d/2,d/2,d))
  root_node.addChildNode_(camera_node) 

  geometry = SCNBox.boxWithWidth_height_length_chamferRadius_(30, 40, 10, 0)

  geometry_node = SCNNode.nodeWithGeometry_(geometry)
  root_node.addChildNode_(geometry_node)

  Materials = []
  colors = ['red','blue','green','yellow','orange','pink']
  for i in range(0,6):
    Material = SCNMaterial.material()
    if i == 0:
      Material.contents = ObjCInstance(asset.get_ui_image())
    else:
      rgb = getrgb(colors[i])
      r,g,b = tuple(c/255.0 for c in rgb)
      Material.contents = ObjCClass('UIColor').colorWithRed_green_blue_alpha_(r,g,b,1.0)
    Materials.append(Material)
  geometry.setMaterials_(Materials)



  # Add a constraint to the camera to keep it pointing to the target geometry
  constraint = SCNLookAtConstraint.lookAtConstraintWithTarget_(geometry_node)
  constraint.gimbalLockEnabled = True
  camera_node.constraints = [constraint]
  
  light_node = SCNNode.node()
  light_node.setPosition_((30, 0, -30))
  light = SCNLight.light()
  #light.setType_('spot')
  light.setType_('probe')
  #light.setType_('directional')
  light.setCastsShadow_(True)
  light.setColor_(UIColor.whiteColor().CGColor())
  light_node.setLight_(light)
  root_node.addChildNode_(light_node)
  
  self.thread_bt = my_thread_bt(geometry_node)
  self.thread_bt.CMRotationRate = CMRotationRate
  self.thread_bt.start()
  
 def will_close(self):
 	global stop_thread
 	stop_thread = True
 	self.thread_bt.join()

def main():	
		
	all_assets = photos.get_assets()
	asset = photos.pick_asset(assets=all_assets, title='pick photo for iPhone face')
	if not asset:
		# cancel by user
		return
	
	w, h = ui.get_screen_size()
	# fs only added to have SceneKit as a subview of fullscreen view
	fs = ui.View()
	fs.background_color = 'lightgray'
	w,h = 400,400
	MainView = MyView(w, h, asset)
	MainView.frame = (100,100,w,h)
	fs.add_subview(MainView)
	fs.present('fullscreen', hide_title_bar=False)
	
# Protect against import	
if __name__ == '__main__':
  main()

