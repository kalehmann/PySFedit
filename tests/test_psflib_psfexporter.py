import unittest
import psflib
import sys
from os.path import dirname

sys.path.append(dirname(__file__))


from data_for_testing import *


class TestPsfExporter(unittest.TestCase):
	
	def test_export_psf2_unicode(self):
		header = psflib.PsfHeaderv2((10,8))
		header.set_flags(psflib.PSF2_HAS_UNICODE_TABLE)
		
		font = psflib.PcScreenFont(header)
		
		glyph_A = font.get_glyph(ord('A'))
		glyph_B = font.get_glyph(ord('B'))
		
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
		
		glyph_A.set_data_from_bytes(psflib.ByteArray.from_bytes(data_A))
		glyph_B.set_data_from_bytes(psflib.ByteArray.from_bytes(data_B))
		
		exp = psflib.PsfExporter(font)
		data = exp.export_bytearray()
		
		self.assertEqual(data, TEST_FONT_PSF2_UNICODE)
