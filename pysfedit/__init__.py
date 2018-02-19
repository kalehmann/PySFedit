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
PySFedit is an editor for pc screen fonts written in python 3.
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
import gettext
import locale

from . import psflib
from . import font_editor
from . import constants as c
from .preferences_window import PreferencesWindow

translation = gettext.translation('pysfedit', localedir=c.LOCALE_DIR,
	fallback=True)
translation.install()
		
class AboutWindow(Gtk.Window):
	"""A window with information about this software and the gpl license
	text.	
	"""
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
		self.notebook.append_page(
			self.page1, Gtk.Label.new_with_mnemonic(_("_Info")))
		
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
		self.notebook.append_page(
			self.page2, Gtk.Label.new_with_mnemonic(_("_Licence")))
		
		
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
		
		size_wrapper = Gtk.Grid()
		size_wrapper.set_row_spacing(5)
		size_wrapper.set_column_spacing(5)
		self.entry_width = Gtk.Entry()
		self.entry_width.set_text("8")
		self.entry_width.set_sensitive(False)
		size_wrapper.attach(self.entry_width, 0, 1, 1, 1)
		
		l_width = Gtk.Label.new_with_mnemonic(_("_Width:"))
		l_width.set_mnemonic_widget(self.entry_width)
		size_wrapper.attach(l_width, 0, 0, 1, 1)
		
		self.entry_height = Gtk.Entry()
		self.entry_height.set_text("8")
		size_wrapper.attach(self.entry_height, 1, 1, 1, 1)
		
		l_height = Gtk.Label.new_with_mnemonic(_("_Height:"))
		l_height.set_mnemonic_widget(self.entry_height)
		size_wrapper.attach(l_height, 1, 0, 1, 1)
		
		box.pack_start(size_wrapper, False, False, 5)
		
		notebook = Gtk.Notebook()
		notebook.connect("switch-page", self.__on_psf_version_changed)
		box.pack_start(notebook, False, False, 0)
		page1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		rb256 = Gtk.RadioButton.new_with_mnemonic(
			None, _("25_6 Glyphs"))
		rb256.connect("toggled", self.__on_radion_btn_glyphs_changed,
			256)
		hbox.pack_start(rb256, False, False, 0)
		rb512 = Gtk.RadioButton.new_with_mnemonic_from_widget(
			rb256, _("_512 Glyphs"))
		rb512.connect("toggled", self.__on_radion_btn_glyphs_changed,
			512)
		hbox.pack_start(rb512, False, False, 0)
		page1.pack_start(hbox, False, False, 0)
		
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		l_unicode_table = Gtk.Label.new_with_mnemonic(
			_("Include _unicode table:"))
		hbox.pack_start(l_unicode_table, False, False, 0)
		check_button = Gtk.CheckButton()
		check_button.connect("toggled", self.__on_btn_uni_table_toggled)
		l_unicode_table.set_mnemonic_widget(check_button)
		hbox.pack_start(check_button, False, False, 0)
		page1.pack_start(hbox, False, False, 0)
		
		notebook.append_page(
			page1, Gtk.Label.new_with_mnemonic(_("_PSF")))
		
		page2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		l_unicode_table = Gtk.Label.new_with_mnemonic(
			_("Include _unicode table:"))
		hbox.pack_start(l_unicode_table, False, False, 0)
		check_button = Gtk.CheckButton()
		check_button.connect("toggled", self.__on_btn_uni_table_toggled)
		l_unicode_table.set_mnemonic_widget(check_button)
		hbox.pack_start(check_button, False, False, 0)
		page2.pack_start(hbox, False, False, 0)
		
		notebook.append_page(
			page2, Gtk.Label.new_with_mnemonic(_("PSF_2")))

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
	"""This class holds the font editor of PySFedit and is a wrapper
	about it for the main window.	
	
	Args:
		window (Gtk.Window): The main window of the application.
	"""
	def __init__(self, window):
		Gtk.Grid.__init__(self)
		self.window = window
		
		self.font_editor = None
				
	def get_file_path(self, title, _type="open"):
		"""Let the user select a file which can be handled by PySFedit.
		
		The following file formats are supported:
			.psf
			.psf.gz
			.asm
		
		Args:
			title (str): The title of the dialog for choosing the file.
			_type (str): Can be "open" or "save". This parameter sets
				whether the dialog for choosing the file appears as
				dialog for opening or saving a file.
		
		Returns:
			string: If the user has selected a file
			None: If the user has aborted		
		"""
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
		filter_psf.set_name(_("PSF files"))
		filter_psf.add_mime_type("application/x-font-linux-psf")
		dialog.add_filter(filter_psf)
		
		filter_asm = Gtk.FileFilter()
		filter_asm.set_name(_("ASM files"))
		filter_asm.add_pattern("*.asm")
		dialog.add_filter(filter_asm)
		
		filter_psfgz = Gtk.FileFilter()
		filter_psfgz.set_name(_("Gzip compressed PSF files"))
		filter_psfgz.add_pattern("*.psf.gz")
		dialog.add_filter(filter_psfgz)

		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			path = dialog.get_filename()
			dialog.destroy()
			
			return path
		dialog.destroy()
		
		return None
		
	def new_font(self):
		"""Show the user a dialog for creating a new font and create a
		font if the user confirms the dialog.
		
		Returns:
			bool: Whether a new font has been created or not
		"""
		if self.font_editor:
			self.font_editor.destroy()
			self.window.set_menu_edit_items_sensitive(False)
			
		d = NewFontDialog(self.window)
		r = d.run()
		if r == Gtk.ResponseType.OK:
			header = d.get_header()
			self.font_editor = font_editor.FontEditor(header)
			self.attach(self.font_editor, 0, 1, 1, 1)
			self.show_all()
			d.destroy()
			self.window.set_menu_edit_items_sensitive(True)

			return True
		d.destroy()
	
	def import_font(self):
		"""Let the user select a font file and import it.
		
		Returns:
			bool: Whether a font has been imported or not.		
		"""
		path = self.get_file_path(_("Import file"))
		if not path:
			return
		if self.font_editor:
			self.font_editor.destroy()
			self.window.set_menu_edit_items_sensitive(False)
		if path.lower().endswith(".asm"):
			font = psflib.AsmImporter.import_from_file(path)
		elif path.lower().endswith('.psf'):
			font = psflib.PsfImporter.import_from_file(path)
		elif path.lower().endswith(".psf.gz"):
			font = psflib.PsfGzImporter.import_from_file(path)
		else:
			
			return
		self.font_editor = font_editor.FontEditor(
			font.get_header(), font)
		self.attach(self.font_editor, 0, 1, 1, 1)
		self.show_all()
		self.window.set_menu_edit_items_sensitive(True)

		return True
		
	def export_font(self):
		"""Export the current font and let the user decide where and in
		which format.
		"""
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
		elif path.lower().endswith(".psf.gz"):
			exporter = psflib.PsfGzExporter(self.font_editor.get_font())
			exporter.export_to_file(path)
		
	def copy_current_bitmap(self):
		"""Copy the data of the glyph bitmap that is currently selected
		in the glyph selector to the clipboard		
		"""
		self.font_editor.copy_current_bitmap_to_clipboard()
	
	def cut_current_bitmap(self):
		"""Copy the data of the glyph bitmap that is currently selected
		in the glyph selector to the clipboard and then clear the data
		of the glyph bitmap.		
		"""
		self.font_editor.cut_current_bitmap_to_clipboard()
	
	def paste_bitmap_from_clipboard(self):
		"""Grab a bitmap from the clipboard (if there is any) and copy
		its content into the glyph bitmap that is currently selected in
		the glyph selector		
		"""
		self.font_editor.paste_bitmap_from_clipboard()
	
	def delete_current_bitmap(self):
		"""Clear the data of the glyph bitmap that is currently selected
		in the glyph selector		
		"""
		self.font_editor.delete_current_bitmap()
		
