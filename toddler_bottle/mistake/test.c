#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
	char *s = argv[1];
	printf("%x\n", s[0]);
	for(int i = 0; i < 10; i++) {
		s[i] ^= 1;
	}
	printf("%x\n", s[0]);
	printf("%s\n", s);
}
