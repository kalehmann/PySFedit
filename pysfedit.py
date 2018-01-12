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
		"""This method gets called when the selected page in the
		notebook with the psf versions has changed.
		
		It sets the psf_version attribute of this dialog to either
		PSF1_VERSION or PSF"_VERSION from the psflib.
		
		Args:
			notebook (Gtk.Notebook): The Notebook that has switched the
				page
			page (Gtk.Widget): The new active page of the notbook
			page_num (int): The index of the active page		
		"""
		if page_num == 0:
			self.entry_width.set_text("8")
			self.entry_width.set_sensitive(False)
			self.psf_version = psflib.PSF1_VERSION
		else:
			self.entry_width.set_editable(True)
			self.entry_width.set_sensitive(True)
			self.psf_version = psflib.PSF2_VERSION
				
	def __on_radion_btn_glyphs_changed(self, button, number_of_glyphs):
		"""This method gets called when one of the radio buttons for 
		the number of glyphs of the old psf has been toggled.
		
		Args:
			button (Gtk.RadioButton): The radio button, that has been
				toggled.
			number_of_glyphs (int): The number of glyphs the font should
				have. Either 256 or 512.	
		"""
		self.glyph_num = number_of_glyphs
		
	def __on_btn_uni_table_toggled(self, button):
		"""This method get called, when the check button for including
		an unicode table of either the old psf or psf2 has been toggled.
		
		Args:
			button (Gtk.CheckBox): The check box, that has been toggled.
		"""
		self.has_unicode_table = button.get_active()
			
	def get_header(self):
		"""Use this method to get the header of the new font once the
		dialogs run method has returned Gtk.ResponseType.OK
		
		Returns:
			psflib.PsfHeader: The header of the new font		
		"""
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
		
class PySFeditContent(Gtk.Grid):
	def __init__(self, window):
		Gtk.Grid.__init__(self)
		self.window = window
		
		self.font_editor = None
				
	def get_file_path(self, title, _type="open"):
		if _type == "open":
			action = Gtk.FileChooserAction.OPEN
		elif _type == "save":
			action = Gtk.FileChooserAction.SAVE
		dialog = Gtk.FileChooserDialog(title, self.window,
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
		
	def new_font_dialog(self):
		if self.font_editor: self.font_editor.destroy()
		d = NewFontDialog(self.window)
		r = d.run()
		if r == Gtk.ResponseType.OK:
			header = d.get_header()
			self.font_editor = font_editor.FontEditor(header)
			self.attach(self.font_editor, 0, 1, 1, 1)
			self.show_all()
			d.destroy()
			
			return True
		d.destroy()
	
	def import_font_dialog(self):
		path = self.get_file_path(_("Import file"))
		if not path:
			return
		if self.font_editor: self.font_editor.destroy()
		if path.lower().endswith(".asm"):
			font = psflib.AsmImporter.import_from_file(path)
		elif path.lower().endswith('.psf'):
			font = psflib.PsfImporter.import_from_file(path)
		else:
			return
		self.font_editor = font_editor.FontEditor(
			font.get_header(), font)
		self.attach(self.font_editor, 0, 1, 1, 1)
		self.show_all()
		
		return True
		
		
	def export_font_dialog(self):
		if not self.font_editor:
			dialog = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.ERROR,
				Gtk.ButtonsType.OK, "Error!")
			dialog.format_secondary_text(
				_("You have not created a font yet."))
			dialog.run()
			dialog.destroy()
			return

		path = self.get_file_path(_("Export file"), "save")
		if not path:
			return
		if path.lower().endswith(".asm"):
			exporter = psflib.AsmExporter(self.font_editor.get_font())
			exporter.export_to_file(path)
		elif path.lower().endswith(".psf"):
			exporter = psflib.PsfExporter(self.font_editor.get_font())
			exporter.export_to_file(path)
		
	
		
