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
This module provides classes for working with bytes.

There is a Byte class, which represents a single byte and allows you to
manipulate each of its bits. It supports comparisation with other bytes
and binary operations like and, or and xor.

And there is a ByteArray class for storing many instances of the Byte
class. You can create on from Bytes, or an integer, an array of
bits or a bytes-like object. The class supports addition of other
ByteArrays and can be exported to an array of integers or an string with
the nasm assembler syntax
"""

class Byte(object):
    """This class represents a byte

    Args:
        bits (list/tuple) (optional) : The bits of the byte. Should have
            a length of 8. All Elements should be either 0 or 1.
            The element at index 0 represents the most significant bit
            and the element at index 7 the least significant bit.
            The standard value for the bits is 8 times a zero

    Raises:
        ValueError if the length of bits is not 8 or if there is a bit
            with an other value than 0 or 1
    """
    def __init__(self, bits = None):
        if not bits:
            self.__bits = [0,0,0,0,0,0,0,0]
        else:
            if len(bits) != 8:
                raise ValueError("A byte should have 8 bits")
            for bit in bits:
                if bit not in (0, 1):
                    raise ValueError("A bit should be either 0 or 1")
            self.__bits = list(bits)

    @staticmethod
    def from_int(integer):
        """Creates a Byte object from an integer

        Args:
            integer (int) : The integer to create the byte from

        Returns:
            Byte ()

        Notes:
            Since the range of values of a byte is 0 to 255, if given
            integer is larger than 255, int(byte) will be integer % 255
            This method automatically converts the integer to a positive
            value
        """
        quotient = abs(integer % 256)    # Thats actually a remainder
        bits = []
        for _ in range(8):
            remainder = quotient % 2
            quotient = quotient // 2
            bits.append(remainder)
        bits = list(reversed(bits))
        return Byte(bits)

    def get_bits(self):
        """Get an array with the 8 bits of the byte.

        Returns:
            list: The bits of the byte
        """
        return self.__bits[:]

    def __getitem__(self, key):
        """Returns the bit with the given key as index

        Args:
            key (int) : The index of the bit. Should be between 0 and 7.
                7 returns the most significant bit and 0 the least
                significant

        Raises:
            IndexError if the key is not between 0 and 7
        """
        if not 0 <= key < 8:
            raise IndexError("The index of a bit in a byte should be " +
                    "between 0 and 7, %d given" % key)
        return self.__bits[key]

    def __setitem__(self, key, value):
        """Sets the bit with the given key to value

        Args:
            key (int) : The index of the bit. Should be between 0 and 7.
                7 sets the most significant bit and 0 the least
                significant
            value (int) : The value to set the bit to. Should be 0 or 1

        Raises:
            IndexError if the key is not between 0 and 7
            ValueError if the value is not zero or one

        """
        if not 0 <= key < 8:
            raise IndexError("The index of a bit in a byte should be " +
                    "between 0 and 7, %d given" % key)
        if value not in (0, 1):
            raise ValueError("A bit should be either 0 or 1")
        self.__bits[key] = value

    def __len__(self):
        """Returns the Number of bits a byte has.

        Returns:
            int : Always 8
        """
        return 8

    def __and__(self, other):
        """Performs a binary and between other and the byte

        Args:
            other (int or at least convertable to int): The value to
                perform the binary and with

        Returns:
            Byte : The new byte.
        """
        return Byte.from_int(int(other) & self.__int__())

    def __or__(self, other):
        """Performs a binary or between other and the byte

        Args:
            other (int or at least convertable to int): The value to
                perform the binary or with

        Returns:
            Byte : The new byte.
        """
        return Byte.from_int(int(other) | self.__int__())

    def __xor__(self, other):
        """Performs a binary xor between other and the byte

        Args:
            other (int or at least convertable to int): The value to
                perform the binary xor with

        Returns:
            Byte : The new byte.
        """
        return Byte.from_int(int(other) ^ self.__int__())

    def __int__(self):
        """Convert the byte to an integer value

        Returns:
            int : The integer value of the byte
        """
        integer = 0
        for i, bit in zip(range(7,-1,-1), self.__bits):
            integer += 2 ** i * bit
        return integer

    def __index__(self):
        return self.__int__()

    def hex(self):
        """Converts the byte to an hexdecimal value

        Returns:
            str : A string with the hexadecimal value of the byte
        """
        return "0x%02x" % self.__int__()

    def __eq__(self, other):
        """Checks if the int value of the byte is equal to the int value
        of another object

        Args:
            other (int or at least convertable to an integer) : The
                object to compare the byte with

        Returns:
            bool : True if the nt value of the byte is equal to the int
                value of the other object else False
        """
        if int(other) == self.__int__():
            return True
        return False

    def __le__(self, other):
        """Checks if the int value of the byte is lower or equal to the
        int value of another object

        Args:
            other (int or at least convertable to an integer) : The
                object to compare the byte with

        Returns:
            bool : True if the int value of the byte is lower or equal
                to the int value of the other object else False
        """
        if self.__int__() <= int(other):
            return True
        return False

    def __lt__(self, other):
        """Checks if the int value of the byte is lower than the int
        value of another object

        Args:
            other (int or at least convertable to an integer) : The
                object to compare the byte with

        Returns:
            bool : True if the int value of the byte is lower than the
                int value of the other object else False
        """
        if self.__int__() < int(other):
            return True
        return False

    def __ge__(self, other):
        """Checks if the int value of the byte is greater or equal to the
        int value of another object

        Args:
            other (int or at least convertable to an integer) : The
                object to compare the byte with

        Returns:
            bool : True if the int value of the byte is greater or equal
                to the int value of the other object else False
        """
        if self.__int__() >= int(other):
            return True
        return False

    def __gt__(self, other):
        """Checks if the int value of the byte is greater than the int
        value of another object

        Args:
            other (int or at least convertable to an integer) : The
                object to compare the byte with

        Returns:
            bool : True if the int value of the byte is greater than the
                int value of the other object else False
        """
        if self.__int__() > int(other):
            return True
        return False

    def __ne__(self, other):
        """Checks if the int value of the byte is not equal to the int
        value of another object

        Args:
            other (int or at least convertable to an integer) : The
                object to compare the byte with

        Returns:
            bool : True if the int value of the byte is not equal to the
                int value of the other object else False
        """
        if int(other) != self.__int__():
            return True
        return False

    def __str__(self):
        """Converts the byte to a string

        Returns:
            str : A string with the hexadecimal value of the bytess
        """
        return self.hex()

    def __bool__(self):
        """The __bool__ function is used for truth-testing

        Returns:
            bool : False if all bits of the byte are zeros else True
        """
        return self.__int__() != 0

class ByteArray(object):
    """As the name suggests this class is an array of bytes.

    Unlike the bytearray or bytes classes from python this class stores
    instances of the Byte class and has some nice extra features, such
    as exporting the data to a string with the nasm asm syntax or
    creating it from an array of bits.

    Args:
        _bytes (list): A list populated with instances of the Byte class
    """
    def __init__(self, _bytes=None):
        if _bytes:
            self.__check_bytes(_bytes)
            self.__bytes = _bytes
        else:
            self.__bytes = []

    @staticmethod
    def from_int(i, fixed_len=0):
        """Create the bytearray from an integer. There is an optional
        parameter named fixed_len, which can be used to truncate or
        expand the ByteArray to a fixed length.

        Args:
            i (int): The integer to create a ByteArray from
            fixed_len (int): Optional parameter for setting the length
                of the resulting ByteArray. The default value 0 means,
                that the length is not fixed

        Notes:
            The resulting ByteArray will be always little endian

        Examples:
            ByteArray.from_int(0x1234) results in a ByteArray with 0x34
                as first and 0x12 as second byte.

        Returns:
            Bytearray
        """
        bytevalues = []
        while i:
            remainder = i % 256
            i = int(i/256)
            bytevalues.append(Byte.from_int(remainder))
        if fixed_len and len(bytevalues) > fixed_len:
            bytevalues = bytevalues[:fixed_len]
        elif fixed_len and len(bytevalues) < fixed_len:
            for _ in range(fixed_len - len(bytevalues)):
                bytevalues.append(Byte.from_int(0))
        return ByteArray(bytevalues)

    @staticmethod
    def from_bit_array(bits):
        """Create the ByteArray from an array of bits.

        Args:
            bits (list): A list of integers (0s and 1s). The length of
                it should be a multiple of 8

        Returns:
            ByteArray
        """
        _bytes = []
        if len(bits) % 8:
            raise ValueError("The length of the bit array must be a " +
                    "multiple of 8")
        for i in range(int(len(bits) / 8)):
            _bytes.append(Byte(bits[i*8:(i+1)*8]))
        return ByteArray(_bytes)

    @staticmethod
    def from_bytes(_bytes):
        """Create the ByteArray from a bytes like object.

        Args:
            _bytes (either bytes or bytearray): The byte like object to
                create the ByteArray from

        Returns:
            ByteArray
        """
        byte_list = []
        for byte in _bytes:
            byte_list.append(Byte.from_int(byte))
        return ByteArray(byte_list)

    def __getitem__(self, index):
        """Get the Byte at the given index from the ByteArray

        Args:
            index (int): The index of the Byte to get in the ByteArray

        Returns:
            Byte: The Byte at the given index
        """
        return self.__bytes[index]

    def __setitem__(self, index, _byte):
        """Set the Byte of the ByteArray at the given index

        Args:
            index (int): The index of the Byte to set
            _byte (Byte): The Byte to set in the ByteArray
        """
        if type(_byte) != Byte:
            raise TypeError(
                "Cannot assign an object that is not an instance " +
                "of the Byte class to the ByteArray"
            )
        self._bytes[index] = _byte

    def __len__(self):
        """Get the number of Bytes this ByteArray has.

        Returns:
            int: The count of Bytes this ByteArray has.
        """
        return len(self.__bytes)

    def __add__(self, other):
        """Add two ByteArrays and return a new one containing the data
        from both.

        Args:
            other (ByteArray): The ByteArray which data should be added
                to the data of this ByteArray

        Returns:
            ByteArray: A new ByteArray containing the data of this
                ByteArray and the other.
        """
        if type(self) != type(other):
            raise NotImplementedError
        return ByteArray(self.__bytes + other.get_bytes())

    def __iadd__(self, other):
        """Add another ByteArray to this inplace.

        Args:
            other (ByteArray): The ByteArray which data should be added
                to this ByteArray in place.

        Returns:
            ByteArray: This ByteArray
        """
        if type(self) != type(other):
            raise NotImplementedError
        self.__bytes += other.get_bytes()
        return self

    def __eq__(self, other):
        """Compare this ByteArray to another and return wether they are
        equal or not.

        Args:
            other (ByteArray): The ByteArray to compare to this

        Returns:
            bool: Wether the ByteArrays are equal or not.
        """
        if type(self) != type(other):
            return False
        if self.__len__() != len(other):
            return False
        for i in range(self.__len__()):
            if int(self.__bytes[i]) != int(other.get_bytes()[i]):
                return False
        return True

    def add_byte(self, byte):
        """Append a single Byte to this ByteArray

        Args:
            byte (Byte): The Byte to append to this ByteArray
        """
        self.add_bytes([byte])

    def add_bytes(self, _bytes):
        """Append multiple Bytes to this ByteArray

        Args:
            _bytes (list): A list of Bytes to append to this ByteArray
        """
        self.__check_bytes(_bytes)
        for byte in _bytes:
            self.__bytes.append(byte)

    def get_bytes(self):
        """Get the Bytes of this ByteArray

        Returns:
            list: A list of the Bytes of this ByteArray
        """
        return self.__bytes

    def to_bytearray(self):
        """Convert this ByteArray to the python builtin bytearray class.

        Returns
            bytearray
        """
        ba = bytearray()
        for byte in self.__bytes:
            ba.append(int(byte))
        return ba

    def to_ints(self, bytes_per_int=1):
        """Convert this ByteArray to a list of integers.

        Args:
            bytes_per_int (int): The number of bytes the use for each
                integer. The length of this ByteArray should be
                divisible by this number.

        Returns:
            list
        """
        if self.__len__() % bytes_per_int:
            raise ValueError(
                ("The length of the bytearray %d is not divisible " +
                 "by %d") % (self.__len__(), bytes_per_int)
            )
        ints = []
        for i in range(int(self.__len__() / bytes_per_int)):
            _int = 0
            for j in range(bytes_per_int):
                _int += (int(self.__bytes[i * bytes_per_int + j]) *
                    (256 ** j))
            ints.append(_int)
        return ints

    def to_asm(self, label='' , linelength=80, indent=0, tab_size=4,
            end_with_linebreak = True):
        """Creates a string in the nasm assembler syntax from the
        ByteArray

        Args:
            label (string): The label for the data. Leave this blank to
                return only a string of hexadecimal values seperated by
                commas.
            linelength (int): The maximum number of characters per line
            indent (int): The number of tabulators to indent the
                resulting data with.
            tab_size (int): The size of a tabulator in spaces.
            end_with_linebreak (bool): Wether the data ends with a
                linebreak or not.

        Returns:
            string: A string containing the ByteArray converted to data
             in the nasm assembler syntax.
        """
        # Check if indent, linel ength and the length of the label are
        # matching.
        if len(label) + 5 + indent * tab_size > linelength:
            raise Exception(
                ("There is a missmatch between the max linelength " +
                 "(%d), the indent (%d) + tabulator size (%d) and " +
                 "the length of the label (%d)") %
                 (linelength, indent, tab_size, len(label)))

        line = " " * indent * tab_size
        declarator = ''
        if label:
            declarator = 'db '
            line += "%s: %s" % (label, declarator)
            indent += 1    # Increase indent for next line

        lines = []
        for i, byte in zip(range(len(self.__bytes)), self.__bytes):
            to_add = byte.hex()
            if i + 1 < len(self.__bytes):
                to_add += ", "
            if len(line) + len(to_add) > linelength:
                # create new line
                lines.append(line[:-2])    # remove the comma at the end
                                        # of the current line
                line = " " * indent * tab_size + declarator + to_add
            else:
                line += to_add
        lines.append(line)
        out = ""
        for line in lines:
            out += "%s\n" % line
        if not end_with_linebreak:
            out = out[:-1]
        return out

    def __int__(self):
        """Make an integer out of the ByteArray

        Returns:
            int: An integer made out of the Bytes of the ByteArray

        Notes:
            This method assumes, that the ByteArray is little endian
        """
        ival = 0
        for i, b in zip(range(self.__len__()), self.__bytes):
            ival += int(b) * (256 ** i)

        return ival

    def __check_bytes(self, _bytes):
        """Check if a list contains only Bytes. Raises an error
        otherwise.

        Args:
            _bytes (list): The list to check.

        Raises:
            TypeError: Raises an TypeArror if one object in the list is
                not an instance of the Byte class
        """
        for byte in _bytes:
            if type(byte) != Byte:
                raise TypeError("Expected _bytes to be instances of " +
                        "Byte")
