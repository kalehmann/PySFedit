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
This is a package for working with pc screen fonts.

It contains classes representing pc screen fonts, their headers and
glyphs. Furthermore there are tools for exporting fonts to .asm or .psf
files and importing these.
"""

from abc import ABC, abstractmethod

from .byteutils import Byte, ByteArray
from .asmutils import AsmParser

PSF1_VERSION = 1
PSF2_VERSION = 2

PSF1_MAGIC_BYTES = [0x36, 0x04]
PSF2_MAGIC_BYTES = [0x72, 0xb5, 0x4a, 0x86]

PSF1_MODE512 = 0x01
PSF1_MODEHASTAB = 0x02
PSF1_MODEHASSEQ = 0x04
PSF1_MAXMODE = 0x05

PSF1_SEPARATOR = 0xFFFF
PSF1_STARTSEQ = 0xFFFE

PSF2_SEPARATOR = 0xFF
PSF2_STARTSEQ = 0xFE

PSF2_MAXVERSION = 0
PSF2_HAS_UNICODE_TABLE = 0x1

TYPE_PLAIN_ASM = 42
TYPE_BINARY_PSF = 43


def bytearray_to_int(_bytearray):
	"""Get the integer value from a bytearray
	
	Args:
		_bytearray (bytearray): The bytearray to get the integer value
			from
			
	Returns:
		int: The integer value from thebytearray
		
	Notes:
		The bytearray should be little endian
	"""
	return int.from_bytes(_bytearray, byteorder='little',
		signed=False)

def get_unicode_str(codepoint):
	"""Get an unicode string from a given codepoint
	
	Args:
		codepoint (int) : The codepoint to get the unicode value from
	
	Returns:
		str : The Unicode string. Is empty, if the codepoint is a
			controll sequence or undefined
	"""
	if 0x20 <= codepoint <= 0x7e or 0xa0 <= codepoint: #<= 0xff:
		return chr(codepoint)
	return ""
		
def get_codepoint(char):
	"""Get the codepoint of a character
	
	Args:
		char (str) : The character to get the codepoint from
		
	Notes:
		char should be decoded with utf-8 and its length should be 1
		
	Returns:
		None : If the length of char is not 1
		int : The codepoint of the given character
	"""
	#char = char.decode('utf-8')
	if len(char) != 1: return None
	codepoint = ord(char)
	return codepoint
	
class Exporter(ABC):
	"""Base class of an exporter for a pc screen font.
	
	Args:
		font (PcScreenFont): The font to export	
	"""
	def __init__(self, font):
		self.__font = font
	
	def export_to_data(self):
		"""Export the font of this exporter as data.
		
		Returns:
			object: Depends on the implementation
		"""
		header = self._build_header()
		bitmaps = self._build_bitmaps()
		if self.__font.has_unicode():
			unicode_table = self._build_unicode_table()
		
			return header + bitmaps + unicode_table
		
		return header + bitmaps

	def export_to_file(self, file_path):
		"""Export the font of this exporter to a file
		
		Args:
			file_path (str): The path of the file to export the font to.
		"""
		data = self.export_to_data()
		self._write_data(file_path, data)
		
	@abstractmethod
	def _write_data(self, file_path, data):
		"""Implement this method to write the data from the exporter
		into a file.
		
		Args:
			file_path (str): The path to the file to write the data
				into.
			data (object): The data to write into the file. The type of
				this argument depends on the implementation.		
		"""
		pass
	
	@abstractmethod
	def _build_header(self):
		"""Convert the header of the font of this exporter into data, 
		like for example a string or bytearray.
		
		Returns:
			object: Depends on the implementation		
		"""
		pass
		
	@abstractmethod
	def _build_bitmaps(self):
		"""Convert the bitmaps of the font of this exporter into data, 
		like for example a string or bytearray.
		
		Returns:
			object: Depends on the implementation		
		"""
		pass
		
	@abstractmethod
	def _build_unicode_table(self):
		"""Convert the unicode table of the font of this exporter into
		data, like for example a string or bytearray.
		
		Returns:
			object: Depends on the implementation		
		"""
		pass
		
	def _get_font(self):
		"""Get the font from the exporter.
		
		Returns:
			PcScreenFont: The font of the exporter.		
		"""
		return self.__font
			
class Importer(ABC):
	"""Base class of an importer for a pc screen font.
	
	Args:
		data: The data to import the font from	
	"""
	def __init__(self, data):
		self.__data = data
		
	@classmethod
	def import_from_data(cls, data):
		"""Build a font from given data
		
		Args:
			data: The data to import the font from
			
		Returns:
			PcScreenFont: The font builded from the given data		
		"""
		importer = cls(data)
	
		return importer.__build_font()
		
	@classmethod
	def import_from_file(cls, file_path):
		"""Build a font from data in a file
		
		Args:
			file_path (str): The path to the file to read the data
				from
		
		Returns:
			PcScreenFont: The font build from the data in the file		
		"""
		data = cls._read_data(file_path)
		
		return cls.import_from_data(data)
	
	@staticmethod
	@abstractmethod
	def _read_data(file_path):
		"""Extract data from a file
		
		Args:
			file_path (str): The path to the file to read data from
			
		Returns:
			The data extracted from the file
		
		Notes:
			In the implementation of this method you can decide wether
			reading the file binary or not.
		"""
		pass
	
	@abstractmethod
	def _build_header(self):
		"""Create a psf header from the data of the importer
		
		Returns:
			PsfHeader: The header builded
			
		Notes:
			Use self.__get_data() to get the data to build the header
			from.		
		"""
		pass
	
	@abstractmethod
	def _parse_unicode_descriptions(self):
		"""Create a list of unicode descriptions from the data of the
		importer.
		
		Returns:
			list: The list of unicode descriptions extracted from the
				data. Note, that the order of the descriptions in the
				list should be the same as in the given data.		
		"""
		unicode_descriptions = []
		
		return unicode_descriptions
	
	@abstractmethod
	def _build_glyph(self, glyph, n):
		"""Read the data of a glyph of the font
		
		Args:
			glyph (Glyph): The glyph to populate with data
			n (int): Occurence of the glyph in the data of the importer
		"""
		pass
		
	def __build_font(self):
		"""Use this method to get a pc screen font from the data of the
		importer.
		
		Returns:
			PcScreenFont
		"""
		self.__header = self._build_header()
		length = self.__header.get_length()
		font = PcScreenFont(self.__header)		
		
		if self.__header.has_unicode_table():
			uc_descriptions = self._parse_unicode_descriptions()
		else:
			uc_descriptions = [[i] for i in range(length)]
				
		if len(uc_descriptions) != length:
			raise Exception(
				"The number of unicode descriptions of the font " +
				"does not match its length."
			)
		
		for i, descriptions in zip(range(length), uc_descriptions):
			if descriptions:
				primary_codepoint = descriptions[0]
				glyph = font.get_glyph(primary_codepoint)
				
				for codepoint in descriptions[1:]:
					glyph.add_unicode_representation(codepoint)
				self._build_glyph(glyph, i)
		
		return font				
	
	def _get_data(self):
		"""Returns the data assigned with this importer
		
		Returns:
			The data assigned with this importer		
		"""
		return self.__data
		
	def _get_header(self):
		"""Returns the header extracted from the data of this importer
		
		Returns:
			PsfHeader: The header	
		"""
		return self.__header
	
class AsmImporter(Importer):
	"""Implementation for importing a PCScreenFont from an assembler
	file. For usage see the Importer base class.
	
	Args:
		data (str): The data to build the font from
	"""
	def __init__(self, data):
		Importer.__init__(self, data)
		self.__asm = AsmParser(data)
		
	@staticmethod
	def _read_data(file_path):
		"""Read the data for the font from a file.
		
		Args:
			file_path (str): The path to the file which should be
				imported
				
		Returns:
			str: The data read from the file
		"""
		with open(file_path, 'r') as f:
			data = f.read()
			
		return data
		
	def _build_header(self):
		"""Build the header of the PcScreenFont.
		
		Build the header of the PcScreenFont out of the data of the
		importer.
		
		Returns:
			PsfHeader: The header built out of the data of the importer.		

		Raises:
			Exception: This method raises an exception if the magic
				bytes of the font do any match any known version of
				a pc screen font.
		"""
		psf1_magic = ByteArray()
		psf2_magic = ByteArray()
		for i in PSF1_MAGIC_BYTES:
			psf1_magic.add_byte(Byte.from_int(i))
		for i in PSF2_MAGIC_BYTES:
			psf2_magic.add_byte(Byte.from_int(i))
		
		if not self.__asm.has_label('magic_bytes'):
			raise Exception(
				'Could not read font from asm file, since it has no ' +
				'label named "magic_bytes"')
		
		if self.__asm.magic_bytes == psf1_magic:
			header = self.__get_header_psf_v1()
		elif self.__asm.magic_bytes == psf2_magic:
			header = self.__get_header_psf_v2()
		else:
			raise Exception(
				'The magic bytes of the font do not match any known ' +
				'magic bytes'
			)
		return header	
	
	def __get_header_psf_v1(self):
		"""Build the header of an old pc screen font out of the data of
		the importer.
		
		Returns:
			PsfHeaderv1: The header built out of the data of the
				importer.		
		"""
		charsize = int(self.__asm.charsize)
		mode = int(self.__asm.mode)
		header = PsfHeaderv1([8, charsize])
		header.set_mode(mode)
		
		return header
		
	def __get_header_psf_v2(self):
		"""Build the header of a new pc screen font out of the data of
		the importer.
		
		Returns:
			PsfHeaderv2: The header built out of the data of the
				importer.		
		"""
		a = self.__asm
		version = int(a.version)
		flags = int(a.flags)
		length = int(a.length)
		height = int(a.height)
		width = int(a.width)
		
		header = PsfHeaderv2([width, height])
		header.set_flags(flags)
		header.set_length(length)
		
		return header
	
	def _parse_unicode_descriptions(self):
		"""Read the unicode descriptions of the glyphs of the font out
		of the data of the importer.
		
		Returns:
			list: A list of lists containing integers which represent
				the codepoints of the unicode representations of the
				glyphs.
		"""
		header = self._get_header()
		if header.version_psf == PSF1_VERSION:
			return self.__parse_unicode_descriptions_psf1()
		elif header.version_psf == PSF2_VERSION:
			return self.__parse_unicode_descriptions_psf2()
				
	def __parse_unicode_descriptions_psf1(self):
		"""Read the unicode descriptions of an old pc screen font out
		of the data of the importer.
		
		Returns:
			list		
		"""
		descriptions = []
		for label, data in self.__asm.get_labels().items():
			if label.startswith('Unicodedescription'):
				data = data.to_ints(2)
				descs = []
				i = 0
				while i < len(data) and data[i] != PSF1_SEPARATOR:
					if data[i] == PSF1_STARTSEQ:
						while ( i < len(data) and
								data[i] != PSF1_SEPARATOR and
								data[i] != PSF1_STARTSEQ):
							pass # @ToDo: Add support for parsing
								 # sequences
							i+=1
					descs.append(data[i])
					i += 1 
				descriptions.append(descs)
			elif label.startswith('Placeholder'):
				descriptions.append(None)
				
		return descriptions
				
	def __parse_unicode_descriptions_psf2(self):
		"""Read the unicode descriptions of a new pc screen font out of
		the data of the importer.
		
		Returns:
			list		
		"""
		descriptions = []
		for label, data in self.__asm.get_labels().items():
			if label.startswith('Unicodedescription'):
				data = data.to_ints()
				descs = []
				i = 0
				while i < len(data) and data[i] != PSF2_SEPARATOR:
					if data[i] == PSF1_STARTSEQ:
						while ( i < len(data) and
								data[i] != PSF2_SEPARATOR and
								data[i] != PSF2_STARTSEQ):
							pass # @ToDo: Add support for parsing
								 # sequences
							i+=1
					descs.append(data[i])
					i += 1 
				descriptions.append(descs)
			elif label.startswith('Placeholder'):
				descriptions.append(None)
				
		return descriptions
				
	def _build_glyph(self, glyph, n):
		"""Read the bitmap of a glyph out of the data of the importer.
		
		Args:
			glyph (Glyph): The glyph to asign the bitmap to
			n (int): The index of the bitmap in the data		
		"""
		data = self.__asm.get_labels()["glyph_%d" % n]
		glyph.set_data_from_bytes(data)
			
class AsmExporter(object):
	def __init__(self, font):
		self.font = font
		self.header = font.get_header()
		if self.header.version_psf == PSF1_VERSION:
			self.version = 1
		elif self.header.version_psf == PSF2_VERSION:
			self.version = 2
		self.string = ""
		
	def __create_header(self):
		self.string += "font_header:\n"
		if self.version == 1:
			magic_bytes = ByteArray(self.header.magic_bytes)
			self.string += magic_bytes.to_asm("magic_bytes")
			self.string += "mode: db %s\n" % hex(self.header.mode)
			self.string += "charsize: db %s\n\n" % hex(self.header.charsize)
		elif self.version == 2:
			magic_bytes = ByteArray(self.header.magic_bytes)
			self.string += magic_bytes.to_asm("magic_bytes")
			self.string += "version: dd %s\n" % hex(self.header.version)
			self.string += "headersize: dd %s\n" % hex(
								self.header.headersize)
			self.string += "flags: dd %s\n" % hex(self.header.flags)
			self.string += "length: dd %s\n" % hex(self.header.length)
			self.string += "charsize: dd %s\n" % hex(
								self.header.charsize)
			self.string += "height: dd %s\n" % hex(self.header.height)
			self.string += "width: dd %s\n\n" % hex(self.header.width)

	def __glyph_to_asm(self, glyph, label):
		bits = []
		for row in glyph.data:
			for bit in row:
				bits.append(bit)
			missing_bits = 8 - len(row) % 8
			if missing_bits < 8:
				for _ in range(8 - len(row) % 8):
					bits.append(0)		
		# -- The following is bullshit --		
		# The number of bits must be a multiple of 8
		#if bits_count % 8:
		#	for _ in range(8- (bits_cound%8)):
		#		bits.append(0)
		_bytes = ByteArray.from_bit_array(bits)		
		return _bytes.to_asm(label)


	def __create_bitmaps(self):
		self.string += "font_bitmaps:\n"
		if self.header.has_unicode_table():
			for i, glyph in zip(range(len(self.font.get_glyphs())),
								self.font.get_glyphs().values()):
				self.string += self.__glyph_to_asm(glyph, "glyph_%d" % i)
			if self.header.version_psf == PSF1_VERSION:
				if self.header.mode & PSF1_MODE512:
					glyph_count = 512 
				else:
					glyph_count = 256
				glyph = Glyph(self.header.size)
				for i in range(len(self.font.get_glyphs()), glyph_count):
					self.string += self.__glyph_to_asm(glyph, "glyph_%d" % i)
			return
			
		# Has no Unicode table
		if self.header.version_psf == PSF1_VERSION:
			if self.header.mode & PSF1_MODE512:
				# 512 Glyphs
				glyph_count = 512
			else:
				# 256 Glyphs
				glyph_count = 256
		else:
			glyph_count = len(self.font)
			
		for i in range(glyph_count):
			glyph = self.font.get_glyph(i)
			self.string += self.__glyph_to_asm(glyph, "glyph_%d" % i)

	def __create_unicode_table(self):
		if self.header.version_psf == PSF1_VERSION:
			if self.header.mode & PSF1_MODE512:
				# 512 Glyphs
				glyph_count = 512
			else:
				# 256 Glyphs
				glyph_count = 256
			for puc, glyph in self.font.get_glyphs().items():
				_bytes = ByteArray.from_int(puc, 2)
				#if len(glyph.get_unicode_representations()) > 1:
				#	_bytes += ByteArray.from_int(0xFFFE, 2)
				for uc in glyph.get_unicode_representations():
					if uc != puc:
						_bytes += ByteArray.from_int(uc, 2)
				_bytes += ByteArray.from_int(0xFFFF, 2)		
				self.string += _bytes.to_asm('Unicodedescription%d' % puc)
			for i in range(glyph_count - len(self.font.get_glyphs())):
				self.string += ByteArray.from_int(0xFFFF, 2).to_asm('Placeholder%d' % i)
		else:	# psf2
			for puc, glyph in self.font.get_glyphs().items():
				_bytes = ByteArray.from_bytes(chr(puc).encode('utf8'))
				for uc in glyph.get_unicode_representations():
					if uc != puc:
						_bytes += ByteArray.from_bytes(
							chr(uc).encode('utf8'))
				_bytes += ByteArray.from_int(0xFF, 1)	
				self.string += _bytes.to_asm('Unicodedescription%d' % puc)	
	
	def export_string(self):
		self.string = ''
		self.__create_header()
		self.__create_bitmaps()
		if self.font.has_unicode():
			self.__create_unicode_table()
		
		return self.string	

	def export_file(self, path):
		data = self.export_string()
		
		with open(path, "w") as f:
			f.write(data)

class PsfExporter(object):
	def __init__(self, font):
		self.font = font
		self.header = font.get_header()
		if self.header.version_psf == PSF1_VERSION:
			self.version = 1
		elif self.header.version_psf == PSF2_VERSION:
			self.version = 2
				
	def int_to_bytes(self, n):
		bts = []
		if 0 <= n <= 0x100 ** 4 - 1:
			for i in range(4):
				bts.append(n % 0x100)
				n = n // 0x100
		return bytearray(bts)
	
	def glyph_to_bytearray(self, glyph):
		ba = bytearray()
		for row in glyph.data:
			if len(row) % 8:
				row = row[:]
				while len(row) % 8:
					row.append(0)
			b = ByteArray.from_bit_array(row)
			for i in b:
				ba.append(int(i))
		return ba	
	
	def create_header(self):
		for i in self.header.magic_bytes:
			self.bytes.append(i)
		if self.version == 1:
			self.bytes.append(self.header.mode)
			self.bytes.append(self.header.charsize)
		elif self.version == 2:
			self.bytes += self.int_to_bytes(self.header.version)
			self.bytes += self.int_to_bytes(self.header.headersize)
			self.bytes += self.int_to_bytes(self.header.flags)
			self.bytes += self.int_to_bytes(self.header.length)
			self.bytes += self.int_to_bytes(self.header.charsize)
			self.bytes += self.int_to_bytes(self.header.height)
			self.bytes += self.int_to_bytes(self.header.width)

	def create_bitmaps(self):
		if self.header.has_unicode_table():
			for i, glyph in zip(range(len(self.font.get_glyphs())),
								self.font.get_glyphs().values()):
				self.bytes += self.glyph_to_bytearray(glyph)
				
			if self.header.version_psf == PSF1_VERSION:
				if self.header.mode & PSF1_MODE512:
					glyph_count = 512 
				else:
					glyph_count = 256
				glyph = Glyph(self.header.size)
				for i in range(len(self.font.get_glyphs()), glyph_count):
					self.bytes += self.glyph_to_bytearray(glyph)
			return
			
		# Has no Unicode table
		if self.header.version_psf == PSF1_VERSION:
			if self.header.mode & PSF1_MODE512:
				# 512 Glyphs
				glyph_count = 512
			else:
				# 256 Glyphs
				glyph_count = 256
		else:
			glyph_count = len(self.font)
			
		for i in range(glyph_count):
			glyph = self.font.get_glyph(i)
			self.bytes += self.glyph_to_bytearray(glyph)
			
	def create_unicode_table(self):
		ba = ByteArray()
		if self.header.version_psf == PSF1_VERSION:
			if self.header.mode & PSF1_MODE512:
				# 512 Glyphs
				glyph_count = 512
			else:
				# 256 Glyphs
				glyph_count = 256
			for puc, glyph in self.font.get_glyphs().items():
				_bytes = ByteArray.from_int(puc, 2)
				#if len(glyph.get_unicode_representations()) > 1:
				#	_bytes += ByteArray.from_int(0xFFFE, 2)
				for uc in glyph.get_unicode_representations():
					if uc != puc:
						_bytes += ByteArray.from_int(uc, 2)
				_bytes += ByteArray.from_int(0xFFFF, 2)		
				ba += _bytes
			for i in range(glyph_count - len(self.font.get_glyphs())):
				ba += ByteArray.from_int(0xFFFF, 2)
		else:	# psf2
			for puc, glyph in self.font.get_glyphs().items():
				_bytes = ByteArray.from_bytes(chr(puc).encode('utf8'))
				for uc in glyph.get_unicode_representations():
					if uc != puc:
						_bytes += ByteArray.from_bytes(
							chr(uc).encode('utf8'))
				_bytes += ByteArray.from_int(0xFF, 1)	
				ba += _bytes
		for i in ba:
			self.bytes.append(int(i))
			
	def export_file(self, path):
		with open(path, "wb") as f:
			f.write(self.export_bytearray())

	def export_bytearray(self):
		self.bytes = bytearray()
		self.create_header()
		self.create_bitmaps()
		if self.header.has_unicode_table():
			self.create_unicode_table()
		return self.bytes

class PsfImporter(Importer):
	"""Implementation for importing a PCScreenFont from an psf file.
	For usage see the Importer base class.
	
	Args:
		data (bytes): The data to build the font from
	"""

	@staticmethod
	def _read_data(file_path):
		"""Read the data for the font from a file.
		
		Args:
			file_path (str): The path to the file which should be
				imported
				
		Returns:
			bytes: The data read from the file
		"""
		with open(file_path, 'rb') as f:
			data = f.read()
			
		return data
		
	def _build_header(self):
		"""Build the header of the PcScreenFont.
		
		Build the header of the PcScreenFont out of the data of the
		importer.
		
		Returns:
			PsfHeader: The header built out of the data of the importer.

		Raises:
			Exception: This method raises an exception if the magic
				bytes of the font do any match any known version of
				a pc screen font.		
		"""
		psf1_magic = bytearray()
		psf2_magic = bytearray()
		for i in PSF1_MAGIC_BYTES:
			psf1_magic.append(i)
		for i in PSF2_MAGIC_BYTES:
			psf2_magic.append(i)
		
		data = self._get_data()
		
		if data[:2] == psf1_magic:
			return self.__get_header_psf_v1(data)
		elif data[:4] == psf2_magic:
			return self.__get_header_psf_v2(data)
		else:
			raise Exception(
				'The magic bytes of the font do not match any known ' +
				'magic bytes'
			)		
		
	def __get_header_psf_v1(self, ba):
		"""Build the header of an old pc screen font out of the data of
		the importer.

		Args:
			ba (bytearray): The bytearray to extract the data for the
				header from
		
		Returns:
			PsfHeaderv1: The header built out of the data of the
				importer.		
		"""
		charsize = ba[3]
		mode = ba[2]
		header = PsfHeaderv1([8, charsize])
		header.set_mode(mode)
		
		return header
		
	def __get_header_psf_v2(self, ba):
		"""Build the header of a new pc screen font out of the data of
		the importer.
		
		Args:
			ba (bytearray): The bytearray to extract the data for the
				header from

		Returns:
			PsfHeaderv2: The header built out of the data of the
				importer.		
		"""
		version = bytearray_to_int(ba[4:8])
		flags = bytearray_to_int(ba[12:16])
		length = bytearray_to_int(ba[16:20])
		height = bytearray_to_int(ba[24:28])
		width = bytearray_to_int(ba[28:32])
				
		header = PsfHeaderv2([width, height])
		header.set_flags(flags)
		header.set_length(length)
		
		return header
		
	def _parse_unicode_descriptions(self):
		"""Read the unicode descriptions of the glyphs of the font out
		of the data of the importer.
		
		Returns:
			list: A list of lists containing integers which represent
				the codepoints of the unicode representations of the
				glyphs.
		"""
		header = self._get_header()
		if header.version_psf == PSF1_VERSION:
			return self.__parse_unicode_table_psf1()
		if header.version_psf == PSF2_VERSION:
			return self.__parse_unicode_table_psf2()	
	
	def __split_psf1_by_separator(self, data):
		"""Split the unicode table of an old pc screen font by the
		seperator for unicode descriptions of an old pc screen font.

		Args:
			data (bytearray): The bytearray containing the unicode table
				of an old pc screen font.

		Returns:
			list: A list of bytearrays
		"""
		sep = bytearray([0xff, 0xff])
		if len(data) % 2:
			raise Exception()
		
		res = []
		current = bytearray()
		
		for i in range(0, len(data), 2):
			if data[i:i+2] == sep:
				res.append(current)
				current = bytearray()
			else:
				current += data[i:i+2]
		
		return res
		
	def __parse_unicode_table_psf1(self):
		"""Read the unicode descriptions of an old pc screen font out
		of the data of the importer.
		
		Returns:
			list		
		"""
		header = self._get_header()
		data = self._get_data()[
			header.get_length() * header.charsize + 4:
		]
		
		descriptions = []
				
		data = self.__split_psf1_by_separator(data)
		for d in data:
			descs = []
			d = d.split(bytearray([0xfe, 0xff]))
			for i in ByteArray.from_bytes(d[0]).to_ints(2):
				descs.append(i)
				
			if len(d) > 1:
				pass # @ToDo: Parse sequences
			descriptions.append(descs)

		return descriptions				
		
	def __parse_unicode_table_psf2(self):
		"""Read the unicode descriptions of a new pc screen font out of
		the data of the importer.
		
		Returns:
			list		
		"""
		header = self._get_header()
		data = self._get_data()[
			header.length * 
			header.charsize +
			header.headersize
			:
		]
		
		descriptions = []
		data = data.split(bytearray([PSF2_SEPARATOR]))[:-1]
		for d in data:
			descs = []
			d = d.split(bytearray([PSF2_STARTSEQ]))
			for i in d[0].decode('utf8'):
				descs.append(ord(i))
				
			if len(d) > 1:
				pass # @ToDo: Parse sequences
			
			descriptions.append(descs)
		
		return descriptions
		
	def _build_glyph(self, glyph, n):
		"""Read the bitmap of a glyph out of the data of the importer.
		
		Args:
			glyph (Glyph): The glyph to asign the bitmap to
			n (int): The index of the bitmap in the data		
		"""
		header = self._get_header()
		
		if header.version_psf == PSF1_VERSION:
			start = n * header.charsize + 4
			end = (n + 1) * header.charsize + 4
			glyph.set_data_from_bytes(
				ByteArray.from_bytes(self._get_data()[start:end])
			)
		elif header.version_psf == PSF2_VERSION:
			start = n * header.charsize + header.headersize
			end = (n + 1) * header.charsize + header.headersize
			glyph.set_data_from_bytes(
				ByteArray.from_bytes(self._get_data()[start:end])
			)
	
class PsfHeader(ABC):
	"""This class is the base for a header for the PC Screen Font
	
	Args:
		version (int): The version of the PC Screen Font. Should be
			PSF1_VERSION or PSF2_VERSION
		size (list of 2 integers): The size of every glyph of the font.
			The first value is the width and the second the height
	"""
	def __init__(self, version, size):
		self.version_psf = version
		self.magic_bytes = []
		self.mode = 0
		self.charsize = 0
		
		self.version = 0
		self.headersize = 0
		self.flags = 0
		self.length = 0
		self.height = 0
		self.width = 0
		
		self.size = size
		
	@abstractmethod	
	def has_unicode_table(self):
		"""Check wether the font has an unicode table or not
		
		Returns:
			bool: True if the font has an unicode table else False
		"""
		pass
		
	@abstractmethod
	def get_length(sefl):
		"""Get the number of glyphs the font has. For psf this value is
		either 256 or 512 and for psf2 variable.
		
		Returns:
			int: The number of glyphs the font has
		"""
		pass
			
class PsfHeaderv1(PsfHeader):
	"""This class represents the header for the pc screen font.
	
	Args:
		size (list of 2 integers): The size of every glyph of the font.
			The first value is the width and the second the height
	"""
	def __init__(self, size):
		PsfHeader.__init__(self, PSF1_VERSION, size)
		for byte in PSF1_MAGIC_BYTES:
			self.magic_bytes.append(Byte.from_int(byte))
		
		if (size[0] != 8):
			raise Exception("Error, for PSF1 the font width must be 8")
		self.charsize = size[1]
		self.mode = 0
	
	def set_mode(self, mode):
		"""Set one or more modes of the PSF1.
		
		Args:
			mode (int): A Number with the bits for the desired modes
				set.		
				
		Notes:
			Allowed modes are
			PSF1_MODE512    = 0x01
			PSF1_MODEHASTAB = 0x02
			PSF1_MODEHASSEQ = 0x04
			PSF1_MAXMODE    = 0x05
		"""
		if mode > 5:
			raise Exception("Error, undefined bits set in PSF1 mode")
		self.mode |= mode
		
	def unset_mode(self, mode):
		"""Unset one or more modi of the PSF1
		
		Args:
			mode (int): A number with the bits for the desired modes
				set.
		
		Notes:
			For allowed modes see the PsfHeaderv1.set_mode method
			Passing 0 to this method has no effect.
		"""
		if mode > 7:
			raise Exception("Error, undefined bits unset in PSF1 mode")
		if mode:
			self.mode |= ~mode
		
	def has_unicode_table(self):
		"""Determine wether the font has an unicode table or not.
		
		Returns:
			bool: True if the font has an unicode table else False		
		"""
		return ( self.mode & PSF1_MODEHASTAB or
			self.mode & PSF1_MODEHASSEQ )
			
	def get_length(self):
		"""Get the number of glyphs the font has.
		
		Returns:
			int: The number of glyphs the font has.		
		"""
		return 512 if self.mode & PSF1_MODE512 else 256

class PsfHeaderv2(PsfHeader):
	"""This class represents the header for the pc screen font 2.
	
	Args:
		size (list of 2 integers): The size of every glyph of the font.
			The first value is the width and the second the height
	"""
	def __init__(self, size):
		PsfHeader.__init__(self, PSF2_VERSION, size)
		for byte in PSF2_MAGIC_BYTES:
			self.magic_bytes.append(Byte.from_int(byte))
		self.version = PSF2_MAXVERSION
		self.headersize = 32	# Values are encoded as 4byte integers
		self.flags = 0
		self.length = 0
		self.width = size[0]
		self.height = size[1]
		self.charsize = size[1] * ((size[0]+7) // 8)

	def set_length(self, length):
		"""Set the number of glyphs of the font
		
		Args:
			length (int): Number of glyphs to set
		"""
		self.length = length

	def set_flags(self, flags):
		"""Set one or more flags of the PSF2.
		
		Args:
			flags (int): Number with the bits for the desired flags set.
			
		Notes:
			The only allowed flag is PSF2_HAS_UNICODE_TABLE = 0x1.
			You could pass 0 to this method, but it has no effect
		"""
		if flags not in (0, PSF2_HAS_UNICODE_TABLE):
			raise Exception("Error, undefined bits set in PSF2 flags")
		self.flags |= flags

	def unset_flags(self, flags):
		"""Unset one or more flags of the PSF2.
		
		Args:
			flags (int): Number with the bits for the desired flags set.
			
		Notes:
			The only allowed flag is PSF2_HAS_UNICODE_TABLE = 0x1.
			You could pass 0 to this method, but it has no effect
		"""
		if flags not in (0, PSF2_HAS_UNICODE_TABLE):
			raise Exception("Error, undefined bits set in PSF2 flags")
		if flags:
			self.flags |= flags
			
	def has_unicode_table(self):
		"""Determine wehter the font has an unicode table or not.
		
		Returns:
			bool: True if the font has an unicode table else False
		"""
		return self.flags & PSF2_HAS_UNICODE_TABLE
	
	def get_length(self):
		"""Get the number of glyphs the font has.
		
		Returns:
			int: The number of glyphs the font has.		
		"""
		return self.length

class PcScreenFont(object):
	"""This class represents a pc screen font
	
	The font contains zero or more glyphs. A glyph is a bitmap of a
	character with unicode values describing the bitmap. The font
	accesses its glyphs by the primary codepoint assigned to the glyph.
		
	Arguments:
		header (PsfHeader): the header of the font
	"""
	def __init__(self, header):
		self.header = header
		self.glyphs = {}
		self.size = header.size
	
	def has_unicode(self):
		"""This function should be used to determine wether the font 
		has an unicode table or not.
			
		Returns:
			bool: True if it has an unicode table else False
		"""
		return self.header.has_unicode_table()
			
	def get_header(self):
		"""Get the header of the font.
		
		Returns:
			PsfHeader: The header of the font		
		"""
		if self.header.version_psf == PSF2_VERSION:
			if self.header.has_unicode_table():
				self.header.set_length(len(self.glyphs))
			else:
				self.header.set_length(self.__len__())
			
		return self.header
			
	def get_glyph(self, codepoint):
		"""Get a glyph of the font by its primary codepoint
		If the font does not have a glyph with the given codepoint as
		primary or additional unicode representation, then a new glyph
		with the given codepoint as primary representation gets added
		to the font and returned.
		
		Args:
			codepoint (int) : the codepoint for the glyph
		
		Returns
			Glyph :	glyph which is represented by the given codepoint
		
		"""
		for glyph in self.glyphs.values():
			if glyph.has_unicode_representation(codepoint):
				return glyph
		glyph = Glyph(self.size)
		glyph.add_unicode_representation(codepoint)
		self.glyphs[codepoint] = glyph
		return glyph
		
	def get_glyphs(self):
		"""Get a dictionary with all glyphs of the font.
		
		Returns:
			dict: A dictionary with the scheme
				{ primary unicode representation : glyph }
		"""
		return self.glyphs.copy()
		
	def update_unicode_representation(self, primary_cp, old_cp, new_cp):
		"""Updates the unicode representation of a glyph
		
		Args:
			primary_cp (int) : The primary codepoint of the glyph
			old_cp (int) : The old value of the unicode representation,
				which should be updated
			new_cp (int) : The new value of the unicode representation,
				which should be updated
		
		Notes:
			If the old_cp is equal to the primary_cp, the the primary
			codepoint of the glyph will be updated
		"""
		if old_cp == new_cp:
			return
		if primary_cp == old_cp:
			self.glyphs[new_cp] = self.glyphs[old_cp]
			del self.glyphs[old_cp]
			self.glyphs[new_cp].update_unicode_representation(old_cp,
									new_cp)
			return
		self.glyphs[primary_cp].update_unicode_representation(old_cp,
									new_cp)
		
	def remove_glyph(self, codepoint):
		"""Remove a glyph from the font
		
		Args:
			codepoint (int) : The primary codepoint of the glyph which
				should be removed
		"""
		if codepoint in self.glyphs.keys():
			del self.glyphs[codepoint]
			
	def __len__(self):
		"""Get the lenght of the font, aka the largest primary codepoint
		of a glyph plus one.
		
		Returns:
			int: the len of the font
		"""
		if self.glyphs:
			return max(self.glyphs.keys()) + 1
		return 0
	
	def __str__(self):
		data = u""
		for i in self.glyphs.keys():
			data += "\n%d : (%s)\n" % (i, get_unicode_str(i))
			data += " -----------\n"
			data += repr(self.glyphs[i])
		return data
	
	def __repr__(self):
		return self.__str__()
			

class Glyph(object):
	"""This class represents a glyph of the pc screen font.
	A glyph consists of a bitmap (the data) and unicode representations
	describing the bitmap.
	
	Args:
		size (tuple(int width, int height)) : size of the bitmap representing the
			character
	"""
	def __init__(self, size):
		"""self.data is a list containing y lists with x elements, where
		x is the width of the glyph an y the height.
		Therefore the correct way to iterate over self.data is:
		
		for row in self.data:
			for bit in row:
				...		
		"""
		self.data = [[0 for i in range(size[0])]
						for j in range(size[1])]
		self.touched = False
		self.width = size[0]
		self.height = size[1]
		self.unicode_representations = []
		
	def add_unicode_representation(self, codepoint):
		"""Add an unicode value to the glyph
		
		Args:
			codepoint (int) : codepoint which should represent the glyph
		"""
		if codepoint not in self.unicode_representations:
			self.unicode_representations.append(codepoint)	
	
	def remove_unicode_representation(self, codepoint):
		"""Remove an unicode value from the glyph
		
		Args:
			codepoint (int) : codepoint which should be removed from the
				glyph
		"""
		if codepoint in self.unicode_representations:
			self.unicode_representations.remove(codepoint)
	
	def update_unicode_representation(self, old_cp, new_cp):
		"""Update the unicode representation of the glyph
		
		Args:
			old_cp (int) : Old value of the unicode representation which
				should be updated
			new_cp (int) : New value of the unicode representation which
				should be updated
		"""
		if new_cp in self.unicode_representations:
			#self.unicode_representations.remove(old_cp)
			return
		for i, cp in zip(range(len(self.unicode_representations)),
						 self.unicode_representations):
			if cp == old_cp:
				self.unicode_representations[i] = new_cp
	
	def has_unicode_representation(self, codepoint):
		"""Check if the glyph is represented by a codepoint
		
		Args:
			codepoint (int) : Codepoint to check
			
		Returns:
			bool : True if the glyph is represented by the given
				codepoint
		"""
		return codepoint in self.unicode_representations
	
	def get_unicode_representations(self):
		"""Get a list with all unicode representations of the glyph
		
		Returns:
			list: A list with all unicode representations of the glyph		
		"""
		return self.unicode_representations
	
	def copy_data(self, data):
		"""Update the bitmap with given data
		
		Args:
			data (list of lists with integers)) : the data to update the
				bitmap with. Each element of the data represents a row
				of the bitmap and each element in a row represents a
				pixel.
				The pixel is set, if its value equal 1.
		
		Notes:
			The dimensions of the data should equal the size of the
			glyph.
		"""
		for i, row in zip(range(self.height), data):
			for j, element in zip(range(self.width), row):
				self.data[i][j] = element
		
	def get_data(self):
		"""Get the bitmap of the glyph
		
		Returns:
			list : A list containing lists, which represent the rows of
				the bitmap. Each element of a row is a integer and
				represents a pixel.
				If the value of this integer is 1, then the pixel is set
		
		"""
		return self.data[:]
	
	def set_data_from_bytes(self, _bytes):
		"""Set the data of the bitmap from an array of byte objects
		
		Args:
			_bytes (a list of Bytes): the bytes to update the Bitmap
				with. 
		"""
		bits_per_line = int(self.width / 8) 
		bits_per_line += 1 if self.width % 8 else 0
		bits_per_line *= 8
		self.data = []
		bits = []
		for b in _bytes: bits += b.get_bits()
		for i in range(self.height):
			line = []
			for j in range(self.width):
				line.append(bits[i * bits_per_line + j])
			self.data.append(line)
		
	def get_size(self):
		"""Get the size of the glyph
		
		Returns:
			tuple: A tuple with the width of the glyph as first value
				and the height as second		
		"""
		return self.width, self.height
		
	def __repr__(self):
		"""Convert the glyph to a human readable string
		
		Returns:
			str: Human readable representation of the glyph		
		"""
		out = "Unicode representations:\n"
		for uc in self.unicode_representations:
			unistr = get_unicode_str(uc)
			out += "  %s : (%d) \n" % (unistr if unistr else "", uc)
		out += "\n"
		for i in self.data:
			for j in i:
				out += "#" if j else "."
			out += "\n"
		return out
