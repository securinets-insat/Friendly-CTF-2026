#include <unistd.h>

int main(void)
{
    return execl("/bin/sh", "sh", NULL);
}
