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
This module tests the PsfImporter class of the psflib.
"""

import unittest
import psflib
import sys
from os.path import dirname

sys.path.append(dirname(__file__))


from data_for_testing import *


class TestPsfImporter(unittest.TestCase):
	
	def test_import_psf_simple(self):
		font = psflib.PsfImporter.import_from_data(
			TEST_FONT_PSF1_512_SIMPLE)
		
		self.assertFalse(font.has_unicode_table())
		self.assertEqual(len(font), 512)
			
		data = [int(psflib.Byte(row))
			for row in font.get_glyph(0).get_data()]
				
		self.assertEqual(data,
			[0x00, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x00])
			
	def test_import_psf_unicode(self):
		font = psflib.PsfImporter.import_from_data(
			TEST_FONT_PSF1_256_UNICODE)
			
		self.assertTrue(font.has_unicode_table())
		self.assertEqual(len(font), 256)
		
		glyph = font.get_glyph_for_unicode_value(0x41)
		data = [int(psflib.Byte(row)) for row in glyph.get_data()]
				
		self.assertEqual(data,
			[0x00, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x00])
	
	def test_import_psf_sequences(self):
		font = psflib.PsfImporter.import_from_data(
			TEST_FONT_PSF1_256_SEQUENCES)
		
		self.assertTrue(font.has_unicode_table())
		self.assertEqual(len(font), 256)
		
		glyph = font.get_glyph_for_unicode_value(0x41)
		index = font.get_glyph_index(glyph)
		
		_, ud = font[index]
		
		self.assertEqual(
			ud.get_sequences(),
			[[0x41, 0x30A]]
		)
		
		data = [int(psflib.Byte(row)) for row in glyph.get_data()]
				
		self.assertEqual(data,
			[0x00, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x00])
		
	
	def test_import_psf2_simple(self):
		font = psflib.PsfImporter.import_from_data(TEST_FONT_PSF2_SIMPLE)
		
		self.assertFalse(font.has_unicode_table())
		self.assertEqual(len(font), 2)
		
		self.assertTrue(font.has_glyph_for_unicode_value(0))
		self.assertTrue(font.has_glyph_for_unicode_value(1))
		
		self.assertEqual(font.get_glyph(0).get_size(), (10, 8))
		self.assertEqual(6,
			sum([sum(row) for row in font.get_glyph(1).get_data()])) 
	
	def test_import_psf2_unicode(self):
		font = psflib.PsfImporter.import_from_data(TEST_FONT_PSF2_UNICODE)
		
		self.assertTrue(font.has_unicode_table())
		self.assertEqual(len(font), 2)
		
		self.assertTrue(font.has_glyph_for_unicode_value(ord('A')))
		self.assertTrue(font.has_glyph_for_unicode_value(ord('B')))
		
		glyph_A = font.get_glyph_for_unicode_value(ord('A'))
		glyph_B = font.get_glyph_for_unicode_value(ord('B'))
		
		self.assertEqual(glyph_A.get_size(), (10, 8))
		
		self.assertEqual(6, sum([sum(row) for row in glyph_B.get_data()]))
