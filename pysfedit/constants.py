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
This module contains some constants like paths to ressources.
"""

from os.path import dirname, abspath
import inspect
from pathlib import Path

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GdkPixbuf
from gi.repository import Gdk
from gi.repository import GLib
import pkg_resources
import PIL

directory = Path(dirname(
        abspath(inspect.getfile(inspect.currentframe()))
        )
)

PROJECT_ROOT = directory.parent.__str__() + '/..'
RES_DIR = PROJECT_ROOT + 'res/'
IMG_DIR = RES_DIR + 'img/'
LOCALE_DIR = RES_DIR + 'locale/'

def get_pixbuf_from_file(path):
    img_fp = pkg_resources.resource_stream(__name__, path)
    img = PIL.Image.open(img_fp).convert("RGBA")
    img.load()
    data = img.tobytes()
    w, h = img.size
    data = GLib.Bytes.new(data)
    return GdkPixbuf.Pixbuf.new_from_bytes(
        data, GdkPixbuf.Colorspace.RGB, True, 8, w, h, w * 4
    )

class Storage(dict):
        """A key value based storage for application data.

        This is a storage for data of the application. It is intended to
        have on instance per class that needs a storage.

        """

        PROJECT_STORAGE = {}

        def __init__(self, *args, **kwargs):
                super(Storage, self).__init__(*args, **kwargs)
                self.__changed_callbacks = {}

        @classmethod
        def get(cls, _object):
                """Get the storage for a class.

                Args:
                        _object: Class or instance of the class to get a storage for.

                Returns:
                        Storage: The storage instance for the class
                """
                if type(_object) == type:
                        name = _object.__name__
                else:
                        name = type(_object).__name__
                if name not in cls.PROJECT_STORAGE:
                        cls.PROJECT_STORAGE[name] = cls()

                return cls.PROJECT_STORAGE[name]

        @classmethod
        def reset(cls):
                cls.PROJECT_STORAGE.clear()

        def register_changed_callback(self, key, callback):
                if not key in self.__changed_callbacks:
                        self.__changed_callbacks[key] = []

                self.__changed_callbacks[key].append(callback)

        def register(self, key, default):
                if not key in self:
                        self[key] = default

        def __setitem__(self, key, value):
                super(Storage, self).__setitem__(key, value)
                if key in self.__changed_callbacks:
                        for cb in self.__changed_callbacks[key]:
                                cb(key, value)
