#! /usr/bin/python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk

class GlyphEditor(Gtk.Widget):
	__gtype_name__ = 'GlyphEditor'
	def __init__(self, *args, **kwds):
		super().__init__(*args, **kwds)
		self.set_size_request(32, 32)
		
	def do_draw(self, cr):
		# paint background
		bg_color = self.get_style_context().get_background_color(Gtk.StateFlags.NORMAL)
		cr.set_source_rgba(*list(bg_color))
		cr.paint()
		# draw a diagonal line
		allocation = self.get_allocation()
		fg_color = self.get_style_context().get_color(Gtk.StateFlags.NORMAL)
		cr.set_source_rgba(*list(fg_color));
		cr.set_line_width(5)
		cr.move_to(0, 0)   # top left of the widget
		cr.line_to(32, 32)
		cr.move_to(32, 0)
		cr.line_to(0, 32)
		cr.stroke()

	def do_realize(self):
		a = self.get_allocation()
		attr = Gdk.WindowAttr()
		attr.window_type = Gdk.WindowType.CHILD
		attr.x = a.x
		attr.y = a.y
		attr.width = a.width
		attr.height = a.height
		attr.visual = self.get_visual()
		attr.event_mask = self.get_events() | Gdk.EventMask.EXPOSURE_MASK
		WAT = Gdk.WindowAttributesType
		mask = WAT.X | WAT.Y | WAT.VISUAL
		window = Gdk.Window(self.get_parent_window(), attr, mask);
		self.set_window(window)
		self.register_window(window)
		self.set_realized(True)
		window.set_background_pattern(None)
