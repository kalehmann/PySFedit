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
This module contains the font editor widget of PySFedit.
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import GLib
from gi.repository import Gdk
from PIL import Image, ImageDraw
import gettext
import re

import psflib
from glyph_editor import GlyphEditor
from edit_description_dialog import EditUnicodeDescriptionDialog
import constants as c

translation = gettext.translation('pysfedit', localedir=c.LOCALE_DIR,
	fallback=True)
translation.install()
		
class GlyphSelectorContext(object):
	
	__GLYPH_SELECTOR_PREVIEW_SIZE = [32, 32]
	__SHOW_GLYPH_INDEX = True
	__ALLOW_ENTERING_SEQUENCES = False
	"""This class represents the context of the glyph selector and can
	be used to modfiy its appeareance.
	
	Args:
		font (PcScreenFont): The font of the glyph selector
		glyph_selector (GlyphSelector): The glyph selector, that uses
			this context
	
	"""
	def __init__(self, font, glyph_selector):
		self.__font = font
		self.__glyph_preview_size = \
			self.__GLYPH_SELECTOR_PREVIEW_SIZE[:]
		self.__parent_glyph_selector = glyph_selector
		self.__show_glyph_index = True
		self.__allow_entering_sequences = \
			self.__ALLOW_ENTERING_SEQUENCES
	
	def switch_rows(self, first, second):
		"""Switch two rows. This also changes the positions of the
		glyphs in the font.
		
		Args:
			first (int): The index of the first row
			second (int): The index of the second row		
		"""
		if first == second:
			
			return
			
		lb = self.__parent_glyph_selector
		first_row = lb.get_row_at_index(first)
		second_row = lb.get_row_at_index(second)
				
		(lower_index, lower_row), (higher_index, higher_row) = sorted(
			[
				(first, first_row),
				(second, second_row)
			],
			key=lambda x: x[0]
		)
		
		lb.remove(lower_row)
		lb.remove(higher_row)
		lb.insert(higher_row, lower_index)
		lb.insert(lower_row, higher_index)
		
		lb.select_row(second_row)
		
		lb.show_all()
		self.update_rows()
		
		self.__font.switch_glyphs(first, second)
	
	def add_glyph(self, index=-1):
		"""Add a new glyph.
		
		Args:
			index (int): The position where the glyph should be added.
				The default is -1 meaning at the end		
		"""
		glyph, _ = self.__font.add_glyph(index)
		if glyph:
			row = GlyphRow(self, len(self.__font) - 1)
			row.connect('drag-data-received',
				self.__parent_glyph_selector._on_drag_data_received,
				row)
			self.__parent_glyph_selector.add(row)
			self.__parent_glyph_selector.show_all()
			self.__parent_glyph_selector.select_row(row)
		if self.__show_glyph_index:
			for row in self.__parent_glyph_selector.get_children():
				row.update()	
	
	def remove_glyph(self, index=-1):
		"""Remove a glyph.
		
		Args:
			index (int): The index of the glyph that should be removed.
				The default is -1 meaning the currently selected glyph		
		"""
		if self.__font.get_header().version_psf == psflib.PSF1_VERSION:
			
			return
		if index == -1:
			row = self.__parent_glyph_selector.get_selected_row()
			index = row.get_index()
		else:
			row = self.__parent.glyph_selector.get_row_at_index(index)
		if not row:
			
			return
		if index > 0:
			next_row = self.__parent_glyph_selector.get_row_at_index(
				index - 1)
			self.__parent_glyph_selector.select_row(next_row)
		elif len(self.__parent_glyph_selector.get_children()) > 1:
			# The row that will be deleted is the first row. Select the
			# second row.
			next_row = self.__parent_glyph_selector.get_row_at_index(1)
			self.__parent_glyph_selector.select_row(next_row)

		row.destroy()
		self.__font.remove_glyph(index)
	
		if self.__show_glyph_index:
			self.update_rows()
	
	def update_rows(self):
		"""Update information of all rows of the glyph selector."""
		for row in self.__parent_glyph_selector.get_children():
			row.update()
	
	def get_font(self):
		"""Get the font of the glyph selector
		
		Returns:
			PcScreenFont: The font of the glyph selector		
		"""
		return self.__font
		
	def get_glyph_preview_size(self):
		"""Get the size of the preview image for each glyph in the glyph
		selector in pixels.
		
		Returns:
			list: The width and the height of the preview images of the
				glyphs in the glyph selector in pixels		
		"""		
		
		return self.__glyph_preview_size
		
	def set_glyph_preview_size(self, size):
		"""Set the size of the preview images of the glyphs in the glyph
		selector in pixels.
		
		Args:
			size (list): The widht and the height of the preview images
				of the glyphs in the glyph selector in pixels.		
		"""
		self.__glyph_preview_size = size
		
	def get_show_glyph_index(self):
		"""Get wether the glyph selector should show the index of each
		glyph in the font or not.
		
		Returns:
			bool: Whether to show the index of each glyph in the font or
				not.		
		"""
		
		return self.__show_glyph_index
		
	def set_show_glyph_index(self, show_glyph_index):
		"""Set wether the glyph selector should show the index of each
		glyph in the font or not.
		
		Args:
			show_glyph_index (bool): Whether to show the index of each
				glyph in the font or not.		
		"""
		self.__show_glyph_index = show_glyph_index

	def get_allow_entering_sequences(self):
		"""Get whether entering unicode sequences is allowed or not.
		
		Returns:
			bool: whether entering unicode sequences is allowed or not.		
		"""
		
		return self.__allow_entering_sequences
		
	def set_allow_entering_sequences(self, allow):
		"""Set whether entering unicode sequences is allowed or not.
		
		Args:
			allow (bool): Whether entering unicode sequences is allowed
				or not.		
		"""
		self.__allow_entering_sequences = allow

