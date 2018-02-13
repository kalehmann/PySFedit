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
This module tests the Byte class of the psflib.
"""

import unittest
import psflib

class TestByte(unittest.TestCase):
	
	def test_from_integer(self):
		byte = psflib.Byte.from_int(8)
		for i, j in zip(byte, [0,0,0,0,1,0,0,0]):
			self.assertEqual(i, j)
			
		byte2 = psflib.Byte.from_int(257)
		self.assertEqual(int(byte2), 1)

	def test_get_item(self):
		byte = psflib.Byte.from_int(18)
		self.assertEqual(byte[0], 0)
		self.assertEqual(byte[3], 1)
		self.assertEqual(byte[6], 1)
		
		with self.assertRaises(IndexError):
			byte[8]
		
	def test_set_item(self):
		byte = psflib.Byte()
		byte[0] = 1
		self.assertEqual(int(byte), 128)
		with self.assertRaises(ValueError):
			byte[2] = 2
			
		with self.assertRaises(IndexError):
			byte[8] = 0

	def test_hex(self):
		byte = psflib.Byte.from_int(32)
		self.assertEqual(byte.hex(), '0x20')
		byte2 = psflib.Byte.from_int(11)
		self.assertEqual(byte2.hex(), '0x0b')
		self.assertEqual(str(byte2), '0x0b')
		
	def test_bool(self):
		byte = psflib.Byte()
		self.assertEqual(bool(byte), False)
		byte2 = psflib.Byte.from_int(1)
		self.assertEqual(bool(byte2), True)
		
	def test_comparisation(self):
		byte = psflib.Byte([0,0,1,0,1,0,1,0])
		self.assertTrue(byte > 41)
		self.assertTrue(byte < 43)
		self.assertTrue(byte == 42.0)
		self.assertTrue(byte >= 42)
		self.assertTrue(byte >= 41)
		self.assertTrue(byte <= 42)
		self.assertTrue(byte <= 43)
		self.assertTrue(byte != 43)
		
	def test_binary_operations(self):
		byte = psflib.Byte.from_int(6)
		self.assertEqual(byte & 4, 4)
		self.assertEqual(byte & 1, 0)
		self.assertEqual(byte | 1, 7)
		self.assertEqual(byte ^ 255, 249)
