import unittest
import psflib

TEST_FONT_PSF1_SIMPLE = """
font_header:
magic_bytes: db 0x36, 0x04
charsize: db 0x08
mode: db 0x00
"""

TEST_FONT_PSF2_SIMPLE = """
font_header:
magic_bytes: db 0x72, 0xb5, 0x4a, 0x86
version: dd 0
headersize: dd 32
flags: dd 0
length: dd 0
charsize: dd 64
height: dd 8
width: dd 8
"""

class TestAsmImporter(unittest.TestCase):
	
	def test_parse_psf1(self):
		psflib.AsmImporter.import_string(TEST_FONT_PSF1_SIMPLE)

	def test_parse_psf2(self):
		psflib.AsmImporter.import_string(TEST_FONT_PSF2_SIMPLE)
