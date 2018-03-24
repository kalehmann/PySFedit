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
