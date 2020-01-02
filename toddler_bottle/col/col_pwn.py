from pwn import *
import struct

hashcode_hex = "0x21DD09EC"
hashcode_int = int(hashcode_hex, 16)

hashcode_0 = hashcode_int/5
hashcode_1 = hashcode_int - hashcode_0*(hashcode_int % (hashcode_0*5))

payload = ""
payload += struct.pack("<L", hashcode_0)*(hashcode_int % (hashcode_0*5))
payload += struct.pack("<L", hashcode_1)

s = ssh(host='pwnable.kr', port=2222, user='col', password='guest')
p = s.process(['./col', payload])
p.interactive()
