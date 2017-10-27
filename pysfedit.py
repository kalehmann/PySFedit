#! /usr/bin/python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import GLib
from PIL import Image, ImageDraw

import psflib

class FontEditor(Gtk.Grid):
	def __init__(self, header):
		Gtk.Grid.__init__(self)
		print(header.size)
		self.font_grid = FontGrid(header.size)
		self.top_grid = Gtk.Grid()
		self.attach(self.top_grid, 0, 0, 1, 1)
		
		self.entry_char = Gtk.Entry()
		self.entry_char.set_width_chars(2)
		self.spin_char = Gtk.SpinButton()
		self.spin_char.set_numeric(True)
		adj = Gtk.Adjustment(0,0,255,1,0,0)
		self.spin_char.set_adjustment(adj)		
		
		self.active_char = 0
		self.char_selector = CharSelector()
		self.top_grid.attach(self.spin_char, 0,0,1,1)
		self.top_grid.attach(self.entry_char, 1, 0, 1, 1)
		self.top_grid.attach(self.char_selector, 1, 1, 1, 1)
		self.attach(self.font_grid, 0,1,1,1)
		self.font = psflib.PcScreenFont(header)
		
		self.glyph_selector = GlyphSelector()
		self.glyph_selector.set_changed_callback(self.on_selector_changed)
		#self.spin_char.connect("value_changed", self.on_spin_char_changed)
		self.entry_char.connect("activate", self.on_entry_char_activate)
		
	def on_entry_char_activate(self, entry):
		char = psflib.get_ord(entry.get_text())
		if char:
			self.spin_char.set_value(char)
		elif psflib.get_unicode_str(self.active_char):
			entry.set_text(psflib.get_unicode_str(self.active_char))
		else:
			entry.set_text("")

		
	def on_selector_changed(self, uc):
		data = self.font_grid.get_data()
		self.font.get_glyph(self.active_char).copy_data(data)
		
		self.active_char = spin.get_value_as_int()
		txt = psflib.get_unicode_str(self.active_char)
		if not txt: txt = ""
		self.entry_char.set_text(txt)
		
		self.font_grid.set_data(self.font.get_glyph(self.active_char).data)


class FontGrid(Gtk.Grid):
	def __init__(self, size):
		Gtk.Grid.__init__(self)
		self.size = size
		self.data = [[ 0 for i in range(size[0])]
						for j in range(size[1])]		
		self.check_boxes = []
		self.touched = False
	
		for i in range(size[0]):
			self.check_boxes.append([])
			for j in range(size[1]):
				rb = Gtk.CheckButton()
				rb.connect("toggled", self.rb_toggled, i, j)
				self.attach(rb, i, j, 1, 1)
				self.check_boxes[i].append(rb)
		self.show_all()
		
	def rb_toggled(self, button, row, col):
		self.data[row][col] = 1 if button.get_active() else 0
		self.touched = True
		
	def get_data(self):
		return self.data
	
	def set_data(self, data):
		for i in range(self.size[1]):
			for j in range(self.size[0]):
				self.check_boxes[i][j].set_active(
					data[i][j] == 1)
						
	def reset(self):
		for child in self.get_children():
			child.set_active(False)
		self.data = [[ 0 for i in range(self.size[0])]
						for j in range(self.size[1])]
						
	def get_touched(self):
		return self.touched

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
		menuitem = Gtk.MenuItem(label="Export")
		menuitem.connect("activate", self.on_menu_export_clicked)
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

		img = Image.new('RGBA', (20, 20), (0,0,0) )
		draw = ImageDraw.Draw(img,)
		draw.rectangle([(0,0), (10,10)], (200,0,0), 5)
		dat = img.tobytes()
		w, h = img.size
		dat = GLib.Bytes.new(dat)
		
		pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(dat, GdkPixbuf.Colorspace.RGB,
												 True, 8, w, h, w * 4)

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

	def on_menu_export_clicked(self, submenu):
		self.export_font_dialog()

	def new_font_dialog(self):
		if self.font_editor: self.font_editor.destroy()
		d = NewFontDialog(self)
		r = d.run()
		if r == Gtk.ResponseType.OK:
			header = d.get_header()
			self.button_new.destroy()
			self.font_editor = FontEditor(header)
			self.top_grid.attach(self.font_editor, 0, 1, 1, 1)
			self.top_grid.show_all()
		d.destroy()
	
	def export_font_dialog(self):
		d = ExportFontDialog(self)
		r = d.run()
		if r == Gtk.ResponseType.OK:
			export_format = d.get_export_format()
			print(export_format)
		d.destroy()
		if not self.font_editor:
			dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
				Gtk.ButtonsType.OK, "Error!")
			dialog.format_secondary_text("You have not created a font yet.")
			dialog.run()
			dialog.destroy()
			return
		
		

