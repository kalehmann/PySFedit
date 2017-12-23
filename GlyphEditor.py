#! /usr/bin/python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
gi.require_foreign("cairo")
from gi.repository import Gtk
from gi.repository import Gdk

class GlyphEditorAttributes(object):
	"""This class represents the attributes of a GlyphEditor, for
	example how it looks and how large all pixels of the glyph are
	drawed on the screen.	
	"""
	__PIXEL_DRAW_SIZE = 12
	__PIXEL_MARGIN = 2
	__SEPERATION_LINES = True
	__UNSET_PIXEL_COLOR = [0.8, 0.8, 0.8, 1]
	__DRAW_UNSET_PIXELS = False
	
	def __init__(self):
		self.__pixel_draw_size = self.__PIXEL_DRAW_SIZE
		self.__pixel_margin = self.__PIXEL_MARGIN
		self.__pixel_size = (
			self.__pixel_draw_size + 2 * self.__pixel_margin
		)
		self.__seperation_lines = self.__SEPERATION_LINES
		self.__unset_pixel_color = self.__UNSET_PIXEL_COLOR[:]
		self.__draw_unset_pixels = False

	def get_pixel_size(self):
		"""Get the total size of a pixel of a glyph on the screen.
		
		Returns:
			int: The total size of a pixel of a glyph on the screen
		"""
		return self.__pixel_size
			
	def set_pixel_margin(self, pixel_margin):
		"""This method sets the margin of a pixel of a glyph on the
		screen
		
		Args:
			pixel_margin (int): The margin of a pixel on the screen.
		"""
		self.__pixel_margin = pixel_margin
		
	def get_pixel_margin(self):
		"""Use this method to get the margin of a pixel on the
		screen.
		
		Returns:
			int: The margin of a pixel		
		"""
		return self.__pixel_margin
		
	def set_pixel_draw_size(self, pixel_draw_size):
		"""This method sets the width and height of a pixel drawed on
		the screen.
		
		Args:
			pixel_draw_size (int): The width and height a pixel of a
				pixel drawed on the screen.		
		"""
		if pixel_draw_size > self.__pixel_size:
			self.__pixel_size = pixel_draw_size
		self.__pixel_draw_size = pixel_draw_size
		
	def get_pixel_draw_size(self):
		"""Use this method to get the width an height of a pixel drawed
		on the screen.
		
		Returns:
			int: Width and height of a pixel drawed on the screen		
		"""
		return self.__pixel_draw_size
	
	def set_seperation_lines(self, seperation_lines):
		"""This method sets wether the pixels of the GlyphEditor widget
		are seperated by lines or not.
		
		Args:
			seperation_lines (bool): Defines wether the pixels of the
				GlyphEditor widget are seperated by lines or no		
		"""
		self.__seperation_lines = seperation_lines
		
	def get_seperation_lines(self):
		"""Use this method to find out, if the pixels of the GlyphEditor
		widget are currently seperated by lines or not.
		
		Returns:
			bool: Wether the pixels of the GlyphEditor widget are
				seperated by lines or not.		
		"""
		return self.__seperation_lines
		
	def set_unset_pixel_color(self, unset_pixel_color):
		"""Use this method to set the color of unset pixels.
		
		Args:
			unset_pixel_color (list): A list of four floating point
				values [red, green, blue, alpha]
		"""
		self.__unset_pixel_color = unset_pixel_color[:]
		
	def get_unset_pixel_color(self):
		"""Use this method to get the color of unset pixels.
		
		Returns:
			list: A list of four floating point values
				[red, green, blue, alpha]
		"""
		return self.__unset_pixel_color
		
	def set_draw_unset_pixels(self, draw_unset_pixels):
		"""Set wether to draw unset pixels or not.
		
		Args:
			draw_unset_pixels (bool): Wether to draw unset pixels or not
		"""
		self.__draw_unset_pixels = draw_unset_pixels
		
	def get_draw_unset_pixels(self):
		"""Get wether to draw unset pixels or not.
		
		Returns:
			bool: Wether to draw unset pixels or not.		
		"""
		return self.__draw_unset_pixels
	
