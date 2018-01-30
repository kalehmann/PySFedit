#! /usr/bin/env python3
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
@ToDo: Add module docstring
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import constants as c

from glyph_editor import GlyphEditorAttributes
from font_editor import GlyphSelectorContext

class PreferencesWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title=_("Preferences"))
		self.set_default_size(600, 450)
		self.set_resizable(True)
		self.set_has_resize_grip(True)
		self.set_skip_taskbar_hint(True)
		
		self.notebook =Gtk.Notebook()
		self.add(self.notebook)
		
		self.page_glyph_editor = GlyphEditorPage()
		self.notebook.append_page(self.page_glyph_editor,
			Gtk.Label(_("GlyphEditor")))
			
		self.page_glyph_selector = GlyphSelectorPage()
		self.notebook.append_page(self.page_glyph_selector,
			Gtk.Label(_("GlyphSelector")))
		
class GlyphEditorPage(Gtk.Grid):
	def __init__(self):
		Gtk.Grid.__init__(self)
	
		self.__storage = c.get_storage(GlyphEditorAttributes)
	
		label_seperation_lines = Gtk.Label(_('Draw seperation lines:'))
		self.seperation_lines = Gtk.CheckButton()
		self.seperation_lines.set_active(
			self.__storage['seperation_lines'])
		self.seperation_lines.connect('toggled',
			self.__on_draw_sep_lines_changed)
		
		self.attach(label_seperation_lines, 0, 0, 1, 1)
		self.attach(self.seperation_lines, 1, 0, 1, 1)
	
		label_pixel_size = Gtk.Label(_('Pixel size:'))
		self.spin_pixel_size = Gtk.SpinButton()
		adj = Gtk.Adjustment(10, 10, 32, 1, 10, 1)
		self.spin_pixel_size.set_adjustment(adj)
		self.spin_pixel_size.set_value(self.__storage['pixel_size'])
		self.spin_pixel_size.connect('value-changed',
			self.__on_pixel_size_changed)
		
		self.attach(label_pixel_size, 0, 1, 1, 1)
		self.attach(self.spin_pixel_size, 1, 1, 1, 1)
		
		label_pixel_margin = Gtk.Label(_('Pixel margin:'))
		self.spin_pixel_margin = Gtk.SpinButton()
		adj = Gtk.Adjustment(0, 0, 10, 1, 10, 1)
		self.spin_pixel_margin.set_adjustment(adj)
		self.spin_pixel_margin.set_value(self.__storage['pixel_margin'])
		self.spin_pixel_margin.connect('value-changed',
			self.__on_pixel_margin_changed)
		
		self.attach(label_pixel_margin, 0, 2, 1, 1)
		self.attach(self.spin_pixel_margin, 1, 2, 1, 1)
		
		self.show_all()
	
	def __on_draw_sep_lines_changed(self, button):
		self.__storage['seperation_lines'] = button.get_active()
	
	def __on_pixel_size_changed(self, button):
		self.__storage['pixel_size'] = int(button.get_value())
		
	def __on_pixel_margin_changed(self, button):
		self.__storage['pixel_margin'] = int(button.get_value())
		
class GlyphSelectorPage(Gtk.Grid):
	def __init__(self):
		Gtk.Grid.__init__(self)
		
		self.__storage = c.get_storage(GlyphSelectorContext)
		
		label_preview_size = Gtk.Label(_("Glyph preview size:"))
		self.spin_preview_size = Gtk.SpinButton()
		adj = Gtk.Adjustment(24, 24, 64, 1, 10, 0)
		self.spin_preview_size.set_adjustment(adj)
		self.spin_preview_size.set_value(
			self.__storage['glyph_preview_size'])
		self.spin_preview_size.connect(
			'value-changed',
			self.__on_glyph_preview_size_changed
		)
		
		self.attach(label_preview_size, 0, 0, 1, 1)
		self.attach(self.spin_preview_size, 1, 0, 1, 1)
		
		label_glyph_indices = Gtk.Label(_("Show glyph indices"))
		self.glyph_indices = Gtk.CheckButton()
		self.glyph_indices.set_active(
			self.__storage['show_glyph_index']
		)
		self.glyph_indices.connect(
			'toggled',
			self.__on_glyph_indices_changed
		)
		
		self.attach(label_glyph_indices, 0, 1, 1, 1)
		self.attach(self.glyph_indices, 1, 1, 1, 1)
		
		label_allow_sequences = Gtk.Label(_('Allow unicode sequences'))
		self.allow_sequences = Gtk.CheckButton()
		self.allow_sequences.set_active(
			self.__storage['allow_entering_sequences']
		)
		self.allow_sequences.connect(
			'toggled',
			self.__on_allow_sequences_changed
		)

		self.attach(label_allow_sequences, 0, 2, 1, 1)
		self.attach(self.allow_sequences, 1, 2, 1, 1)

		self.show_all()

	def __on_glyph_preview_size_changed(self, button):
		self.__storage['glyph_preview_size'] = button.get_value()

	def __on_glyph_indices_changed(self, button):
		self.__storage['show_glyph_index'] = button.get_active()
		
	def __on_allow_sequences_changed(self, button):
		self.__storage['allow_entering_sequences'] = button.get_active()
