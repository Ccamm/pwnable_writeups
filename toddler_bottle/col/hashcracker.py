from pwn import *
import struct

context.log_level = 'debug'

hashcode_hex = "0x21DD09EC"
hashcode_0 = int(hashcode_hex, 16)/5
hashcode_1 = int(hashcode_hex, 16) - hashcode_0*4

print(hex(hashcode_0))
print(hex(hashcode_1))
