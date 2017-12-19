class Byte(object):
	"""This class represents a byte
	
	Args:
		bits (list/tuple) (optional) : The bits of the byte. Should have
			a length of 8. All Elements should be either 0 or 1.
			The element at index 0 represents the most significant bit
			and the element at index 7 the least significant bit.
			The standard value for the bits is 8 times a zero
			
	Raises:
		ValueError if the length of bits is not 8 or if there is a bit
			with an other value than 0 or 1
	"""	
	def __init__(self, bits = None):
		if not bits:
			self.__bits = [0,0,0,0,0,0,0,0]
		else:
			if len(bits) != 8:
				raise ValueError("A byte should have 8 bits")
			for bit in bits:
				if bit not in (0, 1):
					raise ValueError("A bit should be either 0 or 1")
			self.__bits = list(bits)
		
	@staticmethod	
	def from_int(integer):
		"""Creates a Byte object from an integer
		
		Args:
			integer (int) : The integer to create the byte from
			
		Returns:
			Byte ()
			
		Notes:
			Since the range of values of a byte is 0 to 255, if given
			integer is larger than 255, int(byte) will be integer % 255
			This method automatically converts the integer to a positive
			value		
		"""
		quotient = abs(integer % 256)	# Thats actually a remainder
		bits = []
		for _ in range(8):
			remainder = quotient % 2
			quotient = quotient // 2
			bits.append(remainder)
		bits = list(reversed(bits))
		return Byte(bits)
		
	def get_bits(self):
		"""Get an array with the 8 bits of the byte.
		
		Returns:
			list: The bits of the byte		
		"""
		return self.__bits[:]
		
	def __getitem__(self, key):
		"""Returns the bit with the given key as index
		
		Args:
			key (int) : The index of the bit. Should be between 0 and 7.
				7 returns the most significant bit and 0 the least
				significant
		
		Raises:
			IndexError if the key is not between 0 and 7		
		"""
		if not 0 <= key < 8:
			raise IndexError("The index of a bit in a byte should be " +
					"between 0 and 7, %d given" % key)
		return self.__bits[key]
		
	def __setitem__(self, key, value):
		"""Sets the bit with the given key to value
		
		Args:
			key (int) : The index of the bit. Should be between 0 and 7.
				7 sets the most significant bit and 0 the least
				significant
			value (int) : The value to set the bit to. Should be 0 or 1
			
		Raises:
			IndexError if the key is not between 0 and 7
			ValueError if the value is not zero or one
		
		"""
		if not 0 <= key < 8:
			raise IndexError("The index of a bit in a byte should be " +
					"between 0 and 7, %d given" % key)
		if value not in (0, 1):
			raise ValueError("A bit should be either 0 or 1")
		self.__bits[key] = value

	def __len__(self):
		"""Returns the Number of bits a byte has.
		
		Returns:
			int : Always 8		
		"""
		return 8

	def __and__(self, other):
		"""Performs a binary and between other and the byte
		
		Args:
			other (int or at least convertable to int): The value to
				perform the binary and with
				
		Returns:
			Byte : The new byte.
		"""
		return Byte.from_int(int(other) & self.__int__())
		
	def __or__(self, other):
		"""Performs a binary or between other and the byte
		
		Args:
			other (int or at least convertable to int): The value to
				perform the binary or with
				
		Returns:
			Byte : The new byte.
		"""
		return Byte.from_int(int(other) | self.__int__())
		
	def __xor__(self, other):
		"""Performs a binary xor between other and the byte
		
		Args:
			other (int or at least convertable to int): The value to
				perform the binary xor with
				
		Returns:
			Byte : The new byte.
		"""
		return Byte.from_int(int(other) ^ self.__int__())

	def __int__(self):
		"""Convert the byte to an integer value
		
		Returns:
			int : The integer value of the byte		
		"""
		integer = 0
		for i, bit in zip(range(7,-1,-1), self.__bits):
			integer += 2 ** i * bit
		return integer
		
	def __index__(self):
		return self.__int__()
		
	def hex(self):
		"""Converts the byte to an hexdecimal value
		
		Returns:
			str : A string with the hexadecimal value of the byte		
		"""
		return "0x%02x" % self.__int__()
		
	def __eq__(self, other):
		"""Checks if the int value of the byte is equal to the int value
		of another object
	
		Args:
			other (int or at least convertable to an integer) : The
				object to compare the byte with
	
		Returns:
			bool : True if the nt value of the byte is equal to the int
				value of the other object else False
		"""
		if int(other) == self.__int__():
			return True
		return False
		
	def __le__(self, other):
		"""Checks if the int value of the byte is lower or equal to the
		int value of another object
	
		Args:
			other (int or at least convertable to an integer) : The
				object to compare the byte with
	
		Returns:
			bool : True if the int value of the byte is lower or equal
				to the int value of the other object else False
		"""
		if self.__int__() <= int(other):
			return True
		return False
		
	def __lt__(self, other):
		"""Checks if the int value of the byte is lower than the int
		value of another object
	
		Args:
			other (int or at least convertable to an integer) : The
				object to compare the byte with
	
		Returns:
			bool : True if the int value of the byte is lower than the
				int value of the other object else False
		"""
		if self.__int__() < int(other):
			return True
		return False
		
	def __ge__(self, other):
		"""Checks if the int value of the byte is greater or equal to the
		int value of another object
	
		Args:
			other (int or at least convertable to an integer) : The
				object to compare the byte with
	
		Returns:
			bool : True if the int value of the byte is greater or equal
				to the int value of the other object else False
		"""
		if self.__int__() >= int(other):
			return True
		return False
		
	def __gt__(self, other):
		"""Checks if the int value of the byte is greater than the int
		value of another object
	
		Args:
			other (int or at least convertable to an integer) : The
				object to compare the byte with
	
		Returns:
			bool : True if the int value of the byte is greater than the
				int value of the other object else False
		"""
		if self.__int__() > int(other):
			return True
		return False
		
	def __ne__(self, other):
		"""Checks if the int value of the byte is not equal to the int
		value of another object
	
		Args:
			other (int or at least convertable to an integer) : The
				object to compare the byte with
	
		Returns:
			bool : True if the int value of the byte is not equal to the
				int value of the other object else False
		"""
		if int(other) != self.__int__():
			return True
		return False
		
	def __str__(self):
		"""Converts the byte to a string
		
		Returns:
			str : A string with the hexadecimal value of the bytess		
		"""
		return self.hex()
		
	def __bool__(self):
		"""The __bool__ function is used for truth-testing
		
		Returns:
			bool : False if all bits of the byte are zeros else True
		"""
		return self.__int__() != 0