class GlyphRow(Gtk.ListBoxRow):
	GLYPH_ROW_ATOM = Gdk.Atom.intern('GLYPH_ROW', False)
	TARGET_GlYPH_ROW_INFO = 0
	
	"""A row in the glyph selector, containing a handle for rearranging
	the rows, optional the index of the row, a preview image of the
	glyph referenced by the row, a list of unicode representations for
	this glyph and a button for editing these.
	
	Args:
		context (GlyphSelectorContext): The context of the parent
			glyph selector
		index (int): The initial index of the row	
	"""
	def __init__(self, context, index):
		Gtk.ListBoxRow.__init__(self)
		font = context.get_font()
		self.__glyph, self.__description = font[index]
		self.__context = context
		self.__index = index
		self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		self.add(self.box)
		
		self.handle = Gtk.EventBox()
		self.handle.add(
			Gtk.Image.new_from_icon_name(
				"open-menu-symbolic",
				Gtk.IconSize.MENU
			)
		)
		self.handle.connect('drag-data-get', self.__on_drag_data_get)
		self.box.pack_start(self.handle, False, False, 0)
		
		self.l_index = Gtk.Label()
		self.box.pack_start((self.l_index), False, False, 0)
		if self.__context.get_show_glyph_index():
			self.l_index.set_text("%d" % index)
		
		pixbuf = self.get_pixbuf_from_glyph_bitmap(self.__glyph)
		self.image = Gtk.Image.new_from_pixbuf(pixbuf)
		self.box.pack_start(self.image, False, False, 5)
		
		self.l_descriptions = Gtk.Label()
		self.box.pack_start(self.l_descriptions, True, True, 2)
		
		if font.has_unicode_table():
			self.btn_edit = Gtk.Button(None, image=Gtk.Image(
				stock=Gtk.STOCK_EDIT))
			self.btn_edit.connect("clicked", self.__on_btn_edit_clicked)
			self.box.pack_end(self.btn_edit, False, False, 0)
		self.set_label_descriptions()

		self.handle.drag_source_set(
			Gdk.ModifierType.BUTTON1_MASK,
			None,
			Gdk.DragAction.MOVE
		)
		
		self.drag_dest_set(
			Gtk.DestDefaults.ALL,
			None,
			Gdk.DragAction.MOVE
		)

		targets = Gtk.TargetList.new()
		targets.add(self.GLYPH_ROW_ATOM, 0, self.TARGET_GlYPH_ROW_INFO)
		self.handle.drag_source_set_target_list(targets)
		self.drag_dest_set_target_list(targets)
		
	def __on_drag_data_get(self, widget, context, data, info, time):
		"""This method gets called while drag and drop when this row
		has been dropped somewhere.
		
		Args:
			widget (Gtk.Widget): This row
			context (Gtk.DragContext): The drag context
			data (Gtk.SelectionData): The data that needs to be filled
				in this method.
			info (int): The info that has been registered with the 
				target of this drag and drop operation.
			time (int): The timestamp of the event		
		"""
		data.set(self.GLYPH_ROW_ATOM, 0,
			bytes('%d' % self.get_index(), 'utf8'))

	def get_index(self):
		"""Get the index of the row. This method works even before the
		rows has been assigned to the glyph selector.
		
		Returns:
			int: The index of the row
		"""
		if super().get_index() == -1:
			
			return self.__index
		
		return super().get_index()

	def update(self):
		"""This method updates the label with the index of this row."""
		if self.__context.get_show_glyph_index():
			self.l_index.set_text('%d' % self.get_index())
		else:
			self.l_index.set_text()

	def set_label_descriptions(self):
		"""This method updates the label with the unicode
		representations of the glyph referenced by this row.		
		"""
		if self.__description:
			printable = ""
			for uc in self.__description.get_unicode_values():
				printable += chr(uc)
			self.l_descriptions.set_text(printable)
			
			return
		index = 0 if self.get_index() == -1 else self.get_index()

		self.l_descriptions.set_text(chr(self.get_index()))

	def get_pixbuf_from_glyph_bitmap(self, glyph):
		"""Get the a preview image from the given glyph.
		
		Args:
			glyph (psflib.GlyphBitmap): The glyph to the a preview image
				of
		
		Returns:
			GdkPixbuf.Pixbuf: The preview image of the given glyph
				bitmap.		
		"""
		width, height = size = glyph.get_size()
		data = glyph.get_data()
		
		size = max(width, height), max(width, height)
		
		img = Image.new('RGBA', size, (0,0,0,0))
		draw = ImageDraw.Draw(img)
		for y, row in zip(range(height), data):
			for x, pixel in zip(range(width), row):
				if pixel == 1:
					draw.point((x, y), (0,0,0,255))
		data = img.tobytes()
		w, h = img.size
		data = GLib.Bytes.new(data)		
		pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(data,
					GdkPixbuf.Colorspace.RGB, True, 8, w, h, w * 4)
					
		preview_size = self.__context.get_glyph_preview_size()
		return pixbuf.scale_simple(*preview_size,
			GdkPixbuf.InterpType.NEAREST)
	
	def get_glyph_data(self):
		"""Get the data of the glyph referenced by this row.
		
		Returns:
			list: The data of the glyph bitmap referenced by this row		
		"""
		
		return self.__glyph.get_data()
		
	def update_glyph_data(self, data):
		"""Update the data and the preview image of the glyph referenced
		by this row.
		
		Args:
			data (list): The new data of the glyph		
		"""
		self.__glyph.set_data(data)
		pixbuf = self.get_pixbuf_from_glyph_bitmap(self.__glyph)
		self.image.set_from_pixbuf(pixbuf)
		
	def __on_btn_edit_clicked(self, button):
		"""This method gets called when the button for editing the
		unicode descriptions of the glyph referenced by this row has
		been clicked and opens an EditUnicodeDescriptionDialog.
		
		Args:
			button (Gtk.Button): The button for editing the unicode
				description of the glyph referenced by this row		
		"""
		d = EditUnicodeDescriptionDialog(self.get_toplevel(),
			self.__description, self.__context)
		d.run()
		d.destroy()
		self.set_label_descriptions()
	

