#include <stdio.h>
#include <string.h>

int main()
{
	unsigned long hash = 0x21DD09EC;
	unsigned long hashcode = 0x21DD09EC/5;
	printf("%u | %x\n", hash);
	printf("%u | %x\n", hashcode);
}
