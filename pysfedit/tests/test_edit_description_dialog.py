import unittest
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from . import MockedParent
from ..psflib import UnicodeDescription
from ..edit_description_dialog import EditUnicodeDescriptionDialog

class EditDescriptionDialogTest(unittest.TestCase):
	
	class MockedGlyphSelectorContext(object):
		def __init__(self):
			self._allow_sequences = False
		
		def allow_sequences(self):
			self._allow_sequences = True	
		
		def get_allow_entering_sequences(self):
			return self._allow_sequences
	
	def __init__(self, *args, **kwargs):
		super(EditDescriptionDialogTest, self).__init__(*args, **kwargs)
		self.description = None
		self.dialog = None

	def setUp(self):
		self.description = desc = UnicodeDescription()
		self.context = self.MockedGlyphSelectorContext()
		desc.add_unicode_value(0x41)
		desc.add_sequence((0x30a, 0x41))
		self.dialog = EditUnicodeDescriptionDialog(
			MockedParent(), desc, self.context)
		
	def test_adding_values(self):
		self.dialog.btn_add.clicked()
		self.dialog.entry_unicode.set_text("a")
		self.dialog.btn_save.clicked()
		self.dialog.response(Gtk.ResponseType.OK)
		
		self.assertIn(0x41, self.description.get_unicode_values())
		self.assertIn(ord('a'), self.description.get_unicode_values())
		self.assertIn((0x30a, 0x41), self.description.get_sequences())
				
	def tearDown(self):
		self.dialog.destroy()

