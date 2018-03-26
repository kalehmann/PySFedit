import unittest
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from . import MockedParent
from ..psflib import UnicodeDescription, UnicodeValue, UnicodeSequence
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
		desc.add_unicode_value(UnicodeValue(0x41))
		desc.add_sequence(
            UnicodeSequence([
                UnicodeValue(0x41),
                UnicodeValue(0x30a)
            ])
        )
		self.dialog = EditUnicodeDescriptionDialog(
			MockedParent(), desc, self.context)
	
	def test_adding_values(self):
		self.dialog.btn_add.clicked()
		self.dialog.entry_unicode.set_text("a")
		self.dialog.btn_save.clicked()
		self.dialog.response(Gtk.ResponseType.OK)
		
		self.assertIn(0x41, self.description.codepoints)
		self.assertIn(ord('a'), self.description.codepoints)
		self.assertIn([0x41, 0x30a], self.description.seq_codepoints)

	def test_removing_values(self):
		first_row = self.dialog.lb_descriptions.get_row_at_index(0)
		self.dialog.lb_descriptions.select_row(first_row)
		self.dialog.btn_remove.clicked()
		self.dialog.response(Gtk.ResponseType.OK)
		
		self.assertEqual(self.description.unicode_values, [])
		self.assertIn([0x41, 0x30a], self.description.seq_codepoints)

	def test_editing_value(self):
		first_row = self.dialog.lb_descriptions.get_row_at_index(0)
		self.dialog.lb_descriptions.select_row(first_row)
		self.dialog.entry_unicode.set_text("B")
		self.dialog.btn_save.clicked()
		self.dialog.response(Gtk.ResponseType.OK)

		self.assertIn(0x42, self.description.codepoints)
		self.assertIn([0x41, 0x30a], self.description.seq_codepoints)
		
	def test_editing_sequence(self):
		self.context.allow_sequences()
		
		second_row = self.dialog.lb_descriptions.get_row_at_index(2)
		self.dialog.lb_descriptions.select_row(second_row)
		self.dialog.nb_editor.set_current_page(self.dialog.PAGE_VALUES)
		self.dialog.entry_values.set_text(r"\u0042, \u030A")
		self.dialog.btn_save.clicked()
		self.dialog.response(Gtk.ResponseType.OK)

		self.assertIn(0x41, self.description.codepoints)
		self.assertIn([0x42, 0x30a], self.description.seq_codepoints)
		
	def test_abort_editing(self):
		first_row = self.dialog.lb_descriptions.get_row_at_index(0)
		self.dialog.lb_descriptions.select_row(first_row)
		self.dialog.entry_unicode.set_text("B")
		self.dialog.btn_save.clicked()
		self.dialog.response(Gtk.ResponseType.CANCEL)

		self.assertIn(0x41, self.description.codepoints)
		self.assertIn([0x41, 0x30a], self.description.seq_codepoints)

	def tearDown(self):
		self.dialog.destroy()

