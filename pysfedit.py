#! /usr/bin/python3

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import psflib

FONT_SIZES = [
	[(8, 8), "8x8"],
	[(8, 16), "8x16"]
]

ASCII = "abcdefghijklmnop"

class FontEditor(Gtk.Grid):
	def __init__(self, header):
		Gtk.Grid.__init__(self)
		self.font_grid = FontGrid(header.size)
		
		self.combo_char = Gtk.ComboBoxText()
		self.combo_char.set_entry_text_column(0)
		for i in psflib.ASCII_PRINTABLE:
			self.combo_char.append_text(i[1])
		self.combo_char.set_active(0)
		self.combo_char.set_row_span_column(5)
		self.attach(self.combo_char, 0,0,1,1)
		self.attach(self.font_grid, 0,1,1,1)
		self.font = psflib.PcScreenFont(header)
		
	def on_combo_char_changed(self, combo):
		data = self.font_grid.get_data()

class FontGrid(Gtk.Grid):
	def __init__(self, size):
		Gtk.Grid.__init__(self)
		self.change_size(size)
		self.data = [[ 0 for i in range(size[0])]
						for i in range(size[1])]
		
	def change_size(self, size):
		self.data = [[ 0 for i in range(size[0])]
						for i in range(size[1])]
		for child in self.get_children():
			child.destroy()
		for i in range(size[0]):
			for j in range(size[1]):
				rb = Gtk.CheckButton()
				rb.connect("toggled", self.rb_toggled, i, j)
				self.attach(rb, i, j, 1, 1)
		self.show_all()
		
		
	def rb_toggled(self, button, col, row):
		self.data[row][col] = 0 if self.data[row][col] else 1
		
	def get_data(self):
		return self.data

class PySFeditWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title="PySFedit")
		self.set_default_size(400,400)
		self.connect("delete-event", Gtk.main_quit)

		self.top_grid = Gtk.Grid()
		self.add(self.top_grid)


		self.menu_bar = Gtk.MenuBar()
		self.menu_bar.set_hexpand(True)

		menu_file = Gtk.MenuItem("File")
		submenu = Gtk.Menu()
		menu_file.set_submenu(submenu)
		menuitem = Gtk.MenuItem(label="New")
		menuitem.connect("activate", self.on_menu_new_clicked)
		submenu.append(menuitem)
		menuitem = Gtk.MenuItem(label="Open")
		menuitem.connect("activate", self.on_menu_open_clicked)
		submenu.append(menuitem)
		menuitem = Gtk.MenuItem(label="Save")
		menuitem.connect("activate", self.on_menu_save_clicked)
		submenu.append(menuitem)
		self.menu_bar.append(menu_file)

		menu_help = Gtk.MenuItem("Help")
		submenu = Gtk.Menu()
		menu_help.set_submenu(submenu)
		menuitem = Gtk.MenuItem(label="About")
		submenu.append(menuitem)
		self.menu_bar.append(menu_help)		

		self.top_grid.attach(self.menu_bar,0,0,1,1)		
		
		self.button_new = Gtk.Button("New Font")
		self.button_new.connect("clicked", self.on_but_new_clicked)
		self.top_grid.attach(self.button_new,0,1,1,1)
		self.font_editor = None


	def on_but_new_clicked(self, button):
		self.new_font_dialog()

	def on_menu_new_clicked(self, submenu):
		self.new_font_dialog()

	def on_menu_open_clicked(self, submenu):
		dialog = Gtk.FileChooserDialog("Open file", self,
			Gtk.FileChooserAction.OPEN,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			 Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		filter_psf = Gtk.FileFilter()
		filter_psf.set_name("PSF files")
		filter_psf.add_mime_type("application/x-font-linux-psf")
		dialog.add_filter(filter_psf)

		filter_any = Gtk.FileFilter()
		filter_any.set_name("Any files")
		filter_any.add_pattern("*")
		dialog.add_filter(filter_any)

		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			print("File: %s" % dialog.get_filename())
		dialog.destroy()

	def on_menu_save_clicked(self, submenu):
		print("Ya clicked save")

	def new_font_dialog(self):
		if self.font_editor: self.font_editor.destroy()
		d = NewFontDialog(self)
		r = d.run()
		header = d.get_header()
		self.button_new.destroy()
		self.font_editor = FontEditor(header)
		self.top_grid.attach(self.font_editor, 0, 1, 1, 1)
		self.top_grid.show_all()
		d.destroy()


class NewFontDialog(Gtk.Dialog):
	def __init__(self, parent):
		Gtk.Dialog.__init__(self, "New Font", parent, 0,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			 Gtk.STOCK_OK, Gtk.ResponseType.OK))
		self.set_default_size(200,200)
		
		box = self.get_content_area()
		grid = Gtk.Grid()
		box.add(grid)
		
		l1 = Gtk.Label("Font Size:")
		grid.attach(l1, 0, 0, 1, 1)
		
		self.entry_width = Gtk.Entry()
		self.entry_width.set_text("Width")
		grid.attach(self.entry_width, 0, 1, 1, 1)
		
		self.entry_height = Gtk.Entry()
		self.entry_height.set_text("Height")
		grid.attach(self.entry_height, 1, 1, 1, 1)
		
		l2 = Gtk.Label("PSF version:")
		grid.attach(l2, 0, 2, 1, 1)
		
		box_version = Gtk.Box()
		grid.attach(box_version, 1, 2, 1, 1)
		
		self.but_v1 = Gtk.RadioButton.new_with_label_from_widget(None, "PSFv1")
		box_version.pack_start(self.but_v1, False, False, 0)
		
		self.but_v2 = Gtk.RadioButton.new_with_label_from_widget(self.but_v1, "PSFv2")
		box_version.pack_start(self.but_v2, False, False, 0)
		
		l3 = Gtk.Label("Include unicode table:")
		grid.attach(l3, 0, 3, 1, 1)
		
		self.check_table = Gtk.CheckButton()
		grid.attach(self.check_table, 1, 3, 1, 1)
		
		self.show_all()
	
	def get_header(self):
		size = (int(self.entry_width.get_text()),
				int(self.entry_height.get_text()))
		unicode_tab = self.check_table.get_active()
		if self.but_v1.get_active():
			header = psflib.PsfHeaderv1(size)
			if unicode_tab: header.set_mode(psflib.PSF1_MODEHASTAB)
		else:
			header = psflib.PsfHeaderv2(size)
			if unicode_tab: header.set_mode(
				psflib.PSF2_HAS_UNICODE_TABLE)
		return header

window = PySFeditWindow()
window.show_all()
Gtk.main()

