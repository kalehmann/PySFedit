import unittest
import psflib

TEST_STRING_SIMPLE = """
test1:  db 0x10, 0x02, 0o30, 30o, 0q30, 030q
		db 10, 0b10
test2: db 0x03, 0x04
test_words2:
test_words: dw 0xff, 65535
"""

class TestAsmParser(unittest.TestCase):
	
	def test_standard(self):
		ap = psflib.AsmParser(TEST_STRING_SIMPLE)
		self.assertEqual(ap.test1.to_asm(),
			'0x10, 0x02, 0x18, 0x18, 0x18, 0x18, 0x0a, 0x02\n')
		self.assertEqual(ap.test2.to_asm(), '0x03, 0x04\n')
		self.assertEqual(ap.test_words.to_asm(),
			'0xff, 0x00, 0xff, 0xff\n')
		self.assertEqual(ap.test_words2.to_asm(),
			'0xff, 0x00, 0xff, 0xff\n')
		
		
