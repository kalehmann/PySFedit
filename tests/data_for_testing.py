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
import collections
import gzip
import psflib

class TestFont(object):
	Glyph = collections.namedtuple('Glyph',
								   ['unicode_values', 'sequences',
									'bitmap'])
	
	"""This class holds font data for testing.
	
	Args:
		font_data: The data of a pc screen font as a string or binary
			object.
		charsize (tuple): The size of a glyph bitmap in pixels
		unicode_tab (bool): Whether the font contains an unicode table
			or not.
	"""
	def __init__(self, font_data, charsize, unicode_tab=False):
		self.__font_data = font_data
		self.__glyphs = []
		self.__charsize = charsize
		self.__has_tab = unicode_tab
		
		
	def register_glyph(self, unicode_values,
					   glyph_data, sequences=None):
		"""Register the unicode values, bitmap and optional unicode
		sequences of a glyph stored in the font data.
		
		Notes:
			If the font has no unicode table, you can see unicode_values
			as the index of the glyph in the font
		
		Args:
			unicode_values (tuple): The unicode values describing the
				glyph
			glyph_data (psflib.ByteArray): The bitmap of the glyph
			sequences (tuple): Optionally unicode sequences describing
				the glyph
		"""
		
		self.__glyphs.append(self.Glyph(unicode_values=unicode_values,
										sequences=sequences,
										bitmap=glyph_data))
	
	def get_glyphs(self):
		"""Get all glyphs stored in the font data.
		
		Returns:
			list:A list of TestFont.Glyph objects.
		"""
		
		return self.__glyphs
		
	def get_charsize(self):
		"""Get the size of each glyph bitmap in the font data in pixels.
		
		Returns:
			tuple: The size of each glyph bitmap in the font data in
				pixels
		"""
		
		return self.__charsize
	
	def has_unicode_table(self):
		"""Get whehter the font has an unicode table or not.
		
		Returns:
			bool: Whether the font has an unicode table or not.
		"""
		
		return self.__has_tab
	
	def get_data(self):
		"""Get the data of the testfont.
		
		Returns:
			The data of the test font.
		"""
		
		return self.__font_data
	
	def __len__(self):
		"""Get the number of glyphs in the font data.
		
		Returns:
			int: The number of glyphs in the font data
		"""
		
		return len(self.__glyphs)

def getCompressedTestFont(test_font):
	old = test_font.get_data		
	test_font.get_data = lambda: gzip.compress(
			old()
		)
	
	return test_font

def get_font_psf_512_simple_asm():
	"""Get a test font in the asm format with 512 glyph bitmaps and no
	unicode table.
	
	Returns:
		TestFont: The test font	
	"""
	data = """font_header:
magic_bytes: db 0x36, 0x04
mode: db 0x1
charsize: db 0x10

font_bitmaps:
"""
	
	empty_bitmap = (
		"glyph_%d: db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00," +
		" 0x00, 0x00, 0x00\n    db 0x00, 0x00, 0x00, 0x00, 0x00\n"
	)
	
	empty_data = psflib.ByteArray.from_bytes([0 for _ in range(16)])
	
	A_bitmap = (
		"glyph_%d: db 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08," +
		" 0x09, 0x0a, 0x0b\n    db 0x0c, 0x0d, 0x0e, 0x0f, 0x10\n"
	)
	
	A_data = psflib.ByteArray.from_bytes([i+1 for i in range(16)])

	for i in range(512):
		data += empty_bitmap % i if i != 0x41 else A_bitmap	% i

	font = TestFont(data, (8, 16))

	for i in range(512):
		font.register_glyph(
			(i, ),
			empty_data if i != 0x41 else A_data				
		)
	
	return font
	
