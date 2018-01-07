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
from os.path import dirname
import gettext
import locale

import psflib
import font_editor

RES_DIR = dirname(__file__) + 'res/'
IMG_DIR = RES_DIR + 'img/'
LOCALE_DIR = RES_DIR + 'locale/'
		
class PySFeditWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title=_("PySFedit"))
		self.set_default_size(400, 400)
		self.connect("delete-event", self.on_window_delete)
		self.set_icon_from_file(IMG_DIR + "icon.png")

		self.top_grid = Gtk.Grid()
		self.add(self.top_grid)

		self.menu_bar = Gtk.MenuBar()
		self.menu_bar.set_hexpand(True)

		menu_file = Gtk.MenuItem(_("File"))
		submenu = Gtk.Menu()
		menu_file.set_submenu(submenu)
		menuitem = Gtk.MenuItem(label=_("New"))
		menuitem.connect("activate", self.on_menu_new_clicked)
		submenu.append(menuitem)
		menuitem = Gtk.MenuItem(label=_("Import"))
		menuitem.connect("activate", self.on_menu_import_clicked)
		submenu.append(menuitem)
		menuitem = Gtk.MenuItem(label=_("Export"))
		menuitem.connect("activate", self.on_menu_export_clicked)
		submenu.append(menuitem)
		menuitem = Gtk.MenuItem(label=_("Quit"))
		menuitem.connect("activate", self.on_menu_quit_clicked)
		submenu.append(menuitem)
		self.menu_bar.append(menu_file)

		menu_help = Gtk.MenuItem(_("Help"))
		submenu = Gtk.Menu()
		menu_help.set_submenu(submenu)
		menuitem = Gtk.MenuItem(label=_("About"))
		menuitem.connect("activate", self.on_menu_about_clicked)
		submenu.append(menuitem)
		self.menu_bar.append(menu_help)		

		self.top_grid.attach(self.menu_bar,0,0,1,1)		
		
		self.button_new = Gtk.Button(_("New Font"))
		self.button_new.connect("clicked",
			self.__on_but_new_clicked)
		self.top_grid.attach(self.button_new,0,1,1,1)
		
		self.button_import = Gtk.Button(_("Import"))
		self.button_import.connect("clicked",
			self.__on_but_import_clicked)
		self.top_grid.attach(self.button_import, 0,2,1,1)
		
		self.font_editor = None

	def get_file_path(self, title, _type="open"):
		if _type == "open":
			action = Gtk.FileChooserAction.OPEN
		elif _type == "save":
			action = Gtk.FileChooserAction.SAVE
		dialog = Gtk.FileChooserDialog(title, self,
			action,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			 Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		if _type == "save":
			dialog.set_do_overwrite_confirmation(True)
		filter_psf = Gtk.FileFilter()
		filter_psf.set_name(_("PSF files	.psf"))
		filter_psf.add_mime_type("application/x-font-linux-psf")
		dialog.add_filter(filter_psf)
		
		filter_asm = Gtk.FileFilter()
		filter_asm.set_name(_("ASM files	.asm"))
		filter_asm.add_pattern("*.asm")
		dialog.add_filter(filter_asm)

		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			path = dialog.get_filename()
			dialog.destroy()
			return path
		dialog.destroy()
		
	def on_menu_about_clicked(self, submenu):
		dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
			Gtk.ButtonsType.OK, "About")
		dialog.format_secondary_text(
				"@ToDo add info about this program here.")
		dialog.run()
		dialog.destroy()
		
	def on_window_delete(self, widget, event):
		self.on_quit()
	
	def on_menu_quit_clicked(self, submenu):
		self.on_quit()
		
	def on_quit(self):
		Gtk.main_quit()
		
	def __on_but_new_clicked(self, button):
		self.new_font_dialog()

	def __on_but_import_clicked(self, button):
		self.import_font_dialog()

	def on_menu_new_clicked(self, submenu):
		self.new_font_dialog()

	def on_menu_import_clicked(self, submenu):
		self.import_font_dialog()

	def on_menu_export_clicked(self, submenu):
		self.export_font_dialog()

	def new_font_dialog(self):
		if self.font_editor: self.font_editor.destroy()
		d = NewFontDialog(self)
		r = d.run()
		if r == Gtk.ResponseType.OK:
			header = d.get_header()
			self.button_new.destroy()
			self.button_import.destroy()
			self.font_editor = font_editor.FontEditor(header)
			self.top_grid.attach(self.font_editor, 0, 1, 1, 1)
			self.top_grid.show_all()
		d.destroy()
	
	def import_font_dialog(self):
		path = self.get_file_path(_("Import file"))
		if not path: return
		if self.font_editor: self.font_editor.destroy()
		if path.lower().endswith(".asm"):
			font = psflib.AsmImporter.import_from_file(path)
		elif path.lower().endswith('.psf'):
			font = psflib.PsfImporter.import_from_file(path)
		else:
			return
		self.button_new.destroy()
		self.button_import.destroy()
		self.font_editor = font_editor.FontEditor(
			font.get_header(), font)
		self.top_grid.attach(self.font_editor, 0, 1, 1, 1)
		self.top_grid.show_all()
		
		
	def export_font_dialog(self):
		if not self.font_editor:
			dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
				Gtk.ButtonsType.OK, "Error!")
			dialog.format_secondary_text(
				_("You have not created a font yet."))
			dialog.run()
			dialog.destroy()
			return

		path = self.get_file_path(_("Export file"), "save")
		if path == None:
			return
		if path.lower().endswith(".asm"):
			exporter = psflib.AsmExporter(self.font_editor.get_font())
			exporter.export_to_file(path)
		elif path.lower().endswith(".psf"):
			exporter = psflib.PsfExporter(self.font_editor.get_font())
			exporter.export_to_file(path)

