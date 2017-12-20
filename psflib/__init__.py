from psflib.byteutils import Byte, ByteArray
from psflib.asmutils import AsmParser

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
	
class AsmImporter(object):
	
	def __init__(self, asm_data):
		self.__asm = AsmParser(asm_data)
		self.__header = None
		self.__font = None
		
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
		return imp.build_font()

	def build_font(self):
		header = self.__build_header()
		self.__font = PcScreenFont(header)
		self.__build_glyphs()
		
		return self.__font

	def __build_header(self):
		psf1_magic = ByteArray()
		psf2_magic = ByteArray()
		for i in PSF1_MAGIC_BYTES:
			psf1_magic.add_byte(Byte.from_int(i))
		for i in PSF2_MAGIC_BYTES:
			psf2_magic.add_byte(Byte.from_int(i))
		
		if not self.__asm.has_label('magic_bytes'):
			raise Exception(
				'Could not read font from asm file, since it has no ' +
				'label named "magic_bytes"')
		
		if self.__asm.magic_bytes == psf1_magic:
			self.__header = self.__get_header_psf_v1()
		elif self.__asm.magic_bytes == psf2_magic:
			self.__header = self.__get_header_psf_v2()
		else:
			raise Exception(
				'The magic bytes of the font do not match any known ' +
				'magic bytes'
			)
		return self.__header	
			
	def __build_glyphs(self):
		for label, data in self.__asm.get_labels().items():
			if label.startswith('glyph_'):
				primary_codepoint = int(label.replace('glyph_', ''))
				glyph = self.__font.get_glyph(primary_codepoint)
				glyph.set_data_from_bytes(data)
		if self.__has_unicode_table():
			self.__parse_unicode_table()
	
	def __parse_unicode_table(self):
		if self.__header.version_psf == PSF1_VERSION:
			self.__parse_unicode_table_psf1()
			return
		if self.__header.version_psf == PSF2_VERSION:
			self.__parse_unicode_table_psf2()
			return
			
	def __parse_unicode_table_psf1(self):
		descriptions = []
		for label, data in self.__asm.get_labels().items():
			if label.startswith('Unicodedescription'):
				descriptions.append(data.to_ints(2))
		for i in range(len(descriptions), len(self.__font)):
			self.__font.remove_glyph(i)
		for d, i in zip(descriptions, range(len(descriptions))):
			self.__font.update_unicode_representation(i, i, d[0])
			glyph = self.__font.get_glyph(d[0])
			j = 0
			while j < len(d) and d[j] != 0xffff:
				if d[j] == 0xfffe:
					while j < len(d) and d[j] != 0xffff:
						pass # @ToDo: Parse sequences
						j += 1
				else:
					glyph.add_unicode_representation(d[j])
					j += 1

	def __parse_unicode_table_psf2(self):
		descriptions = []
		for label, data in self.__asm.get_labels().items():
			if label.startswith('Unicodedescription'):
				descriptions.append(data)
		for d, i in zip(descriptions, range(len(descriptions))):
			ba = d.to_bytearray()
			ba = ba.replace(bytes([0xff]), bytes())
			uc = ba.split(bytes([0xfe]))[0].decode('utf8')
			sequences = ba.split(bytes([0xfe]))[1:]
			self.__font.update_unicode_representation(i, i, ord(uc[0]))
			glyph = self.__font.get_glyph(ord(uc[0]))
			for u in uc:
				print(u)
				glyph.add_unicode_representation(ord(u))
	
	def __has_unicode_table(self):
		return self.__header.has_unicode_table()
			
	def __get_header_psf_v1(self):
		charsize = int(self.__asm.charsize)
		mode = int(self.__asm.mode)
		header = PsfHeaderv1([8, charsize])
		header.set_mode(mode)
		
		return header
		
	def __get_header_psf_v2(self):
		a = self.__asm
		version = int(a.version)
		flags = int(a.flags)
		length = int(a.length)
		height = int(a.height)
		width = int(a.width)
		
		header = PsfHeaderv2([width, height])
		header.set_flags(flags)
		header.set_length(length)
		
		return header

class AsmExporter(object):
	def __init__(self, font):
		self.font = font
		self.header = font.get_header()
		if self.header.version_psf == PSF1_VERSION:
			self.version = 1
		elif self.header.version_psf == PSF2_VERSION:
			self.version = 2
		self.string = ""
		
	def __create_header(self):
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
			self.string += "length: dd %s\n" % hex(self.header.length)
			self.string += "charsize: dd %s\n" % hex(
								self.header.charsize)
			self.string += "height: dd %s\n" % hex(self.header.height)
			self.string += "width: dd %s\n\n" % hex(self.header.width)

	def __glyph_to_asm(self, glyph, label):
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


	def __create_bitmaps(self):
		self.string += "font_bitmaps:\n"
		if self.header.has_unicode_table():
			for i, glyph in zip(range(len(self.font.get_glyphs())),
								self.font.get_glyphs().values()):
				self.string += self.__glyph_to_asm(glyph, "glyph_%d" % i)
			if self.header.version_psf == PSF1_VERSION:
				if self.header.mode & PSF1_MODE512:
					glyph_count = 512 
				else:
					glyph_count = 256
				glyph = Glyph(self.header.size)
				for i in range(len(self.font.get_glyphs()), glyph_count):
					self.string += self.__glyph_to_asm(glyph, "glyph_%d" % i)
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
			self.string += self.__glyph_to_asm(glyph, "glyph_%d" % i)

	def __create_unicode_table(self):
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
		else:	# psf2
			for puc, glyph in self.font.get_glyphs().items():
				_bytes = ByteArray.from_bytes(chr(puc).encode('utf8'))
				for uc in glyph.get_unicode_representations():
					if uc != puc:
						_bytes += ByteArray.from_bytes(
							chr(uc).encode('utf8'))
				_bytes += ByteArray.from_int(0xFF, 1)	
				self.string += _bytes.to_asm('Unicodedescription%d' % puc)	
	
	def export_string(self):
		self.string = ''
		self.__create_header()
		self.__create_bitmaps()
		if self.font.has_unicode():
			self.__create_unicode_table()
		
		return self.string	

	def export_file(self, path):
		data = self.export_string()
		
		with open(path, "w") as f:
			f.write(data)

class PsfExporter(object):
	def __init__(self, font):
		self.font = font
		self.header = font.get_header()
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
		self.length = 0
		self.width = size[0]
		self.height = size[1]
		self.charsize = size[1] * int((size[0]+7) / 8)

	def set_length(self, length):
		"""Set the number of glyphs of the font
		
		Args:
			length (int): Number of glyphs to set
		"""
		self.length = length

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
		if self.header.version_psf == PSF2_VERSION:
			if self.header.has_unicode_table():
				self.header.set_length(len(self.glyphs))
			else:
				self.header.set_length(self.__len__())
			
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