class ByteArray(object):
	def __init__(self, _bytes=None):
		if _bytes:
			self.__check_bytes(_bytes)
			self.__bytes = _bytes
		else:
			self.__bytes = []
		
	@staticmethod
	def from_int(i, fixed_len=0):
		bytevalues = []
		while i:
			remainder = i % 256
			i = int(i/256)
			bytevalues.append(Byte.from_int(remainder))
		if fixed_len and len(bytevalues) > fixed_len:
			bytevalues = bytevalues[:fixed_len]
		elif fixed_len and len(bytevalues) < fixed_len:
			for _ in range(fixed_len - len(bytevalues)):
				bytevalues.append(Byte.from_int(0))
		return ByteArray(bytevalues)
		
	@staticmethod
	def from_bit_array(bits):
		_bytes = []
		if len(bits) % 8:
			raise ValueError("The length of the bit array must be a " +
					"multiple of 8")
		for i in range(int(len(bits) / 8)):
			_bytes.append(Byte(bits[i*8:(i+1)*8]))
		return ByteArray(_bytes)
		
	def __getitem__(self, key):
		return self.__bytes[key]
		
	def __setitem__(self, key, value):
		self._bytes[key] = value
		
	def __len__(self):
		return len(self.__bytes)
		
	def __add__(self, other):
		if type(self) != type(other):
			raise NotImplementedError
		return ByteArray(self.__bytes + other.get_bytes())
	
	def __iadd__(self, other):
		if type(self) != type(other):
			raise NotImplementedError
		self.__bytes += other.get_bytes()
		return self
		
	def __eq__(self, other):
		if type(self) != type(other):
			return False
		for i in range(self.__len__()):
			if int(self.__bytes[i]) != int(other.get_bytes()[i]):
				return False
		return self.__len__() == len(other)
		
	def add_byte(self, byte):
		self.add_bytes([byte])
		
	def add_bytes(self, _bytes):
		self.__check_bytes(_bytes)
		for byte in _bytes:
			self.__bytes.append(byte)
		
	def get_bytes(self):
		return self.__bytes
		
	def to_bytearray(self):
		ba = bytearray()
		for byte in self.__bytes:
			ba.append(int(byte))
		return ba
		
	def to_ints(self, bytes_per_int=1):
		if self.__len__() % bytes_per_int:
			raise ValueError(
				("The length of the bytearray %d is not divisible " +
				 "by %d") % (self.__len__(), bytes_per_int)
			)
		ints = []
		for i in range(int(self.__len__() / bytes_per_int)):
			_int = 0
			for j in range(bytes_per_int):
				_int += (int(self.__bytes[i * bytes_per_int + j]) *
					(256 ** j))
			ints.append(_int)
		return ints
		
	def to_asm(self, label='' , linelength=80, intent=0, tab_size=4,
			end_with_linebreak = True):
		# Check if intent, linelength and the length of the label are
		# matching.
		if len(label) + 5 + intent * tab_size > linelength:
			raise Exception(
				("There is a missmatch between the max linelength " +
				 "(%d), the intent (%d) + tabulator size (%d) and " + 
				 "the length of the label (%d)") %
				 (linelength, intent, tab_size, len(label)))
					
		line = " " * intent * tab_size
		line += "%s: db " % label if label else ''
		lines = []
		for i, byte in zip(range(len(self.__bytes)), self.__bytes):
			to_add = "%s" % byte.hex()
			if len(line) + len(to_add) > linelength:
				# create new line
				lines.append(line)
				line = " " * (intent + 1) * tab_size + "db " + to_add
			else:
				if i + 1 < len(self.__bytes):
					to_add += ", "
				line += to_add
		lines.append(line)
		out = ""
		for line in lines:
			out += "%s\n" % line
		if not end_with_linebreak:
			out = out[:-1]
		return out
	
	def __int__(self):
		ival = 0
		for i, b in zip(range(self.__len__()), self.__bytes):
			ival += int(b) * (256 ** i)

		return ival
		
	def __check_bytes(self, _bytes):
		for byte in _bytes:
			if type(byte) != Byte:
				raise TypeError("Expected _bytes to be instances of " +
						"Byte")
