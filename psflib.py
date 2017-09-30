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

ASCII_PRINTABLE_OLD = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
ASCII_PRINTABLE = (
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

	def set_flags(self, flags):
		if flags != 1:
			raise Exception("Error, undefined bits set in PSF2 flags")
		self.flags |= flags

class PcScreenFont(object):
	def __init__(self, header):
		self.header = header
		self.glyphs = {}
		self.size = header.size
	
	def has_unicode(self):
		if self.header.psf_version == PSF1_VERSION:
			return True if self.mode & PSF1_MODEHASTAB else False
		else:
			return (True if self.flags & PSF2_HAS_UNICODE_TABLE
						 else False)
			
	
	def get_glyph(self, char):
		if char not in self.glyphs():
			self.glyphs[char] = Glyph()
		return self.glyphs[char]

	def is_touched(self):
		for glyph in self.glyphs.items():
			if glyph.touched: return True
		return False

class Glyhp(object):
	def __init__(self, size):
		self.data = [[0 for i in range(size[0])]
						for j in range(size[1])]
		self.touched = False
		
	def __getitem__(self, key):
		self.touched = True
		return self.data[key]
		

if __name__ == "__main__":
	pass
