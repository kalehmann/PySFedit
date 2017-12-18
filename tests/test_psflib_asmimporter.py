import unittest
import psflib

TEST_FONT_PSF1_SIMPLE = """
font_header:
magic_bytes: db 0x36, 0x04
charsize: db 0x08
mode: db 0x00
"""

class TestAsmImporter(unittest.TestCase):
	
	def test_parse_psf1(self):
		psflib.AsmImporter.import_string(TEST_FONT_PSF1_SIMPLE)