class GlyphSelector(Gtk.ListBox):
	"""A widget for displaying glyphs from a pc screen font.
	
	Args:
		font (psflib.PcScreenFont): The font which glyphs should be
			displayed by this widget		
		glyph_editor (GlyphEditor): The glyph editor widget of the font
			editor
	"""
	def __init__(self, font, glyph_editor):
		Gtk.ListBox.__init__(self)
		self.set_selection_mode(Gtk.SelectionMode.SINGLE)
		
		self.context = GlyphSelectorContext(font, self)
		
		self.connect('row-selected', self.__on_row_selected)
		self.__font = font
		self.__glyph_editor = glyph_editor
		self.__editor_context = glyph_editor.get_context()
		self.__editor_context.register_on_changed_callback(
			self.__on_glyph_edited)

		for i in range(len(self.__font)):
			row = GlyphRow(self.context, i)
			row.connect('drag-data-received',
				self._on_drag_data_received, row)
			self.add(row)
			
		# Select the first row
		if len(font):
			first_row = self.get_row_at_index(0)
			self.select_row(first_row)

	def get_context(self):
		"""Get the context of the glyph selector.
		
		Returns:
			GlyphSelectorContext: The context of the glyph selector		
		"""
		
		return self.context
		
	def _on_drag_data_received(self, widget, context, x, y, data, info,
		time, row):
		"""This method gets called, when a row of the glyph selector has
		received data in a drag and drop operation.
		
		Args:
			widget (Gtk.Widget): The glyph selector row, that has
				received the data
			context (Gtk.DragContext): The drag context
			x (int): X-coordinate of the drop
			y (int): Y-coordinate of the drop
			data (Gtk.SelectionData): The data that needs to be filled
				in this method.
			info (int): The info that has been registered with the 
				target of this drag and drop operation.
			time (int): The timestamp of the event	
		"""	
		self.context.switch_rows(int(data.get_data()),
			row.get_index())

	def __on_glyph_edited(self, data):
		"""This method gets called, when the data of the glyph editor
		widget has changed.
		
		Args:
			data (list): The new data of the glyph editor widget		
		"""
		self.get_selected_row().update_glyph_data(data)
		
	def __on_row_selected(self, listbox, row):
		"""This method gets called, when the selected row changes.
		
		Args:
			row (GlyphSelectorRow): The newly selected row		
		"""
		self.__editor_context.reset_pixels()
		if row:
			self.__glyph_editor.set_data(row.get_glyph_data())

