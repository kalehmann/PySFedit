#! /usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright (c) 2018 by Karsten Lehmann <ka.lehmann@yahoo.com>

#	This file is part of PySFedit.
#
#	PySFedit is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
#	PySFedit is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
#	long with PySFedit. If not, see <http://www.gnu.org/licenses/>.

"""
This module contains a custom gtk widget, which provides a canvas for
drawing glyphs.

Furthermore there is one class for modifiyng the appearance of the
widget and one for managing its data.
"""

import gi
gi.require_version("Gtk", "3.0")
gi.require_foreign("cairo")
from gi.repository import Gtk
from gi.repository import Gdk
import constants as c

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
		self.__storage = s =c.get_storage(self)
		s.register('pixel_draw_size', self.__PIXEL_DRAW_SIZE)
		s.register('pixel_margin', self.__PIXEL_MARGIN)
		s.register(
			'pixel_size',
			self.__PIXEL_DRAW_SIZE + 2 * self.__PIXEL_MARGIN
		)
		s.register('seperation_lines', self.__SEPERATION_LINES)
		s.register('unset_pixel_color', self.__UNSET_PIXEL_COLOR[:])
		s.register('draw_unset_pixels', False)

	def get_pixel_size(self):
		"""Get the total size of a pixel of a glyph on the screen.
		
		Returns:
			int: The total size of a pixel of a glyph on the screen
		"""
		return self.__storage['pixel_size']
			
	def set_pixel_margin(self, pixel_margin):
		"""This method sets the margin of a pixel of a glyph on the
		screen
		
		Args:
			pixel_margin (int): The margin of a pixel on the screen.
		"""
		self.__storage['pixel_margin'] = pixel_margin
		
	def get_pixel_margin(self):
		"""Use this method to get the margin of a pixel on the
		screen.
		
		Returns:
			int: The margin of a pixel		
		"""
		return self.__storage['pixel_margin']
		
	def set_pixel_draw_size(self, pixel_draw_size):
		"""This method sets the width and height of a pixel drawed on
		the screen.
		
		Args:
			pixel_draw_size (int): The width and height a pixel of a
				pixel drawed on the screen.		
		"""
		if pixel_draw_size > self.__storage['pixel_size']:
			self.__storage['pixel_size'] = pixel_draw_size
		self.__storage['pixel_draw_size'] = pixel_draw_size
		
	def get_pixel_draw_size(self):
		"""Use this method to get the width an height of a pixel drawed
		on the screen.
		
		Returns:
			int: Width and height of a pixel drawed on the screen		
		"""
		return self.__storage['pixel_draw_size']
	
	def set_seperation_lines(self, seperation_lines):
		"""This method sets wether the pixels of the GlyphEditor widget
		are seperated by lines or not.
		
		Args:
			seperation_lines (bool): Defines wether the pixels of the
				GlyphEditor widget are seperated by lines or no		
		"""
		self.__storage['seperation_lines'] = seperation_lines
		
	def get_seperation_lines(self):
		"""Use this method to find out, if the pixels of the GlyphEditor
		widget are currently seperated by lines or not.
		
		Returns:
			bool: Wether the pixels of the GlyphEditor widget are
				seperated by lines or not.		
		"""
		return self.__storage['seperation_lines']
		
	def set_unset_pixel_color(self, unset_pixel_color):
		"""Use this method to set the color of unset pixels.
		
		Args:
			unset_pixel_color (list): A list of four floating point
				values [red, green, blue, alpha]
		"""
		self.__storage['unset_pixel_color'] = unset_pixel_color[:]
		
	def get_unset_pixel_color(self):
		"""Use this method to get the color of unset pixels.
		
		Returns:
			list: A list of four floating point values
				[red, green, blue, alpha]
		"""
		return self.__storage['unset_pixel_color']
		
	def set_draw_unset_pixels(self, draw_unset_pixels):
		"""Set wether to draw unset pixels or not.
		
		Args:
			draw_unset_pixels (bool): Wether to draw unset pixels or not
		"""
		self.__storage['draw_unset_pixels'] = draw_unset_pixels
		
	def get_draw_unset_pixels(self):
		"""Get wether to draw unset pixels or not.
		
		Returns:
			bool: Wether to draw unset pixels or not.		
		"""
		return self.__storage['draw_unset_pixels']
	
