import re

PSF1_VERSION = 1
PSF2_VERSION = 2

PSF1_MAGIC_BYTES = [0x36, 0x04]
PSF2_MAGIC_BYTES = [0x72, 0xb5, 0x4a, 0x86]

PSF1_MODE512 = 0x01
PSF1_MODEHASTAB = 0x02
PSF1_MODEHASSEQ = 0x04
PSF1_MAXMODE = 0x05

PSF1_SEPARATOR = 0xFFFF
PSF1_STARTSEQ = 0xFFFE

PSF2_MAXVERSION = 0
PSF2_HAS_UNICODE_TABLE = 0x1

TYPE_PLAIN_ASM = 42
TYPE_BINARY_PSF = 43

def get_unicode_str(codepoint):
	"""Get an unicode string from a given codepoint
	
	Args:
		codepoint (int) : The codepoint to get the unicode value from
	
	Returns:
		str : The Unicode string. Is empty, if the codepoint is a
			controll sequence or undefined
	
	"""
	if 0x20 <= codepoint <= 0x7e or 0xa0 <= codepoint: #<= 0xff:
		return chr(codepoint)
	return ""
		
def get_codepoint(char):
	"""Get the codepoint of a character
	
	Args:
		char (str) : The character to get the codepoint from
		
	Notes:
		char should be decoded with utf-8 and its length should be 1
		
	Returns:
		None : If the length of char is not 1
		int : The codepoint of the given character
	
	"""
	#char = char.decode('utf-8')
	if len(char) != 1: return None
	codepoint = ord(char)
	return codepoint

def import_font_from_asm(path):
	"""Imports a font from an assembler file.
	
	Args:
		path (string): The path to the assembler file
		
	Returns:
		PcScreenFont: The font imported from the assembler file
	"""
	try:
		with open(path, "r") as f:
			raw_data = f.read()
	except Exception as e:
		raise e

	label_expression = re.compile('([a-zA-Z0-9_]+:)')
	data = label_expression.split(raw_data)
	
	i = 0
	labels = {}
	while i<len(data):
		data[i] = data[i].strip()
		if not data[i]:
			del data[i]
			continue
		if label_expression.match(data[i]):
			for j in range(i, len(data)):
				if not label_expression.match(data[j]):
					raw_values  = data[j] \
								.replace('\n', ' ') \
								.replace('db', '') \
								.replace('dd', '') \
								.split(',')
					values = []
					for v in raw_values:
						if v.strip():
							values.append(int(v, 16))
					if values:
						labels[data[i][:-1]] = values
						break
		i += 1
	
	if labels['magic_bytes'] == PSF1_MAGIC_BYTES:
		header = PsfHeaderv1((8, labels['charsize'][0]))
		header.set_mode(labels['mode'][0])
	elif labels['magic_bytes'] == PSF2_MAGIC_BYTES:
		header = PsfHeaderv2(
					(labels['width'][0], labels['height'][0]))
		header.set_flags(labels['flags'][0])
	else:
		raise Exception('The magic bytes do not match PSF ' +
				'version 1 or 2')
				
	labels = {
		k : v 
			for k, v in labels.items() if
				k not in (
					'font_header',
					'magic_bytes',
					'char_size',
					'mode',
					'version',
					'headersize',
					'flags',
					'length',
					'charsize',
					'height',
					'width'
				) and sum(v)
	}

	font = PcScreenFont(header)
	for k in labels.keys():
		pc = int(k.replace('glyph_', ''))
		glyph = font.get_glyph(pc)
		_bytes = [Byte.from_int(i) for i in labels[k]]
		glyph.set_data_from_bytes(_bytes) 
		
	return font
	