class ExportFontDialog(Gtk.Dialog):
	
	__formats = (
		("Plaintext - assembler file", psflib.TYPE_PLAIN_ASM),
		("Binary - PSF file", psflib.TYPE_BINARY_PSF)
	)
	
	def __init__(self, parent):
		Gtk.Dialog.__init__(self, "New Font", parent, 0,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			 Gtk.STOCK_OK, Gtk.ResponseType.OK))
		
		self.export_format = 0
		
		self.grid = Gtk.Grid()
		self.get_content_area().add(self.grid)
		
		self.format_combo = Gtk.ComboBoxText.new()
		for i in self.__formats:
			self.format_combo.append_text(i[0])
		self.format_combo.connect("changed", self.on_format_combo_changed)
		self.format_combo.set_active(0)
	
		l1 = Gtk.Label()
		l1.set_text("Format:")
	
		self.grid.attach(l1, 0, 0, 1, 1)
		self.grid.attach(self.format_combo, 0, 1, 1, 1)
		self.show_all()
		
	def on_format_combo_changed(self, combo):
		self.export_format = self.__formats[combo.get_active()][1]
		
	def get_export_format(self):
		return self.export_format

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
		self.entry_width.set_text("8")
		grid.attach(self.entry_width, 0, 1, 1, 1)
		
		self.entry_height = Gtk.Entry()
		self.entry_height.set_text("8")
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

class GlyphSelector(Gtk.ScrolledWindow):
	def __init__(self):
		Gtk.ScrolledWindow.__init__(self)
		
		self.changed_callback = None
		self.unicode_strings = {}
		
		self.model = Gtk.ListStore(GdkPixbuf.Pixbuf, str)
		self.tree_view = Gtk.TreeView.new_with_model(self.model)

		char_renderer = Gtk.CellRendererPixbuf()
		char_column = Gtk.TreeViewColumn("Char", char_renderer, pixbuf=0)
		self.tree_view.append_column(char_column)
		
		text_renderer = Gtk.CellRendererText()
		text_column = Gtk.TreeViewColumn("Unicode", text_renderer, text=1)
		self.tree_view.append_column(text_column)
		self.add(self.tree_view)
		
		self.set_property("min-content-width", 200)
		self.set_property("min-content-height", 100)
		
		selection = self.tree_view.get_selection()
		selection.set_mode(Gtk.SelectionMode.SINGLE)
		selection.connect("changed", self.on_selection_changed)
		
	def add_entry(self, pixbuf, unicode_str):
		iter = self.model.append([pixbuf, unicode_str])
		if unicode_str in self.unicode_strings.keys():
			self.unicode_strings[unicode_str].append(iter)	
		else:
			self.unicode_strings[unicode_str] = [iter]				
		
	def has_entry(self, unicode_str):
		return unicode_str in self.unicode_strings
		
	def set_changed_callback(self, callback):
		self.changed_callback = callback
		
	def on_selection_changed(self, treeselection):
		model, treepaths = treeselection.get_selected_rows()
		for path in treepaths:
			tree_iter = model.get_iter(path)
			uc = model.get_value(tree_iter, 1)
			if self.changed_callback:
				self.changed_callback(uc)
			


window = PySFeditWindow()
window.show_all()
Gtk.main()

