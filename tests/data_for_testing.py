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
This module contains some data for testing importing and exporting
functionalities.
"""

TEST_FONT_PSF1_512_SIMPLE_ASM = """font_header:
magic_bytes: db 0x36, 0x04
mode: db 0x1
charsize: db 0x8

font_bitmaps:
"""

for i in range(512):
	TEST_FONT_PSF1_512_SIMPLE_ASM += (
		("glyph_%d: db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00\n"
			% i) if i != 0x41 else
		("glyph_%d: db 0x00, 0x38, 0x44, 0x44, 0x44, 0x44, 0x38, 0x00\n"
			%i)
	)

TEST_FONT_PSF1_256_UNICODE_ASM = """font_header:
magic_bytes: db 0x36, 0x04
mode: db 0x2
charsize: db 0x8

font_bitmaps:
glyph_0: db 0x00, 0x38, 0x44, 0x44, 0x44, 0x44, 0x38, 0x00
"""
for i in range(1, 256):
	TEST_FONT_PSF1_256_UNICODE_ASM += (
		"glyph_%d: db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00\n"
		% i
	)
TEST_FONT_PSF1_256_UNICODE_ASM += "unicode_table:\n"
TEST_FONT_PSF1_256_UNICODE_ASM += (
	"Unicodedescription0: db 0x30, 0x00, 0x4f, 0x00, 0xff, 0xff\n"
)
for i in range(1,256):
	TEST_FONT_PSF1_256_UNICODE_ASM += (
		"Unicodedescription%d: db 0xff, 0xff\n" % i
	)

TEST_FONT_PSF1_256_SEQUENCES_ASM = """font_header:
magic_bytes: db 0x36, 0x04
mode: db 0x2
charsize: db 0x8

font_bitmaps:
glyph_0: db 0x00, 0x38, 0x44, 0x44, 0x44, 0x44, 0x38, 0x00
"""
for i in range(1, 256):
	TEST_FONT_PSF1_256_SEQUENCES_ASM += (
		"glyph_%d: db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00\n"
		% i
	)
TEST_FONT_PSF1_256_SEQUENCES_ASM += "unicode_table:\n"
TEST_FONT_PSF1_256_SEQUENCES_ASM += (
	"Unicodedescription0: db 0x30, 0x00, 0x4f, 0x00, 0xfe, 0xff, " +
	"0x41, 0x00, 0x0a\n    db 0x03, 0xff, 0xff\n"
)
for i in range(1,256):
	TEST_FONT_PSF1_256_SEQUENCES_ASM += (
		"Unicodedescription%d: db 0xff, 0xff\n" % i
	)


TEST_FONT_PSF2_SIMPLE_ASM = """font_header:
magic_bytes: db 0x72, 0xb5, 0x4a, 0x86
version: dd 0x0
headersize: dd 0x20
flags: dd 0x0
length: dd 0x1
charsize: dd 0x10
height: dd 0x8
width: dd 0xa

font_bitmaps:
glyph_0: db 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01
    db 0x00, 0x01, 0x00, 0x00, 0x00
"""

TEST_FONT_PSF2_UNICODE_ASM = """font_header:
magic_bytes: db 0x72, 0xb5, 0x4a, 0x86
version: dd 0x0
headersize: dd 0x20
flags: dd 0x1
length: dd 0x1
charsize: dd 0x10
height: dd 0x8
width: dd 0xa

font_bitmaps:
glyph_0: db 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01
    db 0x00, 0x01, 0x00, 0x00, 0x00
unicode_table:
Unicodedescription0: db 0x41, 0xff
"""

TEST_FONT_PSF2_SEQUENCES_ASM = """font_header:
magic_bytes: db 0x72, 0xb5, 0x4a, 0x86
version: dd 0x0
headersize: dd 0x20
flags: dd 0x1
length: dd 0x1
charsize: dd 0x10
height: dd 0x8
width: dd 0xa

font_bitmaps:
glyph_0: db 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01
    db 0x00, 0x01, 0x00, 0x00, 0x00
