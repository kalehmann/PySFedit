#! /usr/bin/python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import GLib
from gi.repository import Gdk
from PIL import Image, ImageDraw
from GlyphEditor import GlyphEditor

import psflib

class FontEditor(Gtk.Grid):
	def __init__(self, header, font = None):
		Gtk.Grid.__init__(self)
		
		self.size = header.size
		
		self.font_grid = GlyphEditor()
		ctx = self.font_grid.get_context()
		ctx.set_glyph_size(header.size)
		self.font_grid.set_context(ctx)
		self.font_grid.get_attributes().set_seperation_lines(True)
		self.font_grid.get_attributes().set_draw_unset_pixels(True)
		
		self.top_grid = Gtk.Grid()
		self.attach(self.top_grid, 0, 0, 1, 1)
		
		self.clean_pixbuf = self.get_pixbuf()
		self.active_char = None

		if font:
			self.font = font
			min_cp = min(font.get_glyphs().keys())
			first_glyph = font.get_glyph(min_cp)
			self.font_grid.set_data(first_glyph.get_data())
			self.active_char = min_cp
		else:
			self.font = psflib.PcScreenFont(header)
				
		self.button_add = Gtk.Button(None,
				image=Gtk.Image(stock=Gtk.STOCK_ADD))
		self.button_remove = Gtk.Button(None,
				image=Gtk.Image(stock=Gtk.STOCK_REMOVE))
		self.glyph_selector = GlyphSelector(font)	
		
		self.button_debug = Gtk.Button("Debug")
		self.button_debug.connect("clicked", self.on_debug)
		self.top_grid.attach(self.button_debug, 2, 0, 1, 1)
		
		self.top_grid.attach(self.button_add, 0, 0, 1, 1)
		self.top_grid.attach(self.button_remove, 1, 0, 1, 1)
		self.attach(self.glyph_selector, 3, 1, 1, 1)
		self.attach(self.font_grid, 0,1,3,1)
		
		
		self.glyph_selector.set_changed_callback(
				self.on_selector_changed)
		self.glyph_selector.set_edited_callback(
				self.on_char_edited)
		self.glyph_selector.set_repr_added_callback(
				self.on_repr_added)
		self.glyph_selector.set_repr_removed_callback(
				self.on_repr_removed)
				
		self.button_add.connect("clicked", self.on_button_add_clicked)
		self.button_remove.connect("clicked",
				self.on_button_remove_clicked)
				
	@staticmethod
	def initialize_with_font(font):
		return FontEditor(font.get_header(), font)
				
	def get_font(self):
		return self.font

	def get_pixbuf(self):
		img = Image.new('RGBA', self.size, (0,0,0,0))
		draw = ImageDraw.Draw(img)
		for y, row in zip(range(self.size[1]),
								self.font_grid.get_data()):
			for x, pixel in zip(range(self.size[0]), row):
				if pixel == 1:
					draw.point((x, y), (0,0,0,255))
		data = img.tobytes()
		w, h = img.size
		data = GLib.Bytes.new(data)		
		pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(data,
					GdkPixbuf.Colorspace.RGB, True, 8, w, h, w * 4)
		return pixbuf
		
	def on_button_add_clicked(self, button):		
		pixbuf = self.clean_pixbuf
		char_id = self.glyph_selector.get_new_id()
		self.glyph_selector.add_glyph(char_id, pixbuf)
				
	def on_char_change(self, new_id):
		if self.active_char == None:
			self.glyph_selector.update_pixbuf(new_id, self.get_pixbuf())
			glyph = self.font.get_glyph(new_id)
			glyph.copy_data(self.font_grid.get_data())
			return
		glyph = self.font.get_glyph(self.active_char)
		glyph.copy_data(self.font_grid.get_data())
		pixbuf = self.get_pixbuf()
		self.font_grid.reset()
		self.glyph_selector.update_pixbuf(self.active_char, pixbuf)
		glyph = self.font.get_glyph(new_id)
		self.font_grid.set_data(glyph.get_data())
		
	def on_button_remove_clicked(self, button):
		if self.active_char != None:
			char_id = self.active_char
			self.glyph_selector.remove_glyph(self.active_char)
			self.font.remove_glyph(char_id)
			self.active_char = self.glyph_selector.get_selected_id()
			
	def on_selector_changed(self, char_id):
		self.on_char_change(char_id)
		self.active_char = char_id

	def on_char_edited(self, primary_cp, old_cp, new_cp):
		self.font.update_unicode_representation(primary_cp, old_cp,
				new_cp)
		if primary_cp == old_cp:
			self.active_char = new_cp
			
	def on_repr_added(self, primary_cp, repr_cp):
		glyph = self.font.get_glyph(primary_cp)
		glyph.add_unicode_representation(repr_cp)
		
	def on_repr_removed(self, primary_cp, repr_cp):
		glyph = self.font.get_glyph(primary_cp)
		glyph.remove_unicode_representation(repr_cp)
		
	def on_debug(self, button):
		print(self.font)
		
	def __set_font(self):
		print("test")
		
