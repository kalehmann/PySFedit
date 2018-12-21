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

class SkeletonTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(SkeletonTest, self).__init__(*args, **kwargs)
        self.widget = None

    def setUp(self):
        self.widget = type(
                'Widget', (object,),
                    {

                        "destroy": lambda: None,
                        "doSomeThing": lambda:42
                    })

    def testSomething(self):
        self.assertEqual(self.widget.doSomeThing(), 42)

    def tearDown(self):
        self.widget.destroy()
