#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2018 by Karsten Lehmann <mail@kalehmann.de>
#
#    This file is part of PySFedit.
#
#    PySFedit is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PySFedit is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    long with PySFedit. If not, see <http://www.gnu.org/licenses/>.


"""
This module tests the UnicodeDescription, UnicodeSequence and UnicodeValues
classes of the psflib.
"""

import unittest
from ...psflib import UnicodeValue, UnicodeSequence, UnicodeDescription

class TestUnicodeDescription(unittest.TestCase):
    def test_value(self):
        value = UnicodeValue(0x61)

        self.assertEqual(str(value), 'a')
        self.assertEqual(int(value), 0x61)

        value2 = UnicodeValue.new_from_string('a')

        self.assertEqual(value, value2)

    def test_sequence(self):
        seq = UnicodeSequence([0x41, 0x30A])

        self.assertEqual(seq.codepoints, [0x41, 0x30A])

        uv = UnicodeValue

        self.assertEqual(seq, UnicodeSequence([uv(0x41), uv(0x30A)]))

    def test_description_add_value(self):
        description = UnicodeDescription()
        description.add_unicode_value(ord('a'))
        description.add_unicode_value(UnicodeValue.new_from_string('A'))

        self.assertEqual(description.codepoints, [ord('a'), ord('A')])

        description.add_unicode_value(ord('a'))
        self.assertEqual(description.codepoints, [ord('a'), ord('A')])

    def test_description_remove_value(self):
        description = UnicodeDescription()
        description.add_unicode_value(ord('a'))
        description.add_unicode_value(ord('b'))
        description.add_unicode_value(ord('c'))
        self.assertEqual(description.codepoints, [ord('a'), ord('b'), ord('c')])

        description.remove_unicode_value(ord('b'))
        self.assertEqual(description.codepoints, [ord('a'), ord('c')])

        description.remove_unicode_value(UnicodeValue(ord('a')))
        self.assertEqual(description.unicode_values[0], ord('c'))

    def test_description_add_sequence(self):
        seq1 = UnicodeSequence([1, 2, 3])
        seq2 = UnicodeSequence([4, 5, 6])

        desc = UnicodeDescription()
        desc.add_sequence(seq1)
        desc.add_sequence(seq1)
        self.assertEqual(len(desc.sequences), 1)

        desc.add_sequence(seq2)
        self.assertEqual(desc.seq_codepoints, [[1, 2, 3], [4, 5, 6]])

    def test_description_remove_sequence(self):
        seq1 = UnicodeSequence([1, 2, 3])
        seq2 = UnicodeSequence([4, 5, 6])

        desc = UnicodeDescription()
        desc.add_sequence(seq1)
        desc.add_sequence(seq2)

        desc.remove_sequence(seq1)

        self.assertEqual(desc.seq_codepoints, [[4, 5, 6]])

        desc.remove_sequence(seq2)
        self.assertEqual(desc.seq_codepoints, [])
