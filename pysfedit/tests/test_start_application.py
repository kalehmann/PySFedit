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


import unittest
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GLib
from .. import PySFeditWindow

class StartApplicationTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(StartApplicationTest, self).__init__(*args, **kwargs)
        self.window = None
        self.mainloop = None

    def setUp(self):
        self.mainloop = GLib.MainLoop()
        self.window = PySFeditWindow(self.mainloop)
        self.window.show_all()

    def test_start(self):
        self.assertIsNotNone(self.window.button_new)
        self.assertIsNotNone(self.window.button_import)

    def tearDown(self):
        self.window.destroy()
