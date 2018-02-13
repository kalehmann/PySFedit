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
This module tests the ByteArray class of the psflib.
"""

import unittest
import psflib

BITS = [1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0]   

class TestByteArray(unittest.TestCase):
	
	def test_from_bits(self):
		ba = psflib.ByteArray.from_bit_array(BITS)
		self.assertEqual(int(ba[0]), 255)
		self.assertEqual(int(ba[1]), 0)
		
		# Test with only 15 bits
		bits = BITS[1:]
		with self.assertRaises(ValueError):
			psflib.ByteArray.from_bit_array(bits)
			
	def test_initialisation(self):
		b1 = psflib.Byte()
	
		with self.assertRaises(TypeError):
			psflib.ByteArray([b1, object()])
			
	def test_from_int(self):
		ba = psflib.ByteArray.from_int(255)
		self.assertEqual(ba.to_asm(), "0xff\n")
		ba = psflib.ByteArray.from_int(65535)
		self.assertEqual(ba.to_asm(), "0xff, 0xff\n")
		ba = psflib.ByteArray.from_int(7 ** 30)
		self.assertEqual(ba.to_asm(), "0xd1, 0x00, 0x00, 0x00, 0xb3, 0xe1, 0xe1, 0x15, 0xe4, 0xa4, 0x12\n")
		ba = psflib.ByteArray.from_int(0xFFFFF, 2)
		self.assertEqual(ba.to_asm(), "0xff, 0xff\n")
		ba = psflib.ByteArray.from_int(16, 4)
		self.assertEqual(ba.to_asm(), "0x10, 0x00, 0x00, 0x00\n")

	def test_to_int(self):
		ba = psflib.ByteArray.from_int(256)
		self.assertEqual(int(ba), 256)
		ba = psflib.ByteArray.from_int(256289)
		self.assertEqual(int(ba), 256289)

	def test_addition(self):
		b = psflib.Byte.from_int
		ba1 = psflib.ByteArray([b(1), b(2)])
		ba2 = psflib.ByteArray([b(3), b(4)])
		
		self.assertEqual((ba1 + ba2).to_asm(), "0x01, 0x02, 0x03, 0x04\n")
		
		ba1 += ba2		
		self.assertEqual(ba1.to_asm(), "0x01, 0x02, 0x03, 0x04\n")
		
	def test_comparisation(self):
		b = psflib.Byte.from_int
		ba1 = psflib.ByteArray([b(1), b(2), b(3), b(4)])
		ba2 = psflib.ByteArray([b(1), b(2), b(3), b(4)])
		ba3 = psflib.ByteArray([b(1), b(2), b(3), b(4), b(5)])
		ba4 = object()
		
		self.assertEqual(ba1, ba2)
		self.assertNotEqual(ba1, ba3)
		self.assertNotEqual(ba1, ba4)

	def test_to_ints(self):
		b = psflib.Byte.from_int
		ba1 = psflib.ByteArray([b(1), b(2), b(3)])
		self.assertEqual(ba1.to_ints(), [1,2,3])
		
		ba2 = psflib.ByteArray([b(0xff), b(0x01), b(0x34), b(0x12)])
		self.assertEqual(ba2.to_ints(2), [0x1ff, 0x1234])
		
		with self.assertRaises(ValueError):
			ba2.to_ints(3)
			
	def test_from_bytes(self):
		_bytes = b"\x12\x34\x56\x78"
		
		ba = psflib.ByteArray.from_bytes(_bytes)
		
		self.assertEqual(ba.to_ints(), [0x12, 0x34, 0x56, 0x78])

	def test_to_bytearray(self):
		b = psflib.Byte.from_int
		
		ba = psflib.ByteArray([b(1), b(2), b(3), b(4)])
		
		ba = ba.to_bytearray()
		
		self.assertEqual(type(ba), bytearray)
		self.assertEqual(len(ba), 4)
		self.assertEqual(ba[0], 1)
		self.assertEqual(ba[1], 2)
		self.assertEqual(ba[2], 3)
		self.assertEqual(ba[3], 4)
		
	def test_to_asm(self):		
		ba = psflib.ByteArray.from_bytes(bytes(range(20)))
		
		ba_asm = (
"Test: db 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, " +
"0x09, 0x0a\n    db 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10, 0x11, " +
"0x12, 0x13\n"
		)
		
		self.assertEqual(ba.to_asm("Test"), ba_asm)
		
		ba_asm = (
"   Test: db 0x00, 0x01, 0x02, 0x03, 0x04, 0x05\n" + 
"      db 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b\n" +
"      db 0x0c, 0x0d, 0x0e, 0x0f, 0x10, 0x11\n" + 
"      db 0x12, 0x13\n"
		)
		
		self.assertEqual(ba.to_asm('Test', 50, 1, 3), ba_asm)
		
		ba_asm = (
"0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, " + 
"0x0b, 0x0c\n0x0d, 0x0e, 0x0f, 0x10, 0x11, 0x12, 0x13"		
		)

		self.assertEqual(ba.to_asm(end_with_linebreak=False), ba_asm)
