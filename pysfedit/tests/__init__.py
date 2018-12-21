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


import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class MockedParent(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title='MockedParentWindow')

class ChangedCallback(object):
        def __init__(self, test_case, expected_key, expected_value):
            self.called = False
            self._test_case = test_case
            self._expected_key = expected_key
            self._expected_value = expected_value

        def __call__(self, key, value):
            self.called = True
            self._test_case.assertEqual(self._expected_key, key)
            self._test_case.assertEqual(self._expected_value, value)
