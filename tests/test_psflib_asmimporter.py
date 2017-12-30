import unittest
import sys
from os.path import dirname
import psflib

sys.path.append(dirname(__file__))

from data_for_testing import *

TEST_FONT_PSF2_SIMPLE = """
font_header:
magic_bytes: db 0x72, 0xb5, 0x4a, 0x86
version: dd 0x0
headersize: dd 0x20
flags: dd 0x0
length: dd 0x1
charsize: dd 0x8
height: dd 0x8
width: dd 0x8

font_bitmaps:
glyph_0: db 0x00, 0x38, 0x44, 0x44, 0x44, 0x44, 0x38, 0x00
"""

class TestAsmImporter(unittest.TestCase):
	
	def test_parse_psf1(self):
		font = psflib.AsmImporter.import_from_data(
			TEST_FONT_PSF1_256_UNICODE)
		
		self.assertTrue(font.has_unicode())
		self.assertEqual(len(font.get_glyphs()), 1)
		self.assertEqual(
			font.get_glyphs()[48].get_unicode_representations(),
			[48, 79])

	def test_parse_psf2(self):
		psflib.AsmImporter.import_from_data(TEST_FONT_PSF2_SIMPLE)
