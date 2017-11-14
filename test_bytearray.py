import psflib

bytes = []

for i in range(100):
    bytes.append(psflib.Byte.from_int(i))

b = psflib.ByteArray(bytes)
print(b.bytestring("test", 50, 2))
