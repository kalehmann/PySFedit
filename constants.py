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
This module contains some constants like paths to ressources.
"""

from os.path import dirname

PROJECT_ROOT = dirname(__file__) + '/'
RES_DIR = PROJECT_ROOT + 'res/'
IMG_DIR = RES_DIR + 'img/'
LOCALE_DIR = RES_DIR + 'locale/'

PROJECT_STORAGE = {}

def get_storage(_object):
	if type(_object) == type:
		name = _object.__name__
	else:
		name = type(_object).__name__
	if name not in PROJECT_STORAGE:
		PROJECT_STORAGE[name] = Storage()
	
	return PROJECT_STORAGE[name]

class Storage(dict):
	def __init__(self, *args, **kwargs):
		super(Storage, self).__init__(*args, **kwargs)
		self.__changed_callbacks = {}
	
	def register_changed_callback(self, key, callback):
		if not key in self.__changed_callbacks:
			self.__changed_callbacks[key] = []
		
		self.__changed_callbacks[key].append(callback)
	
	def register(self, key, default):
		if not key in self:
			self[key] = default
	
	def __setitem__(self, key, value):
		if key in self.__changed_callbacks:
			for cb in self.__changed_callbacks[key]:
				cb(key, value)
		
		super(Storage, self).__setitem__(key, value)