class AsmImporter(object):
	
	def __init__(self, asm_data):
		self.asm = AsmParser(asm_data)
		self.header = None
		
	def __build_header(self):
		psf1_magic = ByteArray()
		psf2_magic = ByteArray()
		for i in PSF1_MAGIC_BYTES:
			psf1_magic.add_byte(Byte.from_int(i))
		for i in PSF2_MAGIC_BYTES:
			psf2_magic.add_byte(Byte.from_int(i))		
		
	"""This method reads an assemblerfile, which contains psf data.
	
	Returns:
		PcScreenFont	
	"""	
	@staticmethod
	def import_file(file_path):
		with open(file_path, "r") as _file:
			data = _file.read()
				
		return AsmImporter.import_string(data)
		
	@staticmethod
	def import_string(_str):
		imp = AsmImporter(_str)
		
		

class AsmParser(object):
	"""This class exists to import and parse data from the nasm
	assembler format.
	
	Args:
		asm_string (string): The raw nasm assembler code	
		
	Notes:
		All labels found in the code are accesible as attributes at an
		instance of this class
	"""
	__LABEL_EXPR = re.compile('([a-zA-Z0-9_]+:)')
	# There are more operants for declaring initialized data, but we
	# just need these two
	__DECLARATORS_EXPR = re.compile('(db|DB|dw|DW)')
	__HEXADECIMAL_EXPR = re.compile(
		'(0[x|h][0-9a-fA-F]+|[0-9a-fA-F]+h)')
	__OCTAL_EXPR = re.compile('(0[o|q][0-7]+|[0-7]+[o|q])')
	__BINARY_EXPR = re.compile(
		'(0[yb](?!_)[0-1_]+(?<!_)|(?!_)[0-1_]+(?<!_)[by])')
	__DECIMAL_EXPR = re.compile('(0d[0-9]+|[0-9]+d|[0-9]+)')
	__DECLARATOR_BYTES_LOWER = 'db'
	__DECLARATOR_WORDS_LOWER = 'dw'
	
	
	def __init__(self, asm_string):
		self.__labels = {}
		self.__parse_asm(asm_string)
		
	
	def get_labels(self):
		"""This method returns all labels, which were found in the
		assembler code and their data as bytearrays.
	
		Returns:
			dict: A dictionary with the labels as keys and their data as
				values
		"""	
		return self.__labels
		
	def has_label(self, name):
		"""This method can be used to determine wether the parsed asm
		code contains a label or name.
		
		Args:
			name (str): The name of the label to check
			
		Returns:
			bool: Wether the parsed code contains the label or not
		
		"""
		return name in self.__labels
		
	def __getattr__(self, name):
		"""This method allows you to access labels found in the code as
		class attributes
		"""
		if name in self.__labels:
			return self.__labels[name]
		raise AttributeError
		
	def __split_n_cleanup(self, asm_string):
		"""This method splits the nasm asm code before and after every label
		and removes linebreaks and tabs.
	
		Returns:
			list: A list with the splitted code
		"""
		data = self.__LABEL_EXPR.split(asm_string)
		i = 0
		while i < len(data):
			data[i] = data[i].strip()\
				.replace('\t', ' ')\
				.replace('\n', ' ')
			if not data[i]: del data[i]
			i += 1
			
		return data
	
	def __make_bytearray(self, data_string):
		"""This method parses a string with declared initialized data
		(see http://www.nasm.us/doc/nasmdoc3.html#section-3.2.1) and
		makes a bytearray out of it.
	
		Returns:
			ByteArray	
		"""
		data = self.__DECLARATORS_EXPR.split(data_string)
		
		i = 0
		
		ba = ByteArray()				
						
		while i < len(data):
			if not data[i]:
				i +=1
				continue
				
			if None == self.__DECLARATORS_EXPR.search(data[i]):
				if (i == 0 or
				    None == self.__DECLARATORS_EXPR.search(data[i-1])):
					raise Exception(
						("Error while parsing %s, could not extract " +
						 "values") % data_string)
			if data[i-1].lower() == self.__DECLARATOR_BYTES_LOWER:
				for j in self.__get_integers(data[i]):
					ba.add_byte(Byte.from_int(j))
			elif data[i-1].lower() == self.__DECLARATOR_WORDS_LOWER:
				for j in self.__get_integers(data[i]):
					ba += ByteArray().from_int(j, 2)
			i += 1
		return ba 	
	
	
	def __get_integers(self, data_string):
		"""This method parses integers from a string in many different
		formats (decimal, binary, octal, hexadecimal).
		For allowed notations see
		(http://www.nasm.us/doc/nasmdoc3.html#section-3.4.1)
	
		Args:
			data_string (str): A string with numbers seperated by
				commatas.
	
		Returns:
			list: A list with the integers extraced from the data_string	
		"""
		ints = []
		for i in data_string.replace(' ', '').split(','):
			if None != self.__BINARY_EXPR.match(i):
				i = i.replace('y', 'b').replace('_', '')
				ints.append(int(i, 2))
			elif None != self.__OCTAL_EXPR.match(i):
				i = i.replace('q', '').replace('o', '')
				ints.append(int(i, 8))
			elif None != self.__HEXADECIMAL_EXPR.match(i):
				i = i.replace('h', '')
				ints.append(int(i, 16))
			elif None != self.__DECIMAL_EXPR.match(i):
				i = i.replace('d', '')
				ints.append(int(i, 10))
			else:
				raise ValueError('Could not parse %s in %s as integer' %
					i, data_string)
		return ints			
				
	def __parse_asm(self, asm_string):
		"""This method parses an raw nasm assembler string and fills
		self.__labels
	
		Args:
			asm_string (str): The raw nasm assembler code
		"""
		data = self.__split_n_cleanup(asm_string)
	
		labels = []

		i = 0
		while i < len(data):
			if self.__LABEL_EXPR.match(data[i]):
				labels.append(data[i])
			else:
				ba = self.__make_bytearray(data[i])
				for l in labels:
					self.__labels[l.replace(':', '')] = ba
				labels = []
			i += 1

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
		
	def __check_bytes(self, _bytes):
		for byte in _bytes:
			if type(byte) != Byte:
				raise TypeError("Expected _bytes to be instances of " +
						"Byte")