def get_font_psf_256_unicode_asm():
	"""Get a test font in the asm format with 256 glyph bitmaps and an
	unicode table.
	
	Returns:
		TestFont: The test font		
	"""
	data = """font_header:
magic_bytes: db 0x36, 0x04
mode: db 0x2
charsize: db 0x10

font_bitmaps:
"""
	empty_bitmap = (
		"glyph_%d: db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00," +
		" 0x00, 0x00, 0x00, 0x00\n    db 0x00, 0x00, 0x00, 0x00, 0x00\n"
	)
	
	empty_data = psflib.ByteArray.from_bytes([0 for _ in range(16)])
	
	A_bitmap = (
		"glyph_%d: db 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08," +
		" 0x09, 0x0a, 0x0b\n    db 0x0c, 0x0d, 0x0e, 0x0f, 0x10\n"
	)
	
	A_data = psflib.ByteArray.from_bytes([i+1 for i in range(16)])

	for i in range(256):
		data += empty_bitmap % i if i != 0x41 else A_bitmap	% i
	data += "unicode_table:\n"
	for i in range(256):
		if i == 0x41:
			data += "Unicodedescription65: db 0x41, 0x00, 0xff, 0xff\n"
			
			continue
		data += "Unicodedescription%d: db 0xff, 0xff\n" % i

	font = TestFont(data, (8, 16), True)

	for i in range(256):
		if i == 0x41:
			font.register_glyph((0x41, ), A_data)
		else:
			font.register_glyph((), empty_data)
	
	return font
	
def get_font_psf_256_sequences_asm():
	"""Get a test font in the asm format with 256 glyph bitmaps and an
	unicode table.
	
	Returns:
		TestFont: The test font		
	"""
	data = """font_header:
magic_bytes: db 0x36, 0x04
mode: db 0x4
charsize: db 0x10

font_bitmaps:
"""
	empty_bitmap = (
		"glyph_%d: db 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00," +
		" 0x00, 0x00, 0x00, 0x00\n    db 0x00, 0x00, 0x00, 0x00, 0x00\n"
	)
	
	empty_data = psflib.ByteArray.from_bytes([0 for _ in range(16)])
	
	A_bitmap = (
		"glyph_%d: db 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08," +
		" 0x09, 0x0a, 0x0b\n    db 0x0c, 0x0d, 0x0e, 0x0f, 0x10\n"
	)
	
	A_data = psflib.ByteArray.from_bytes([i+1 for i in range(16)])

	for i in range(256):
		data += empty_bitmap % i if i != 0x41 else A_bitmap	% i
	data += "unicode_table:\n"
	for i in range(256):
		if i == 0x41:
			data += (
				"Unicodedescription65: db 0x41, 0x00, 0xfe, 0xff, " + 
				"0x41, 0x00, 0x0a, 0x03, 0xff\n    db 0xff\n"
			)
		else:
			data += "Unicodedescription%d: db 0xff, 0xff\n" % i

	font = TestFont(data, (8, 16), True)

	for i in range(256):
		if i == 0x41:
			font.register_glyph((0x41, ), A_data, [[0x41, 0x30a]])
		else:
			font.register_glyph((), empty_data)
	
	return font
	
def get_font_psf2_simple_asm():
	"""Get a psf2 test font in the asm format with no unicode table.
	
	Returns:
		TestFont: The test font.	
	"""
	data = """font_header:
magic_bytes: db 0x72, 0xb5, 0x4a, 0x86
version: dd 0x0
headersize: dd 0x20
flags: dd 0x0
length: dd 0x1
charsize: dd 0x10
height: dd 0x8
width: dd 0xa

font_bitmaps:
glyph_0: db 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01
    db 0x00, 0x01, 0x00, 0x01, 0x00
"""
	font = TestFont(data, (10, 8))
	
	data_0 = psflib.ByteArray.from_bytes([
		0 if i % 2 else 1 for i in range(16)
	])
	
	font.register_glyph((0,), data_0)
	
	return font
	
def get_font_psf2_unicode_asm():
	"""Get a psf2 test font in the asm format with an unicode table.
	
	Returns:
		TestFont: The test font.
	"""
	data = """font_header:
magic_bytes: db 0x72, 0xb5, 0x4a, 0x86
version: dd 0x0
headersize: dd 0x20
flags: dd 0x1
length: dd 0x1
charsize: dd 0x10
height: dd 0x8
width: dd 0xa

font_bitmaps:
glyph_0: db 0xff, 0x40, 0xff, 0x40, 0xff, 0x40, 0xff, 0x40, 0xff, 0x40, 0xff
    db 0x40, 0xff, 0x40, 0xff, 0x40
unicode_table:
Unicodedescription0: db 0x41, 0xff
"""

	font = TestFont(data, (10, 8), True)
	
	data_0 = psflib.ByteArray.from_bytes([
		0x40 if i % 2 else 0xff for i in range(16)
	])
	
	font.register_glyph((0x41,), data_0)

	return font