class FontGrid(Gtk.Grid):
	"""Grid with checkbuttons to edit the pixel representation of a char
	
		Arguments:
			size -> size of the character in pixels. 2-value tuple
					first value is the width and second the height
	"""
	def __init__(self, size):
		Gtk.Grid.__init__(self)
		self.size = size
		self.checkbuttons = []
	
		for y in range(size[1]):
			self.checkbuttons.append([])
			for x in range(size[0]):
				cb = Gtk.CheckButton()
				self.attach(cb, x, y, 1, 1)
				self.checkbuttons[y].append(cb)
		self.show_all()
		
	def get_data(self):
		data = []
		for row in self.checkbuttons:
			r = []
			for checkbutton in row:
				r.append(1 if checkbutton.get_active() else 0)
			data.append(r)
		return data
	
	def set_data(self, data):
		for i, row in zip(range(self.size[1]), data):
			for j, element in zip(range(self.size[0]), row):
				self.checkbuttons[i][j].set_active(element == 1)
						
	def reset(self):
		for child in self.get_children():
			child.set_active(False)

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
		menuitem = Gtk.MenuItem(label="Import")
		menuitem.connect("activate", self.on_menu_import_clicked)
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
		self.button_new.connect("clicked",
			self.__on_but_new_clicked)
		self.top_grid.attach(self.button_new,0,1,1,1)
		
		self.button_import = Gtk.Button("Import")
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
		filter_psf.set_name("PSF files	.psf")
		filter_psf.add_mime_type("application/x-font-linux-psf")
		dialog.add_filter(filter_psf)
		
		filter_asm = Gtk.FileFilter()
		filter_asm.set_name("ASM files	.asm")
		filter_asm.add_pattern("*.asm")
		dialog.add_filter(filter_asm)

		#filter_any = Gtk.FileFilter()
		#filter_any.set_name("Any files	.*")
		#filter_any.add_pattern("*")
		#dialog.add_filter(filter_any)

		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			path = dialog.get_filename()
			dialog.destroy()
			return path
		dialog.destroy()
		
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
			self.font_editor = FontEditor(header)
			self.top_grid.attach(self.font_editor, 0, 1, 1, 1)
			self.top_grid.show_all()
		d.destroy()
	
	def import_font_dialog(self):
		if self.font_editor: self.font_editor.destroy()
		path = self.get_file_path("Import file")
		if path.lower().endswith(".asm"):
			font = psflib.AsmImporter.import_file(path)
		elif path.lower.endswith('.psf'):
			pass
		else:
			return
		self.button_new.destroy()
		self.button_import.destroy()
		self.font_editor = FontEditor(font.get_header(), font)
		self.top_grid.attach(self.font_editor, 0, 1, 1, 1)
		self.top_grid.show_all()
		
		
	def export_font_dialog(self):
		if not self.font_editor:
			dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
				Gtk.ButtonsType.OK, "Error!")
			dialog.format_secondary_text(
					"You have not created a font yet.")
			dialog.run()
			dialog.destroy()
			return

		path = self.get_file_path("Export file", "save")
		if path == None:
			return
		if path.lower().endswith(".asm"):
			exporter = psflib.AsmExporter(self.font_editor.get_font())
			exporter.export_file(path)
		elif path.lower().endswith(".psf"):
			pass

