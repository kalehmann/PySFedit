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
This modules tests the AsmExporter class of the psflib.
"""

import unittest
import sys
from os.path import dirname
import psflib

sys.path.append(dirname(__file__))

from data_for_testing import *

class TestAsmExporter(unittest.TestCase):
	
	def test_psf_512_simple(self):
		header = psflib.PsfHeaderv1((8,8))
		header.set_mode(psflib.PSF1_MODE512)
		
		font = psflib.PcScreenFont(header)
		
		glyph = font.get_glyph(0x41)
		
		b = psflib.Byte.from_int
		
		ba = psflib.ByteArray(
			[b(0), b(0x38), b(0x44), b(0x44), b(0x44), b(0x44), b(0x38),
			 b(0)])
		
		glyph.set_data_from_bytes(ba)
		
		exporter = psflib.AsmExporter(font)
		self.assertEqual(exporter.export_to_data(),
			TEST_FONT_PSF1_512_SIMPLE_ASM)
	
	def test_psf_256_unicode(self):
		header = psflib.PsfHeaderv1((8,8))
		header.set_mode(psflib.PSF1_MODEHASTAB)
		
		font = psflib.PcScreenFont(header)
		
		glyph, description = font[0]
		description.add_unicode_value(48)
		description.add_unicode_value(79)
		
		b = psflib.Byte.from_int
		
		ba = psflib.ByteArray(
			[b(0), b(0x38), b(0x44), b(0x44), b(0x44), b(0x44), b(0x38),
			 b(0)])
		
		glyph.set_data_from_bytes(ba)
		
		exporter = psflib.AsmExporter(font)

		self.assertEqual(exporter.export_to_data(),
			TEST_FONT_PSF1_256_UNICODE_ASM)
			
	def test_psf2_simple(self):
		header = psflib.PsfHeaderv2((10, 8))
		font = psflib.PcScreenFont(header)
		
		glyph, _ = font.add_glyph()
		
		glyph.set_data(
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
		
		exporter = psflib.AsmExporter(font)
		
		self.assertEqual(exporter.export_to_data(),
			TEST_FONT_PSF2_SIMPLE_ASM)
			
	def test_psf2_unicode(self):
		header = psflib.PsfHeaderv2((10, 8))
		header.set_flags(psflib.PSF2_HAS_UNICODE_TABLE)
		font = psflib.PcScreenFont(header)
		glyph, description = font.add_glyph()
		
		description.add_unicode_value(0x41)
		
		glyph.set_data(
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
		
		exporter = psflib.AsmExporter(font)
		
		self.assertEqual(exporter.export_to_data(),
			TEST_FONT_PSF2_UNICODE_ASM)