class GlyphEditorContext(object):
	"""This class represent the context of a glyph editor widget,
	therefore it holds information about the state of the widget.	
	"""
	__GLYPH_SIZE = [8, 8]
	__BLANK_PIXEL = 0
	__SET_PIXEL = 1
	BUTTON_LEFT = 1
	BUTTON_RIGHT = 3
	
	def __init__(self):
		self.__glyph_size = self.__GLYPH_SIZE[:]
		self.__pixels = self.__get_pixel_list()
		
	def __get_pixel_list(self):
		"""Returns a list representing the pixels of the glyph.
		Say for example, you have a glyph with a width of x and a height
		of y, then a list of y lists of x integers is returned.
		So you can access a pixel by pixels[y][x].
		
		Returns:
			list: A list of lists of integers
		
		"""
		return [
			[0 for _ in range(self.__glyph_size[0])]
				for _ in range(self.__glyph_size[1])
		]
		
	def get_pixels(self):
		return self.__pixels

	def set_glyph_size(self, glyph_size):
		"""This method sets the number of pixels representing a glyph.
		
		Args:
			glyph_size (list):	The size of a glyph [width, height]
		"""
		self.__glyph_size = glyph_size[:]
		
		# We do not overwrite self.__pixels here, but modify it. So
		# if someone have a reference to self.__pixels, for example
		# over the get_pixels() method, he can still use it.
		self.__pixels.clear()
		self.__pixels += self.__get_pixel_list()
		
	def get_glyph_size(self):
		"""Get the number of pixels representing a glyph.
		
		Returns:
			list: Width and height of a glyph.		
		"""
		return self.__glyph_size[:]
		
	def handle_pixel_event(self, x, y, button):
		if button == self.BUTTON_LEFT:
			self.__pixels[y][x] = 1
		elif button == self.BUTTON_RIGHT:
			self.__pixels[y][x] = 0
			
	def reset_pixels(self):
		# We do not overwrite self.__pixels here, but modify it. So
		# if someone have a reference to self.__pixels, for example
		# over the get_pixels() method, he can still use it.
		self.__pixels.clear()
		self.__pixels += self.__get_pixel_list()

