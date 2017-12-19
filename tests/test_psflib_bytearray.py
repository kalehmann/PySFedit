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
		self.assertEqual(ba.to_asm(), "0xd1, 0x00, 0x00, 0x00, 0xb3, 0xe1, 0xe1, 0x15, 0xe4, 0xa4, 0x12\n")
		ba = psflib.ByteArray.from_int(0xFFFFF, 2)
		self.assertEqual(ba.to_asm(), "0xff, 0xff\n")
		ba = psflib.ByteArray.from_int(16, 4)
		self.assertEqual(ba.to_asm(), "0x10, 0x00, 0x00, 0x00\n")

	def test_to_int(self):
		ba = psflib.ByteArray.from_int(256)
		self.assertEqual(int(ba), 256)
		ba = psflib.ByteArray.from_int(256289)
		self.assertEqual(int(ba), 256289)

	def test_addition(self):
		b = psflib.Byte.from_int
		ba1 = psflib.ByteArray([b(1), b(2)])
		ba2 = psflib.ByteArray([b(3), b(4)])
		
		self.assertEqual((ba1 + ba2).to_asm(), "0x01, 0x02, 0x03, 0x04\n")
		
		ba1 += ba2		
		self.assertEqual(ba1.to_asm(), "0x01, 0x02, 0x03, 0x04\n")
		
	def test_comparisation(self):
		b = psflib.Byte.from_int
		ba1 = psflib.ByteArray([b(1), b(2), b(3), b(4)])
		ba2 = psflib.ByteArray([b(1), b(2), b(3), b(4)])
		ba3 = psflib.ByteArray([b(1), b(2), b(3), b(4), b(5)])
		ba4 = object()
		
		self.assertEqual(ba1, ba2)
		self.assertNotEqual(ba1, ba3)
		self.assertNotEqual(ba1, ba4)

	def test_to_ints(self):
		b = psflib.Byte.from_int
		ba1 = psflib.ByteArray([b(1), b(2), b(3)])
		self.assertEqual(ba1.to_ints(), [1,2,3])
		
		ba2 = psflib.ByteArray([b(0xff), b(0x01), b(0x34), b(0x12)])
		self.assertEqual(ba2.to_ints(2), [0x1ff, 0x1234])
		
		with self.assertRaises(ValueError):
			ba2.to_ints(3)
