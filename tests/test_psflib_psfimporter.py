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
		
		self.assertFalse(font.has_unicode())
		self.assertEqual(len(font.get_glyphs()), 512)
			
		data = [int(psflib.Byte(row))
			for row in font.get_glyph(0).get_data()]
				
		self.assertEqual(data,
			[0x00, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x00])
			
	def test_import_psf_unicode(self):
		font = psflib.PsfImporter.import_from_data(
			TEST_FONT_PSF1_256_UNICODE)
			
		self.assertTrue(font.has_unicode())
		self.assertEqual(len(font.get_glyphs()), 1)
		self.assertTrue(0x41 in font.get_glyphs())
		
		data = [int(psflib.Byte(row))
			for row in font.get_glyph(0x41).get_data()]
				
		self.assertEqual(data,
			[0x00, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x00])
	
	def test_import_psf2_simple(self):
		font = psflib.PsfImporter.import_from_data(TEST_FONT_PSF2_SIMPLE)
		
		self.assertFalse(font.has_unicode())
		self.assertEqual(len(font.get_glyphs()), 2)
		
		self.assertTrue(0 in font.get_glyphs())
		self.assertTrue(1 in font.get_glyphs())
		
		self.assertEqual(font.get_glyph(0).get_size(), (10, 8))
		self.assertEqual(6,
			sum([sum(row) for row in font.get_glyph(1).get_data()])) 
	
	def test_import_psf2_unicode(self):
		font = psflib.PsfImporter.import_from_data(TEST_FONT_PSF2_UNICODE)
		
		self.assertTrue(font.has_unicode())
		self.assertEqual(len(font.get_glyphs()), 2)
		
		self.assertTrue(ord('A') in font.get_glyphs())
		self.assertTrue(ord('B') in font.get_glyphs())
		
		glyph_A = font.get_glyph(ord('A'))
		glyph_B = font.get_glyph(ord('B'))
		
		self.assertEqual(glyph_A.get_size(), (10, 8))
		
		self.assertEqual(6, sum([sum(row) for row in glyph_B.get_data()]))
