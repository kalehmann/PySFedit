#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2018 by Karsten Lehmann <ka.lehmann@yahoo.com>

#	This file is part of PySFedit.
#
#	PySFedit is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
#	PySFedit is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
#	long with PySFedit. If not, see <http://www.gnu.org/licenses/>.

"""
This module tests all exporters of the psflib.
"""

import unittest
from ... import psflib
from .data_for_testing import *

class ExportersTest(unittest.TestCase):
	
	def test_exporting_psf_simple(self):
		to_test = [
			[psflib.AsmExporter, get_font_psf_512_simple_asm()],
			[psflib.PsfExporter, get_font_psf_512_simple()],
			[psflib.PsfGzExporter, get_font_psf_512_simple_compressed()]
		]
		
		for exporter, test_font in to_test:
			with self.subTest(exporter=exporter, test_font=test_font):
				header = psflib.PsfHeaderv1(test_font.get_charsize())
				header.set_mode(psflib.PSF1_MODE512)
								
				font = psflib.PcScreenFont(header)
				
				for glyph, i in zip(test_font.get_glyphs(),
									range(len(test_font))):
					real_glyph = font.get_glyph(i)
					real_glyph.set_data_from_bytes(glyph.bitmap)
				
				data = exporter(font).export_to_data()
				self.assertEqual(data, test_font.get_data())
	
	def test_exporting_psf_unicode(self):
		to_test = [
			[psflib.AsmExporter, get_font_psf_256_unicode_asm()],
			[psflib.PsfExporter, get_font_psf_256_unicode()],
			[psflib.PsfGzExporter,
				get_font_psf_256_unicode_compressed()]
		]
		
		for exporter, test_font in to_test:
			with self.subTest(exporter=exporter, test_font=test_font):
				header = psflib.PsfHeaderv1(test_font.get_charsize())
				header.set_mode(psflib.PSF1_MODEHASTAB)
								
				font = psflib.PcScreenFont(header)
				
				for glyph, i in zip(test_font.get_glyphs(),
									range(len(test_font))):
					real_glyph = font.get_glyph(i)
					real_glyph.set_data_from_bytes(glyph.bitmap)
					
					real_desc = font.get_unicode_description(i)
					for uv in glyph.unicode_values:
						real_desc.add_unicode_value(uv)
				
				data = exporter(font).export_to_data()
				self.assertEqual(data, test_font.get_data())

	def test_exporting_psf_sequences(self):		
		to_test = [
			[psflib.AsmExporter, get_font_psf_256_sequences_asm()],
			[psflib.PsfExporter, get_font_psf_256_sequences()],
			[psflib.PsfGzExporter,
				get_font_psf_256_sequences_compressed()]
		]
		
		for exporter, test_font in to_test:
			with self.subTest(exporter=exporter, test_font=test_font):
				header = psflib.PsfHeaderv1(test_font.get_charsize())
				header.set_mode(psflib.PSF1_MODEHASTAB)
								
				font = psflib.PcScreenFont(header)
				
				for glyph, i in zip(test_font.get_glyphs(),
									range(len(test_font))):
					real_glyph = font.get_glyph(i)
					real_glyph.set_data_from_bytes(glyph.bitmap)
					
					real_desc = font.get_unicode_description(i)
					for uv in glyph.unicode_values:
						real_desc.add_unicode_value(uv)
					if not glyph.sequences:
						
						continue
					for seq in glyph.sequences:
						real_desc.add_sequence(seq)
				
				data = exporter(font).export_to_data()
				self.assertEqual(data, test_font.get_data())
	
	def test_exporting_psf2_simple(self):
		to_test = [
			[psflib.AsmExporter, get_font_psf2_simple_asm()],
			[psflib.PsfExporter, get_font_psf2_simple()],
			[psflib.PsfGzExporter, get_font_psf2_simple_compressed()]
		]
		
		for exporter, test_font in to_test:
			with self.subTest(exporter=exporter, test_font=test_font):
				header = psflib.PsfHeaderv2(test_font.get_charsize())
								
				font = psflib.PcScreenFont(header)
				
				for glyph in test_font.get_glyphs():
					real_glyph, _ = font.add_glyph()
					real_glyph.set_data_from_bytes(glyph.bitmap)
				
				data = exporter(font).export_to_data()
				self.assertEqual(data, test_font.get_data())
	
	def test_exporting_psf2_unicode(self):
		to_test = [
			[psflib.AsmExporter, get_font_psf2_unicode_asm()],
			[psflib.PsfExporter, get_font_psf2_unicode()],
			[psflib.PsfGzExporter,
				get_font_psf2_unicode_compressed()]
		]
		
		for exporter, test_font in to_test:
			with self.subTest(exporter=exporter, test_font=test_font):
				header = psflib.PsfHeaderv2(test_font.get_charsize())
				header.set_flags(psflib.PSF2_HAS_UNICODE_TABLE)
								
				font = psflib.PcScreenFont(header)
				
				for glyph in test_font.get_glyphs():
					real_glyph, real_desc = font.add_glyph()
					real_glyph.set_data_from_bytes(glyph.bitmap)
					for uv in glyph.unicode_values:
						real_desc.add_unicode_value(uv)
				
				data = exporter(font).export_to_data()
				self.assertEqual(data, test_font.get_data())

	def test_exporting_psf2_sequences(self):
		to_test = [
			[psflib.AsmExporter, get_font_psf2_sequences_asm()],
			[psflib.PsfExporter, get_font_psf2_sequences()],
			[psflib.PsfGzExporter,
				get_font_psf2_sequences_compressed()]
		]
		
		for exporter, test_font in to_test:
			with self.subTest(exporter=exporter, test_font=test_font):
				header = psflib.PsfHeaderv2(test_font.get_charsize())
				header.set_flags(psflib.PSF2_HAS_UNICODE_TABLE)
								
				font = psflib.PcScreenFont(header)
				
				for glyph in test_font.get_glyphs():
					real_glyph, real_desc = font.add_glyph()
					real_glyph.set_data_from_bytes(glyph.bitmap)
					for uv in glyph.unicode_values:
						real_desc.add_unicode_value(uv)
					if not glyph.sequences:
						
						continue
					for seq in glyph.sequences:
						real_desc.add_sequence(seq)
				
				data = exporter(font).export_to_data()
				self.assertEqual(data, test_font.get_data())
