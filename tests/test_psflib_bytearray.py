import unittest
import psflib

BITS = [1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0]

class TestByteArray(unittest.TestCase):
	
	def test_from_bits(self):
		ba = psflib.ByteArray.from_bit_array(BITS)
		self.assertEqual(int(ba[0]), 255)
		self.assertEqual(int(ba[1]), 0)
		
		# Test with only 15 bits
		bits = BITS[1:]
		with self.assertRaises(ValueError):
			psflib.ByteArray.from_bit_array(bits)
			
	def test_initialisation(self):
		b1 = psflib.Byte()
	
		with self.assertRaises(TypeError):
			psflib.ByteArray([b1, object()])
			
	def test_from_int(self):
		ba = psflib.ByteArray.from_int(255)
		self.assertEqual(ba.to_asm(), "0xff\n")
		ba = psflib.ByteArray.from_int(65535)
		self.assertEqual(ba.to_asm(), "0xff, 0xff\n")
		ba = psflib.ByteArray.from_int(7 ** 30)
		self.assertEqual(ba.to_asm(), "0x12, 0xa4, 0xe4, 0x15, 0xe1, 0xe1, 0xb3, 0x00, 0x00, 0x00, 0xd1\n")


	def test_addition(self):
		b = psflib.Byte.from_int
		ba1 = psflib.ByteArray([b(1), b(2)])
		ba2 = psflib.ByteArray([b(3), b(4)])
		
		self.assertEqual((ba1 + ba2).to_asm(), "0x01, 0x02, 0x03, 0x04\n")
		
		ba1 += ba2		
		self.assertEqual(ba1.to_asm(), "0x01, 0x02, 0x03, 0x04\n")
