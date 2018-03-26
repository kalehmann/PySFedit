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
                self.font = PcScreenFont(self.header)
                for i in range(5):
                        glyph, desc = self.font.add_glyph()
                self.font_editor = FontEditor(self.header, self.font)
                
        def test_add_glyph(self):
                self.font_editor.button_add.clicked()

                self.assertEqual(len(self.font), 6)

        def test_remove_glyph(self):
                row = self.font_editor.glyph_selector.get_row_at_index(0)
                self.font_editor.glyph_selector.select_row(row)
                self.font_editor.button_remove.clicked()

                self.assertEqual(len(self.font), 4)

        def test_glyph_show_index(self):
                glyph_selector = self.font_editor.glyph_selector
                context = glyph_selector.context
                context.set_show_glyph_index(True)
                row = glyph_selector.get_row_at_index(0)
                self.assertEqual(row.l_index.get_text(), '0')

                context.set_show_glyph_index(False)
                self.assertEqual(row.l_index.get_text(), '')

        def test_cut_copy_paste_glyph(self):
                data1 = self.font.get_glyph(1).get_data()
                data1[0][0] = 1
                glyph_selector = self.font_editor.glyph_selector
                row = glyph_selector.get_row_at_index(1)
                glyph_selector.select_row(row)
                self.font_editor.copy_current_bitmap_to_clipboard()
                
                row = glyph_selector.get_row_at_index(0)
                glyph_selector.select_row(row)
                self.font_editor.paste_bitmap_from_clipboard()
                data0 = self.font.get_glyph(0).get_data()
                self.assertEqual(data1, data0)

                self.font_editor.cut_current_bitmap_to_clipboard()
                self.assertEqual(data0, [[0 for _ in range(8)] for i in range(8)])

                row = glyph_selector.get_row_at_index(2)
                glyph_selector.select_row(row)
                self.font_editor.paste_bitmap_from_clipboard()
                data2 = self.font.get_glyph(2).get_data()
                self.assertEqual(data1, data2)
                
        def tearDown(self):
                self.font_editor.destroy()
