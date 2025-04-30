import tkinter as tk
from tkinter import Frame, Canvas, Label
import threading
import obspython as obs
import os
import math

overlay_position	= "top_right"		# top_left, top_right, bottom_left, bottom_right
slide_from			= "none"			# none, left, right, top, bottom
offset_x			= 0					# additional X offset (px)
offset_y			= 0					# additional Y offset (px)
overlay_width		= 0					# fixed overlay width (px), 0 = auto
overlay_height		= 0					# fixed overlay height (px), 0 = auto
overlay_size		= 64				# max icon size (px)
icon_padding		= 10				# padding between icon and text (px)
slide_steps			= 10				# slide animation steps
slide_interval		= 30				# slide frame interval (ms)
display_time		= 2000				# display duration before fade out (ms)

default_font_size	= 11

icon_rec_start_path = ""
icon_rec_saved_path = ""
icon_rb_start_path  = ""
icon_rb_saved_path  = ""

icon_rec_start	= None
icon_rec_saved	= None
icon_rb_start	= None
icon_rb_saved	= None

app_instance 	= None
thd 			= None
margin 			= 20


class Application(tk.Tk):
	def __init__(self):
		super().__init__()
		self.attributes('-topmost', True)
		self.overrideredirect(True)
		self.configure(bg='#000000')
		self.attributes('-transparentcolor', '#000000')
		self.attributes('-alpha', 0.0)
		
		self.queue = []
		self.is_animating = False
		
		self.container = Frame(self, bg='#333333', bd=2, relief='ridge')
		self.container.pack()
		
		global canvas, label
		canvas = Canvas(self.container, bg='#333333', highlightthickness=0)
		self.font_size = default_font_size
		canvas.grid(row=0, column=0)
		label = Label(self.container, text='', font=('Roboto', self.font_size, 'bold'), bg='#333333', fg='#ffffff')
		label.grid(row=0, column=1)
		
		self.after(50, self.process_queue)

	def compute_content_size(self):
		self.container.update_idletasks()
		if overlay_width > 0:
			w = overlay_width
		else:
			w = self.container.winfo_reqwidth()
		if overlay_height > 0:
			h = overlay_height
		else:
			h = self.container.winfo_reqheight()
		return w, h

	def compute_position(self, w, h):
		sw = self.winfo_screenwidth(); sh = self.winfo_screenheight()
		if overlay_position == 'top_left':
			x, y = margin, margin
		elif overlay_position == 'bottom_left':
			x, y = margin, sh - h - margin
		elif overlay_position == 'bottom_right':
			x, y = sw - w - margin, sh - h - margin
		else:  # top_right
			x, y = sw - w - margin, margin
		x += offset_x; y += offset_y
		
		x = max(margin, min(x, sw - w - margin))
		y = max(margin, min(y, sh - h - margin))
		return x, y

	def slide_to(self, w, h, fx, fy):
		if slide_from == 'none' or slide_steps <= 0:
			self.geometry(f"{w}x{h}+{fx}+{fy}")
			self.attributes('-alpha', 0.95)
			return
		
		if slide_from == 'left':   sx, sy = -w, fy
		elif slide_from == 'right': sx, sy = self.winfo_screenwidth(), fy
		elif slide_from == 'top':	sx, sy = fx, -h
		else:						 sx, sy = fx, self.winfo_screenheight()
		steps = max(1, slide_steps)
		dx = (fx - sx) / steps; dy = (fy - sy) / steps
		self._anim_step = 0
		self._anim_steps = steps
		self._sx, self._sy, self._dx, self._dy = sx, sy, dx, dy
		self._anim_wh = (w, h)
		self.geometry(f"{w}x{h}+{int(sx)}+{int(sy)}")
		self.attributes('-alpha', 0.95)
		self.after(slide_interval, self._anim_step_func)

	def _anim_step_func(self):
		w, h = self._anim_wh
		if self._anim_step < self._anim_steps:
			x = self._sx + self._dx * (self._anim_step + 1)
			y = self._sy + self._dy * (self._anim_step + 1)
			self.geometry(f"{w}x{h}+{int(x)}+{int(y)}")
			self._anim_step += 1
			self.after(slide_interval, self._anim_step_func)

	def show_notification(self, typ, state):
		global icon_rec_start, icon_rec_saved, icon_rb_start, icon_rb_saved
		canvas.delete('all')
		if typ == 'recording':
			txt = 'Recording Started' if state == 'started' else 'Recording Saved'
			img = icon_rec_start if state == 'started' else icon_rec_saved
		else:
			txt = 'Replay Enabled' if state == 'started' else 'Replay Saved'
			img = icon_rb_start if state == 'started' else icon_rb_saved
		label.config(text=txt)
		canvas.grid_configure(padx=(0, icon_padding)); label.grid_configure(padx=(0, icon_padding))
		
		if img:
			canvas.config(width=img.width(), height=img.height())
			canvas.create_image(img.width()//2, img.height()//2, image=img)
		else:
			canvas.config(width=48, height=48)
			canvas.create_text(24, 24, text='?', fill='#ff5555', font=('Segoe UI',24,'bold'))
			
		w, h = self.compute_content_size()
		fx, fy = self.compute_position(w, h)
		self.slide_to(w, h, fx, fy)
		
		self.after(display_time, self.fade_out)

	def fade_out(self):
		a = self.attributes('-alpha')
		if a > 0.1:
			self.attributes('-alpha', a - 0.05)
			self.after(30, self.fade_out)
		else:
			self.attributes('-alpha', 0.0)
			self.is_animating = False
			self.process_queue()

	def process_queue(self):
		if not self.is_animating and self.queue:
			self.is_animating = True
			typ, state = self.queue.pop(0)
			self.show_notification(typ, state)

def load_and_scale(path):
	if not path or not os.path.isfile(path):
		return None
	try:
		img = tk.PhotoImage(file=path)
	except:
		return None

	w, h = img.width(), img.height()

	if overlay_size <= 0:
		return img

	scale = max(w, h) / float(overlay_size)
	if scale > 1:
		factor = math.ceil(scale)
		img = img.subsample(factor, factor)

	return img

def load_icons():
	global icon_rec_start, icon_rec_saved, icon_rb_start, icon_rb_saved
	icon_rec_start = load_and_scale(icon_rec_start_path)
	icon_rec_saved  = load_and_scale(icon_rec_saved_path)
	icon_rb_start   = load_and_scale(icon_rb_start_path)
	icon_rb_saved   = load_and_scale(icon_rb_saved_path)

def runtk():
	global app_instance
	app_instance = Application()
	load_icons()
	app_instance.mainloop()
	app_instance = None

def start_thread():
	global thd
	if not thd or not thd.is_alive():
		thd = threading.Thread(target=runtk, daemon=True)
		thd.start()

def frontend_event_handler(evt):
	if evt == obs.OBS_FRONTEND_EVENT_FINISHED_LOADING:
		start_thread(); return
	mapping = {
		obs.OBS_FRONTEND_EVENT_RECORDING_STARTING: ('recording','started'),
		obs.OBS_FRONTEND_EVENT_RECORDING_STOPPED: ('recording','saved'),
		obs.OBS_FRONTEND_EVENT_REPLAY_BUFFER_STARTED: ('replay','started'),
		obs.OBS_FRONTEND_EVENT_REPLAY_BUFFER_SAVED: ('replay','saved')
	}
	if evt in mapping and app_instance:
		app_instance.queue.append(mapping[evt])
		app_instance.process_queue()


def script_description():
	return ("ShadowPlay-style notifications. Created by Daniluk2")

def script_defaults(settings):
	obs.obs_data_set_default_string(settings, "p_rec_start", "")
	obs.obs_data_set_default_string(settings, "p_rec_saved", "")
	obs.obs_data_set_default_string(settings, "p_rb_start", "")
	obs.obs_data_set_default_string(settings, "p_rb_saved", "")

	obs.obs_data_set_default_int(settings, "p_overlay_size", 40)
	obs.obs_data_set_default_int(settings, "p_icon_padding", 0)
	obs.obs_data_set_default_int(settings, "p_overlay_width", 0)
	obs.obs_data_set_default_int(settings, "p_overlay_height", 0)
	obs.obs_data_set_default_int(settings, "p_offset_x", 0)
	obs.obs_data_set_default_int(settings, "p_offset_y", 0)
	obs.obs_data_set_default_int(settings, "p_slide_steps", 35)
	obs.obs_data_set_default_int(settings, "p_slide_interval", 10)
	obs.obs_data_set_default_int(settings, "p_font_size", default_font_size)

	obs.obs_data_set_default_string(settings, "p_overlay_position", "top_right")
	obs.obs_data_set_default_string(settings, "p_slide_from",	   "right")

def script_properties():
	props = obs.obs_properties_create()
	obs.obs_properties_add_path(props, "p_rec_start", "Icon: Recording Started", obs.OBS_PATH_FILE, "*.png;*.gif;*.jpg", None)
	obs.obs_properties_add_path(props, "p_rec_saved", "Icon: Recording Saved", obs.OBS_PATH_FILE, "*.png;*.gif;*.jpg", None)
	obs.obs_properties_add_path(props, "p_rb_start", "Icon: Replay Enabled", obs.OBS_PATH_FILE, "*.png;*.gif;*.jpg", None)
	obs.obs_properties_add_path(props, "p_rb_saved", "Icon: Replay Saved", obs.OBS_PATH_FILE, "*.png;*.gif;*.jpg", None)
	obs.obs_properties_add_int(props, "p_overlay_size", "Max icon size (px)", 1, 512, 1)
	obs.obs_properties_add_int(props, "p_icon_padding", "Icon-text padding (px)", 0, 50, 1)
	obs.obs_properties_add_int(props, "p_overlay_width", "Overlay width (px,0=auto)", 0, 1920, 1)
	obs.obs_properties_add_int(props, "p_overlay_height","Overlay height (px,0=auto)", 0, 1080, 1)
	obs.obs_properties_add_int(props, "p_offset_x", "Offset X (px)", -500, 500, 1)
	obs.obs_properties_add_int(props, "p_offset_y", "Offset Y (px)", -500, 500, 1)
	obs.obs_properties_add_int(props, "p_slide_steps", "Slide steps", 1, 100, 1)
	obs.obs_properties_add_int(props, "p_slide_interval", "Slide interval (ms)", 1, 1000, 10)
	p = obs.obs_properties_add_list(props, "p_overlay_position", "Overlay position", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
	for txt,val in [("Top Right","top_right"),("Top Left","top_left"),("Bottom Left","bottom_left"),("Bottom Right","bottom_right")]:
		obs.obs_property_list_add_string(p, txt, val)
	d = obs.obs_properties_add_list(props, "p_slide_from", "Slide from", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
	for txt,val in [("None","none"),("Left","left"),("Right","right"),("Top","top"),("Bottom","bottom")]:
		obs.obs_property_list_add_string(d, txt, val)
	
	obs.obs_properties_add_int(props, "p_font_size", "Font Size", 6, 72, 1)
	return props

def script_update(settings):
	global icon_rec_start_path, icon_rec_saved_path, icon_rb_start_path, icon_rb_saved_path
	global overlay_size, icon_padding, overlay_position, slide_from, offset_x, offset_y
	global overlay_width, overlay_height, slide_steps, slide_interval
	global default_font_size
	icon_rec_start_path = obs.obs_data_get_string(settings, 	"p_rec_start")
	icon_rec_saved_path = obs.obs_data_get_string(settings, 	"p_rec_saved")
	icon_rb_start_path  = obs.obs_data_get_string(settings, 	"p_rb_start")
	icon_rb_saved_path  = obs.obs_data_get_string(settings, 	"p_rb_saved")
	overlay_size		= obs.obs_data_get_int(settings,		"p_overlay_size")
	icon_padding		= obs.obs_data_get_int(settings,		"p_icon_padding")
	overlay_width		= obs.obs_data_get_int(settings,		"p_overlay_width")
	overlay_height		= obs.obs_data_get_int(settings,		"p_overlay_height")
	offset_x			= obs.obs_data_get_int(settings,		"p_offset_x")
	offset_y			= obs.obs_data_get_int(settings,		"p_offset_y")
	slide_steps			= obs.obs_data_get_int(settings,		"p_slide_steps")
	slide_interval		= obs.obs_data_get_int(settings,		"p_slide_interval")
	overlay_position	= obs.obs_data_get_string(settings,		"p_overlay_position")
	slide_from			= obs.obs_data_get_string(settings,		"p_slide_from")
	default_font_size	= obs.obs_data_get_int(settings,		"p_font_size")
	if app_instance:
		app_instance.after(0, load_icons)
	
def script_load(settings):
	obs.obs_frontend_add_event_callback(frontend_event_handler)