class GlyphEditorContext(object):
	"""This class represent the context of a glyph editor widget,
	therefore it holds information about the state of the widget.	
	"""
	__GLYPH_SIZE = [8, 8]
	__BLANK_PIXEL = 0
	__SET_PIXEL = 1
	SET_PIXEL = 1
	CLEAR_PIXEL = 2
	
	def __init__(self, glyph_editor):
		self.__glyph_size = self.__GLYPH_SIZE[:]
		self.__pixels = self.__get_pixel_list()
		self.__parent_glyph_editor = glyph_editor
		self.__on_changed_callbacks = []	
		
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
		"""Get a reference to the list representing the pixels of a
		glyph.
		
		Returns:
			list: A list of lists of integers.		
		"""
		return self.__pixels
		
	def set_pixels(self, data):
		"""Set the pixels of the glyph editor.
		
		Args:
			data (list): A list of the data to update the pixels of the
				glyph editor with. Its dimensions should equal the
				glyph size
		"""
		width, height = self.__glyph_size
		if len(data[0]) != width or len(data) != height:
			raise Exception(
				"data should have the same dimensions as the glyphs"
			)
		for x in range(width):
			for y in range(height):
				self.__pixels[y][x] = data[y][x]

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
		self.__parent_glyph_editor.make_size_request()
		
	def get_glyph_size(self):
		"""Get the number of pixels representing a glyph.
		
		Returns:
			list: Width and height of a glyph.		
		"""
		return self.__glyph_size[:]
		
	def handle_pixel_event(self, x, y, action):
		"""Call this method when a pixel of a glyph get modified.
		
		Action represents the action on this pixel (self.SET_PIXEL or
		self.CLEAR_PIXEL)
		
		Args:
			x (int): The x coordinate of the pixel
			y (int): The y coordinate of the pixel
			action (int): The action to perform on this pixel (set or
				clear)
		"""
		if action == self.SET_PIXEL:
			self.__pixels[y][x] = 1
		elif action == self.CLEAR_PIXEL:
			self.__pixels[y][x] = 0
		
		for callback in self.__on_changed_callbacks:
			callback(self.__pixels)
			
	def reset_pixels(self):
		"""Clear all pixels		
		"""
		# We do not overwrite self.__pixels here, but modify it. So
		# if someone have a reference to self.__pixels, for example
		# over the get_pixels() method, he can still use it.
		self.__pixels.clear()
		self.__pixels += self.__get_pixel_list()
		self.__parent_glyph_editor.queue_draw()
		
	def register_on_changed_callback(self, callback):
		"""Register a callback that should be called every time the
		pixels of the glyph editor are edited.
		
		Args:
			callback (callable): The callback. It should take the pixels
				of the glyph editor as onyl argument.
		"""
		self.__on_changed_callbacks.append(callback)
		
	def unregister_on_changed_callback(self, callback):
		"""Unregister a callback.
		
		Args:
			callback (callable): The callback that shoudl be
				unregistered
		"""
		if callback in self.__on_changed_callbacks:
			self.__on_changed_callbacks.remove(callback)


class GlyphEditor(Gtk.Widget):
	"""Custom widget for drawing glyphs.
	
	This is a custom gtk widget, which provides a canvas for drawing
	glyphs.
	
	The appeareance of the GlyphEditor can be controlled with an
	instance of GlyphEditorAttributes. You can get on with the
	get_attributes method or create your own and the apply it with
	set_attributes.
	
	The size of a glyph in pixels can be set with the set_glyph_size
	method of the GlyphEditorContext class. Simply get an instance with
	the get_context method.	
	"""
	
	__gtype_name__ = 'GlyphEditor'
	
	def __init__(self, *args, **kwds):
		super().__init__(*args, **kwds)
		
		self.__context = None
		self.__attrs = None
		self.__requested_size = None
		
		self.set_context(GlyphEditorContext(self))
		self.set_attributes(GlyphEditorAttributes())
		
	def get_data(self):
		"""Get a reference to the data representing the pixels of a
		glyph
		
		Returns:
			list: A list of lists of integers representing the pixels of
				a glyph
		"""
		return self.__context.get_pixels()[:]
		
	def set_data(self, data):
		"""Sets the pixels of the glyph editor widget
		
		Args:
			data (list): A list containg lists (the rows) of integers
				(the pixels)
		"""
		self.__context.set_pixels(data)
		self.queue_draw()
		
	def reset(self):
		"""Clear the canvas - reset all pixels		
		"""
		self.__context.reset_pixels()
		
	def set_context(self, context):
		"""Set the GlyphEditorContext of the widget.
		
		Args:
			context (GlyphEditorContext): The context of the widget		
		"""
		self.__context = context
		self.__pixels = context.get_pixels()
		
		self.make_size_request()
		
	def get_context(self):
		"""Get a reference to the GlyphEditorContext of the widget.
		
		Returns:
			GlyphEditorContext: The context of the widget		
		"""
		return self.__context
	
	def make_size_request(self):
		"""Let the widget request the size it needs for itself.
		Should be called before realization.		
		"""
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
		
		self.make_size_request()
			
		
	def get_attributes(self):
		"""Get a reference to the attributes of this widget.
		
		Returns:
			GlyphEditorAttributes: The attributes of the widget		
		"""
		return self.__attrs
		
	def do_draw(self, cr):
		"""Gets called, wenn the widget should draw itself.
		
		Args:
			cr (Cairo.Context): The cairo context, the widget should
				draw itself on.		
		"""
		# paint background
		bg_color = self.get_style_context().get_background_color(
			Gtk.StateFlags.NORMAL)
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
		"""This method gets called, when there is a mouse motion over
		the widget.
		
		Args:
			e (Gdk.EventMotion): The event of the motion		
		"""
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
				action = GlyphEditorContext.SET_PIXEL
			elif state & Gdk.ModifierType.BUTTON3_MASK:
				action = GlyphEditorContext.CLEAR_PIXEL
			else:
				return
			
			self.__context.handle_pixel_event(x,y, action)
			self.queue_draw()
			
	def do_button_press_event(self, event):
		"""This method gets called, when a mousebutton gets pressed in
		the area of the widget.
		
		Args:
			event (Gdk.EventButton): The event of the button press		
		"""
		x = event.x
		y = event.y
		button = event.button
				
		if (0 < x < self.requested_size[0] and
			0 < y < self.requested_size[1]):
			x = int(x / self.__attrs.get_pixel_size())
			y = int(y / self.__attrs.get_pixel_size())
			
			if button == 1: # Left mouse button
				self.__context.handle_pixel_event(x,y,
					GlyphEditorContext.SET_PIXEL)
			elif button == 3: # Right mouse button
				self.__context.handle_pixel_event(x,y,
					GlyphEditorContext.CLEAR_PIXEL)
			self.queue_draw()

	def do_realize(self):
		"""This method creates the Gdk ressources associated with the
		widget.
		"""
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
