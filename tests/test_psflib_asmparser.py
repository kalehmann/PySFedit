#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2018 by Karsten Lehmann <ka.lehmann@yahoo.com>

#	This file is part of PySFedit.
#
#	PySFedit is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
#	PySFedit is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
#	long with PySFedit. If not, see <http://www.gnu.org/licenses/>.

"""
This module tests the AsmParser of the psflib.
"""

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
		self.assertTrue(ap.has_label('test2'))
		self.assertFalse(ap.has_label('test3'))
		
		
