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
This module tests all importers of the psflib.
"""

import unittest
import gzip
from ... import psflib
from .data_for_testing import *

class ImportersTest(unittest.TestCase):
	
	def test_importing_psf_simple(self):
		to_test = [
			[psflib.AsmImporter, get_font_psf_512_simple_asm()],
			[psflib.PsfImporter, get_font_psf_512_simple()],
			[psflib.PsfGzImporter, get_font_psf_512_simple_compressed()]
		]
		
		for importer, test_font in to_test:
			with self.subTest(importer=importer, test_font=test_font):
				font = importer.import_from_data(test_font.get_data())
								
				self.assertEqual(len(font), len(test_font))

				self.assertEqual(font.has_unicode_table(),
								 test_font.has_unicode_table())
				self.assertEqual(tuple(font.get_header().size),
								 test_font.get_charsize())
				
				for glyph in test_font.get_glyphs():
					real_glyph = font.get_glyph(glyph.unicode_values[0])
					self.assertEqual(real_glyph.to_bytearray(),
									 glyph.bitmap)
									 
	def test_importing_psf_unicode(self):
		to_test = [
			[psflib.AsmImporter, get_font_psf_256_unicode_asm()],
			[psflib.PsfImporter, get_font_psf_256_unicode()],
			[psflib.PsfGzImporter,
				get_font_psf_256_unicode_compressed()]
		]
		
		for importer, test_font in to_test:
			with self.subTest(importer=importer, test_font=test_font):
				font = importer.import_from_data(test_font.get_data())
				self.assertEqual(len(font), len(test_font))

				self.assertEqual(font.has_unicode_table(),
								 test_font.has_unicode_table())
				self.assertEqual(tuple(font.get_header().size),
								 test_font.get_charsize())
				
				for glyph, (real_glyph, description) in zip(
						test_font.get_glyphs(),
						font):
					self.assertEqual(real_glyph.to_bytearray(),
									 glyph.bitmap)
					self.assertEqual(
						list(description.get_unicode_values()),
						list(glyph.unicode_values)
					)
					
	def test_import_psf_sequences(self):
		to_test = [
			[psflib.AsmImporter, get_font_psf_256_sequences_asm()],
			[psflib.PsfImporter, get_font_psf_256_sequences()],
			[psflib.PsfGzImporter,
				get_font_psf_256_sequences_compressed()]
		]
		
		for importer, test_font in to_test:
			with self.subTest(importer=importer, test_font=test_font):
				font = importer.import_from_data(test_font.get_data())
				self.assertEqual(len(font), len(test_font))

				self.assertEqual(font.has_unicode_table(),
								 test_font.has_unicode_table())
				self.assertEqual(tuple(font.get_header().size),
								 test_font.get_charsize())
				
				for glyph, (real_glyph, description) in zip(
						test_font.get_glyphs(),
						font):
					self.assertEqual(real_glyph.to_bytearray(),
									 glyph.bitmap)
					self.assertEqual(
						list(description.get_unicode_values()),
						list(glyph.unicode_values)
					)
					if glyph.sequences:
						self.assertEqual(
							len(glyph.sequences),
							len(description.get_sequences())
						)
						for test_seq, real_seq in zip(
								glyph.sequences,
								description.get_sequences()):
							self.assertEqual(
								list(test_seq), list(real_seq)
							)

	def test_importing_psf2_simple(self):
		to_test = [
			[psflib.AsmImporter, get_font_psf2_simple_asm()],
			[psflib.PsfImporter, get_font_psf2_simple()],
			[psflib.PsfGzImporter,
				get_font_psf2_simple_compressed()]
		]

		for importer, test_font in to_test:
			with self.subTest(importer=importer, test_font=test_font):
				font = importer.import_from_data(test_font.get_data())
								
				self.assertEqual(len(font), len(test_font))

				self.assertEqual(font.has_unicode_table(),
								 test_font.has_unicode_table())
				self.assertEqual(tuple(font.get_header().size),
								 test_font.get_charsize())
				
				for glyph in test_font.get_glyphs():
					real_glyph = font.get_glyph(glyph.unicode_values[0])
					self.assertEqual(real_glyph.to_bytearray(),
									 glyph.bitmap)
	
	def test_importing_psf2_unicode(self):
		to_test = [
			[psflib.AsmImporter, get_font_psf2_unicode_asm()],
			[psflib.PsfImporter, get_font_psf2_unicode()],
			[psflib.PsfGzImporter,
				get_font_psf2_unicode_compressed()]
		]

		for importer, test_font in to_test:
			with self.subTest(importer=importer, test_font=test_font):
				font = importer.import_from_data(test_font.get_data())
				self.assertEqual(len(font), len(test_font))

				self.assertEqual(font.has_unicode_table(),
								 test_font.has_unicode_table())
				self.assertEqual(tuple(font.get_header().size),
								 test_font.get_charsize())
				
				for glyph, (real_glyph, description) in zip(
						test_font.get_glyphs(),
						font):
					self.assertEqual(real_glyph.to_bytearray(),
									 glyph.bitmap)
					self.assertEqual(
						list(description.get_unicode_values()),
						list(glyph.unicode_values)
					)
	
	def test_importing_psf2_sequences(self):
		to_test = [
			[psflib.AsmImporter, get_font_psf2_sequences_asm()],
			[psflib.PsfImporter, get_font_psf2_sequences()],
			[psflib.PsfGzImporter,
				get_font_psf2_sequences_compressed()]
		]
		
		for importer, test_font in to_test:
			with self.subTest(importer=importer, test_font=test_font):
				font = importer.import_from_data(test_font.get_data())
				self.assertEqual(len(font), len(test_font))

				self.assertEqual(font.has_unicode_table(),
								 test_font.has_unicode_table())
				self.assertEqual(tuple(font.get_header().size),
								 test_font.get_charsize())
				
				for glyph, (real_glyph, description) in zip(
						test_font.get_glyphs(),
						font):
					self.assertEqual(real_glyph.to_bytearray(),
									 glyph.bitmap)
					self.assertEqual(
						list(description.get_unicode_values()),
						list(glyph.unicode_values)
					)
					if glyph.sequences:
						self.assertEqual(
							len(glyph.sequences),
							len(description.get_sequences())
						)
						for test_seq, real_seq in zip(
								glyph.sequences,
								description.get_sequences()):
							self.assertEqual(
								list(test_seq), list(real_seq)
							)