class GlyphEditor(Gtk.Widget):
	__gtype_name__ = 'GlyphEditor'
	
	
	def __init__(self, *args, **kwds):
		super().__init__(*args, **kwds)
		
		self.__context = None
		self.__attrs = None
		self.__requested_size = None
		
		self.set_context(GlyphEditorContext())
		self.set_attributes(GlyphEditorAttributes())
		
	def get_data(self):
		return self.__context.get_pixels()[:]
		
	def set_data(self, data):
		for row, i in zip(data, range(len(self.__pixels))):
			for d, j in zip(row, range(len(row))):
				self.__pixels[i][j] = d
		self.queue_draw()
		
	def reset(self):
		self.__context.reset_pixels()
		
	def set_context(self, context):
		self.__context = context
		self.__pixels = context.get_pixels()
		
		self.__make_size_request()
		
	def get_context(self):
		return self.__context
	
	def __make_size_request(self):
		if self.__context and self.__attrs:
			pixel_size = self.__attrs.get_pixel_size()
			glyph_size = self.__context.get_glyph_size()
			
			self.requested_size = (
				pixel_size * glyph_size[0],
				pixel_size * glyph_size[1]
			)
			
			self.set_size_request(*self.requested_size)	
	
	def set_attributes(self, attrs):
		"""Use this method to set the attributes of the GlyphEditor
		widget.
		"""
		if self.get_realized():
			raise Exception(
				"Can not change the attributes of the GlyphEditor " +
				"after realization."
			)
		self.__attrs = attrs
		
		self.__make_size_request()
			
		
	def get_attributes(self):
		return self.__attrs
		
	def do_draw(self, cr):
		# paint background
		bg_color = self.get_style_context().get_background_color(Gtk.StateFlags.NORMAL)
		cr.set_source_rgba(*list(bg_color))
		cr.paint()
		# draw a diagonal line
		allocation = self.get_allocation()
		fg_color = self.get_style_context().get_color(Gtk.StateFlags.NORMAL)
		cr.set_source_rgba(*list(fg_color));
		cr.set_line_width(1)
		glyph_size = self.__context.get_glyph_size()
		pixels = self.__pixels
		pixel_size = self.__attrs.get_pixel_size()
		pixel_draw_size = self.__attrs.get_pixel_draw_size()
		pixel_margin = self.__attrs.get_pixel_margin()
		
		for y, row in zip(range(glyph_size[1]), pixels):
			for x, i in zip(range(glyph_size[0]), row):
				if i:
					cr.rectangle(
						x * pixel_size + pixel_margin,
						y * pixel_size + pixel_margin,
						pixel_draw_size,
						pixel_draw_size
					)
					cr.fill()
		cr.stroke()		
		
		if self.__attrs.get_seperation_lines():
			for i in range(1, glyph_size[0]):
				cr.move_to(i * pixel_size, 0)
				cr.line_to(i * pixel_size,
					pixel_size * glyph_size[1])
			for i in range(1, glyph_size[1]):
				cr.move_to(0, i * pixel_size)
				cr.line_to(pixel_size * glyph_size[0],
					i * pixel_size)
			cr.stroke()
		
		if self.__attrs.get_draw_unset_pixels():
			cr.set_source_rgba(*self.__attrs.get_unset_pixel_color())
			
			for y, row in zip(range(glyph_size[1]), pixels):
				for x, i in zip(range(glyph_size[0]), row):
					if not i:
						cr.rectangle(
							x * pixel_size + pixel_margin,
							y * pixel_size + pixel_margin,
							pixel_draw_size,
							pixel_draw_size
						)
						cr.fill()
			cr.stroke()				
			
	def do_motion_notify_event(self, e):
		if e.is_hint:
			_,x,y,state = e.window.get_pointer()
		else:
			x = e.x
			y = e.y
			state = e.state
		if (0 < x < self.requested_size[0] and
			0 < y < self.requested_size[1]):
				
			x = int(x / self.__attrs.get_pixel_size())
			y = int(y / self.__attrs.get_pixel_size())
			
			if state & Gdk.ModifierType.BUTTON1_MASK:
				button = GlyphEditorContext.BUTTON_LEFT
			elif state & Gdk.ModifierType.BUTTON3_MASK:
				button = GlyphEditorContext.BUTTON_RIGHT
			else:
				return
			
			self.__context.handle_pixel_event(x,y, button)
			self.queue_draw()
			
	def do_button_press_event(self, event):
		x = event.x
		y = event.y
		button = event.button
				
		if (0 < x < self.requested_size[0] and
			0 < y < self.requested_size[1]):
			x = int(x / self.__attrs.get_pixel_size())
			y = int(y / self.__attrs.get_pixel_size())
			
			if button == 1: # Left mouse button
				self.__context.handle_pixel_event(x,y,
					GlyphEditorContext.BUTTON_LEFT)
			elif button == 3: # Right mouse button
				self.__context.handle_pixel_event(x,y,
					GlyphEditorContext.BUTTON_RIGHT)
			self.queue_draw()

	def do_realize(self):
		a = self.get_allocation()
		attr = Gdk.WindowAttr()
		attr.window_type = Gdk.WindowType.CHILD
		attr.x = a.x
		attr.y = a.y
		attr.width = a.width
		attr.height = a.height
		attr.visual = self.get_visual()
		attr.event_mask = ( self.get_events() |
			Gdk.EventMask.EXPOSURE_MASK |
			Gdk.EventMask.POINTER_MOTION_MASK |
			Gdk.EventMask.BUTTON1_MOTION_MASK |
			Gdk.EventMask.BUTTON3_MOTION_MASK |
			Gdk.EventMask.BUTTON_PRESS_MASK |
			Gdk.EventMask.POINTER_MOTION_HINT_MASK
		)
		
		WAT = Gdk.WindowAttributesType
		mask = WAT.X | WAT.Y | WAT.VISUAL
		window = Gdk.Window(self.get_parent_window(), attr, mask);
		self.set_window(window)
		self.register_window(window)
		self.set_realized(True)
		window.set_background_pattern(None)
