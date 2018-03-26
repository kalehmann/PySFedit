import unittest
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GLib
from .. import PySFeditWindow

class StartApplicationTest(unittest.TestCase):
	def __init__(self, *args, **kwargs):
		super(StartApplicationTest, self).__init__(*args, **kwargs)
		self.window = None
		self.mainloop = None
	
	def setUp(self):
		self.mainloop = GLib.MainLoop()
		self.window = PySFeditWindow(self.mainloop)
		self.window.show_all()
	
	def test_start(self):
		self.assertIsNotNone(self.window.button_new)
		self.assertIsNotNone(self.window.button_import)
	
	def test_create_new_font(self):
		self.window.button_new
		
	def tearDown(self):
		self.window.destroy()
