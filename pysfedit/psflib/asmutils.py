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
This module provide a parser for data stored in the nasm assembler
syntax. It parses string with the assembler data and provides the data
foreach label as ByteArray.
"""

import re
from collections import OrderedDict
from .byteutils import Byte, ByteArray

class AsmParser(object):
    """This class exists to import and parse data from the nasm
    assembler format.

    Args:
        asm_string (string): The raw nasm assembler code

    Notes:
        All labels found in the code are accesible as attributes at an
        instance of this class
    """
    __LABEL_EXPR = re.compile('([a-zA-Z0-9_]+:)')
    # There are more operants for declaring initialized data, but we
    # just need these two
    __DECLARATORS_EXPR = re.compile('\\b(db|DB|dw|DW|dd|DD)')
    __HEXADECIMAL_EXPR = re.compile(
        '(0[x|h][0-9a-fA-F]+|[0-9a-fA-F]+h)')
    __OCTAL_EXPR = re.compile('(0[o|q][0-7]+|[0-7]+[o|q])')
    __BINARY_EXPR = re.compile(
        '(0[yb](?!_)[0-1_]+(?<!_)|(?!_)[0-1_]+(?<!_)[by])')
    __DECIMAL_EXPR = re.compile('(0d[0-9]+|[0-9]+d|[0-9]+)')
    __DECLARATOR_BYTES_LOWER = 'db'
    __DECLARATOR_WORDS_LOWER = 'dw'
    __DECLARATOR_DWORDS_LOWER = 'dd'


    def __init__(self, asm_string):
        self.__labels = OrderedDict()
        self.__parse_asm(asm_string)


    def get_labels(self):
        """This method returns all labels, which were found in the
        assembler code and their data as bytearrays.

        Returns:
            dict: A dictionary with the labels as keys and their data as
                values
        """
        return self.__labels

    def has_label(self, name):
        """This method can be used to determine wether the parsed asm
        code contains a label or name.

        Args:
            name (str): The name of the label to check

        Returns:
            bool: Wether the parsed code contains the label or not

        """
        return name in self.__labels

    def __getattr__(self, name):
        """This method allows you to access labels found in the code as
        class attributes
        """
        if name in self.__labels:
            return self.__labels[name]
        raise AttributeError

    def __split_n_cleanup(self, asm_string):
        """This method splits the nasm asm code before and after every label
        and removes linebreaks and tabs.

        Returns:
            list: A list with the splitted code
        """
        data = self.__LABEL_EXPR.split(asm_string)
        i = 0
        while i < len(data):
            data[i] = data[i].strip()\
                .replace('\t', ' ')\
                .replace('\n', ' ')
            if not data[i]: del data[i]
            i += 1

        return data

    def __make_bytearray(self, data_string):
        """This method parses a string with declared initialized data
        (see http://www.nasm.us/doc/nasmdoc3.html#section-3.2.1) and
        makes a bytearray out of it.

        Returns:
            ByteArray
        """
        data = self.__DECLARATORS_EXPR.split(data_string)

        i = 0

        ba = ByteArray()

        while i < len(data):
            if not data[i]:
                i +=1
                continue

            if None == self.__DECLARATORS_EXPR.search(data[i]):
                if (i == 0 or
                    None == self.__DECLARATORS_EXPR.search(data[i-1])):
                    raise Exception(
                        ("Error while parsing %s, could not extract " +
                         "values") % data_string)

            if data[i-1].lower() == self.__DECLARATOR_BYTES_LOWER:
                for j in self.__get_integers(data[i]):
                    ba.add_byte(Byte.from_int(j))
            elif data[i-1].lower() == self.__DECLARATOR_WORDS_LOWER:
                for j in self.__get_integers(data[i]):
                    ba += ByteArray().from_int(j, 2)
            elif data[i-1].lower() == self.__DECLARATOR_DWORDS_LOWER:
                for j in self.__get_integers(data[i]):
                    ba += ByteArray().from_int(j, 4)

            i += 1
        return ba


    def __get_integers(self, data_string):
        """This method parses integers from a string in many different
        formats (decimal, binary, octal, hexadecimal).
        For allowed notations see
        (http://www.nasm.us/doc/nasmdoc3.html#section-3.4.1)

        Args:
            data_string (str): A string with numbers seperated by
                commatas.

        Returns:
            list: A list with the integers extraced from the data_string
        """
        ints = []
        for i in data_string.replace(' ', '').split(','):
            if None != self.__BINARY_EXPR.match(i):
                i = i.replace('y', 'b').replace('_', '')
                ints.append(int(i, 2))
            elif None != self.__OCTAL_EXPR.match(i):
                i = i.replace('q', '').replace('o', '')
                ints.append(int(i, 8))
            elif None != self.__HEXADECIMAL_EXPR.match(i):
                i = i.replace('h', '')
                ints.append(int(i, 16))
            elif None != self.__DECIMAL_EXPR.match(i):
                i = i.replace('d', '')
                ints.append(int(i, 10))
            else:
                raise ValueError('Could not parse %s in %s as integer' %
                    (i, data_string))
        return ints

    def __parse_asm(self, asm_string):
        """This method parses an raw nasm assembler string and fills
        self.__labels

        Args:
            asm_string (str): The raw nasm assembler code
        """
        data = self.__split_n_cleanup(asm_string)

        labels = []

        i = 0
        while i < len(data):
            if self.__LABEL_EXPR.match(data[i]):
                labels.append(data[i])
            else:
                ba = self.__make_bytearray(data[i])
                for l in labels:
                    self.__labels[l.replace(':', '')] = ba
                labels = []
            i += 1