class AsmExporter(object):
	def __init__(self, font):
		self.font = font
		self.header = font.header
		if self.header.version_psf == PSF1_VERSION:
			self.version = 1
		elif self.header.version_psf == PSF2_VERSION:
			self.version = 2
		self.string = ""
		
	def create_header(self):
		self.string += "font_header:\n"
		if self.version == 1:
			magic_bytes = ByteArray(self.header.magic_bytes)
			self.string += magic_bytes.to_asm("magic_bytes")
			self.string += "mode: db %s\n" % hex(self.header.mode)
			self.string += "charsize: db %s\n\n" % hex(self.header.charsize)
		elif self.version == 2:
			magic_bytes = ByteArray(self.header.magic_bytes)
			self.string += magic_bytes.to_asm("magic_bytes")
			self.string += "version: dd %s\n" % hex(self.header.version)
			self.string += "headersize: dd %s\n" % hex(
								self.header.headersize)
			self.string += "flags: dd %s\n" % hex(self.header.flags)
			self.string += "length: dd %s\n" % hex(len(self.font))
			self.string += "charsize: dd %s\n" % hex(
								self.header.charsize)
			self.string += "height: dd %s\n" % hex(self.header.height)
			self.string += "width: dd %s\n\n" % hex(self.header.width)

	def glyph_to_asm(self, glyph, label):
		bits = []
		for row in glyph.data:
			for bit in row:
				bits.append(bit)
			missing_bits = 8 - len(row) % 8
			if missing_bits < 8:
				for _ in range(8 - len(row) % 8):
					bits.append(0)		
		# -- The following is bullshit --		
		# The number of bits must be a multiple of 8
		#if bits_count % 8:
		#	for _ in range(8- (bits_cound%8)):
		#		bits.append(0)
		_bytes = ByteArray.from_bit_array(bits)		
		return _bytes.to_asm(label)


	def create_bitmaps(self):
		self.string += "font_bitmaps:\n"
		if self.header.has_unicode_table():
			for i, glyph in zip(range(len(self.font.get_glyphs())),
								self.font.get_glyphs().values()):
				self.string += self.glyph_to_asm(glyph, "glyph_%d" % i)
			if self.header.version_psf == PSF1_VERSION:
				if self.header.mode & PSF1_MODE512:
					glyph_count = 512 
				else:
					glyph_count = 256
				glyph = Glyph(self.header.size)
				for i in range(len(self.font.get_glyphs()), glyph_count):
					self.string += self.glyph_to_asm(glyph, "glyph_%d" % i)
			return
			
		# Has no Unicode table
		if self.header.version_psf == PSF1_VERSION:
			if self.header.mode & PSF1_MODE512:
				# 512 Glyphs
				glyph_count = 512
			else:
				# 256 Glyphs
				glyph_count = 256
		else:
			glyph_count = len(self.font)
			
		for i in range(glyph_count):
			glyph = self.font.get_glyph(i)
			self.string += self.glyph_to_asm(glyph, "glyph_%d" % i)

	def create_unicode_table(self):
		if self.header.version_psf == PSF1_VERSION:
			if self.header.mode & PSF1_MODE512:
				# 512 Glyphs
				glyph_count = 512
			else:
				# 256 Glyphs
				glyph_count = 256
			for puc, glyph in self.font.get_glyphs().items():
				_bytes = ByteArray.from_int(puc, 2)
				#if len(glyph.get_unicode_representations()) > 1:
				#	_bytes += ByteArray.from_int(0xFFFE, 2)
				for uc in glyph.get_unicode_representations():
					if uc != puc:
						_bytes += ByteArray.from_int(uc, 2)
				_bytes += ByteArray.from_int(0xFFFF, 2)		
				self.string += _bytes.to_asm('Unicodedescription%d' % puc)
			for i in range(glyph_count - len(self.font.get_glyphs())):
				self.string += ByteArray.from_int(0xFFFF, 2).to_asm('Placeholder%d' % i)
		else:
			pass
			

	def export(self, path):
		self.create_header()
		self.create_bitmaps()
		if self.font.has_unicode():
			self.create_unicode_table()
		
		with open(path, "w") as f:
			f.write(self.string)

