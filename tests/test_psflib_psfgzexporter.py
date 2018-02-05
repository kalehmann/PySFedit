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
This module tests the PsfGzExporter class of the psflib.
"""

import unittest
import psflib
import sys
import gzip
from os.path import dirname

sys.path.append(dirname(__file__))


from data_for_testing import *


class TestPsfExporter(unittest.TestCase):
	
	def test_export_psf_simple(self):
		header = psflib.PsfHeaderv1((8, 8))
		header.set_mode(psflib.PSF1_MODE512)
		font = psflib.PcScreenFont(header)
		glyph_0 = font.get_glyph(0)
		
		data_0 = bytearray(
			[0x00, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x00])
			
		glyph_0.set_data_from_bytes(psflib.ByteArray.from_bytes(data_0))
		
		exp = psflib.PsfGzExporter(font)
		data = exp.export_to_data()
		
		compressed_data = gzip.compress(TEST_FONT_PSF1_512_SIMPLE)
		self.assertEqual(data, compressed_data)
		
	def test_export_psf_unicode(self):
		header = psflib.PsfHeaderv1((8, 8))
		header.set_mode(psflib.PSF1_MODEHASTAB)
		font = psflib.PcScreenFont(header)
		glyph_A, ud = font[0]
		ud.add_unicode_value(0x41)
		
		data_A = bytearray(
			[0x00, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x00])
			
		glyph_A.set_data_from_bytes(psflib.ByteArray.from_bytes(data_A))
		
		exp = psflib.PsfGzExporter(font)
		data = exp.export_to_data()
		
		compressed_data = gzip.compress(TEST_FONT_PSF1_256_UNICODE)
		self.assertEqual(data, compressed_data)
	
	def test_export_psf2_simple(self):
		header = psflib.PsfHeaderv2((10, 8))
		font = psflib.PcScreenFont(header)
		
		glyph_0, _ = font.add_glyph()
		glyph_1, _ = font.add_glyph()
		
		data_0 = bytearray([
			0x00, 0x00,
			0x00, 0x00,
			0x00, 0x00,
			0x00, 0x00,
			0x00, 0x00,
			0x00, 0x00,
			0x00, 0x00,
			0x00, 0x00,
		])
		data_1 = bytearray([
			0x00, 0x00,
			0x01, 0x00,
			0x01, 0x00,
			0x01, 0x00,
			0x01, 0x00,
			0x01, 0x00,
			0x01, 0x00,
			0x00, 0x00,
		])
		
		glyph_0.set_data_from_bytes(psflib.ByteArray.from_bytes(data_0))
		glyph_1.set_data_from_bytes(psflib.ByteArray.from_bytes(data_1))
	
		exp = psflib.PsfGzExporter(font)
		data = exp.export_to_data()
		
		compressed_data = gzip.compress(TEST_FONT_PSF2_SIMPLE)
		self.assertEqual(data, compressed_data)
	
	def test_export_psf2_unicode(self):
		header = psflib.PsfHeaderv2((10, 8))
		header.set_flags(psflib.PSF2_HAS_UNICODE_TABLE)
		
		font = psflib.PcScreenFont(header)
		
		glyph_A, udA = font.add_glyph()
		glyph_B, udB = font.add_glyph()
		
		udA.add_unicode_value(ord('A'))
		udB.add_unicode_value(ord('B'))
		
		data_A = bytearray([
			0x00, 0x00,
			0x00, 0x00,
			0x00, 0x00,
			0x00, 0x00,
			0x00, 0x00,
			0x00, 0x00,
			0x00, 0x00,
			0x00, 0x00,
		])
		data_B = bytearray([
			0x00, 0x00,
			0x01, 0x00,
			0x01, 0x00,
			0x01, 0x00,
			0x01, 0x00,
			0x01, 0x00,
			0x01, 0x00,
			0x00, 0x00,
		])
		
		glyph_A.set_data_from_bytes(data_A)
		glyph_B.set_data_from_bytes(data_B)
		
		exp = psflib.PsfGzExporter(font)
		data = exp.export_to_data()
		
		compressed_data = gzip.compress(TEST_FONT_PSF2_UNICODE)
		self.assertEqual(data, compressed_data)

