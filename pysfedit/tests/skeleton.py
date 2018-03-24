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
