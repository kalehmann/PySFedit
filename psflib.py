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

def get_unicode_str(char):
	if 0x20 <= char <= 0x7e or 0xa0 <= char <= 0xff:
		return unichr(char)
		
def get_ord(txt):
	if len(txt) != 1: return None
	n = ord(txt)
	if 0x20 <= n <= 0x7e or 0xa0 <= n <= 0xff:
		return n
	return None

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
	def __init__(self, header):
		self.header = header
		self.glyphs = []
		self.size = header.size
	
	def has_unicode(self):
		if self.header.psf_version == PSF1_VERSION:
			return True if self.mode & PSF1_MODEHASTAB else False
		else:
			return (True if self.flags & PSF2_HAS_UNICODE_TABLE
						 else False)
			
	
	def get_glyph(self, uc):
		for glyph in self.glyphs:
			if glyph.has_unicode_representation(uc):
				return glyph
		glyph = Glyph(self.size)
		glyph.add_unicode_representation(uc)
		self.glyphs.append(glyph)
		return glyph

	def is_touched(self):
		for glyph in self.glyphs.items():
			if glyph.touched: return True
		return False

class Glyph(object):
	def __init__(self, size):
		self.data = [[0 for i in range(size[0])]
						for j in range(size[1])]
		self.touched = False
		self.width = size[0]
		self.height = size[1]
		self.unicode_representations = []
		
	def add_unicode_representation(self, uc):
		self.unicode_representations.append(uc)	
	
	def has_unicode_representation(self, uc):
		return uc in self.unicode_representations
	
	def copy_data(self, data):
		self.touched = True
		for i in range(self.height):
			for j in range(self.width):
				self.data[i][j] = data[i][j]
		
	def __repr__(self):
		out = ""
		for i in self.data:
			for j in i:
				out += "#" if j else "."
			out += "\n"
		return out.encode('UTF-8')

if __name__ == "__main__":
	pass