class PySFeditWindow(Gtk.Window):
	"""This is the main window of PySFedit.
	
	Initially only the menu bar and two buttons for creating and
	importing a font are visible on this window. After a font has been
	created or imported the two buttons get destroyed and the
	PySFeditContent containing the font editor becomes visible.	
	"""
	def __init__(self):
		Gtk.Window.__init__(self, title=_("PySFedit"))
		self.set_default_size(500, 400)
		self.connect("delete-event", self.__on_window_delete)
		self.set_default_icon_from_file(c.IMG_DIR + "icon.png")

		self.has_font = False
		self.about_window = None

		self.grid = Gtk.Grid()
		self.add(self.grid)

		self.menu_bar = Gtk.MenuBar()
		self.menu_bar.set_hexpand(True)

		menu_file = Gtk.MenuItem(_("File"))
		submenu = Gtk.Menu()
		menu_file.set_submenu(submenu)
		menuitem = Gtk.MenuItem(label=_("New"))
		menuitem.connect("activate", self.__on_menu_new_clicked)
		submenu.append(menuitem)
		menuitem = Gtk.MenuItem(label=_("Import"))
		menuitem.connect("activate", self.__on_menu_import_clicked)
		submenu.append(menuitem)
		menuitem = Gtk.MenuItem(label=_("Export"))
		menuitem.connect("activate", self.__on_menu_export_clicked)
		submenu.append(menuitem)
		menuitem = Gtk.MenuItem(label=_("Preferences"))
		menuitem.connect("activate", self.__on_menu_preferences_clicked)
		submenu.append(menuitem)
		menuitem = Gtk.MenuItem(label=_("Quit"))
		menuitem.connect("activate", self.__on_menu_quit_clicked)
		submenu.append(menuitem)
		self.menu_bar.append(menu_file)

		menu_edit = Gtk.MenuItem(_("Edit"))
		submenu = Gtk.Menu()
		menu_edit.set_submenu(submenu)
		menuitem = Gtk.MenuItem(label=_("Copy"))
		menuitem.connect("activate", self.__on_menu_copy_clicked)
		submenu.append(menuitem)
		menuitem = Gtk.MenuItem(label=_("Cut"))
		menuitem.connect("activate", self.__on_menu_cut_clicked)
		submenu.append(menuitem)
		menuitem = Gtk.MenuItem(label=_("Paste"))
		menuitem.connect("activate", self.__on_menu_paste_clicked)
		submenu.append(menuitem)
		menuitem = Gtk.MenuItem(label=_("Delete"))
		menuitem.connect("activate", self.__on_menu_delete_clicked)
		submenu.append(menuitem)
		self.menu_bar.append(menu_edit)

		menu_help = Gtk.MenuItem(_("Help"))
		submenu = Gtk.Menu()
		menu_help.set_submenu(submenu)
		menuitem = Gtk.MenuItem(label=_("About"))
		menuitem.connect("activate", self.__on_menu_about_clicked)
		submenu.append(menuitem)
		self.menu_bar.append(menu_help)
		
		self.grid.attach(self.menu_bar,0,0,1,1)		
		
		self.button_new = Gtk.Button(_("New Font"))
		self.button_new.connect("clicked",
			self.__on_but_new_clicked)
		self.grid.attach(self.button_new,0,1,1,1)
		
		self.button_import = Gtk.Button(_("Import"))
		self.button_import.connect("clicked",
			self.__on_but_import_clicked)
		self.grid.attach(self.button_import, 0,2,1,1)
		
		self.content = PySFeditContent(self)
		self.grid.attach(self.content, 0,3,1,1)		
		
	def __on_menu_new_clicked(self, menu_item):
		"""This method gets called when the entry "new" of the menu
		"file" has been clicked and tells the PySFeditContent to create
		a new font.
		
		Args:
			menu_item (Gtk.MenuItem): The "new" item of the "file" menu		
		"""
		if self.content.new_font_dialog() and not self.has_font:
			self.button_import.destroy()
			self.button_new.destroy()

	def __on_menu_import_clicked(self, menu_item):
		"""This method gets called when the entry "import" of the menu
		"file" has been clicked and tells the PySFeditContent to import
		an existing font.
		
		Args:
			menu_item (Gtk.MenuItem): The "import" item of the "file"
				menu		
		"""
		if self.content.import_font_dialog() and not self.has_font:
			self.button_import.destroy()
			self.button_new.destroy()

	def __on_menu_export_clicked(self, menu_item):
		"""This method gets called when the entry "export" of the menu
		"file" has been clicked and tells the PySFeditContent to export
		the current font.
		
		Args:
			menu_item (Gtk.MenuItem): The "export" item of the "file"
				menu			
		"""
		self.content.export_font_dialog()
		
	def __on_menu_preferences_clicked(self, menu_item):
		"""This method gets called when the entry "preferences" of the
		menu "file" has been clicked and opens the PreferencesWindow.
		
		Args:
			menu_item (Gtk.MenuItem): The "preferences" item of the
				"file" menu		
		"""
		pass
		
	def __on_menu_quit_clicked(self, menu_item):
		"""This method gets called when the entry "quit" of the menu
		"file" has been clicked and initiates the quit process of the
		application.
		
		Args:
			menu_item (Gtk.MenuItem): The "quit" item of the "file" menu
		"""
		self.__on_quit()
		
	def __on_menu_copy_clicked(self, menu_item):
		"""This method gets called when the entry "copy" of the menu
		"edit" has been clicked and tells the PySFeditContent to copy
		the bitmap of the current glyph of the font editor to the
		clipboard.
		
		Args:
			menu_item (Gtk.MenuItem): The "copy" item of the "edit" menu		
		"""
		pass
		
	def __on_menu_cut_clicked(self, menu_item):
		"""This method gets called when the entry "cut" of the menu
		"edit" has been clicked and tells the PySFeditContent to copy
		the bitmap of the current glyph of the font editor to the
		clipboard and clear it afterwards.

		Args:
			menu_item (Gtk.MenuItem): The "cut" item of the "edit" menu
		"""
		pass
		
	def __on_menu_paste_clicked(self, menu_item):
		"""This method gets called when the entry "paste" of the menu
		"edit" has been clicked and tells the PySFeditContent to copy
		the bitmap stored in the clipboard to the current glyph.
		
		Args:
			menu_item (Gtk.MenuItem): The "paste" item of the "edit"
				menu
		"""
		pass
		
	def __on_menu_delete_clicked(self, menu_item):
		"""This method gets called when the entry "delete" of the menu
		"edit" has been clicked and tells the PySFeditContent to clear
		the bitmap of the current glyph of the font editor.
		
		Args:
			menu_item (Gtk.MenuItem): The "delete" item of the "edit"
				menu		
		"""
		pass
		
	def __on_menu_about_clicked(self, menu_item):
		"""This method gets called when the entry "about" of the menu
		"help" has been clicked and show the AboutWindow.
		
		Args:
			menu_item (Gtk.MenuItem): The "about" item of the "help"
				menu
		"""
		if self.about_window:
			self.about_window.destroy()
		self.about_window = AboutWindow()
		self.about_window.show_all()
		
	def __on_window_delete(self, widget, event):
		"""This method gets called on the delete event of the window and
		initiates the termination process of the appliication.
		
		Args:
			widget (Gtk.Widget): The window that received the delete
				event
			event (Gdk.Widget): The delete event received by the window
		"""
		self.__on_quit()
		
	def __on_quit(self):
		"""This method terminates the application"""
		Gtk.main_quit()
		
	def __on_but_new_clicked(self, button):
		"""This method gets called when the initial button for creating
		a new font has been clicked and tells the PySFeditContent to
		create a new font.
		
		Args:
			button (Gtk.Button): The intial button for creating a new
				font		
		"""
		if self.content.new_font_dialog() and not self.has_font:
			self.button_import.destroy()
			self.button_new.destroy()

	def __on_but_import_clicked(self, button):
		"""This method gets called when the initial button for importing
		a font has been clicked and tells the PySFeditContent to import
		a font.
		
		Args:
			button (Gtk.Button): The initial button for importing a font		
		"""
		if self.content.import_font_dialog() and not self.has_font:
			self.button_import.destroy()
			self.button_new.destroy()
			

if __name__ == "__main__":
	window = PySFeditWindow()
	window.show_all()
	Gtk.main()

