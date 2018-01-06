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
		
		glyph = font.get_glyph(48)
		glyph.add_unicode_representation(79)
		
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
		
		glyph = font.get_glyph(0)
		
		glyph.copy_data(
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
		
		glyph = font.get_glyph(0x41)
		
		glyph.copy_data(
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
