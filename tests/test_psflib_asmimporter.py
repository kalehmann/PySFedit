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

	def test_parse_psf2(self):
		psflib.AsmImporter.import_from_data(TEST_FONT_PSF2_SIMPLE_ASM)