class PsfExporter(object):
	def __init__(self, font):
		self.font = font
		self.header = font.header
		if self.header.version_psf == PSF1_VERSION:
			self.version = 1
		elif self.header.version_psf == PSF2_VERSION:
			self.version = 2
		self.bytes = bytearray()
	
	def int_to_bytes(self, n):
		bts = []
		if 0 <= n <= 4294967295:
			for i in range(4):
				bts.append(n % 0x100)
				n = n / 0x100
		return bts.reverse()
	
	def create_header(self):
		for i in self.header.magic_bytes:
			self.bytes.append(i)
		if self.version == 1:
			self.bytes.append(self.header.mode)
			self.bytes.append(self.header.charsize)
		elif self.version == 2:
			self.bytes.append(self.int_to_bytes(self.header.version))
			self.bytes.append(self.int_to_bytes(self.header.headersize))
			self.bytes.append(self.int_to_bytes(self.header.flags))
			self.bytes.append(self.int_to_bytes(self.header.length))
			self.bytes.append(self.int_to_bytes(self.header.charsize))
			self.bytes.append(self.int_to_bytes(self.header.height))
			self.bytes.append(self.int_to_bytes(self.header.width))



class PsfHeader(object):
	"""This class is the base for a header for the PC Screen Font
	
	Args:
		version (int): The version of the PC Screen Font. Should be
			PSF1_VERSION or PSF2_VERSION
		size (list of 2 integers): The size of every glyph of the font.
			The first value is the width and the second the height
	"""
	def __init__(self, version, size):
		self.version_psf = version
		self.magic_bytes = []
		self.mode = 0
		self.charsize = 0
		
		self.version = 0
		self.headersize = 0
		self.flags = 0
		self.length = 0
		self.height = 0
		self.width = 0
		
		self.size = size
		
	def has_unicode_table(self):
		"""Check wether the font has an unicode table or not
		
		Returns:
			bool: True if the font has an unicode table else False
		"""
		if self.version_psf == PSF1_VERSION:
			return self.mode & PSF1_MODEHASTAB
		else:
			return self.flags & PSF2_HAS_UNICODE_TABLE
			
