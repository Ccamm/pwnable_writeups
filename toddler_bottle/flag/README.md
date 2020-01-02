# Pwnable.kr: Toddler's Bottle
## flag

This is just a simple reverse engineering task for finding the flag located inside of an executable binary that we can download from http://pwnable.kr/bin/flag.

After downloading the binary and running it, we are given the hint that the flag will be copied into a buffer.

*output*
```
I will malloc() and strcpy the flag there. take it.
```

So let's run the binary inside of *gdb* to try and find this flag. However, we immediately run into an issue when trying to disassemble the main function.

```
gdb-peda$ disas main
No symbol table is loaded.  Use the "file" command.
```

Welp, let's run the *file* command and try to figure out why we cannot disassemble the main function.

```
$ file flag
flag: ELF 64-bit LSB executable, x86-64, version 1 (GNU/Linux), statically linked, no section header
```

Well we know we have an executable, but it does not give us anymore useful information besides that we cannot use *ltrace* to find the *strcpy* call since it is not dynamically linked. Let's try *strings flag* and see if we can find anything.

Aha! Running *strings flag* shows us that the executable starts with 'UPX!' at the start and end of the file, and a quick google search tells us that UPX is a executable packer. This means that we probably need to decompress the flag binary by running *upx -d flag* then run it in *gdb*.

Now we can disassemble the main function inside of *gdb*!

<pre>
gdb-peda$ disas main
Dump of assembler code for function main:
   0x0000000000401164 <+0>:	push   rbp
   0x0000000000401165 <+1>:	mov    rbp,rsp
   0x0000000000401168 <+4>:	sub    rsp,0x10
   0x000000000040116c <+8>:	mov    edi,0x496658
   0x0000000000401171 <+13>:	call   0x402080 <puts>
   0x0000000000401176 <+18>:	mov    edi,0x64
   0x000000000040117b <+23>:	call   0x4099d0 <malloc>
   0x0000000000401180 <+28>:	mov    QWORD PTR [rbp-0x8],rax
   <b>0x0000000000401184 <+32>:	mov    rdx,QWORD PTR [rip+0x2c0ee5]        # 0x6c2070 <flag></b>
   0x000000000040118b <+39>:	mov    rax,QWORD PTR [rbp-0x8]
   0x000000000040118f <+43>:	mov    rsi,rdx
   0x0000000000401192 <+46>:	mov    rdi,rax
   0x0000000000401195 <+49>:	call   0x400320
   0x000000000040119a <+54>:	mov    eax,0x0
   0x000000000040119f <+59>:	leave  
   0x00000000004011a0 <+60>:	ret    
End of assembler dump.
</pre>

It looks like the writers of the challenge have given us a hint by pointing out when the flag is moved into the RDX register. Let's check by creating a break point at 0x000000000040118b and see what is stored inside the RDX register.

<pre>
gdb-peda$ b * main+39
Breakpoint 1 at 0x40118b
gdb-peda$ r
Starting program: /home/ghostccamm/Desktop/pwnable/write_ups/toddler_bottle/flag/flag
I will malloc() and strcpy the flag there. take it.
[----------------------------------registers-----------------------------------]
RAX: 0x6c96b0 --> 0x0
RBX: 0x401ae0 (<__libc_csu_fini>:	push   rbx)
RCX: 0x8
<b>RDX: 0x496628 ("UPX...? sounds like a delivery service :)")</b>
</pre>

There we go! The address of the flag is right there for us to see.

An alternative way we could of found the flag was running *strings -n 10 flag* and looking for any strings with words in it near the string "I will malloc() and strcpy the flag there. take it." which we know the executable has. Once again we can find the flag sitting just before the string that we know is already inside the binary.

*snippet from output of strings -n 10 flag*
```
UPX...? sounds like a delivery service :)
I will malloc() and strcpy the flag there. take it.
```
