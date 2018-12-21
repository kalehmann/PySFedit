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
This is a package for working with pc screen fonts.

It contains classes representing pc screen fonts, their headers and
glyphs. Furthermore there are tools for exporting fonts to .asm or .psf
files and importing these.
"""

from abc import ABC, abstractmethod
import gzip

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

def get_str_form_unicode_sequence(sequence):
    """Get an unicode string with a combining character from a sequence
    of unicode values.

    Args:
        sequence (list): A list of integers representing unicode values

    Returns:
        str: A string with the combining character
    """
    _str = u""
    for value in sequence:
        _str += chr(value)

    return _str

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
        if self.__font.get_header().has_unicode_table():
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
        font = PcScreenFont(self.__header)

        for i in range(len(font)):
            glyph = font.get_glyph(i)
            self._build_glyph(glyph, i)

        if not self.__header.has_unicode_table():

            return font

        uc_descriptions = self._parse_unicode_descriptions()

        if len(uc_descriptions) != len(font):
            raise Exception(
                "The number of unicode descriptions of the font " +
                "does not match its length."
            )

        for (_, ud), descriptions in zip(font, uc_descriptions):
            if descriptions:
                for desc in descriptions:
                    if type(desc) == int:
                        ud.add_unicode_value(UnicodeValue(desc))
                        continue
                    seq = []
                    for value in desc:
                        seq.append(UnicodeValue(value))
                    ud.add_sequence(UnicodeSequence(seq))
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
                        i += 1
                        sequence = []
                        while ( i < len(data) and
                                data[i] != PSF1_SEPARATOR and
                                data[i] != PSF1_STARTSEQ):
                            sequence.append(data[i])
                            i+=1
                        descs.append(sequence)
                    else:
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
                    if data[i] == PSF2_STARTSEQ:
                        i += 1
                        seq_bytes = bytearray()
                        while ( i < len(data) and
                                data[i] != PSF2_SEPARATOR and
                                data[i] != PSF2_STARTSEQ):
                            seq_bytes.append(data[i])
                            i+=1
                        descs.append(
                            [ord(i)for i in seq_bytes.decode('utf8')]
                        )
                    else:
                        descs.append(data[i])
                    i += 1
                descriptions.append(descs)

        return descriptions

    def _build_glyph(self, glyph, n):
        """Read the bitmap of a glyph out of the data of the importer.

        Args:
            glyph (Glyph): The glyph to asign the bitmap to
            n (int): The index of the bitmap in the data
        """
        data = self.__asm.get_labels()["glyph_%d" % n]
        glyph.set_data_from_bytes(data)

class AsmExporter(Exporter):
    """Implementation for exporting a PCScreenFont to an asm file.
    For usage see the Exporter base class.

    Args:
        font (PcScreenFont): The font to export
    """
    def __init__(self, font):
        Exporter.__init__(self, font)
        self.__header = font.get_header()
        self.version =self.__header.version_psf

    def __glyph_to_asm(self, glyph, label):
        """Convert the bitmap of a glyph into a string with data in the
        nasm assembler syntax.

        Args:
            glyph (Glyph): The glyph to get the bitmap from
            label (str): The label to put before the data

        Returns:
            str: A string containing data in the nasm assembler syntax
                representing the bitmap of the given glyph.
        """

        return glyph.to_bytearray().to_asm(label)

    def _write_data(self, file_path, data):
        """Write the data made from the font into a file.

        Args:
            file_path (str): The path of the file to write the data
                into.
            data (str): The data to write into the file.
        """
        with open(file_path, "w") as f:
            f.write(data)

    def _build_header(self):
        """Convert the header of the font of the exporter into a string
        with the data from the header in the nasm assembler syntax.

        Returns:
            str: The string containing the data from the header of the
                font of the exporter.
        """
        data = "font_header:\n"
        if self.version == PSF1_VERSION:
            mode = self.__header.mode
            if self._get_font().has_sequences():
                mode = (mode & 1) | PSF1_MODEHASSEQ

            magic_bytes = ByteArray(self.__header.magic_bytes)
            data += magic_bytes.to_asm("magic_bytes")
            data += "mode: db %s\n" % hex(mode)
            data += "charsize: db %s\n\n" % hex(
                self.__header.charsize)

            return data

        magic_bytes = ByteArray(self.__header.magic_bytes)
        data += magic_bytes.to_asm("magic_bytes")
        data += "version: dd %s\n" % hex(self.__header.version)
        data += "headersize: dd %s\n" % hex(
                            self.__header.headersize)
        data += "flags: dd %s\n" % hex(self.__header.flags)
        data += "length: dd %s\n" % hex(self.__header.length)
        data += "charsize: dd %s\n" % hex(
                            self.__header.charsize)
        data += "height: dd %s\n" % hex(self.__header.height)
        data += "width: dd %s\n\n" % hex(self.__header.width)

        return data

    def _build_bitmaps(self):
        """Convert the bitmaps of the font of the exporter into a string
        with the data from the bitmaps in the nasm assembler syntax.

        Returns:
            str: The string containing the data from the bitmaps of the
                font of the exporter.
        """
        data = "font_bitmaps:\n"
        font = self._get_font()
        if self.__header.has_unicode_table():
            for i, (glyph, _) in zip(range(len(font)), font):
                data += self.__glyph_to_asm(glyph, "glyph_%d" % i)

            return data

        glyph_count = self.__header.get_length()

        for i in range(glyph_count):
            glyph = font.get_glyph(i)
            data += self.__glyph_to_asm(glyph, "glyph_%d" % i)

        return data

    def _build_unicode_table(self):
        """Convert the unicode table of the font of the exporter into a
        string with the data from the unicode table in the nasm
        assembler syntax.

        Returns:
            str: The string containing the data from the unicode table
                of the font of the exporter.
        """
        data = "unicode_table:\n"
        font = self._get_font()
        if self.version == PSF1_VERSION:
            glyph_count = self.__header.get_length()
            for (glyph, description), i in zip(font, range(len(font))):
                _bytes = ByteArray()
                for uc in description.unicode_values:
                    _bytes += ByteArray.from_int(int(uc), 2)
                for seq in description.sequences:
                    _bytes += ByteArray.from_int(0xFFFE, 2)
                    for uc in seq.values:
                        _bytes += ByteArray.from_int(int(uc), 2)
                _bytes += ByteArray.from_int(0xFFFF, 2)
                data += _bytes.to_asm('Unicodedescription%d' % i)

            return data
        # psf2
        for (glyph, description), i in zip(font, range(len(font))):
            _bytes = ByteArray()
            for uc in description.unicode_values:
                _bytes += ByteArray.from_bytes(str(uc).encode('utf8'))
            for seq in description.sequences:
                _bytes += ByteArray.from_int(0xFE, 1)
                seq_str = u""
                for uc in seq.values:
                    seq_str += str(uc)
                _bytes += ByteArray.from_bytes(seq_str.encode('utf8'))
            _bytes += ByteArray.from_int(0xFF, 1)
            data += _bytes.to_asm('Unicodedescription%d' % i)

        return data

class PsfExporter(Exporter):
    """Implementation for exporting a PCScreenFont to a psf file.
    For usage see the Exporter base class.

    Args:
        font (PcScreenFont): The font to export
    """
    def __init__(self, font):
        Exporter.__init__(self, font)
        self.__header = font.get_header()
        self.version = self.__header.version_psf

    def int_to_bytes(self, n):
        """Convert an integer to a bytearray with a lenght of 4.

        Args:
            n (int): The integer to convert to a bytearray.

        Returns:
            bytearray: The bytearray created from the integer.

        Notes:
            The resulting bytearray will be little endian.
        """
        bts = []
        if 0 <= n <= 0x100 ** 4 - 1:
            for i in range(4):
                bts.append(n % 0x100)
                n = n // 0x100
        return bytearray(bts)

    def glyph_to_bytearray(self, glyph):
        """Convert the bitmap from a glyph to a bytearray.

        Args:
            glyph (Glyph): The glyph to get the bitmap which should be
                converted to a bytearray from.

        Returns:
            bytearray: The bytearray built from the bitmap of the glyph.
        """


        return glyph.to_bytearray().to_bytearray()

    def _write_data(self, file_path, data):
        """Write the data made from the font into a file.

        Args:
            file_path (str): The path of the file to write the data
                into.
            data (bytearray): The data to write into the file.
        """
        with open(file_path, "wb") as f:
            f.write(data)

    def _build_header(self):
        """Convert the header of the font of the exporter into a
        bytearray.

        Returns:
            bytearray: The bytearray containing the data from the header
                of the font of the exporter.
        """
        _bytes = bytearray()
        for i in self.__header.magic_bytes:
            _bytes.append(i)
        if self.version == PSF1_VERSION:
            mode = self.__header.mode
            if self._get_font().has_sequences():
                mode = (mode & 1) | PSF1_MODEHASSEQ
            _bytes.append(mode)
            _bytes.append(self.__header.charsize)
        elif self.version == PSF2_VERSION:
            _bytes += self.int_to_bytes(self.__header.version)
            _bytes += self.int_to_bytes(self.__header.headersize)
            _bytes += self.int_to_bytes(self.__header.flags)
            _bytes += self.int_to_bytes(self.__header.length)
            _bytes += self.int_to_bytes(self.__header.charsize)
            _bytes += self.int_to_bytes(self.__header.height)
            _bytes += self.int_to_bytes(self.__header.width)

        return _bytes

    def _build_bitmaps(self):
        """Convert the bitmaps of the font of the exporter into a
        bytearray.

        Returns:
            bytearray: The bytearray containing the bitmaps from the
                font from the exporter.
        """
        _bytes = bytearray()
        font = self._get_font()
        if self.__header.has_unicode_table():
            for glyph, _ in font:
                _bytes += self.glyph_to_bytearray(glyph)

            return _bytes

        # Has no Unicode table
        glyph_count = self.__header.get_length()

        for i in range(glyph_count):
            glyph = font.get_glyph(i)
            _bytes += self.glyph_to_bytearray(glyph)

        return _bytes

    def _build_unicode_table(self):
        """Convert the unicode table from the font from the exporter
        into a bytearray.

        Returns:
            bytearray: The bytearray containing the unicode table from
                the font from the exporter.
        """
        ba = ByteArray()
        font = self._get_font()
        if self.version == PSF1_VERSION:
            glyph_count = self.__header.get_length()
            for glyph, ud in font:
                _bytes = ByteArray()
                for uc in ud.unicode_values:
                    _bytes += ByteArray.from_int(int(uc), 2)
                for seq in ud.sequences:
                    _bytes += ByteArray.from_int(0xFFFE, 2)
                    for uc in seq.values:
                        _bytes += ByteArray.from_int(int(uc), 2)
                _bytes += ByteArray.from_int(0xFFFF, 2)
                ba += _bytes
        else:   # psf2
            for glyph, ud in font:
                _bytes = ByteArray()
                for uc in ud.unicode_values:
                    _bytes += ByteArray.from_bytes(
                        str(uc).encode('utf8'))
                for seq in ud.sequences:
                    _bytes += ByteArray.from_int(0xFE, 1)
                    seq_str = u''
                    for uc in seq.values:
                        seq_str += str(uc)
                    seq_bytes = bytes(seq_str, 'utf8')
                    _bytes += ByteArray.from_bytes(seq_bytes)
                _bytes += ByteArray.from_int(0xFF, 1)
                ba += _bytes

        return ba.to_bytearray()

class PsfImporter(Importer):
    """Implementation for importing a PCScreenFont from a psf file.
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
                for sequence in d[1:]:
                    descs.append(
                        ByteArray.from_bytes(sequence).to_ints(2)
                    )
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
                for sequence in d[1:]:
                    seq_str = sequence.decode('utf8')
                    seq = []
                    for i in seq_str:
                        seq.append(ord(i))
                descs.append(seq)

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