def get_font_psf2_sequences_asm():
	"""Get a psf2 test font in the asm format with an unicode table with
	unicode sequences.
	
	Returns:
		TestFont: The test font.
	"""
	data = """font_header:
magic_bytes: db 0x72, 0xb5, 0x4a, 0x86
version: dd 0x0
headersize: dd 0x20
flags: dd 0x1
length: dd 0x1
charsize: dd 0x10
height: dd 0x8
width: dd 0xa

font_bitmaps:
glyph_0: db 0xff, 0x40, 0xff, 0x40, 0xff, 0x40, 0xff, 0x40, 0xff, 0x40, 0xff
    db 0x40, 0xff, 0x40, 0xff, 0x40
unicode_table:
Unicodedescription0: db 0x41, 0xfe, """
	for uc in u"\u0041\u030A".encode('utf8'):
		data += "0x"+("%02x, " % uc)
	data += "0xff\n"
	font = TestFont(data, (10, 8), True)
	
	data_0 = psflib.ByteArray.from_bytes([
		0x40 if i % 2 else 0xff for i in range(16)
	])
	
	font.register_glyph((0x41,), data_0, [[0x41, 0x30a]])

	return font

def get_font_psf2_simple():
	"""Get a psf2 test font with binary data without an unicode table.
	
	Returns:
		TestFont: The test font.	
	"""
	data_0 = [0b11000000 if i%2 else 255 for i in range(16)]
	data_1 = [64 if i%2 else 254 for i in range(16)]
	
	data = bytearray([
		0x72, 0xb5, 0x4a, 0x86,			# magic bytes
		0x00, 0x00, 0x00, 0x00,			# version
		0x20, 0x00, 0x00, 0x00,			# headersize
		0x00, 0x00, 0x00, 0x00,			# flags
		0x02, 0x00, 0x00, 0x00,			# length
		0x10, 0x00, 0x00, 0x00,			# charsize
		0x08, 0x00, 0x00, 0x00,			# height
		0x0A, 0x00, 0x00, 0x00,			# width
	]) + bytearray(data_0) + bytearray(data_1)
	
	font = TestFont(data, (10, 8))
	
	font.register_glyph((0,), psflib.ByteArray.from_bytes(data_0))
	font.register_glyph((1,), psflib.ByteArray.from_bytes(data_1))
	
	return font

def get_font_psf2_unicode():
	"""Get a psf2 test font with binary data and an unicode table.
	
	Returns:
		TestFont: The test font.	
	"""
	data_A = [i if not i%2 else 0  for i in range(16)]
	data_B = [i if not i%2 else 0 for i in range(16, 0, -1)]
	
	data = bytearray([
		0x72, 0xb5, 0x4a, 0x86,			# magic bytes
		0x00, 0x00, 0x00, 0x00,			# version
		0x20, 0x00, 0x00, 0x00,			# headersize
		0x01, 0x00, 0x00, 0x00,			# flags
		0x02, 0x00, 0x00, 0x00,			# length
		0x10, 0x00, 0x00, 0x00,			# charsize
		0x08, 0x00, 0x00, 0x00,			# height
		0x0A, 0x00, 0x00, 0x00,			# width
	]) + bytearray(data_A) + bytearray(data_B) + bytearray([
		# Unicode Tabel
		# First Glyph
		0x41, 0xFF,
		# Second Glyph
		0x42, 0xFF
	])
	
	font = TestFont(data, (10, 8), True)
	
	font.register_glyph((0x41,), psflib.ByteArray.from_bytes(data_A))
	font.register_glyph((0x42,), psflib.ByteArray.from_bytes(data_B))
	
	return font

def get_font_psf2_sequences():
	"""Get a psf2 test font with binary data and an unicode table with
	unicode sequences.
	
	Returns:
		TestFont: The test font.	
	"""
	data_A = [i if not i%2 else 0  for i in range(16)]
	
	data = bytearray([
		0x72, 0xb5, 0x4a, 0x86,			# magic bytes
		0x00, 0x00, 0x00, 0x00,			# version
		0x20, 0x00, 0x00, 0x00,			# headersize
		0x01, 0x00, 0x00, 0x00,			# flags
		0x01, 0x00, 0x00, 0x00,			# length
		0x10, 0x00, 0x00, 0x00,			# charsize
		0x08, 0x00, 0x00, 0x00,			# height
		0x0A, 0x00, 0x00, 0x00,			# width
	]) + bytearray(data_A) + bytearray([
		# Unicode Tabel
		# First Glyph
		0x41, 0xFE
	]) + bytes(u'\u0041\u030A', 'utf8') + bytes([0xFF])
	
	font = TestFont(data, (10, 8), True)
	
	font.register_glyph((0x41,), psflib.ByteArray.from_bytes(data_A),
						((0x41, 0x30a),))
	
	return font