unicode_table:
Unicodedescription0: db 0x41, 0xFE, """

for uc in u"\u0041\u030A".encode('utf8'):
	TEST_FONT_PSF2_SEQUENCES_ASM += "0x"+("%02x, " % uc).upper()
TEST_FONT_PSF2_SEQUENCES_ASM += "0xFF\n"

print(TEST_FONT_PSF2_SEQUENCES_ASM)

TEST_FONT_PSF2_UNICODE = bytearray([
	0x72, 0xb5, 0x4a, 0x86,			# magic bytes
	0x00, 0x00, 0x00, 0x00,			# version
	0x20, 0x00, 0x00, 0x00,			# headersize
	0x01, 0x00, 0x00, 0x00,			# flags
	0x02, 0x00, 0x00, 0x00,			# length
	0x10, 0x00, 0x00, 0x00,			# charsize
	0x08, 0x00, 0x00, 0x00,			# height
	0x0A, 0x00, 0x00, 0x00,			# width
	# First Glyph
	0x00, 0x00,
	0x00, 0x00,
	0x00, 0x00,
	0x00, 0x00,
	0x00, 0x00,
	0x00, 0x00,
	0x00, 0x00,
	0x00, 0x00,
	# Second Glyph
	0x00, 0x00,
	0x01, 0x00,
	0x01, 0x00,
	0x01, 0x00,
	0x01, 0x00,
	0x01, 0x00,
	0x01, 0x00,
	0x00, 0x00,
	# Unicode Tabel
	# First Glyph
	0x41, 0xFF,
	# Second Glyph
	0x42, 0xFF
])

TEST_FONT_PSF2_SEQUENCES = bytearray([
	0x72, 0xb5, 0x4a, 0x86,			# magic bytes
	0x00, 0x00, 0x00, 0x00,			# version
	0x20, 0x00, 0x00, 0x00,			# headersize
	0x01, 0x00, 0x00, 0x00,			# flags
	0x01, 0x00, 0x00, 0x00,			# length
	0x10, 0x00, 0x00, 0x00,			# charsize
	0x08, 0x00, 0x00, 0x00,			# height
	0x0A, 0x00, 0x00, 0x00,			# width
	# First Glyph
	0x00, 0x00,
	0x00, 0x00,
	0x00, 0x00,
	0x00, 0x00,
	0x00, 0x00,
	0x00, 0x00,
	0x00, 0x00,
	0x00, 0x00,
	
	# Unicode Tabel
	# First Glyph
	0x41, 0xFE
]) + bytes(u'\u0041\u030A', 'utf8') + bytes([0xFF])

TEST_FONT_PSF2_SIMPLE = bytearray([
	0x72, 0xb5, 0x4a, 0x86,			# magic bytes
	0x00, 0x00, 0x00, 0x00,			# version
	0x20, 0x00, 0x00, 0x00,			# headersize
	0x00, 0x00, 0x00, 0x00,			# flags
	0x02, 0x00, 0x00, 0x00,			# length
	0x10, 0x00, 0x00, 0x00,			# charsize
	0x08, 0x00, 0x00, 0x00,			# height
	0x0A, 0x00, 0x00, 0x00,			# width
	# First Glyph
	0x00, 0x00,
	0x00, 0x00,
	0x00, 0x00,
	0x00, 0x00,
	0x00, 0x00,
	0x00, 0x00,
	0x00, 0x00,
	0x00, 0x00,
	# Second Glyph
	0x00, 0x00,
	0x01, 0x00,
	0x01, 0x00,
	0x01, 0x00,
	0x01, 0x00,
	0x01, 0x00,
	0x01, 0x00,
	0x00, 0x00,
])

TEST_FONT_PSF1_512_SIMPLE = bytearray(
	[0x36, 0x04, 0x01, 0x08] +
	# Glyph1
	[0x00, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x00] + 
	[0x00 for _ in range(8 * 511)] 
)

TEST_FONT_PSF1_256_UNICODE = bytearray(
	[0x36, 0x04, 0x02, 0x08] +
	# Glyph1
	[0x00, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x00] + 
	[0x00 for _ in range(8 * 255)] +
	[0x41, 0x00, 0xFF, 0xFF] + 
	[0xFF for _ in range(255 * 2)]
)

TEST_FONT_PSF1_256_SEQUENCES = bytearray(
	[0x36, 0x04, 0x02, 0x08] +
	# Glyph1
	[0x00, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x00] + 
	[0x00 for _ in range(8 * 255)] +
	[0x41, 0x00, 0xFE, 0xFF, 0x41, 0x00, 0x0A, 0x03, 0xFF, 0xFF] + 
	[0xFF for _ in range(255 * 2)]
)
