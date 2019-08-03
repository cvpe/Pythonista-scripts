# bugs
# ----
# - bug: parfois cases vides mais pgm dit qu'il y a une photo
# - bug: souvent exception decode....
#			line pil2 = img.pil.copy()
#			AttributeError: 'ImagingDecoder' object has no attribute 'cleanup'
# - bug: souvent crash sans indication
# - bug: tap au dessus dit parfois " hors cases"
#
# todo
# ----
#
# - revoir flag save set/reset
# - pan/pinch zoom/center
#
import console
import os
import ui
import sys
import webbrowser
import photos
import io
import colorsys
import ImageColor
import ImageFont
from PIL import Image
from PIL.ExifTags import TAGS
from objc_util import *
from Gestures import Gestures
import time
from  VersionInStatusBar import VersionInStatusBar

version = '01.01'
VersionInStatusBar(version=version)

def pil2ui(imgIn):
	with io.BytesIO() as bIO:
		imgIn.save(bIO, 'PNG')
		imgOut = ui.Image.from_data(bIO.getvalue())
	del bIO
	return imgOut

def my_list_popover(elements,val=None,x=None,y=None,color='white',multiple=False,title=None,selectable=True):
	global back,couleurs,grids,thumbs
	class my_list(ui.View):
		def __init__(self,selected):

			# In multiple selection mode, an "ok" button is needed
			if multiple:
				ok_button = ui.ButtonItem()
				ok_button.title = 'ok'
				ok_button.action = self.ok_button_action
				self.right_button_items = [ok_button]
				
			# ListDataSource for clients TableView
			elements_lst = ui.ListDataSource(items=lst)
			# ListDataSource has no attribute "name"
			elements_lst.delete_enabled = False
			elements_lst.move_enabled = False
			elements_txt = ui.TableView(name='elements_txt')
			elements_txt.allows_multiple_selection = multiple
			elements_txt.allows_selection = selectable
			elements_txt.text_color = 'black'
			elements_txt.font= ('Courier',12)
			if elements == grids:
				elements_txt.row_height = back.thumb_size
			else:
				elements_txt.row_height = elements_txt.font[1] * 2
			h = len(lst) *	elements_txt.row_height
			font = ImageFont.truetype('Courier',16)
			w = 0

			if elements == grids:
				ws, hs = ui.get_screen_size()
				w = int(elements_txt.row_height*ws/hs)
				h_ele = elements_txt.row_height
				h_max = h_screen*0.9
			else:
				for element in lst:
					w_ele,h_ele = font.getsize(element)
					if w_ele > w:
						w = w_ele
				w = w + 32
				h_max = h_screen*0.8
			elements_txt.content_size = (w,h)
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
			if not multiple:
				if selected >= 0:
					elements_txt.selected_row = (0,selected)
			else:
				if selected_lst != []:
					elements_txt.selected_rows = selected_lst
						
			elements_txt.delegate  = self
			self.add_subview(elements_txt)	
			self.width = elements_txt.width   + 8
			self.height = elements_txt.height + 8
			self.corner_radius = 20
			self.border_color = 'blue'
			self.border_width = 2
			self.background_color = color
			if title and multiple:
				# title bar displayed in multiple
				self.name = title
			self.pending = []

		def ok_button_action(self,sender):
			lst.append(str(multiples)) # '['xxxx','yyyy']'
			v.close()
			
		def tableview_did_deselect(self, tableview, section, row):
			# Called when a row was deselected (multiple only)
			if multiple:
				multiples.remove(lst[row])
				#print(multiples)
				
		def tableview_did_select(self, tableview, section, row):
			# Called when a row was selected
			if multiple:
				multiples.append(lst[row]) 				# ['xxxx','yyyy']
				#print(multiples)
			else:
				lst.append(lst[row])
				v.close()
		
		def tableview_accessory_button_tapped(self, tableview, section, row):
			# Called when the accessory (ex: info) tapped
			if multiple:
				multiples.append('tapped'+lst[row])
				lst.append(str(multiples)) 		# '['xxxx','yyyy','tapped.....']'
			else:
				lst.append('tapped'+lst[row]) # 'tapped...'
			v.close()
			
		def tableview_cell_for_row(self, tableview, section, row):
			cell = ui.TableViewCell()
			selected_cell = ui.View()
			selected_cell.border_color = 'black'
			selected_cell.border_width = 2
			selected_cell.corner_radius = 10
			data = tableview.data_source.items[row]
			if elements == grids:
				selected_cell.bg_color = 'lightgray'
			elif elements != couleurs:
				selected_cell.bg_color = 'cornflowerblue'
			cell.selected_background_view = selected_cell

			cell.text_label.text = data
			cell.text_label.alignment = ui.ALIGN_LEFT
			ch1 = cell.text_label.text[0]						# 1st char of text
			if ch1 == '🈸':
				g = ui.Button()
				g.background_color = 'white'
				g.image = ui.Image.named('iob:grid_32')
				g.width  = 28
				g.height = 28
				g.x = 12
				g.y = 0
				cell.content_view.add_subview(g)	
			cell.text_label.text_color = 'black'
			if elements == couleurs:
				cell.bg_color = data
			else:
				cell.bg_color = color
				
			if elements == grids:
				cell.text_label.text = ''
				h = tableview.row_height
				w = tableview.width
				rows = data.split('/')
				ny = len(rows)
				x0 = 2
				y0 = 5
				dy = int((h-2*y0)/ny)	
				y = y0
				bs = {}
				for iy in range(0,ny):				# loop on rows
					x = x0
					nx = len(rows[iy])					# should be equal on each row
					dx = int((w-2*x0)/nx)	
					for ix in range(0,nx):
						c = rows[iy][ix]					# cell n°
						if c not in bs:
							b = ui.Button()
							b.enabled = False
							if ix < (nx-1):
								wx = dx
							else:
								wx = (w-2*x0) - x # force all last right same
							b.border_width = 1
							b.border_color = 'blue'
							b.title = c
							b.tint_color ='blue'
							b.frame = (x,y,wx,dy)
						else:
							# split cell on several rows or columns: dx or dy will change
							b = bs[c]
							if b.y == y:
								b.width = (x + wx - 1) - b.x + 1 # same row
							else:
								b.height = (y + dy - 1) - b.y + 1 # same col
						bs[c] = b							
						k = 'Photo ' + c
						if k in thumbs:
							if 'Image' in str(type(thumbs[k])):
								img = ui.ImageView()
								img.frame = (0,0,b.width,b.height)
								img.content_mode = ui.CONTENT_SCALE_ASPECT_FILL
								img.flex = 'WH'
								img.image = thumbs[k]
								b.add_subview(img)
							elif type(thumbs[k]) is str:
								b.title = b.title + ' ' + thumbs[k]	
						cell.content_view.add_subview(b)
						x = x + dx - 1
					y = y + dy - 1
				del bs
			return cell		
	
	lst = []
	i = 0
	selected = -1
	if type(elements) is dict:
		elements_list = sorted(elements.keys())
	elif type(elements) is list:
		elements_list = elements
	if multiple:
		# val = ['xxx','yyy']
		if val:  # not None
			val_lst = ast.literal_eval(val) # convert str -> dict
		else:
			val_lst = []
		selected_lst = []
		multiples = []
	if elements == couleurs: 
		ncmax_colors = 0
		for element in elements_list:
			l = len(element)
			if l > ncmax_colors:
				ncmax_colors = l
	for element in elements_list:
		lst.append(element)
		if not multiple:
			if element == val:
				selected = i
		else:
			if element in val_lst:
				selected_lst.append((0,i))
				multiples.append(element)
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
	if not multiple:
		v.present('popover',popover_location=(x,y),hide_title_bar=True)
	else:
		v.present('popover',popover_location=(x,y),hide_title_bar=False)
	v.wait_modal()
	return lst[len(lst)-1]	# return last
	