class PsfHeaderv1(PsfHeader):
	"""This class represents the header for the Pc Screen Font 1.
	
	Args:
		size (list of 2 integers): The size of every glyph of the font.
			The first value is the width and the second the height
	"""
	def __init__(self, size):
		PsfHeader.__init__(self, PSF1_VERSION, size)
		for byte in PSF1_MAGIC_BYTES:
			self.magic_bytes.append(Byte.from_int(byte))
		
		if (size[0] != 8):
			raise Exception("Error, for PSF1 the font width must be 8")
		self.charsize = size[1]
		self.mode = 0
	
	def set_mode(self, mode):
		"""Set one or more modes of the PSF1.
		
		Args:
			mode (int): A Number with the bits for the desired modes
				set.		
				
		Notes:
			Allowed modes are
			PSF1_MODE512    = 0x01
			PSF1_MODEHASTAB = 0x02
			PSF1_MODEHASSEQ = 0x04
			PSF1_MAXMODE    = 0x05
		"""
		if mode > 5:
			raise Exception("Error, undefined bits set in PSF1 mode")
		self.mode |= mode
	def unset_mode(self, mode):
		"""Unset one or more modi of the PSF1
		
		Args:
			mode (int): A number with the bits for the desired modes
				set.
		
		Notes:
			For allowed modes see the PsfHeaderv1.set_mode method
			Passing 0 to this method has no effect.
		"""
		if mode > 7:
			raise Exception("Error, undefined bits unset in PSF1 mode")
		if mode:
			self.mode |= ~mode
		

class PsfHeaderv2(PsfHeader):
	"""This class represents the header for the Pc Screen Font 1.
	
	Args:
		size (list of 2 integers): The size of every glyph of the font.
			The first value is the width and the second the height
	"""
	def __init__(self, size):
		PsfHeader.__init__(self, PSF2_VERSION, size)
		for byte in PSF2_MAGIC_BYTES:
			self.magic_bytes.append(Byte.from_int(byte))
		self.version = PSF2_MAXVERSION
		self.headersize = 32	# Values are encoded as 4byte integers
		self.flags = 0
		self.width = size[0]
		self.height = size[1]
		self.charsize = size[1] * int((size[0]+7) / 8)

	def set_flags(self, flags):
		"""Set one or more flags of the PSF2.
		
		Args:
			flags (int): Number with the bits for the desired flags set.
			
		Notes:
			The only allowed flag is PSF2_HAS_UNICODE_TABLE = 0x1.
			You could pass 0 to this method, but it has no effect
		"""
		if flags not in (0, PSF2_HAS_UNICODE_TABLE):
			raise Exception("Error, undefined bits set in PSF2 flags")
		self.flags |= flags

	def unset_flags(self, flags):
		"""Unset one or more flags of the PSF2.
		
		Args:
			flags (int): Number with the bits for the desired flags set.
			
		Notes:
			The only allowed flag is PSF2_HAS_UNICODE_TABLE = 0x1.
			You could pass 0 to this method, but it has no effect
		"""
		if flags not in (0, PSF2_HAS_UNICODE_TABLE):
			raise Exception("Error, undefined bits set in PSF2 flags")
		if flags:
			self.flags |= flags

