import unittest
import sys
from os.path import dirname
import psflib

sys.path.append(dirname(__file__))

from data_for_testing import *

class TestAsmImporter(unittest.TestCase):
	
	def test_parse_psf1(self):
		font = psflib.AsmImporter.import_from_data(
			TEST_FONT_PSF1_256_UNICODE_ASM)
		
		self.assertTrue(font.has_unicode())
		self.assertEqual(len(font.get_glyphs()), 1)
		self.assertEqual(
			font.get_glyphs()[48].get_unicode_representations(),
			[48, 79])

	def test_parse_psf2_simple(self):
		font = psflib.AsmImporter.import_from_data(
			TEST_FONT_PSF2_SIMPLE_ASM)
		
		self.assertEqual(len(font.get_glyphs()), 1)
		self.assertFalse(font.has_unicode())
		self.assertEqual(
			font.get_glyphs()[0].get_data(),
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
			
		self.assertEqual(len(font.get_glyphs()), 1)
		self.assertTrue(font.has_unicode())
		self.assertTrue(0x41 in font.get_glyphs())
		
		self.assertEqual(
			font.get_glyphs()[0x41].get_data(),
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