class PsfGzExporter(PsfExporter):
    """Implementation for exporting a PcScreenFont to a gzip compressed
    psf file. For usage see the Exporter base class.

    Args:
        font (PcScreenFont): The font to export
    """
    def export_to_data(self):
        """We simply override the export_to_data method of the psf
        exporter to compress our data before exporting.

        Returns:
            bytes: A bytes object with the compressed psf data.
        """
        data = super(PsfExporter, self).export_to_data()

        return gzip.compress(data)

class PsfGzImporter(PsfImporter):
    """Implementation for importing a PCScreenFont from a gzip
    compressed psf file.
    For usage see the Importer base class.

    Args:
        data (bytes): The data to build the font from
    """
    @classmethod
    def import_from_data(cls, data):
        """We simply override the import_to_data method of the psf
        importer to decompress our data before importing.

        Args:
            data (bytes): The binary data containing the compressed psf
                data.

        Returns:
            PcScreenFont: The font imported from the compressed data.
        """
        data = gzip.decompress(data)

        return PsfImporter.import_from_data(data)

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

        return bool( self.mode & PSF1_MODEHASTAB or
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
        self.headersize = 32    # Values are encoded as 4byte integers
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
    """This class represents a pc screen font.

    Args:
        header (PsfHeader): The header of the font
    """
    def __init__(self, header):
        self.__header = header
        self.__glyph_bitmaps = [
            GlyphBitmap(header.size)for _ in range(self.__len__())
        ]
        self.__unicode_info = [
            UnicodeDescription() for _ in range(self.__len__())
        ] if header.has_unicode_table() else None

    def has_unicode_table(self):
        """Get whether this font has an unicode table or not.

        Returns:
            bool: Whether the font has an unicode table or not
        """

        return self.__header.has_unicode_table()

    def has_sequences(self):
        """Get if any glyph bitmap of the font is described by an
        unicode sequence.

        Returns:
            bool: Whether any glyph bitmap of the font is described by
                an unicode sequence or not.
        """
        if not self.has_unicode_table():

            return
        for ud in self.__unicode_info:
            if ud.sequences:

                return True

        return False

    def get_header(self):
        """Get the header of this font.

        Returns:
            PsfHeader: The header of this font
        """

        return self.__header

    def add_glyph(self, index=-1):
        """Add a new glyph to the font.

        Args:
            index (int): The position where the new glyph should be
                added in the font. The default is -1 for adding the new
                glyph at the end of the font.

        Returns:
            tuple: A tuple with the bitmap of the newly added glyph and
                its unicode description or None if the font has no
                unicode table
            None: None gets returned when the font already has the
                maximum number of glyphs for the old psf format.
        """
        if (self.__header.version_psf == PSF1_VERSION and
            self.__header.get_length() == len(self.__glyph_bitmaps)):

            return None, None
        if index < 0:
            index = self.__len__()

        if index > self.__len__():
            raise ValueError("Index out of bounds")

        glyph = GlyphBitmap(self.__header.size)
        self.__glyph_bitmaps.insert(index, glyph)

        unicode_description = None
        if self.__header.has_unicode_table():
            unicode_description = UnicodeDescription()
            self.__unicode_info.insert(index, unicode_description)
        self.__header.length += 1

        return glyph, unicode_description

    def remove_glyph(self, index):
        """Remove a glyph from the font by its index.

        Notes:
            Can only remove glyphs from psf2

        Args:
            index (int): The index of the glyph in the font
        """
        if self.__header.version_psf == PSF1_VERSION:

            return

        if index >= self.__len__():

            return

        self.__glyph_bitmaps.pop(index)
        if self.__header.has_unicode_table():
            self.__unicode_info.pop(index)

        self.__header.length -= 1

    def get_glyph(self, index):
        """Get a glyph at the given position in the font.

        Args:
            index (int): The position of the glyph in the font.

        Returns:
            GlyphBitmap: The glyph at the given position in the font
        """
        if index >= self.__len__():
            raise ValueError("Glyph index out of bounds")

        return self.__glyph_bitmaps[index]

    def get_unicode_description(self, index):
        """Get the unicode description for a glyph at a given position
        of the font.

        Args:
            index (int): Position of the unicode description in the
                font

        Returns:
            UnicodeDescription: The unicode description
        """
        if index >= self.__len__():
            raise ValueError("Unicode description index out of bounds")

        if self.__header.has_unicode_table():

            return self.__unicode_info[index]

        return None

    def move_glyph(self, old_index, new_index):
        """Move a glyph in the font from the old index to the new index.

        Args:
            old_index (int): The current index of the glyph that should
                be moved.
            new_index (int): The new index of the glyph that should be
                moved.
        """
        glyph = self.__glyph_bitmaps.pop(old_index)
        self.__glyph_bitmaps.insert(new_index, glyph)

        if not self.__header.has_unicode_table():

            return

        description = self.__unicode_info.pop(old_index)
        self.__unicode_info.insert(new_index, description)

    def has_glyph_for_unicode_value(self, unicode_value):
        """Use this method to determine whether the font has a glyph for
        a given unicode value or not.

        Args:
            unicode_value (int): The unicode value

        Returns:
            bool: Whether an unicode description of a glyph in the font
                contains the unicode value or not
        """
        if not self.__header.has_unicode_table():

            return unicode_value < self.__len__()
        for unicode_description in self.__unicode_info:
            values = unicode_description.get_unicode_values()
            if unicode_value in values:

                return True

    def get_glyph_for_unicode_value(self, unicode_value):
        """Use this method to get a glyph bitmap for a given unicode
        value.

        Args:
            unicode_value (int): The unicode value

        Returns:
            GlyphBitmap: The glyph bitmap for the given unicode value,
                if the font has one
            None: gets returned if the font has no glyph bitmap for the
                given unicode value
        """
        if not self.__header.has_unicode_table():
            if unicode_value < self.__len__():

                return self.__glyph_bitmaps[unicode_value]

            return None
        for i in range(self.__len__()):
            unicode_description = self.__unicode_info[i]
            values = unicode_description.get_unicode_values()
            if unicode_value in values:

                return self.__glyph_bitmaps[i]

        return None

    def get_glyph_index(self, glyph):
        """Get the index of a glyph.

        Args:
            glyph (GlyphBitmap): The glyph

        Returns:
            int: The index of the glyph in the font
        """

        return self.__glyph_bitmaps.index(glyph)

    def __len__(self):
        """Get the number of glyphs and unicode descriptions this font
        contains.

        Returns:
            int: The number of glyphs this font has.
        """

        return self.__header.get_length()

    def __getitem__(self, key):
        """Get the glyph and unicode description for the given index.

        Args:
            key (int): The index of the glyph and its unicode
                description in the font.

        Returns:
            tuple: A tuple containing the glyph and its unicode
                description. The unicode description is None if the
                font has no unicode table.
        """
        if key >= self.__len__():
            raise AttributeError(
                "Error, index greather than the number of glyphs in " +
                "the font.")

        return (
            self.__glyph_bitmaps[key],
            self.__unicode_info[key]
                if self.__header.has_unicode_table() else None
        )

    def __iter__(self):
        """Get an interator for the font

        Returns:
            generator: An iterator for the font
        """
        for i in range(self.__len__()):
            yield self[i]

class GlyphBitmap(object):
    """This class represents the bitmap of a glyph

    Args:
        size (tuple): A tuple containing the width and the height of the
            glyph bitmap.
    """
    def __init__(self, size):
        self.__size = size
        self.__width = size[0]
        self.__height = size[1]
        self.__data = [
            [0 for _ in range(size[0])] for _ in range(size[1])
        ]

    def get_size(self):
        """Get the size of the glyph in pixels.

        Returns:
            tuple: A tuple with the width of the bitmap as first value
                and the height as second.
        """
        return tuple(self.__size)

    def get_data(self):
        """Get the data representing the bitmap of the glyph.

        The bitmap of the glyph is represented by a 2 dimensional list.

        Examples:
            data = glyph.get_data()
            width, height = glyph.get_size()

            for x in range(width):
                for y in range(height):
                    data[y][x]
            ...
            for row in glyph.get_data():
                for pixel in row:
                    ...

        Returns:
            list: A list of lists, where each list represents a row of
                the glyph bitmap and contains integers representing
                each pixel.
        """

        return self.__data

    def set_data(self, data):
        """Set the data representing the bitmap of the glyph.

        Args:
            data (list): A list of lists, where each list represents a
                row of the glyph bitmap and contains integers
                representing each pixel. Its dimensions should equal the
                size of the glyph bitmap
        """
        if (len(data) != len(self.__data) or
            len(data[0]) != len(self.__data[0])):
            raise ValueError(
                "Expected data to have the same dimensions as the " +
                "GlyphBitmap"
            )
        for j in range(self.__height):
            for i in range(self.__width):
                self.__data[j][i] = data[j][i]

    def set_data_from_bytes(self, _bytes):
        """Set the data of the bitmap from bytes

        Args:
            _bytes (ByteArray/bytes/bytearray): the bytes to update the
                Bitmap with.
        """
        if type(_bytes) != ByteArray:
            _bytes = ByteArray.from_bytes(_bytes)

        bits_per_line = self.__width // 8
        bits_per_line += 1 if self.__width % 8 else 0
        bits_per_line *= 8
        self.__data.clear()
        bits = []
        for b in _bytes: bits += b.get_bits()
        for i in range(self.__height):
            line = []
            for j in range(self.__width):
                line.append(bits[i * bits_per_line + j])
            self.__data.append(line)

    def to_bytearray(self):
        """Get a byte array from the data of the glyph bitmap.

        Returns:
            psflib.ByteArray: The byte array from the data of the glyph
                bitmap.
        """

        ba = ByteArray()
        for row in self.get_data():
            if len(row) % 8:
                row = row[:]
                while len(row) % 8:
                    row.append(0)
            ba +=  ByteArray.from_bit_array(row)

        return ba


class UnicodeDescription(object):
    """This class represents the unicode description of a glyph in a pc
    screen font.

    It can hold unicode values and/or sequences of unicode value
    describing the glyph.
    """
    def __init__(self):
        self._unicode_values = []
        self._sequences = []

    @property
    def unicode_values(self):
        return self._unicode_values

    @unicode_values.setter
    def unicode_values(self, values):
        self._unicode_values.clear()
        for value in values:
            self.add_unicode_value(value)

    def add_unicode_value(self, value):
        """Add an unicode value to the description.

        Args:
            value: The unicode value to add to the description
        """
        if type(value) == UnicodeValue:
            if int(value) not in self.codepoints:
                self._unicode_values.append(value)

            return
        if value not in self.codepoints:
            self._unicode_values.append(UnicodeValue(value))

    def remove_unicode_value(self, value):
        """Remove an unicode value from the description

        Args:
            value: The unicode value or its codepoint to remove from the
                   description
        """
        for v in self._unicode_values:
            if int(value) == int(v):
                self._unicode_values.remove(v)

                return

    @property
    def codepoints(self):
        """Get a list of the codepoints of all unicode values of the unicode
        description.

        Returns:
            list: A list of the codepoints of all unicode values of the
                  description.
        """
        return [int(v) for v in self._unicode_values]

    def add_sequence(self, sequence):
        """Add a sequence of unicode values to the description

        Args:
            sequence (list): The sequence of unicode values to add to
                             the description
        """
        if sequence not in self._sequences:
            self._sequences.append(sequence)

    def remove_sequence(self, sequence):
        """Remove a sequence of unicode values from the description

        Args:
            sequence (list): The sequence of unicode values to remove
                from the description
        """
        if sequence in self._sequences:
            self._sequences.remove(sequence)

    @property
    def sequences(self):
        """Get a list with all sequences from the description

        Returns:
            list: A list with all sequences from the description
        """
        return self._sequences

    @sequences.setter
    def sequences(self, sequences):
        self._sequences.clear()
        for seq in sequences:
            self.add_sequence(seq)

    @property
    def seq_codepoints(self):
        return [s.codepoints for s in self._sequences]

class UnicodeValue(object):
    """This class represents a single unicode value.

    Args:
        value (int): The codepoint of the unicode value
    """
    def __init__(self, value):
        self.value = value

    @classmethod
    def new_from_string(cls, string):
        """Use this method to create an UnicodeValue instance from a
        string.

        Args:
            string (str): The string to create the UnicodeValue instance
                          from.

        Returns:
            UnicodeValue: The UnicodeValue instance from the string.
        """
        return cls(ord(string))

    def get_printable(self):
        """Get a printable representation of the unicode value.

        This method returns a char from the unicode value.

        Returns:
            str: A string with the char from the unicode value.
        """
        return chr(self.value)

    def __int__(self):
        """Get an integer representation of the unicode value (its
        codepoint)

        Returns:
            int: The codepoint of the unicode value
        """
        return self.value

    def __eq__(self, other):
        if type(other) == type(self):
            return self.value == other.value
        return int(self) == other

    def __str__(self):
        """Get a printable representation of the unicode value.

        This method returns a char from the unicode value.

        Returns:
            str: A string with the char from the unicode value.
        """
        return self.get_printable()

class SequenceTooShortException(Exception):
    """Exception for trying to create an unicode sequence with less than
    two values.
    """
    MESSAGE = ("Error, an unicode sequence should at least consist of "
               "2 unicode values"
               )

    def __init__(self):
        super().__init__(self, self.MESSAGE)

class UnicodeSequence(object):
    """This class represents a sequence of combining unicode values.

    Args:
        values (list): A list of either the codepoints of the unicode
                       values or UnicodeValue instances.
    """
    def __init__(self, values):
        self._values = []
        self.values = values

    @property
    def values(self):
        """Get the combining unicode values of the sequence.

        Returns:
            list: A list of UnicodeValues
        """
        return self._values

    @values.setter
    def values(self, values):
        """Set the combining unicode values of the sequence.

        Args:
            values (list): A list of either the codepoints of the unicode
                           values or UnicodeValue instances.
        """
        if len(values) < 2:

            raise SequenceTooShortException()
        self._values.clear()
        for value in values:
            if type(value) == UnicodeValue:
                self._values.append(value)

                continue
            self._values.append(UnicodeValue(value))

    @property
    def codepoints(self):
        return [int(v) for v in self._values]

    def get_printable(self):
        """Get a string representation of the sequence.

        Returns:
            str: The string representation of the sequence.
        """
        _str = u""
        for value in self.values:
            _str += str(value)

        return _str

    def __eq__(self, other):
        if type(self) != type(other):
            raise NotImplementedError
        if sorted(self.codepoints) == sorted(other.codepoints):
            return True
        return False

    def __str__(self):
        return self.get_printable()
