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
	setenv("\xde\xad\xbe\xef", "\xca\xfe\xba\xbe", 1);
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