class FontEditorContext(object):
	"""The context of the font editor widget.
	
	Args:
		font (psflib.PcScreenFont): The font that the font editor
			handles.	
	"""
	def __init__(self, font=None):
		self.__header = font.get_header()
		self.__bitmap_size = None
		self.__font = font
	
	def get_font(self):
		"""Get the font that the font editor handles.
		
		Returns:
			psflib.PcScreenFont: The font that the font editor handles		
		"""
		return self.__font
		
class FontEditor(Gtk.Box):
	"""The font editor widget.
	
	A widget for editing the glyph bitmaps of a pc screen font and
	setting	their unicode representations.
	
	Args:
		header (psflib.PsfHeader): The header of the font that should be
			edited in this font editor.
		font (psflib.PcScreenFont): The font that should be edited in
			this font editor. If None is given a new on will be created
			with the header.	
	"""
	def __init__(self, header, font=None):
		Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
		
		if not font:
			font = psflib.PcScreenFont(header)
		
		self.context = FontEditorContext(font)
		
		# GlyphEditor
		self.glyph_editor = GlyphEditor()
		self.glyph_editor.get_context().set_glyph_size(header.size)
		self.glyph_editor.get_attributes().set_seperation_lines(True)
		self.glyph_editor.get_attributes().set_draw_unset_pixels(True)
		
		glyph_editor_wrapper = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL)
		self.pack_start(glyph_editor_wrapper, True, True, 0)
		
		button_wrapper = Gtk.Box(
			orientation=Gtk.Orientation.HORIZONTAL)
		glyph_editor_wrapper.pack_start(button_wrapper, False, True, 1)
		
		# ButtonAdd
		self.button_add = Gtk.Button(None,
				image=Gtk.Image(stock=Gtk.STOCK_ADD))
		self.button_add.connect("clicked", self.__on_btn_add_clicked)
		self.button_add.set_sensitive(
			header.version_psf != psflib.PSF1_VERSION
		)
		button_wrapper.pack_start(self.button_add, True, True, 1)
		
		# ButtonRemove
		self.button_remove = Gtk.Button(None,
				image=Gtk.Image(stock=Gtk.STOCK_REMOVE))
		self.button_remove.set_sensitive(
			bool(len(font)) and
			header.version_psf != psflib.PSF1_VERSION
		)
		self.button_remove.connect("clicked",
			self.__on_btn_remove_clicked)
		button_wrapper.pack_start(self.button_remove, True, True, 0)
		
		glyph_editor_wrapper.pack_start(self.glyph_editor, True, True,
			0)
		
		# GlyphSelector
		self.glyph_selector_wrapper = Gtk.ScrolledWindow()
		self.glyph_selector = GlyphSelector(
			self.context.get_font(), self.glyph_editor)
		self.glyph_selector_wrapper.add(self.glyph_selector)
		self.glyph_selector_wrapper.set_propagate_natural_height(True)
		self.glyph_selector_wrapper.set_min_content_width(250)
		self.pack_start(self.glyph_selector_wrapper, True, True, 10)
		
	def get_font(self):
		"""Get the font handled by this font editor.
		
		Returns:
			psflib.PcScreenFont: The font handled by this font editor.		
		"""
		
		return self.context.get_font()

	def __on_btn_add_clicked(self, button):
		"""This method gets called when the button for adding a new
		glyph to the font handled by this widget has been clicked.
		
		Args:
			button (Gtk.Button): The button for adding a new glyph to
				the font handled by this widget		
		"""
		self.glyph_selector.get_context().add_glyph()
				
		def row_tick_callback(widget, clock, self):
			"""Gtk.TickCallback
			A callback that gets called before a new frame. 
			
			Args:
				widget (Gtk.Widget): The widget this callback has been
					added to.
				clock (Gdk.FrameClock): The frame clock for this widget
				self (FontEditor): The font editor, explicit is better
					than implicit ;)
			
			Returns:
				GLib.SOURCE_CONTINUE: if the callback should be called
					another time.
				Glib.SOURCE_REMOVE: if the callback should be removed
					from the widget.
			
			"""
			_, y = widget.translate_coordinates(self.glyph_selector,
				0, 0)
			if y == -1:
			
				return GLib.SOURCE_CONTINUE
			vadj = self.glyph_selector_wrapper.get_vadjustment()
			vadj.set_value(int(y))
			
			return GLib.SOURCE_REMOVE
		
		row = self.glyph_selector.get_children()[-1]
		row.add_tick_callback(row_tick_callback, self)
		
		self.button_remove.set_sensitive(True)
		
	def __on_btn_remove_clicked(self, button):
		"""This method gets called when the button for removing a glyph
		from the font handled by this widget has been clicked.
		
		Args:
			button (Gtk.Button): The button for removing a glyph from
				the font handled by this widget		
		"""
		self.glyph_selector.get_context().remove_glyph()

		if not self.glyph_selector.get_children():
			button.set_sensitive(False)
