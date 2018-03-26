import unittest
from . import ChangedCallback
from .. import constants as c

class StorageTest(unittest.TestCase):
	class Foo(object): pass

	def __init__(self, *args, **kwargs):
		super(StorageTest, self).__init__(*args, **kwargs)
		
	def tearDown(self):
		c.Storage.reset()
		
	def test_get_storage(self):
		foo = self.Foo()
		
		s1 = c.Storage.get(self.Foo)
		s2 = c.Storage.get(foo)
		
		self.assertEqual(s1, s2)

	def test_storage_register_key(self):
		s = c.Storage.get(self.Foo)
		s.register("MeaningOfEverything", 42)
		
		self.assertEqual(s["MeaningOfEverything"], 42)
	
	def test_storage_changed_callback(self):			
		s = c.Storage.get(self.Foo)
		changed_callback = ChangedCallback(self, "TestProperty",
												"test")
		
		s.register("TestProperty", None)
		s.register_changed_callback("TestProperty", changed_callback)
		s["TestProperty"] = "test"
		
		self.assertTrue(changed_callback.called)
		
