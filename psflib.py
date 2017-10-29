PSF1_VERSION = 1
PSF2_VERSION = 2

PSF1_MODE512 = 0x01
PSF1_MODEHASTAB = 0x02
PSF1_MODEHASSEQ = 0x04
PSF1_MAXMODE = 0x05

PSF1_SEPARATOR = 0xFFFF
PSF1_STARTSEQ = 0xFFFE

PSF2_MAXVERSION = 0
PSF2_HAS_UNICODE_TABLE = 0x1

ASCII_PRINTABLE_OLDER = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
ASCII_PRINTABLE_OLD = (
	(" " , "Space"),
	("!" , "Exclamation mark"),
	('"' , "Quotation mark"),
	("#" , "Number sign"),
	("$" , "Dollar sign"),
	("%" , "Percent sign"),
	("&" , "Ampersant"),
	("'" , "Apostrophe"),
	("(" , "Left parenthesis"),
	(")" , "Right parenthesis"),
	("*" , "Asterisk") ,
	("+" , "Plus sign"),
	("," , "Hyphen minus"),
	("." , "Full stop"),
	("/" , "Slash"),
	("0" , "Zero"),
	("1" , "One")
)
ASCII_PRINTABLE = {}

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
		self.string += "font:\n"
		if self.version == 1:
			magic_bytes = (hex(self.header.magic_bytes[0]),
						   hex(self.header.magic_bytes[1]))
			self.string += "magic_bytes: db %s, %s" % hex(s)
			self.string += "mode:	db %s" % hex(self.header.mode)
			self.string += "charsize: db %s" % hex(self.header.charsize)

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
	def readFromFile(self, psf_file):
		pass
		
	def has_unicode_table(self):
		if self.version_psf == PSF1_VERSION:
			return self.mode & PSF1_MODEHASTAB
		else:
			return self.flags & PSF2_HAS_UNICODE_TABLE
			
class PsfHeaderv1(PsfHeader):
	def __init__(self, size):
		PsfHeader.__init__(self, PSF1_VERSION, size)
		self.magic_bytes = [0x36, 0x04]
		
		if (size[0] != 8):
			raise Exception("Error, for PSF1 the font width must be 8")
		self.charsize = size[1]
		self.mode = 0
	
	def set_mode(self, mode):
		if mode > 7:
			raise Exception("Error, undefined bits set in PSF1 mode")
		self.mode |= mode

class PsfHeaderv2(PsfHeader):
	def __init__(self, size):
		PsfHeader.__init__(self, PSF2_VERSION, size)
		self.magic_bytes = [0x72, 0xb5, 0x4a, 0x86]
		self.version = PSF2_MAXVERSION
		self.header_size = 32	# Values are encoded as 4byte integers
		self.flags = 0
		self.charsize = size[1] * (size[0]+7) / 8

	def set_flags(self, flags):
		if flags != 1:
			raise Exception("Error, undefined bits set in PSF2 flags")
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
		if self.header.psf_version == PSF1_VERSION:
			return True if self.mode & PSF1_MODEHASTAB else False
		else:
			return (True if self.flags & PSF2_HAS_UNICODE_TABLE
						 else False)
			
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
	
	def __str__(self):
		data = u""
		print(self.glyphs.keys())
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
		size (tuple(int, int)) : size of the bitmap representing the
			character
	"""
	def __init__(self, size):
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
			self.unicode_representations.remove(old_cp)
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
	
	def copy_data(self, data):
		"""Update the bitmap with given data
		
		Args:
			data (list of lists with integers)) : the data to update the
				bitmap with. Each element of the data represents a row
				of the bitmap and each element in a row represents a
				pixel.
				The pixel is set, if its value equal 1.
		
		"""
		self.touched = True
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
		return self.data
		
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