class NewFontDialog(Gtk.Dialog):
	def __init__(self, parent):
		Gtk.Dialog.__init__(self, "New Font", parent, 0,
			(Gtk.STOCK_OK, Gtk.ResponseType.OK,
			 Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
		self.set_default_size(200,200)
		
		box = self.get_content_area()
		grid = Gtk.Grid()
		box.add(grid)
		
		l1 = Gtk.Label("Font Size:")
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

		lglyph_num = Gtk.Label("Number of Glyphs:")
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


		l3 = Gtk.Label("Include unicode table:")
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
		
class NewUnicodeRepresentationDialog(Gtk.Dialog):
	def __init__(self, parent, codepoint):
		Gtk.Dialog.__init__(self, "New Font", parent, 0,
			(Gtk.STOCK_OK, Gtk.ResponseType.OK,
			 Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
		self.set_default_size(150,100)
		
		self.codepoint = codepoint
		
		box = self.get_content_area()
		grid = Gtk.Grid()
		box.add(grid)
		
		l1 = Gtk.Label("Unicode")
		l2 = Gtk.Label("Codepoint")
		
		self.entry_uc = Gtk.Entry()
		self.entry_uc.set_text(psflib.get_unicode_str(codepoint))
		self.entry_uc.connect("activate", self.__on_entry_uc_changed)
		
		adjustment = Gtk.Adjustment(0, 0, 65535, 1, 1, 0)
		self.spin_cp = Gtk.SpinButton()
		self.spin_cp.set_numeric(True)
		self.spin_cp.connect("value-changed", self.__on_spin_cp_changed)
		self.spin_cp.set_adjustment(adjustment)
		self.spin_cp.set_value(codepoint)
		
		grid.attach(l1, 0, 0, 1, 1)
		grid.attach(l2, 1, 0, 1, 1)
		grid.attach(self.entry_uc, 0, 1, 1, 1)
		grid.attach(self.spin_cp, 1, 1, 1, 1)
		
		self.show_all()
		
	def __on_spin_cp_changed(self, spin):
		self.codepoint = int(spin.get_value())
		uc = psflib.get_unicode_str(self.codepoint)
		self.entry_uc.set_text(uc)

	def __on_entry_uc_changed(self, entry):
		txt = entry.get_text()
		codepoint = psflib.get_codepoint(txt)
		if codepoint:
			self.codepoint = codepoint
			self.spin_cp.set_value(codepoint)
		else:
			uc = psflib.get_unicode_str(self.codepoint)
			entry.set_text(uc)

	def get_codepoint(self):
		return self.codepoint

class GlyphSelector(Gtk.Grid):
	"""
	
	Args:
		font (PcScreenFont): A font to initialize the glyphselector
			with.	
	"""
	TITLE_CODEPOINT = "Codepoint"
	TITLE_UNICODE = "Unicode"
	
	def __init__(self, font = None):
		Gtk.ScrolledWindow.__init__(self)
		
		self.changed_callback = None
		self.edited_callback = None
		self.repr_added_callback = None
		self.repr_removed_callback = None
		
		self.chars = {}
		self.char_display_size = (24, 24)
		
		self.clean_pixbuf = GdkPixbuf.Pixbuf.new(
								GdkPixbuf.Colorspace.RGB, True, 8, 1, 1)
		self.clean_pixbuf.fill(0)
		
		self.scrolled_window = Gtk.ScrolledWindow()
		
		self.model = Gtk.TreeStore(GdkPixbuf.Pixbuf, str, str)
		self.tree_view = Gtk.TreeView.new_with_model(self.model)

		char_renderer = Gtk.CellRendererPixbuf()
		char_column = Gtk.TreeViewColumn("Char", char_renderer,
						pixbuf=0)
		self.tree_view.append_column(char_column)
		
		unicode_renderer = Gtk.CellRendererText(
							mode=Gtk.CellRendererMode.EDITABLE)
		unicode_renderer.set_property("editable", True)
		unicode_renderer.connect("edited", self.__on_unicode_edited)
		unicode_column = Gtk.TreeViewColumn("Unicode", unicode_renderer,
							text=1)
		self.tree_view.append_column(unicode_column)
		
		codepoint_renderer = Gtk.CellRendererText(
								mode=Gtk.CellRendererMode.EDITABLE)
		codepoint_renderer.set_property("editable", True)
		codepoint_renderer.connect("edited", self.__on_codepoint_edited)
		codepoint_column = Gtk.TreeViewColumn("Codepoint",
							codepoint_renderer, text=2)
		self.tree_view.append_column(codepoint_column)
		
		box = Gtk.Box()
		box.add(self.tree_view)
		self.scrolled_window.add(box)		
		self.scrolled_window.set_property("min-content-width", 250)
		self.scrolled_window.set_property("min-content-height", 200)
		
		self.selection = self.tree_view.get_selection()
		self.selection.set_mode(Gtk.SelectionMode.SINGLE)
		self.selection.connect("changed", self.__on_selection_changed)
		self.tree_view.connect("button-press-event",
				self.__on_treeview_clicked_event)
		self.tree_view.set_enable_tree_lines(True)
		
		self.attach(self.scrolled_window, 0, 1, 1, 1)
		
		if font:
			self.__load_font_data(font)
		
	def set_glyph_display_size(self, size):
		"""Set the display size of the pixbuf showing a glyph
		
		Args:
			size (tuple/list) : Contains the with and height		
		"""
		self.char_display_size = size
		iter = self.model.get_iter_first()
		while iter:
			pixbuf = self.model.get(iter, 0)[0]
			pixbuf = pixbuf.scale_simple(self.char_display_size[0],
						self.char_display_size[1],
						GdkPixbuf.InterpType.NEAREST)
			self.model.set_value(iter, 0, pixbuf)
			iter = self.model.iter_next(iter)
		
	def add_glyph(self, primary_codepoint, pixbuf):
		"""Add a glyph
		
		Args:
			primary_codepoint (int) : The primary codepoint of the glyph
			pixbuf (GdkPixbuf.Pixbuf) : The pixbuf showing the glyph
		
		"""
		pixbuf = pixbuf.scale_simple(self.char_display_size[0],
						self.char_display_size[1],
						GdkPixbuf.InterpType.NEAREST)
		uc = psflib.get_unicode_str(primary_codepoint)
		iter = self.model.append(None, [pixbuf, uc,
						str(primary_codepoint)])
		path = self.model.get_path(iter)
		if self.has_glyph(primary_codepoint):
			self.remove_glyph(primary_codepoint)
		self.chars[primary_codepoint] = []
		self.selection.select_iter(iter)
		self.add_repr(primary_codepoint, primary_codepoint)
		
	def add_repr(self, primary_codepoint, codepoint):
		"""Add an unicode representation to an glyph
		
		Args:
			primary_codepoint (int) : The primary codepoint of the glyph
				to add a representation to
			codepoitn : The codepoint of the representation to add
		"""
		if codepoint in self.chars[primary_codepoint]:
			return
		self.chars[primary_codepoint].append(codepoint)
		iter = self.__get_iter_by_cp(primary_codepoint)
		uc = psflib.get_unicode_str(codepoint)
		self.model.append(iter, [self.clean_pixbuf, uc, str(codepoint)])
		if self.repr_added_callback:
			self.repr_added_callback(primary_codepoint, codepoint)
		
	def remove_glyph(self, primary_codepoint):
		"""Removes a glyhp
		
		Args:
			primary_codepoint (int) : The primary codepoint of the glyph		
		"""
		iter = self.__get_iter_by_cp(primary_codepoint)
		if iter:	
			self.model.remove(iter)
		del self.chars[primary_codepoint]
		
		to_select = self.model.get_iter_first()
		if to_select:
			self.selection.select_iter(to_select)
			
	def remove_repr(self, primary_codepoint, codepoint):
		"""Remove an unicode representation from a glyph
		
		Args:
			primary_codepoint (int) : The primary codepoint of the glyph
				to remove a representation from
			codepoint (int) : The codepoint of the representation
		"""
		iter = self.__get_iter_by_cp(primary_codepoint)
		child = self.model.iter_children(iter)
		self.chars[primary_codepoint].remove(codepoint)
		while child:
			child_cp = int(self.model.get(child, 2)[0])
			if child_cp == codepoint:
				self.model.remove(child)
				break
			child = self.model.iter_next(child)
		to_select = self.__get_iter_by_cp(primary_codepoint)
		if to_select:
			self.selection.select_iter(to_select)
		if self.repr_removed_callback:
			self.repr_removed_callback(primary_codepoint, codepoint)
		
	def update_pixbuf(self, primary_codepoint, pixbuf):
		"""Update the pixbuf of a glyph in the treeview
		
		Args:
			primary_codepoint (int) : The primary codepoint of the glyph
				which pixbuf should be updated
			pixbuf (GdkPixbuf.Pixbuf) : The new pixbuf of the glyph
		"""
		iter = self.__get_iter_by_cp(primary_codepoint)
		if iter:
			pixbuf = pixbuf.scale_simple(self.char_display_size[0],
						self.char_display_size[1],
						GdkPixbuf.InterpType.NEAREST)
			self.model.set_value(iter, 0, pixbuf)
		
	def has_glyph(self, primary_codepoint):
		"""Test if a glyph with the given primary codepoint already
		exists
		
		Returns:
			bool : True if there is already a glyph with the given
				primary codepoint else false
		"""
		return primary_codepoint in self.chars.keys()
		
	def get_new_id(self):
		"""Return a new codepoint which is not yet associated to a glyph
		
		Returns:
			int : codepoint which is not yet associated to a glyph
		"""
		values = []
		for reprs in self.chars.values():
			for _repr in reprs:
				if _repr not in values:
					values.append(_repr)
		for value in values:
			if value-1 not in values and value > 1:
				return value - 1
			if value+1 not in values:
				return value + 1
		return 0
	
	def set_changed_callback(self, callback):
		"""Sets a callback that gets called, when a new glyph has been
		selected
		
		Args:
			callback (callable) : The callback to call when a new glyph
			has been selected
		
		Arguments passed to the callback:
			-> the primary codepoint of the newly selected char
		"""
		self.changed_callback = callback
		
	def set_edited_callback(self, callback):
		"""Sets a callback that gets called, when the unicode
		information of a glyph has been edited
		
		Args:
			callback (callable) : The callback to call when the unicode
				value of a glyph has been edited
		
	    Arguments passed to the callback:
			-> the primary codepoint of the char
			-> the old unicode representation
			-> the new unicode representation
		"""
		self.edited_callback = callback
		
	def set_repr_added_callback(self, callback):
		"""Sets a callback that gets called when a unicode
		representation is added to a glyph.
		
		Args:
			callback (callable) : The callback to call when a new
				representation has been added to a glyph
		
		Arguments passed to the callback:
			-> the primary codepoint of the glyph
			-> the codepoint of the newly added representation
		"""
		self.repr_added_callback = callback
		
	def set_repr_removed_callback(self, callback):
		"""Sets a callback that gets called when a unicode
		representation is removed from a glyph.
		
		Args:
			callback (callable) : The callback to call when a 
				representation has been removed from a glyph
		
		Arguments passed to the callback:
			-> the primary codepoint of the glyph
			-> the codepoint of the removed representation
		"""
		self.repr_removed_callback = callback
				
	def get_selected_id(self):
		"""Returns the primary codepoint of the currently selected glyph
		
		Returns:
			int : The primary codepoint of the currently selected glyph
		"""
		model, iter = self.selection.get_selected()
		if iter:
			return int(model.get_value(iter, 2))
		return None
		
	def __get_iter_by_cp(self, primary_codepoint):
		"""Get a structure for accessing a row in the treemodel by the
		primary codepoint of the glyph in the row
		
		Args:
			primary_codepoint (int) : The primary codepoint of the glyph
				in the row
				
		Returns
			Gtk.TreeIter : Structure for accessing the row in the
				treemodel	
			None : If there is no glyph with the given primary codepoint	
		"""
		iter = self.model.get_iter_first()
		while iter:
			if int(self.model.get(iter, 2)[0]) == primary_codepoint:
				return iter
			iter = self.model.iter_next(iter)
		return None
		
		
	def __on_selection_changed(self, treeselection):
		"""This method is called when a new row in the treeview is
		selected
		
		Args:
			treeselection (Gtk.TreeSelection) : The treeselection
				associated with the treeview
		
		"""
		model, treepaths = treeselection.get_selected_rows()
		for path in treepaths:
			iter = model.get_iter(path)
			
			while iter:
				char_id = model.get_value(iter, 2)
				iter = self.model.iter_parent(iter)
		
			if self.changed_callback:
				self.changed_callback(int(char_id))
		
	def __on_codepoint_edited(self, cellrenderer, path, new_cp_str):
		"""This method is called when a codepoint in the treeview has
		been edited
		
		Args:
			cellrenderer (Gtk.CellRendererText) : The renderer of the
				edited cell
			path (Gtk.TreePath) : The path of the row in the treeview
			new_cp_str (str) : A string which contains the new codepoint
		"""
		iter = self.model.get_iter(path)
		try:
			old_codepoint = int(self.model.get(iter, 2)[0])
			new_codepoint = int(new_cp_str)
		except ValueError:
			return
		if old_codepoint == new_codepoint:
			return
		self.__update_glyph_repr(iter, old_codepoint,
				new_codepoint)
			
	def __on_unicode_edited(self, cellrenderer, path, new_uc):
		"""This method is called when an unicode value in the treeview
		has been edited
		
		Args:
			cellrenderer (Gtk.CellRendererText) : The renderer of the
				edited cell
			path (Gtk.TreePath) : The path of the row in the treeview
			new_uc (str) : The new unicode representation as string
		
		"""
		iter = self.model.get_iter(path)
		old_codepoint = int(self.model.get(iter, 2)[0])
		new_codepoint = psflib.get_codepoint(new_uc)
		if not new_codepoint:
			return
		self.__update_glyph_repr(iter, old_codepoint,
				new_codepoint)
			
	def __update_glyph_repr(self, iter, old_codepoint,
			new_codepoint):
		"""This method updates a representation of a glyph.
		
		Args:
			iter (Gtk.TreeIter) : The structure for accessing the row
				of the representation
			old_codepoint (int) : The old codepoint of the
				representation
			new_codepoint (int) : The new codepoint of the
				representation
		"""
		new_uc = psflib.get_unicode_str(new_codepoint)
		parent_iter = self.model.iter_parent(iter)
		if parent_iter:
			# Additional representation
			primary_codepoint = int(self.model.get(parent_iter, 2)[0])
			if new_codepoint in self.chars[primary_codepoint]:
				return
			self.chars[primary_codepoint].remove(old_codepoint)
			self.chars[primary_codepoint].append(new_codepoint)
			if old_codepoint == primary_codepoint:
				self.chars[new_codepoint] = self.chars[old_codepoint]
				del self.chars[old_codepoint]
				parent_uc = psflib.get_unicode_str(new_codepoint)
				self.model.set_value(parent_iter, 1, parent_uc)
				self.model.set_value(parent_iter, 2, str(new_codepoint))
				
		else:
			# Primary representation
			if new_codepoint in self.chars.keys():
				return
			primary_codepoint = old_codepoint
			self.chars[new_codepoint] = self.chars[old_codepoint]
			del self.chars[old_codepoint]
			child = self.model.iter_children(iter)
			child_old_cp = None
			child_new_cp = None
			while child:
				child_cp = int(self.model.get(child, 2)[0])
				if child_cp == old_codepoint:
					child_old_cp = child
				elif child_cp == new_codepoint:
					child_new_cp = child
				child = self.model.iter_next(child)
			if not child_new_cp:
				self.model.set_value(child_old_cp, 1, new_uc)
				self.model.set_value(child_old_cp, 2,
					str(new_codepoint))
				self.chars[new_codepoint].remove(old_codepoint)
				self.chars[new_codepoint].append(new_codepoint)
					
		self.model.set_value(iter, 1, new_uc)
		self.model.set_value(iter, 2, str(new_codepoint))
		if self.edited_callback:
			self.edited_callback(primary_codepoint, old_codepoint,
					new_codepoint)

	def __load_font_data(self, font):
		"""Load glyphs and their unicode representations from a
		PcScreenFont.
		
		Args:
			font (PcScreenFont): The font to laod glyphs and unicode
				representations from.
		"""
		for pc, glyph in font.get_glyphs().items():
			pixbuf = self.__pixbuf_from_glyph(glyph)
			self.add_glyph(pc, pixbuf)
			for cp in glyph.get_unicode_representations():
				self.add_repr(pc, cp)
		to_select = self.model.get_iter_first()
		if to_select:
			self.selection.select_iter(to_select)
			
	def __pixbuf_from_glyph(self, glyph):
		size = glyph.get_size()
		img = Image.new('RGBA', size, (0,0,0,0))
		draw = ImageDraw.Draw(img)
		for y, row in zip(range(size[1]),
								glyph.get_data()):
			for x, pixel in zip(range(size[0]), row):
				if pixel == 1:
					draw.point((x, y), (0,0,0,255))
		data = img.tobytes()
		w, h = img.size
		data = GLib.Bytes.new(data)		
		pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(data,
					GdkPixbuf.Colorspace.RGB, True, 8, w, h, w * 4)
		return pixbuf
			
	def __on_treeview_clicked_event(self, treeview, event):
		"""This method is called, when the user does a right click
		at the tree view.
		
		Args:
			treeview (Gtk.TreeView) : The treeview on which the right
				click occured
			event (Gdk.Event) : The event of the click
		"""
		if event.button == 3:
			data = treeview.get_path_at_pos(int(event.x), int(event.y))
			if data: #and event.type == Gdk.EventType._2BUTTON_PRESS:
				path, column, x, y = data
				iter = self.model.get_iter(path)
				
				menu = Gtk.Menu()
				
				parent_iter = self.model.iter_parent(iter)
				if parent_iter:
					# Addtional representation
					parent_cp = int(self.model.get(parent_iter, 2)[0])
					cp = int(self.model.get(iter, 2)[0])
					menu_add_repr = Gtk.MenuItem(
						"Add Unicode Representation")
					menu_add_repr.connect("activate",
						self.__on_add_representation_clicked, parent_cp)
					menu_rm_repr = Gtk.MenuItem(
						"Remove Unicode Representation")
					menu_rm_repr.connect("activate",
						self.__on_remove_representation_clicked,
						parent_cp, cp)
					menu.append(menu_add_repr)
					menu.append(menu_rm_repr)
				else:
					# Primary representation
					menu_add_repr = Gtk.MenuItem(
						"Add Unicode Representation")
					menu_add_repr.connect("activate",
						self.__on_add_representation_clicked, 
						int(self.model.get(iter, 2)[0]))
					menu.append(menu_add_repr)
					
				menu.show_all()
				menu.popup(None, None, None, self, 3, event.time)

	def __on_add_representation_clicked(self, menuitem, codepoint):
		"""This method is called when the user requested to add an
		unicode representation to an glyph.
		
		It gives the user an dialog to enter the new unicode
		representation
		
		Args:
			menuitem (Gtk.MenuItem) : The menu item which generated
				this call
			codepoint (int) : The codepoint of the glyph to add a
				representation to.
		"""
		d = NewUnicodeRepresentationDialog(self.get_toplevel(),
				codepoint)
		r = d.run()
		if r == Gtk.ResponseType.OK:
			cp = d.get_codepoint()
			self.add_repr(codepoint, cp)
		d.destroy()
		
	def __on_remove_representation_clicked(self, menuitem, primary_cp,
			codepoint):
		"""This method is called when the user requested the removal
		of an unicode representation of a glyph.
		
		It asks the user if to confirm the removal and removes the 
		representation if necessary.
		
		Args:
			menuitem (Gtk.MenuItem) : The menu item which generated this
				call
			primary_cp (int) : The primary codepoint of the glyph  to
				remove an unicode representation from
			codepoint (int) : The codepoint to remove from the glyph
		"""	
		if codepoint == primary_cp:
			dialog = Gtk.MessageDialog(self.get_toplevel(), 0,
						Gtk.MessageType.INFO, Gtk.ButtonsType.OK,
						"Confirmation")
			dialog.format_secondary_text(
				"You cannot remove this representation, because it is "+
				"the primary representation for this glyph")
			dialog.run()
			dialog.destroy()
			return
		
		dialog = Gtk.MessageDialog(self.get_toplevel(), 0,
					Gtk.MessageType.QUESTION, (Gtk.STOCK_OK,
					Gtk.ResponseType.OK, Gtk.STOCK_CANCEL,
					Gtk.ResponseType.CANCEL), "Confirmation")
		dialog.format_secondary_text("Please confirm, that you want "+
					"to remove this additional unicode representation")		
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			self.remove_repr(primary_cp, codepoint)
		dialog.destroy()

if __name__ == "__main__":
	window = PySFeditWindow()
	window.show_all()
	Gtk.main()

