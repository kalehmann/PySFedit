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
This module tests the AsmImporter class of the psflib.
"""

import unittest
import sys
from os.path import dirname
import psflib

sys.path.append(dirname(__file__))

from data_for_testing import *

class TestAsmImporter(unittest.TestCase):
	
	def test_parse_psf1_simple(self):
		font = psflib.AsmImporter.import_from_data(
			TEST_FONT_PSF1_512_SIMPLE_ASM)
		
		self.assertFalse(font.has_unicode_table())
		self.assertEqual(len(font), 512)
		glyph, _ = font[0x41]
		self.assertEqual(
			glyph.get_data(),
			[
				[0,0,0,0,0,0,0,0],
				[0,0,1,1,1,0,0,0],
				[0,1,0,0,0,1,0,0],
				[0,1,0,0,0,1,0,0],
				[0,1,0,0,0,1,0,0],
				[0,1,0,0,0,1,0,0],
				[0,0,1,1,1,0,0,0],
				[0,0,0,0,0,0,0,0]
			]
		)
	
	def test_parse_psf1_unicode(self):
		font = psflib.AsmImporter.import_from_data(
			TEST_FONT_PSF1_256_UNICODE_ASM)
		
		self.assertTrue(font.has_unicode_table())
		self.assertEqual(len(font), 256)
		glyph, description = font[0]
		self.assertEqual(
			description.get_unicode_values(),
			[48, 79])

	def test_parse_psf2_simple(self):
		font = psflib.AsmImporter.import_from_data(
			TEST_FONT_PSF2_SIMPLE_ASM)
		
		self.assertEqual(len(font), 1)
		self.assertFalse(font.has_unicode_table())
		glyph, _ = font[0]
		self.assertEqual(
			glyph.get_data(),
			[
				[0,0,0,0,0,0,0,0,0,0],
				[0,0,0,0,0,0,0,1,0,0],
				[0,0,0,0,0,0,0,1,0,0],
				[0,0,0,0,0,0,0,1,0,0],
				[0,0,0,0,0,0,0,1,0,0],
				[0,0,0,0,0,0,0,1,0,0],
				[0,0,0,0,0,0,0,1,0,0],
				[0,0,0,0,0,0,0,0,0,0]
			]
		)
	
	def test_parse_psf2_unicode(self):
		font = psflib.AsmImporter.import_from_data(
			TEST_FONT_PSF2_UNICODE_ASM)
			
		self.assertEqual(len(font), 1)
		self.assertTrue(font.has_unicode_table())
		self.assertTrue(font.has_glyph_for_unicode_value(0x41))
		
		glyph, _ = font[0]
		
		self.assertEqual(
			glyph.get_data(),
			[
				[0,0,0,0,0,0,0,0,0,0],
				[0,0,0,0,0,0,0,1,0,0],
				[0,0,0,0,0,0,0,1,0,0],
				[0,0,0,0,0,0,0,1,0,0],
				[0,0,0,0,0,0,0,1,0,0],
				[0,0,0,0,0,0,0,1,0,0],
				[0,0,0,0,0,0,0,1,0,0],
				[0,0,0,0,0,0,0,0,0,0]
			]
		)