class NewFontDialog(Gtk.Dialog):
	def __init__(self, parent):
		Gtk.Dialog.__init__(self, _("New Font"), parent, 0,
			(Gtk.STOCK_OK, Gtk.ResponseType.OK,
			 Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
		self.set_default_size(200,200)
		
		box = self.get_content_area()
		grid = Gtk.Grid()
		box.add(grid)
		
		l1 = Gtk.Label(_("Font Size:"))
		grid.attach(l1, 0, 0, 1, 1)
		
		self.entry_width = Gtk.Entry()
		self.entry_width.set_text("8")
		self.entry_width.set_sensitive(False)
		grid.attach(self.entry_width, 0, 1, 1, 1)
		
		self.entry_height = Gtk.Entry()
		self.entry_height.set_text("8")
		grid.attach(self.entry_height, 1, 1, 1, 1)
		
		stack = Gtk.Stack()
		stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
		stack.set_transition_duration(50)
		
		grid_v1 = Gtk.Grid()
		
		grid_v2 = Gtk.Grid()
				
		stack.add_titled(grid_v1, "grid_v1", "PSFv1")
		stack.add_titled(grid_v2, "grid_v2", "PSFv2")
		
		stack.connect("notify::visible-child", self.__on_stack_changed)
		
		stack_switcher = Gtk.StackSwitcher()
		stack_switcher.set_stack(stack)
		
		grid.attach(stack_switcher, 0, 2, 2, 1)
		grid.attach(stack, 0, 3, 2, 1)
		self.stack = stack

		lglyph_num = Gtk.Label(_("Number of Glyphs:"))
		box = Gtk.Box()
		self.button256 = Gtk.RadioButton.new_with_label_from_widget(
			None, "256")
		self.button256.connect("toggled", self.__on_glyph_num_changed,
			256)
		box.pack_start(self.button256, False, False, 0)
		self.button512 = Gtk.RadioButton.new_with_label_from_widget(
			self.button256, "512")
		self.button512.connect("toggled", self.__on_glyph_num_changed,
			512)
		box.pack_start(self.button512, False, False, 0)
		grid_v1.attach(lglyph_num, 0,0,1,1)
		grid_v1.attach(box, 1,0,1,1)


		l3 = Gtk.Label(_("Include unicode table:"))
		grid.attach(l3, 0, 4, 1, 1)
		
		self.check_table = Gtk.CheckButton()
		grid.attach(self.check_table, 1, 4, 1, 1)
				
		self.show_all()
		
	def __on_glyph_num_changed(self, button, number):
		pass	
	
	def __on_stack_changed(self, stack, name):
		if stack.get_visible_child_name() == "grid_v1":
			self.entry_width.set_text("8")
			self.entry_width.set_sensitive(False)
		else:
			self.entry_width.set_editable(True)
			self.entry_width.set_sensitive(True)
				
	def get_header(self):
		size = (int(self.entry_width.get_text()),
				int(self.entry_height.get_text()))
		unicode_tab = self.check_table.get_active()
		if self.stack.get_visible_child_name() == "grid_v1":
			header = psflib.PsfHeaderv1(size)
			if unicode_tab: header.set_mode(psflib.PSF1_MODEHASTAB)
			if self.button512.get_active():
				header.set_mode(psflib.PSF1_MODE512)
		else:
			header = psflib.PsfHeaderv2(size)
			if unicode_tab:
				header.set_flags(psflib.PSF2_HAS_UNICODE_TABLE)
		return header

if __name__ == "__main__":
	translation = gettext.translation('pysfedit', localedir=LOCALE_DIR,
		fallback=True)
	translation.install()
	
	window = PySFeditWindow()
	window.show_all()
	Gtk.main()

