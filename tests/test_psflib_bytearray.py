import unittest
import psflib

BITS = [1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0]

class TestByteArray(unittest.TestCase):
	
	def test_from_bits(self):
		ba = psflib.ByteArray.from_bit_array(BITS)
		self.assertEqual(int(ba[0]), 255)
		self.assertEqual(int(ba[1]), 0)
		
		bits = BITS[1:]
		with self.assertRaises(ValueError):
			psflib.ByteArray.from_bit_array(bits)
			
	def test_initialisation(self):
		b1 = psflib.Byte()
	
		with self.assertRaises(TypeError):
			psflib.ByteArray([b1, object()])
			
	def test_to_asm(self):
		pass