class MyView(ui.View):
	def __init__(self,w,h):
		self.width = w
		self.height = h	
		self.grid = '1'
		self.line_width = 1
		self.line_color = 'blue'
		self.saved = None
		d_button = 20
		y_button = 20
		
		# End button
		end_button = ui.Button(name='end_button')
		end_button.title = '❌'
		end_button.width  = 32
		end_button.height = 32
		end_button.x = d_button
		end_button.y = y_button
		end_button.font= ('Courier-Bold',20)
		end_button.action = self.end_button_action
		self.add_subview(end_button)	
		
		# Help button
		help_button = ui.Button(name='help_button')
		help_button.title = '❓'
		help_button.width  = 32
		help_button.height = 32
		help_button.x = end_button.x + end_button.y + d_button
		help_button.y = y_button
		help_button.font= ('Courier-Bold',20)
		help_button.action = self.help_button_action
		self.add_subview(help_button)			
		
		# grid button
		grid_button = ui.Button(name='grid_button')
		grid_button.image = ui.Image.named('iob:grid_32')
		#grid_button.title = '🈸'
		grid_button.width  = 32
		grid_button.height = 32
		grid_button.x = self.width - d_button - grid_button.width
		grid_button.y = y_button
		grid_button.action = self.grid_button_action
		self.add_subview(grid_button)	
		
		# thick button
		thick_button = ui.Button(name='thick_button')
		#thick_button.image = ui.Image.named('iob:arrow_expand_32')
		thick_button.title = '✏️'
		thick_button.width  = 32
		thick_button.height = 32
		thick_button.x = grid_button.x - d_button - thick_button.width
		thick_button.y = y_button
		thick_button.border_color = self.line_color
		thick_button.border_width = self.line_width
		thick_button.action = self.thick_button_action
		self.add_subview(thick_button)	
		
		# line button
		line_button = ui.Button(name='line_button')
		#line_button.image = ui.Image.named('emj:Horizontal_Traffic_Light').with_rendering_mode(ui.RENDERING_MODE_ORIGINAL) 
		line_button.title = '🖍'
		line_button.width  = 32
		line_button.height = 32
		line_button.x = thick_button.x - d_button - line_button.width
		line_button.y = y_button
		line_button.border_color = self.line_color
		line_button.border_width = 3
		line_button.action = self.line_button_action
		self.add_subview(line_button)		
		
		# save button
		save_button = ui.Button(name='save_button')
		save_button.title = '💾'
		save_button.width  = 32
		save_button.height = 32
		save_button.x = line_button.x - d_button - save_button.width
		save_button.y = y_button
		save_button.action = self.save_button_action
		save_button.enabled = True
		self.add_subview(save_button)	
		
		# Title Label
		title_label = ui.Label(name='title_label')
		title_label.x = help_button.x + help_button.width + d_button
		title_label.y = y_button
		title_label.width = save_button.x - d_button - title_label.x
		title_label.height = 32
		title_label.text = 'Collage de photos'
		title_label.alignment = ui.ALIGN_CENTER
		title_label.font= ('Courier-Bold',20)
		title_label.text_color = 'blue'
		self.add_subview(title_label)
		
		self.x0 = 5
		self.y0 = title_label.y + title_label.height + 5
		self.thumb_size = 128
		
		self.build_cells()
		
		self.g = Gestures()
		self.g.add_tap(self,self.tap)		
		self.g.add_pan(self,self.pan)		
		
		self.cursor = None

		# open popover menu of grids of next line uncommented
		#self.grid_button_action(grid_button)
		
	def build_cells(self):
		#print('build_cells: split.grid='+self.grid)
		rows = self.grid.split('/')
		ny = len(rows)
		dy = int((self.height-self.y0-5)/ny)	
		y = self.y0
		bs = {}
		for iy in range(0,ny):				# loop on rows
			x = self.x0
			nx = len(rows[iy])
			dx = int((self.width-2*self.x0)/nx)	
			for ix in range(0,nx):
				c = rows[iy][ix]					# cell n°
				if not self['Photo '+c]:
					b = ui.Button()
					b.name = 'Photo '+c
					b.action = self.tap_cell
					b.touch_enabled = False
					b.title = ''
					b.border_width = self.line_width
					b.border_color = self.line_color
					self.add_subview(b)
				else:
					b = self['Photo '+c]
				if ix < (nx-1):
					wx = dx
				else:
					wx = (self.width-2*self.x0) - x # force all last right same
				if c not in bs:
					b.frame = (x,y,wx,dy)
				else:
					if b.y == y:
						b.width = (x + wx - 1) - b.x + 1 # same row
					else:
						b.height = (y + dy - 1) - b.y + 1 # same col
				bs[c] = b							
				x = x + dx - self.line_width 
			y = y + dy - self.line_width
		self.extr = (self.x0,self.y0,x,y)
			
		for s in self.subviews:
			if 'Photo'in s.name:
				photo_n = s.name.split(' ')
				c = photo_n[1]
				if c not in bs:
					thumbs[s.name] = ''
					self.remove_subview(s)
		del bs	
			
		self.saved = None
		
	@ui.in_background																
	def help_button_action(self,sender):
		x = sender.x + sender.width/2
		y = sender.y + sender.height
		help = [" ", "❌ = fin du programme,", "          vous devrez confirmer si vous avez modifié le collage depuis son dernier sauvetage", "❓ = affichage de cette aide", "💾 = sauver le collage dans les photos enregistrées", "🖍 = changer la couleur de la grille", "✏️ = changer l'épaisseur des lignes de la grille", "🈸 = choix de la grille du collage", " ", "Pour sortir d'un menu déroulant,", "     tapez en dehors ou sur l'élément à sélecter", "Tapez dans une case pour y ajouter ou remplacer une photo", "    à choisir parmi vos toutes photos enregistrées", "Tapez sur une ligne séparant deux cases pour les réunir en une seule", "     impossible si les deux cases sont occupées par une photo","     une confirmation vous sera demandée","Si vous tapez sur une photo, vous verrez apparaître un petit menu où vous pourrez:", "     - remplacer la photo", "     - supprimer la photo, ce que vous devrez confirmer", "     - tourner la photo de", "          90° dans le sens des aiguilles d'une montre", "          180° dans le sens des aiguilles d'une montre", "          90° dans le sens inverse des aiguilles d'une montre", "     - faire une copie miroir haut<->bas de la photo","     - faire une copie miroir gauche<->droite de la photo","Si vous placez votre doigt sur un côté d'une photo et le déplacez,","     vois pourrez changer la dimension des cases ayant ce côté","     et celles ayant un côté le prolongeant"]
		my_list_popover(help,'',x=x,y=y,color='white',selectable=False)	

	@ui.in_background																
	def grid_button_action(self,sender):		
		x = sender.x + sender.width/2
		y = sender.y
		g = my_list_popover(grids,self.grid,x=x,y=y,color='white')
		if g == None:
			return
		if g == self.grid:
			return
		self.grid = g		
		self.build_cells()

	@ui.in_background													
	def line_button_action(self,sender):
		x = sender.x + sender.width/2
		y = sender.y
		c = my_list_popover(couleurs,self.line_color,x=x,y=y,color='white')
		if c == None:
			return
		if c == self.line_color:
			return
		self.line_color = c
		self['line_button'].border_color = self.line_color
		self['thick_button'].border_color = self.line_color
		for s in self.subviews:
			if 'Photo'in s.name:
				s.border_color = self.line_color
				
	@ui.in_background													
	def thick_button_action(self,sender):
		x = sender.x + sender.width/2
		y = sender.y
		thicks = []
		for i in range(0,10):
			thicks.append(str(i))
		t = my_list_popover(thicks,thicks[self.line_width],x=x,y=y,color='white')
		if t == None:
			return
		if t == thicks[self.line_width]:
			return
		if t == '0':
			for s in self.subviews:
				if 'Photo'in s.name:
					# button has zero or one subview if already photo
					if len(s.subviews) == 0:
						console.hud_alert("l'épaisseur de la ligne ne peut pas encore être 0",'error',3)
						return
		self.line_width = thicks.index(t)
		self['thick_button'].border_width = self.line_width
		rows = self.grid.split('/')
		ny = len(rows)
		dy = int((self.height-self.y0-5)/ny)	
		y = self.y0
		bs = {}
		for iy in range(0,ny):				# loop on rows
			x = self.x0
			nx = len(rows[iy])
			dx = int((self.width-2*self.x0)/nx)	
			for ix in range(0,nx):
				c = rows[iy][ix]					# cell n°
				b = self['Photo '+c]
				if ix < (nx-1):
					wx = dx
				else:
					wx = (self.width-2*self.x0) - x # force all last right same
				if c not in bs:
					b.frame = (x,y,wx,dy)
				else:
					if b.y == y:
						b.width = (x + wx - 1) - b.x + 1 # same row
					else:
						b.height = (y + dy - 1) - b.y + 1 # same col
				bs[c] = b				
				b.border_width = self.line_width
				x = x + dx - self.line_width
			y = y + dy - self.line_width
		
	def save_button_action(self,sender):
		path = 'temp.jpg'
		with ui.ImageContext(self.width,self.height) as ctx:
			self.draw_snapshot()				# draw entire view
			ui_image = ctx.get_image()
		pil = Image.open(io.BytesIO(ui_image.to_png()))
		x_min = 9999
		y_min = 9999
		x_max = 0
		y_max = 0
		for s in self.subviews:
			if 'Photo'in s.name:
				if s.x < x_min:
					x_min = int(s.x)
				if s.y < y_min:
					y_min = int(s.y)
				if (s.x + s.width - 1) > x_max:
					x_max = int(s.x + s.width - 1)
				if (s.y + s.height - 1) > y_max:
					y_max = int(s.y + s.height - 1)
		crop_pil = pil.crop((x_min*2,y_min*2,x_max*2,y_max*2))
		crop_pil.save(path , quality=95)
		photos.create_image_asset(path)
		os.remove(path)
		self.saved = True

	@ui.in_background																
	def tap_cell(self,sender):
		assets = photos.get_assets()
		asset = photos.pick_asset(assets=assets,title='Choisissez la photo', multi=None)			
		if not asset:
			return
	
		if len(sender.subviews)	== 0:
			img = ui.ImageView()
			img.name = 'photo'
			img.frame = (0,0,sender.width,sender.height)
			img.content_mode = ui.CONTENT_SCALE_ASPECT_FILL
			img.flex = 'WH'
			sender.add_subview(img)
		else:
			img = sender['photo']
					
		img.image = asset.get_ui_image()
		
		self.set_act(img,'mémoriser photo')
		self.pil_store_params = img
		ui.delay(self.pil_store,0.1)	
		self.sender = sender	# for build_thumb				
		
	def pil_store(self):
		# save pil image also so it os computed only once
		img = self.pil_store_params
		img.pil = Image.open(io.BytesIO(img.image.to_png()))
		self.stop_act(img)	
		
		self.set_act(img,'création miniature')
		ui.delay(self.build_thumb,0.1)

	def set_act(self,img,explic):	
		self.act = ui.ActivityIndicator()
		self.act.x = img.width/2
		self.act.y = img.height/2
		self.act.background_color = (0.0,0.0,1.0,0.5)
		self.act.name = 'Activity_Indicator'
		self.act.style = ui.ACTIVITY_INDICATOR_STYLE_WHITE_LARGE
		img.add_subview(self.act)
		self.expl = ui.Label()
		self.expl.text = explic
		self.expl.background_color = (0.0,0.0,1.0,0.5)
		self.expl.text_color = 'white'
		self.expl.width = 142
		self.expl.height = 30
		self.expl.x = self.act.x + self.act.width/2 - self.expl.width/2
		self.expl.y = self.act.y - self.expl.height 
		img.add_subview(self.expl)
		self.act.start()
		
	def stop_act(self,img):
		self.act.stop()
		img.remove_subview(self.act)
		img.remove_subview(self.expl)
		
	def build_thumb(self):
		# ImageView of photo
		img = self[self.sender.name]['photo']		
		# save thumb as ui.Image for use in popover		
		pil2 = img.pil.copy()
		pil2.thumbnail((self.thumb_size,self.thumb_size))
		thumbs[self.sender.name] = pil2ui(pil2)
		del pil2

		self.stop_act(img)		
		
		enab = True
		for s in self.subviews:
			if 'Photo'in s.name:
				if len(s.subviews) == 0:
					enab = False
					break
		if enab:
			# all buttons have a photo
			self.saved = False

	def tapped_cell(self,x,y):
		d = 20	
		# check if cell tapped
		for s in self.subviews:
			if 'Photo' in s.name:
				if (x > (s.x+d)) and (x < (s.x+s.width-d)) and (y>(s.y+d)) and (y<(s.y+s.height-d)):
					return s
		return None
		
	def tapped_side(self,x,y):
		d = 20	
		# check if side tapped
		cells = []
		for s in self.subviews:
			if 'Photo' in s.name:
				if abs(x-s.x) <= d and y > s.y and y < (s.y + s.height):
					cells.append((s.name,'left'))
				elif abs(x-(s.x+s.width)) <= d and y > s.y and y < (s.y + s.height):
					cells.append((s.name,'right'))
				elif abs(y-s.y) <= d and x > s.x and x < (s.x + s.width):
					cells.append((s.name,'top'))
				elif abs(y-(s.y+s.height)) <= d and x > s.x and x < (s.x + s.width):
					cells.append((s.name,'bottom'))
		return cells
		
	def same_side(self,c1,c2):
		c = self[c1[0]]
		s = c1[1]
		#print(c.frame,s)
		if s == 'left':
			p1 = (c.x,c.y)
			p2 = (c.x,c.y+c.height)
		elif s == 'right':
			p1 = (c.x+c.width,c.y)
			p2 = (c.x+c.width,c.y+c.height)
		elif s == 'top':
			p1 = (c.x,c.y)
			p2 = (c.x+c.width,c.y)
		elif s == 'bottom':
			p1 = (c.x,c.y+c.height)
			p2 = (c.x+c.width,c.y+c.height)
		#print(p1,p2)
		c = self[c2[0]]
		s = c2[1]
		#print(c.frame,s)
		if s == 'left':
			pp1 = (c.x,c.y)
			pp2 = (c.x,c.y+c.height)
		elif s == 'right':
			pp1 = (c.x+c.width,c.y)
			pp2 = (c.x+c.width,c.y+c.height)
		elif s == 'top':
			pp1 = (c.x,c.y)
			pp2 = (c.x+c.width,c.y)
		elif s == 'bottom':
			pp1 = (c.x,c.y+c.height)
			pp2 = (c.x+c.width,c.y+c.height)
		#print(pp1,pp2)
		if abs(p1[0]-pp1[0]) <= self.line_width and abs(p1[1]-pp1[1]) <= self.line_width and abs(p2[0]-pp2[0]) <= self.line_width and abs(p2[1]-pp2[1]) <= self.line_width:
			same = True
		else:
			same = False
		return same	
		
	def prolong_side(self,c1,c2):
		# called if both sides have same direction
		c = self[c1[0]]
		s = c1[1]
		#print(c.frame,s)
		if s == 'left':
			p1 = (c.x,c.y)
			p2 = (c.x,c.y+c.height)
		elif s == 'right':
			p1 = (c.x+c.width,c.y)
			p2 = (c.x+c.width,c.y+c.height)
		elif s == 'top':
			p1 = (c.x,c.y)
			p2 = (c.x+c.width,c.y)
		elif s == 'bottom':
			p1 = (c.x,c.y+c.height)
			p2 = (c.x+c.width,c.y+c.height)
		c = self[c2[0]]
		s = c2[1]
		#print(c.frame,s)
		if s == 'left':
			pp1 = (c.x,c.y)
			pp2 = (c.x,c.y+c.height)
		elif s == 'right':
			pp1 = (c.x+c.width,c.y)
			pp2 = (c.x+c.width,c.y+c.height)
		elif s == 'top':
			pp1 = (c.x,c.y)
			pp2 = (c.x+c.width,c.y)
		elif s == 'bottom':
			pp1 = (c.x,c.y+c.height)
			pp2 = (c.x+c.width,c.y+c.height)
		#print(p1,p2,pp1,pp2)
		if (abs(p1[0]-pp1[0]) <= self.line_width and abs(p1[1]-pp1[1]) <= self.line_width) or (abs(p2[0]-pp2[0]) <= self.line_width and abs(p2[1]-pp2[1]) <= self.line_width)	or (abs(p1[0]-pp2[0]) <= self.line_width and abs(p1[1]-pp2[1]) <= self.line_width) or (abs(p2[0]-pp1[0]) <= self.line_width and abs(p2[1]-pp1[1]) <= self.line_width):
			# one point is common 
			prolong = True
		else:
			prolong = False
		return prolong	
		
	@ui.in_background																
	def tap(self,data):
		if self.cursor:
			return
		#print('tap',data.state,data.number_of_touches)
		x = data.location.x
		y = data.location.y
		if data.state == 3:
			# ended
			s = self.tapped_cell(x,y)
			if not s:
				cells = self.tapped_side(x,y)
				if cells == []:
					console.hud_alert('hors cases','error',2)
					return
				else:
					b = console.alert('vous voulez vraiment joindre deux cases?','', 'oui', 'non', hide_cancel_button=True)
					if b == 2:
						return 
					if len(cells) == 1:
						console.hud_alert('côté pas commun à deux cases','error',2)
						return
					elif len(cells) > 2:
						console.hud_alert('côté commun à plus de deux cases','error',2)
						return
					else:
						# tapped side common to two cells
						# check if sides totally equal, not partially
						if not self.same_side(cells[0],cells[1]):
							console.hud_alert('les deux cases n\'ont pas un côté entièrement commun','error',2)
							return
						if cells[0][0] in thumbs and cells[1][0] in thumbs:
							console.hud_alert('on ne peut pas joindre deux cases occupées par des photos','error',2)
							return
						if cells[0][0] in thumbs:
							i = 1
						elif cells[1][0] in thumbs:
							i = 0
						else:
							i = 1
						c_dele = cells[i][0].split(' ')[1]		# Photo n -> n
						c_keep = cells[1-i][0].split(' ')[1]	# Photo n -> n
						self.grid = self.grid.replace(c_dele,c_keep)
						self.build_cells()
						return
			if s.name not in thumbs:
				# no yet a photo in this cell
				self.tap_cell(s)
				return
			menu = []
			menu.append('remplacer la photo')	# for replacing
			if self.grid != '1':
				menu.append('déplacer la photo')
			menu.append('supprimer la photo')
			menu.append('tourner la photo ⤵️')
			menu.append('tourner la photo ⤴️')
			menu.append('tourner la photo ↩️')
			menu.append('faire une copie miroir gauche<->droite de la photo ↔️')
			menu.append('faire une copie miroir haut<->bas de la photo ↕️')
			t = my_list_popover(menu,'',x=x,y=y,color='white')
			if t == None:
				return
			elif t == 'remplacer la photo':
				# simulate normal tap
				self.tap_cell(s)
			elif t == 'déplacer la photo':
				self.move_delete()			# delete eventual moving photo
				# create an ImageView with the thumb
				self.move_begin(x,y,s.name)
			elif t == 'supprimer la photo':
				b = console.alert('Vous confirmez la suppression de la photo', '', 'oui', 'non', hide_cancel_button=True)
				if b == 2:
					return
				# remove photo of cell
				del thumbs[s.name]
				s.remove_subview(s['photo'])
			elif ('tourner la photo' in t) or ('miroir' in t):
				if '⤴️' in t:
					method = 2 #ROTATE_90
				elif '⤵️' in t:
					method = 4 #ROTATE_270				
				elif '↩️' in t:
					method = 3 #ROTATE_180				
				elif '↔️' in t:
					method = 0 #FLIP_LEFT_RIGHT			
				elif '↕️' in t:
					method = 1 #FLIP_TOP_BOTTOM										

				# ImageView of photo
				img = s['photo']				
				self.pil_transpose_params = (img,method)
				self.set_act(img,'calcul en cours')
				ui.delay(self.pil_transpose,0.1)	
				
	def pil_transpose(self):
		#print('pil_transpose')
		img,method = self.pil_transpose_params
		pil = img.pil
		pil = pil.transpose(method)
		# save pil image also so it is computed only once
		img.pil = pil
		img.image = pil2ui(pil)
		if img.image == None:
			print(('ici'))
		del pil
		self.stop_act(img)	
				
		self.set_act(img,'création miniature')
		self.sender = img.superview			
		ui.delay(self.build_thumb,0.1)	
											
	def move_begin(self,x,y,button_name):
		img = ui.ImageView()
		w = button_name												# ex: Photo 1
		img.name = w.replace('Photo','Move')	# ex: Move 1
		img.content_mode = ui.CONTENT_SCALE_ASPECT_FILL
		img.flex = 'WH'
		img.image = thumbs[button_name]
		w,h = img.image.size
		img.frame = (x-w/2,y-h/2,w,h)
		img.border_width = 2
		img.border_color = (.15, 1.0, .44)
		img.bring_to_front()
		self.add_subview(img)
		self.cursor = img
		
	def move_delete(self):
		if self.cursor:
			self.remove_subview(self.cursor)
			self.cursor = None

	@ui.in_background															
	def move_process(self,data):
		x = data.location.x
		y = data.location.y
		if data.state == 1:
			# began
			self.xp = x
			self.yp = y
		elif data.state == 2:
			# changed
			dx = x - self.xp
			dy = y - self.yp
			self.xp = x
			self.yp = y	
			self.cursor.x = self.cursor.x + dx
			self.cursor.y = self.cursor.y + dy
		elif data.state == 3:
			# ended
			b = console.alert('déplacer la photo ici?', '','oui', 'non, continuer le déplacement', 'annuler le déplacement', hide_cancel_button=True)
			if b == 3:
				# cancel move
				self.move_delete()
				return
			elif b == 2:
				# continue move
				return
			# try to move here
			s = self.tapped_cell(x,y)
			if not s:
				console.hud_alert('hors cases','error',2)
				self.move_delete()
				return
			original_name = self.cursor.name.replace('Move','Photo')
			if original_name == s.name:
				console.hud_alert('même case, pas de modification','error',2)
				self.move_delete()
				return
			if len(s.subviews) > 0:
				b = console.alert('la case contient déja une photo','remplacer?','oui','non',hide_cancel_button=True)
				if b == 2:
					self.move_delete()
					return
				# remove photo of destination cell
				del thumbs[s.name]
				s.remove_subview(s['photo'])
			# move photo in destination cell
			orig = self[original_name]
			img = orig['photo']
			img.frame = (0,0,s.width,s.height)
			orig.remove_subview(img)
			s.add_subview(img)
			thumbs[s.name] = thumbs[original_name]
			del thumbs[original_name]								
			self.move_delete()
					
	def pan(self,data):
		#print('pan',data.state,data.translation)
		if self.cursor:
			self.move_process(data)
			return
		x = data.location.x
		y = data.location.y
		if data.state == 1:
			# began
			self.xp = None
			# search cells of tapped side
			self.moved_cells = self.tapped_side(x,y)	# [(name,side),...]
			if self.moved_cells == []:
				console.hud_alert('aucun côté choisi','error',2)
				return
			#print('before',self.moved_cells)
			# search other cells with sides prolongating selected sides
			moving = {}
			for s_name,s_c in self.moved_cells:
				moving[s_name] = s_c 		# moving cells as a dictionnary
			i_move = 0
			while i_move < len(self.moved_cells):
				# this loop supports adding new cells during its loop
				s_name,s_c = self.moved_cells[i_move]
				# for each moving cell, search in other cells
				for s in self.subviews:
					if 'Photo' in s.name:
						if s.name in moving:
							continue
						# cell not already in moving cells
						#print(s_name,'moving checked vs',s.name,'not yet moving')
						for c in ('left','right','top','bottom'):
							#print('   ',s_c,'moving checked vs',c,'not yet moving')
							if (c in ['left','right'] and s_c not in ['left','right']) or (c not in ['left','right'] and s_c in ['left','right']):
								continue # check only if sides of same direction
							# check if one side is prolongating a moving side
							#print('      same direction, call prolong_side')
							if self.prolong_side((s_name,s_c),(s.name,c)):		
								self.moved_cells.append((s.name,c))
								moving[s.name] = c
								break	# leave loop on sides								
				i_move = i_move + 1								
			#print('after',self.moved_cells)
			d = 20	
			self.xp = x
			self.yp = y
			return
		elif data.state == 3:
			# ended
			self.moved_cells = []
		# changed	
		if not self.xp:
			return 
		dx = x - self.xp
		dy = y - self.yp
		self.xp = x
		self.yp = y	
		#dx,dy = data.translation		# always from began pont
		# check no moving side will not reach its opposite side
		for s_name,c in self.moved_cells:
			s = self[s_name]
			if c == 'left': # move left side
				if (s.width - dx) <= 20: 	# new width could become negative
					dx = s.width - 20
			elif c == 'right': # move right side
				if (s.width + dx) <= 20: 	# new width could become negative
					dx = 20 - s.width	
			elif c == 'top': # move top side
				if (s.height - dy) <= 20: 	# new height could become negative
					dy = s.height - 20
			elif c == 'bottom': # move bottom side
				if (s.height + dy) <= 20: 	# new height could become negative
					dy = 20 - s.height
		# check does not go outside the sheet
		for s_name,c in self.moved_cells:
			s = self[s_name]
			#print(s_name,c,s.frame,dx,dy)
			if c == 'left': # move left side
				s.x = s.x + dx
				s.width = s.width - dx
			elif c == 'right': # move right side
				s.width = s.width + dx
			elif c == 'top': # move top side
				s.y = s.y + dy
				s.height = s.height - dy
			elif c == 'bottom': # move bottom side
				s.height = s.height + dy
			if s.x < self.extr[0]:
				s.x = self.extr[0]
			if s.y < self.extr[1]:
				s.y = self.extr[1]
			if (s.x+s.width) > self.extr[2]:
				s.width = self.extr[2]-s.x
			if (s.y+s.height) > self.extr[3]:
				s.height = self.extr[3]-s.y
				
	@ui.in_background											
	def end_button_action(self,sender):
		if self.saved != None:
			if not self.saved:
				b = console.alert('Projet non sauvé',"sauver d'abord?",'oui','non',hide_cancel_button=True)
				if b == 1:
					self.save_button_action('auto')
		if ('from_launcher' in sys.argv) or ('Christian' not in 		str(ObjCClass('UIDevice').currentDevice().name())): # if from shortcut
			# launched by Launcher or by shortcut in Pam device
			# Back to home screen
			webbrowser.open('launcher://crash')		
		self.close()
		VersionInStatusBar(version=False)
			