class PcScreenFont(object):
	"""This class represents a pc screen font
	
	The font contains zero or more glyphs. A glyph is a bitmap of a
	character. The font accesses its glyphs by the primary codepoint
	assigned to the glyph. Furthermore every glyph has zero or more
	codepoints for additional unicode representations
		
	Arguments:
		header (PsfHeader)	: the header of the font
	"""
	def __init__(self, header):
		self.header = header
		self.glyphs = {}
		self.size = header.size
	
	def has_unicode(self):
		"""This function should be used to determine wether the font 
		has an unicode table or not.
			
		Returns:
			bool : True if it has an unicode table else False
		"""
		if self.header.version_psf == PSF1_VERSION:
			return True if self.header.mode & PSF1_MODEHASTAB else False
		else:
			return (True if self.header.flags & PSF2_HAS_UNICODE_TABLE
						 else False)
			
	def get_header(self):
		"""Get the header of the font.
		
		Returns:
			PsfHeader: The header of the font		
		"""
		return self.header
			
	def get_glyph(self, codepoint):
		"""Get a glyph of the font by its primary codepoint
		If the font does not have a glyph with the given codepoint as
		primary or additional unicode representation, then a new glyph
		with the given codepoint as primary representation gets added
		to the font and returned.
		
		Args:
			codepoint (int) : the codepoint for the glyph
		
		Returns
			Glyph :	glyph which is represented by the given codepoint
		
		"""
		for glyph in self.glyphs.values():
			if glyph.has_unicode_representation(codepoint):
				return glyph
		glyph = Glyph(self.size)
		glyph.add_unicode_representation(codepoint)
		self.glyphs[codepoint] = glyph
		return glyph
		
	def get_glyphs(self):
		"""Get a dictionary with all glyphs of the font.
		
		Returns:
			dict: A dictionary with the scheme
				{ primary unicode representation : glyph }
		"""
		return self.glyphs.copy()
		
	def update_unicode_representation(self, primary_cp, old_cp, new_cp):
		"""Updates the unicode representation of a glyph
		
		Args:
			primary_cp (int) : The primary codepoint of the glyph
			old_cp (int) : The old value of the unicode representation,
				which should be updated
			new_cp (int) : The new value of the unicode representation,
				which should be updated
		
		Notes:
			If the old_cp is equal to the primary_cp, the the primary
			codepoint of the glyph will be updated
		"""
		if old_cp == new_cp:
			return
		if primary_cp == old_cp:
			self.glyphs[new_cp] = self.glyphs[old_cp]
			del self.glyphs[old_cp]
			self.glyphs[new_cp].update_unicode_representation(old_cp,
									new_cp)
			return
		self.glyphs[primary_cp].update_unicode_representation(old_cp,
									new_cp)
		
	def remove_glyph(self, codepoint):
		"""Remove a glyph from the font
		
		Args:
			codepoint (int) : The primary codepoint of the glyph which
				should be removed
		"""
		if codepoint in self.glyphs.keys():
			del self.glyphs[codepoint]
			
	def __len__(self):
		"""Get the lenght of the font, aka the largest primary codepoint
		of a glyph plus one.
		
		Returns:
			int: the len of the font
		"""
		if self.glyphs:
			return max(self.glyphs.keys()) + 1
		return 0
	
	def __str__(self):
		data = u""
		for i in self.glyphs.keys():
			data += "\n%d : (%s)\n" % (i, get_unicode_str(i))
			data += " -----------\n"
			data += repr(self.glyphs[i])
		return data
	
	def __repr__(self):
		return self.__str__()
			

