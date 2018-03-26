import unittest
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GLib
from .. import NewFontDialog
from . import MockedParent

class NewFontDialogTest(unittest.TestCase):
	def __init__(self, *args, **kwargs):
		super(NewFontDialogTest, self).__init__(*args, **kwargs)
		self.dialog = None
	
	def setUp(self):
		parent = MockedParent()
		self.dialog = NewFontDialog(parent)
	
	def test_create_psf_256(self):
		self.dialog.entry_height.set_text("12")
		self.dialog.btn_unicode_psf1.set_active(True)
		
		header = self.dialog.get_header()
		self.assertEqual(header.size, (8, 12))
		self.assertTrue(header.has_unicode_table())
	
	def test_create_psf_512(self):
		self.dialog.rb512.set_active(True)
		
		header = self.dialog.get_header()
		self.assertEqual(header.get_length(), 512)
	
	def test_create_psf2(self):
		self.dialog.entry_width.set_text("12")
		self.dialog.entry_height.set_text("10")
		self.dialog.notebook.set_current_page(1)
		
		header = self.dialog.get_header()
		self.assertEqual(header.size, (12, 10))
		self.assertFalse(header.has_unicode_table())
		
	def tearDown(self):
		self.dialog.destroy()
