import unittest
from ..psflib import PsfHeaderv2, PcScreenFont
from ..font_editor import FontEditor

class FontEditorTest(unittest.TestCase):
	def __init__(self, *args, **kwargs):
		super(FontEditorTest, self).__init__(*args, **kwargs)
		self.header = None
		self.font = None
		self.font_editor = None
		
	def setUp(self):
		self.header = PsfHeaderv2((8, 8))
		self.header.set_length(2)
		self.font = PcScreenFont(self.header)
		for i in range(2):
			glyph, desc = self.font.add_glyph()
		self.font_editor = psflib.FontEditor(self.header)
		
	def test_add_glyph(self):
		pass
		
	def tearDown(self):
		self.font_editor.destroy()
