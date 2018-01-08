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
import gettext
import locale

import psflib
import font_editor
import constants as c

translation = gettext.translation('pysfedit', localedir=c.LOCALE_DIR,
	fallback=True)
translation.install()
		
class AboutWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title=_("About"))
		self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		top_box = Gtk.Box()
		top_box.pack_start(
			Gtk.Image.new_from_file(c.IMG_DIR + 'icon.png'), False,
			False, 5)
		l = Gtk.Label()
		l.set_markup(
			'<span font-size="x-large" font-weight="heavy">%s</span>' %
			_("PySFedit"))
		top_box.pack_start(l, False, False, 30)
		self.box.add(top_box)
		self.add(self.box)
		self.set_default_size(600, 450)
		self.set_resizable(True)
		self.set_has_resize_grip(True)
		self.set_skip_taskbar_hint(True)
		
		self.notebook = Gtk.Notebook()
		self.box.add(self.notebook)
		
		self.page1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		l = Gtk.Label()
		l.set_markup(
"""<span font-size="large" font-weight="bold">%s</span>

%s Karsten Lehmann \
<a href="mailto:ka.lehmann@yahoo.com">&lt;ka.lehmann@yahoo.com&gt;</a>

%s"""	% (
			_("An editor for psf files written in python"),
			_("Copyright (c) 2018 by"),
			_(
"""PSF is short for pc screen font...
"""			)
			)
		)
		self.page1.add(l)
		self.notebook.append_page(self.page1, Gtk.Label(_("Info")))
		
		self.page2 = Gtk.Box()
		scrolled_window = Gtk.ScrolledWindow()
		scrolled_window.set_hexpand(True)
		scrolled_window.set_vexpand(True)
		self.page2.pack_start(scrolled_window,True, True, 10)
		textview = Gtk.TextView()
		textview.set_editable(False)
		textbuffer = textview.get_buffer()
		scrolled_window.add(textview)
		with open(c.PROJECT_ROOT + 'gpl-3.0.txt', "r") as f:
			textbuffer.set_text(f.read())
		self.notebook.append_page(self.page2, Gtk.Label(_("Licence")))
		
		
