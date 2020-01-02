# Pwnable.kr: Toddler's Bottle
## col

This challenge requires us finding a hash collision for a poorly designed hashing algorithm. Below is the source code showing us that the hashing algorithm is summing up the groups 4 bytes from a password of length 20 bytes.

```c
#include <stdio.h>
#include <string.h>
unsigned long hashcode = 0x21DD09EC;
unsigned long check_password(const char* p){
	int* ip = (int*)p;
	int i;
	int res=0;
	for(i=0; i<5; i++){
		res += ip[i];
	}
	return res;
}

int main(int argc, char* argv[]){
	if(argc<2){
		printf("usage : %s [passcode]\n", argv[0]);
		return 0;
	}
	if(strlen(argv[1]) != 20){
		printf("passcode length should be 20 bytes\n");
		return 0;
	}

	if(hashcode == check_password( argv[1] )){
		system("/bin/cat flag");
		return 0;
	}
	else
		printf("wrong passcode.\n");
	return 0;
}
```

Now obviously, there are an infinite number of hash collisions for *0x21dd09ec*, but we are constrained by the size of integers being 4 bytes long and it is signed so if we try to parse a integer with the first bit set it would subtract instead. Therefore we need to make the integers we input in as close to each other so the first bit is not set, they are 4 bytes long each and we don't accidentally send any null bytes.

We can do this by dividing the hash by 5 (since we need 5 integers) and for the remainder of hash/5 we can put into the last number we send it. We can now write our pwn script.

```python
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
```

Bingo! We got the flag!

<pre>
[+] Connecting to pwnable.kr on port 2222: Done
[*] col@pwnable.kr:
    Distro    Ubuntu 16.04
    OS:       linux
    Arch:     amd64
    Version:  4.4.179
    ASLR:     Enabled
[+] Starting remote process './col' on pwnable.kr: pid 244695
[*] Switching to interactive mode
daddy! I just managed to create a hash collision :)
</pre>
