import unittest
import psflib

TEST_STRING_SIMPLE = """
test1:  db 0x01, 0x02
		db 0x01, 0x02
test2: db 0x03, 0x04
"""

class TestAsmParser(unittest.TestCase):
	
	def test_standard(self):
		ap = psflib.AsmParser(TEST_STRING_SIMPLE)
		