class NewFontDialog(Gtk.Dialog):
	"""A dialog for the user to create the header of a new font.
	After the dialog has been closed you can get the header with the
	get_header method.
	
	Args:
		parent (Gtk.Widget): The parent widget creating this dialog.	
	"""
	def __init__(self, parent):
		Gtk.Dialog.__init__(self, _("New Font"), parent, 0,
			(Gtk.STOCK_OK, Gtk.ResponseType.OK,
			 Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
		self.set_default_size(200,200)
		
		self.psf_version = psflib.PSF1_VERSION
		self.glyph_num = 256
		self.has_unicode_table = False
		
		box = self.get_content_area()
		box.set_orientation(Gtk.Orientation.VERTICAL)
		
		l1 = Gtk.Label()
		l1.set_markup(
			'<span font-size="large" font-weight="bold">%s</span>' %
			_("Font Size:")
		)
		box.pack_start(l1, False, False, 5)
		
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		self.entry_width = Gtk.Entry()
		self.entry_width.set_text("8")
		self.entry_width.set_sensitive(False)
		hbox.pack_start(self.entry_width, False, False, 5)
		
		self.entry_height = Gtk.Entry()
		self.entry_height.set_text("8")
		hbox.pack_start(self.entry_height, False, False, 5)
		box.pack_start(hbox, False, False, 5)
		
		notebook = Gtk.Notebook()
		notebook.connect("switch-page", self.__on_psf_version_changed)
		box.pack_start(notebook, False, False, 0)
		page1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		rb256 = Gtk.RadioButton.new_with_label(None, _("256 Glyphs"))
		rb256.connect("toggled", self.__on_radion_btn_glyphs_changed,
			256)
		hbox.pack_start(rb256, False, False, 0)
		rb512 = Gtk.RadioButton.new_from_widget(rb256)
		rb512.set_label(_("512 Glyphs"))
		rb512.connect("toggled", self.__on_radion_btn_glyphs_changed,
			512)
		hbox.pack_start(rb512, False, False, 0)
		page1.pack_start(hbox, False, False, 0)
		
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		label = Gtk.Label(_("Include unicode table:"))
		hbox.pack_start(label, False, False, 0)
		check_button = Gtk.CheckButton()
		check_button.connect("toggled", self.__on_btn_uni_table_toggled)
		hbox.pack_start(check_button, False, False, 0)
		page1.pack_start(hbox, False, False, 0)
		
		notebook.append_page(page1, Gtk.Label(_("PSF")))
		
		page2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		label = Gtk.Label(_("Include unicode table:"))
		hbox.pack_start(label, False, False, 0)
		check_button = Gtk.CheckButton()
		check_button.connect("toggled", self.__on_btn_uni_table_toggled)
		hbox.pack_start(check_button, False, False, 0)
		page2.pack_start(hbox, False, False, 0)
		
		notebook.append_page(page2, Gtk.Label(_("PSF2")))

		self.show_all()
		
	def __on_psf_version_changed(self, notebook, page, page_num):
		if page_num == 0:
			self.entry_width.set_text("8")
			self.entry_width.set_sensitive(False)
			self.psf_version = psflib.PSF1_VERSION
		else:
			self.entry_width.set_editable(True)
			self.entry_width.set_sensitive(True)
			self.psf_version = psflib.PSF2_VERSION
				
	def __on_radion_btn_glyphs_changed(self, button, number_of_glyphs):
		self.glyph_num = number_of_glyphs
		
	def __on_btn_uni_table_toggled(self, button):
		self.has_unicode_table = button.get_active()
			
	def get_header(self):
		size = (int(self.entry_width.get_text()),
				int(self.entry_height.get_text()))
		if self.psf_version == psflib.PSF1_VERSION:
			header = psflib.PsfHeaderv1(size)
			if self.has_unicode_table:
				header.set_mode(psflib.PSF1_MODEHASTAB)
			if self.glyph_num == 512:
				header.set_mode(psflib.PSF1_MODE512)
		else:
			header = psflib.PsfHeaderv2(size)
			if self.has_unicode_table:
				header.set_flags(psflib.PSF2_HAS_UNICODE_TABLE)
		return header
		
class PySFeditWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title=_("PySFedit"))
		self.set_default_size(500, 400)
		self.connect("delete-event", self.on_window_delete)
		self.set_default_icon_from_file(c.IMG_DIR + "icon.png")

		self.top_grid = Gtk.Grid()
		self.add(self.top_grid)

		self.menu_bar = Gtk.MenuBar()
		self.menu_bar.set_hexpand(True)
		self.build_menu()
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
		self.about_window = None

	def build_menu(self):
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
		menuitem = Gtk.MenuItem(label=_("Preferences"))
		menuitem.connect("activate", self.on_menu_preferences_clicked)
		submenu.append(menuitem)
		menuitem = Gtk.MenuItem(label=_("Quit"))
		menuitem.connect("activate", self.on_menu_quit_clicked)
		submenu.append(menuitem)
		self.menu_bar.append(menu_file)

		menu_edit = Gtk.MenuItem(_("Edit"))
		submenu = Gtk.Menu()
		menu_edit.set_submenu(submenu)
		menuitem = Gtk.MenuItem(label=_("Copy"))
		menuitem.connect("activate", self.on_menu_copy_clicked)
		submenu.append(menuitem)
		menuitem = Gtk.MenuItem(label=_("Cut"))
		menuitem.connect("activate", self.on_menu_cut_clicked)
		submenu.append(menuitem)
		menuitem = Gtk.MenuItem(label=_("Paste"))
		menuitem.connect("activate", self.on_menu_paste_clicked)
		submenu.append(menuitem)
		menuitem = Gtk.MenuItem(label=_("Delete"))
		menuitem.connect("activate", self.on_menu_delete_clicked)
		submenu.append(menuitem)
		self.menu_bar.append(menu_edit)

		menu_help = Gtk.MenuItem(_("Help"))
		submenu = Gtk.Menu()
		menu_help.set_submenu(submenu)
		menuitem = Gtk.MenuItem(label=_("About"))
		menuitem.connect("activate", self.on_menu_about_clicked)
		submenu.append(menuitem)
		self.menu_bar.append(menu_help)		

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
		
	def on_menu_preferences_clicked(self, submenu):
		pass
		
	def on_menu_copy_clicked(self, submenu):
		pass
		
	def on_menu_cut_clicked(self, submenu):
		pass
		
	def on_menu_paste_clicked(self, submenu):
		pass
		
	def on_menu_delete_clicked(self, submenu):
		pass
		
	def on_menu_about_clicked(self, submenu):
		if self.about_window:
			self.about_window.destroy()
		self.about_window = AboutWindow()
		self.about_window.show_all()
		
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

if __name__ == "__main__":
	window = PySFeditWindow()
	window.show_all()
	Gtk.main()