def get_font_psf_512_simple():
	"""Get a test font with binary data, 512 glyphs and no unicode
	table.
	
	Returns:
		TestFont: The test font
	"""
	data_0 = [i for i in range(10)]
	data_empty = [0 for _ in range(10)]
	
	data = bytearray(
		[0x36, 0x04, 0x01, 0x0a] +
		# Glyph1
		data_0 + 
		data_empty * 511 
	)
	
	font = TestFont(data, (8, 10))
	
	font.register_glyph((0,), psflib.ByteArray.from_bytes(data_0))
	
	for i in range(1, 512):
		font.register_glyph((i,),
							psflib.ByteArray.from_bytes(data_empty))
		
	return font
	
def get_font_psf_256_unicode():
	"""Get a test font with binary data, 256 glyphs and an unicode
	table.
	
	Returns:
		TestFont: The test font
	"""
	data_A = [i for i in range(10)]
	data_empty = [0 for _ in range(10)]
	
	data = bytearray(
		[0x36, 0x04, 0x02, 0x0a] +
		# Glyph1
		data_A + 
		data_empty * 255 +
		[0x41, 0x00, 0xFF, 0xFF] + 
		[0xFF for _ in range(255 * 2)]
	)
	
	font = TestFont(data, (8, 10), True)
	
	font.register_glyph((0x41,), psflib.ByteArray.from_bytes(data_A))
	for _ in range(255):
		font.register_glyph((), psflib.ByteArray.from_bytes(data_empty))
	
	return font

def get_font_psf_256_sequences():
	"""Get a test font with binary data, 256 glyphs, an unicode table
	and unicode sequences.
	
	Returns:
		TestFont: The test font
	"""
	data_A = [i for i in range(10)]
	data_empty = [0 for _ in range(10)]
	
	data = bytearray(
		[0x36, 0x04, 0x04, 0x0a] +
		# Glyph1
		data_A + 
		data_empty * 255 +
		[0x41, 0x00, 0xFE, 0xFF, 0x41, 0x00, 0x0A, 0x03, 0xFF, 0xFF] + 
		[0xFF for _ in range(255 * 2)]
	)
	
	font = TestFont(data, (8, 10), True)
	
	font.register_glyph((0x41,), psflib.ByteArray.from_bytes(data_A), 
						((0x41, 0x30a),))
	for _ in range(255):
		font.register_glyph((), psflib.ByteArray.from_bytes(data_empty))
	
	return font

def get_font_psf2_sequences_compressed():
	
	return getCompressedTestFont(get_font_psf2_sequences())

def get_font_psf2_simple_compressed():
	
	return getCompressedTestFont(get_font_psf2_simple())

def get_font_psf2_unicode_compressed():
	
	return getCompressedTestFont(get_font_psf2_unicode())
	
def get_font_psf_256_sequences_compressed():
	
	return getCompressedTestFont(get_font_psf_256_sequences())

def get_font_psf_256_unicode_compressed():
	
	return getCompressedTestFont(get_font_psf_256_unicode())

def get_font_psf_512_simple_compressed():
	
	return getCompressedTestFont(get_font_psf_512_simple())

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
mode: db 0x4
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
Unicodedescription0: db 0x41, 0xfe, """

for uc in u"\u0041\u030A".encode('utf8'):
	TEST_FONT_PSF2_SEQUENCES_ASM += "0x"+("%02x, " % uc)
TEST_FONT_PSF2_SEQUENCES_ASM += "0xff\n"

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
	[0x36, 0x04, 0x04, 0x08] +
	# Glyph1
	[0x00, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x00] + 
	[0x00 for _ in range(8 * 255)] +
	[0x41, 0x00, 0xFE, 0xFF, 0x41, 0x00, 0x0A, 0x03, 0xFF, 0xFF] + 
	[0xFF for _ in range(255 * 2)]
)