def main():
	global back,couleurs,grids,thumbs

	#----- Main code ------------------------
	console.clear()

	grids = ['1', '12', '1/2','123', '11/23', '12/33',  '1/2/3', '12/32', '12/13', '1234', '111/234', '12/34', '123/444', '11/22/34', '12/33/44', '11/23/44', '1/2/3/4', '12/13/14', '12/32/42', '11/23/43', '123/143', '123/425', '1234/5678/9abc/defg', '12345/67890/abcde/fghij/klmno'] #, '5', '1/4', '4/1', '2/3', f'3/2', '1/1/3', '1/3/1', '2/1/2', '2/2/1', '1/2/2', '3/1/1','1/1/1/2', '1/1/2/1', '1/2/1/1', '2/1/1/1', '1/1/1/1/1']		
	
	couleurs = ['aliceblue', 'antiquewhite', 'aqua', 'aquamarine', 'azure', 'beige', 'bisque', 'blanchedalmond',  'burlywood', 'cadetblue', 'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan', 'deeppink', 'deepskyblue', 'dimgray', 'dimgrey', 'dodgerblue', 'firebrick', 'floralwhite', 'forestgreen', 'fuchsia', 'gainsboro', 'ghostwhite', 'gold', 'goldenrod', 'gray', 'green', 'greenyellow', 'grey', 'honeydew', 'hotpink', 'indianred', 'indigo', 'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen', 'lemonchiffon', 'lightblue', 'lightcoral', 'lightcyan', 'lightgoldenrodyellow', 'lightgray', 'lightgreen', 'lightgrey', 'lightpink', 'lightsalmon', 'lightseagreen', 'lightskyblue', 'lightslategray', 'lightslategrey', 'lightsteelblue', 'lightyellow', 'lime', 'limegreen', 'linen', 'magenta', 'maroon', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 'midnightblue', 'mintcream', 'mistyrose', 'moccasin', 'navajowhite', 'navy', 'oldlace', 'olive', 'olivedrab', 'orange', 'orangered', 'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'purple', 'red', 'rosybrown', 'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna', 'silver', 'skyblue', 'slateblue', 'slategray', 'slategrey', 'snow', 'springgreen', 'steelblue', 'tan', 'teal', 'thistle', 'tomato', 'turquoise', 'violet', 'wheat', 'white', 'whitesmoke', 'yellow', 'yellowgreen','black', 'blue', 'blueviolet', 'brown', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkgrey', 'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray', 'darkslategrey', 'darkturquoise', 'darkviolet']
	# Sort colors on HSL H=Hue(teinte) S=Saturation L=Lightness(luminosité)
	couleurs = sorted(couleurs,key=lambda x:colorsys.rgb_to_hsv(ImageColor.getrgb(x)[0],ImageColor.getrgb(x)[1],ImageColor.getrgb(x)[2]))
	
	w, h = ui.get_screen_size()
	disp = 'full_screen'
	back = MyView(w,h)
	back.background_color='white'
	back.present(disp, hide_title_bar=True)		
	
	thumbs = {}
	
if __name__ == '__main__':
	main()