class PySFeditWindow(Gtk.Window):
	"""This is the main window of PySFedit.
	
	Initially only the menu bar and two buttons for creating and
	importing a font are visible on this window. After a font has been
	created or imported the two buttons get destroyed and the
	PySFeditContent containing the font editor becomes visible.
	
	Args:
		main_loop (GLib.MainLoop): The main loop of the application.
	"""
	def __init__(self, main_loop):
		Gtk.Window.__init__(self, title=_("PySFedit"))
		
		self.__main_loop = main_loop
		
		self.set_default_size(500, 400)
		self.connect("delete-event", self.__on_window_delete)
		self.set_default_icon_from_file(c.IMG_DIR + "icon.png")

		self.accel_group = Gtk.AccelGroup()
		self.add_accel_group(self.accel_group)

		self.has_font = False
		self.about_window = None
		self.preferences_window = None

		self.grid = Gtk.Grid()
		self.add(self.grid)

		self.menu_bar = Gtk.MenuBar()
		self.menu_bar.set_hexpand(True)

		menu_file = Gtk.MenuItem.new_with_mnemonic(_("_File"))
		submenu = Gtk.Menu()
		menu_file.set_submenu(submenu)
		menuitem = Gtk.MenuItem.new_with_mnemonic(_("_New"))
		menuitem.connect("activate", self.__on_menu_new_clicked)
		menuitem.add_accelerator(
			"activate", self.accel_group, Gdk.KEY_n, 
			Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE
		)
		submenu.append(menuitem)
		menuitem = Gtk.MenuItem.new_with_mnemonic(_("_Import"))
		menuitem.connect("activate", self.__on_menu_import_clicked)
		menuitem.add_accelerator(
			"activate", self.accel_group, Gdk.KEY_o, 
			Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE
		)
		submenu.append(menuitem)
		menuitem = Gtk.MenuItem.new_with_mnemonic(_("_Export"))
		menuitem.connect("activate", self.__on_menu_export_clicked)
		menuitem.add_accelerator(
			"activate", self.accel_group, Gdk.KEY_s, 
			Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE
		)
		submenu.append(menuitem)
		menuitem = Gtk.MenuItem.new_with_mnemonic(_("_Preferences"))
		menuitem.connect("activate", self.__on_menu_preferences_clicked)
		submenu.append(menuitem)
		menuitem = Gtk.MenuItem.new_with_mnemonic(_("_Quit"))
		menuitem.connect("activate", self.__on_menu_quit_clicked)
		menuitem.add_accelerator(
			"activate", self.accel_group, Gdk.KEY_q, 
			Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE
		)
		submenu.append(menuitem)
		self.menu_bar.append(menu_file)

		menu_edit = Gtk.MenuItem.new_with_mnemonic(_("_Edit"))
		submenu = Gtk.Menu()
		menu_edit.set_submenu(submenu)
		self.mi_copy = Gtk.MenuItem.new_with_mnemonic(_("_Copy"))
		self.mi_copy.connect("activate", self.__on_menu_copy_clicked)
		self.mi_copy.add_accelerator(
			"activate", self.accel_group, Gdk.KEY_c, 
			Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE
		)
		self.mi_copy.set_sensitive(False)
		submenu.append(self.mi_copy)
		self.mi_cut = Gtk.MenuItem.new_with_mnemonic(_("Cu_t"))
		self.mi_cut.connect("activate", self.__on_menu_cut_clicked)
		self.mi_cut.add_accelerator(
			"activate", self.accel_group, Gdk.KEY_x, 
			Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE
		)
		self.mi_cut.set_sensitive(False)
		submenu.append(self.mi_cut)
		self.mi_paste = Gtk.MenuItem.new_with_mnemonic(_("_Paste"))
		self.mi_paste.connect("activate", self.__on_menu_paste_clicked)
		self.mi_paste.add_accelerator(
			"activate", self.accel_group, Gdk.KEY_v, 
			Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE
		)
		self.mi_paste.set_sensitive(False)
		submenu.append(self.mi_paste)
		self.mi_delete = Gtk.MenuItem.new_with_mnemonic(_("_Delete"))
		self.mi_delete.connect("activate",
			self.__on_menu_delete_clicked)
		self.mi_delete.add_accelerator(
			"activate", self.accel_group, Gdk.KEY_d, 
			Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE
		)
		self.mi_delete.set_sensitive(False)
		submenu.append(self.mi_delete)
		self.menu_bar.append(menu_edit)
		
		self.edit_menu_items = [
			self.mi_copy,
			self.mi_cut,
			self.mi_paste,
			self.mi_delete
		]

		menu_help = Gtk.MenuItem.new_with_mnemonic(_("_Help"))
		submenu = Gtk.Menu()
		menu_help.set_submenu(submenu)
		menuitem = Gtk.MenuItem.new_with_mnemonic(_("_About"))
		menuitem.connect("activate", self.__on_menu_about_clicked)
		menuitem.add_accelerator(
			"activate", self.accel_group, Gdk.KEY_F1, 
			0, Gtk.AccelFlags.VISIBLE
		)
		submenu.append(menuitem)
		self.menu_bar.append(menu_help)
		
		self.grid.attach(self.menu_bar,0,0,1,1)		
		
		self.button_new = Gtk.Button.new_with_mnemonic(_("_New Font"))
		self.button_new.connect("clicked",
			self.__on_but_new_clicked)
		self.grid.attach(self.button_new,0,1,1,1)
		
		self.button_import = Gtk.Button.new_with_mnemonic(_("_Import"))
		self.button_import.connect("clicked",
			self.__on_but_import_clicked)
		self.grid.attach(self.button_import, 0,2,1,1)
		
		self.content = PySFeditContent(self)
		self.grid.attach(self.content, 0,3,1,1)		
		
	def set_menu_edit_items_sensitive(self, value):
		"""Call set_sensitive on all menu items in the edit menu.
		
		Args:
			value (bool): Whether to set the menu items sensitive or
				not.
		"""
		for mi in self.edit_menu_items:
			mi.set_sensitive(value)
		self.show_all()
		
	def __on_menu_new_clicked(self, menu_item):
		"""This method gets called when the entry "new" of the menu
		"file" has been clicked and tells the PySFeditContent to create
		a new font.
		
		Args:
			menu_item (Gtk.MenuItem): The "new" item of the "file" menu		
		"""
		if self.content.new_font() and not self.has_font:
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
		if self.content.import_font() and not self.has_font:
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
		self.content.export_font()
		
	def __on_menu_preferences_clicked(self, menu_item):
		"""This method gets called when the entry "preferences" of the
		menu "file" has been clicked and opens the PreferencesWindow.
		
		Args:
			menu_item (Gtk.MenuItem): The "preferences" item of the
				"file" menu		
		"""
		if self.preferences_window:
			self.preferences_window.destroy()
		self.preferences_window = PreferencesWindow()
		self.preferences_window.show_all()
		
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
		self.content.copy_current_bitmap()
		
	def __on_menu_cut_clicked(self, menu_item):
		"""This method gets called when the entry "cut" of the menu
		"edit" has been clicked and tells the PySFeditContent to copy
		the bitmap of the current glyph of the font editor to the
		clipboard and clear it afterwards.

		Args:
			menu_item (Gtk.MenuItem): The "cut" item of the "edit" menu
		"""
		self.content.cut_current_bitmap()
		
	def __on_menu_paste_clicked(self, menu_item):
		"""This method gets called when the entry "paste" of the menu
		"edit" has been clicked and tells the PySFeditContent to copy
		the bitmap stored in the clipboard to the current glyph.
		
		Args:
			menu_item (Gtk.MenuItem): The "paste" item of the "edit"
				menu
		"""
		self.content.paste_bitmap_from_clipboard()
		
	def __on_menu_delete_clicked(self, menu_item):
		"""This method gets called when the entry "delete" of the menu
		"edit" has been clicked and tells the PySFeditContent to clear
		the bitmap of the current glyph of the font editor.
		
		Args:
			menu_item (Gtk.MenuItem): The "delete" item of the "edit"
				menu		
		"""
		self.content.delete_current_bitmap()
		
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
		self.__main_loop.quit()
		
	def __on_but_new_clicked(self, button):
		"""This method gets called when the initial button for creating
		a new font has been clicked and tells the PySFeditContent to
		create a new font.
		
		Args:
			button (Gtk.Button): The intial button for creating a new
				font		
		"""
		if self.content.new_font() and not self.has_font:
			self.button_import.destroy()
			self.button_new.destroy()

	def __on_but_import_clicked(self, button):
		"""This method gets called when the initial button for importing
		a font has been clicked and tells the PySFeditContent to import
		a font.
		
		Args:
			button (Gtk.Button): The initial button for importing a font		
		"""
		if self.content.import_font() and not self.has_font:
			self.button_import.destroy()
			self.button_new.destroy()

def main():
	main = GLib.MainLoop()
	window = PySFeditWindow(main)
	window.show_all()
	try:
		main.run()
	except KeyboardInterrupt:
		pass
		
if __name__ == "__main__":
	main()	
