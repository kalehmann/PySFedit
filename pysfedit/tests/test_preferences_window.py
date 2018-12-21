#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2018 by Karsten Lehmann <mail@kalehmann.de>
#
#    This file is part of PySFedit.
#
#    PySFedit is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PySFedit is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    long with PySFedit. If not, see <http://www.gnu.org/licenses/>.


import unittest

from . import ChangedCallback
from .. import PreferencesWindow

from ..constants import Storage
from ..glyph_editor import GlyphEditorAttributes
from ..font_editor import GlyphSelectorContext

class PreferencesWindowTest(unittest.TestCase):
        def __init__(self, *args, **kwargs):
                super(PreferencesWindowTest, self).__init__(*args, **kwargs)
                self.window = None

        def setUp(self):
                self.window = PreferencesWindow()

        def test_glyph_editor_page(self):
                pixel_size_cc = ChangedCallback(self, "pixel_size", 15)
                pixel_margin_cc = ChangedCallback(self, "pixel_margin", 5)
                sep_lines_cc = ChangedCallback(self, "seperation_lines", False)

                s = Storage.get(GlyphEditorAttributes)
                s.register_changed_callback("seperation_lines", sep_lines_cc)
                s.register_changed_callback("pixel_size", pixel_size_cc)
                s.register_changed_callback("pixel_margin", pixel_margin_cc)

                page = self.window.page_glyph_editor

                page.seperation_lines.set_active(False)
                self.assertTrue(sep_lines_cc.called)

                page.spin_pixel_size.set_value(15)
                self.assertTrue(pixel_size_cc.called)

                page.spin_pixel_margin.set_value(5)
                self.assertTrue(pixel_margin_cc.called)

        def test_glyph_selector_page(self):
                page = self.window.page_glyph_selector
                page.spin_preview_size.set_value(32)
                page.glyph_indices.set_active(True)
                page.allow_sequences.set_active(False)

                prev_size_cc = ChangedCallback(self, "glyph_preview_size", 35)
                show_index_cc = ChangedCallback(self, "show_glyph_index", False)
                allow_seqs_cc = ChangedCallback(self,
                                                "allow_entering_sequences",
                                                True)

                s = Storage.get(GlyphSelectorContext)

                s.register_changed_callback("glyph_preview_size", prev_size_cc)
                s.register_changed_callback("show_glyph_index", show_index_cc)
                s.register_changed_callback("allow_entering_sequences",
                                                                        allow_seqs_cc)

                page.spin_preview_size.set_value(35)
                self.assertTrue(prev_size_cc.called)

                page.glyph_indices.set_active(False)
                self.assertTrue(show_index_cc.called)

                page.allow_sequences.set_active(True)
                self.assertTrue(allow_seqs_cc.called)

        def tearDown(self):
                self.window.destroy()