class Glyph(object):
	"""This class represents a glyph of the pc screen font
	
	Args:
		size (tuple(int width, int height)) : size of the bitmap representing the
			character
	"""
	def __init__(self, size):
		"""self.data is a list containing y lists with x elements, where
		x is the width of the glyph an y the height.
		Therefore the correct way to iterate over self.data is:
		
		for row in self.data:
			for bit in row:
				...		
		"""
		self.data = [[0 for i in range(size[0])]
						for j in range(size[1])]
		self.touched = False
		self.width = size[0]
		self.height = size[1]
		self.unicode_representations = []
		
	def add_unicode_representation(self, codepoint):
		"""Add an unicode value to the glyph
		
		Args:
			codepoint (int) : codepoint which should represent the glyph
		"""
		if codepoint not in self.unicode_representations:
			self.unicode_representations.append(codepoint)	
	
	def remove_unicode_representation(self, codepoint):
		"""Remove an unicode value from the glyph
		
		Args:
			codepoint (int) : codepoint which should be removed from the
				glyph
		"""
		if codepoint in self.unicode_representations:
			self.unicode_representations.remove(codepoint)
	
	def update_unicode_representation(self, old_cp, new_cp):
		"""Update the unicode representation of the glyph
		
		Args:
			old_cp (int) : Old value of the unicode representation which
				should be updated
			new_cp (int) : New value of the unicode representation which
				should be updated
		"""
		if new_cp in self.unicode_representations:
			#self.unicode_representations.remove(old_cp)
			return
		for i, cp in zip(range(len(self.unicode_representations)),
						 self.unicode_representations):
			if cp == old_cp:
				self.unicode_representations[i] = new_cp
	
	def has_unicode_representation(self, codepoint):
		"""Check if the char is represented by a codepoint
		
		Args:
			codepoint (int) : Codepoint to check
			
		Returns:
			bool : True if the glyph is represented by the given
				codepoint
		"""
		return codepoint in self.unicode_representations
	
	def get_unicode_representations(self):
		"""Get a list with all unicode representations of the glyph
		
		Returns:
			list: A list with all unicode representations of the glyph		
		"""
		return self.unicode_representations
	
	def copy_data(self, data):
		"""Update the bitmap with given data
		
		Args:
			data (list of lists with integers)) : the data to update the
				bitmap with. Each element of the data represents a row
				of the bitmap and each element in a row represents a
				pixel.
				The pixel is set, if its value equal 1.
		
		"""
		for i, row in zip(range(self.height), data):
			for j, element in zip(range(self.width), row):
				self.data[i][j] = element
		
	def get_data(self):
		"""Get the data of the bitmap
		
		Returns:
			list : A list containing lists, which represent the rows of
				the bitmap. Each element of a row is a integer and
				represents a pixel.
				If the value of this integer is 1, then the pixel is set
		
		"""
		return self.data[:]
	
	def set_data_from_bytes(self, _bytes):
		"""Set the data of the bitmap from an array of byte objects
		
		Args:
			_bytes (a list of Bytes): the bytes to update the Bitmap
				with. Each 
		"""
		bits_per_line = int(self.width / 8) 
		bits_per_line += 1 if self.width % 8 else 0
		bits_per_line *= 8
		self.data = []
		bits = []
		for b in _bytes: bits += b.get_bits()
		for i in range(self.height):
			line = []
			for j in range(self.width):
				line.append(bits[i * bits_per_line + j])
			self.data.append(line)
		
	def get_size(self):
		"""Get the size of the glyph
		
		Returns:
			tuple: A tuple with the width of the glyph as first value
				and the height as second		
		"""
		return self.width, self.height
		
	def __repr__(self):
		out = "Unicode representations:\n"
		for uc in self.unicode_representations:
			unistr = get_unicode_str(uc)
			out += "  %s : (%d) \n" % (unistr if unistr else "", uc)
		out += "\n"
		for i in self.data:
			for j in i:
				out += "#" if j else "."
			out += "\n"
		return out
		
if __name__ == "__main__":
	pass
