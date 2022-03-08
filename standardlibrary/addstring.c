#include <string.h>
#include <malloc.h>
#include <stdio.h>

char *addstring(const char *a, const char *b){
    size_t len_a = strlen(a);
    size_t len_b = strlen(b);
    char *c = malloc(len_a+len_b+1);
    char *d = stpcpy(c, a);
    stpcpy(d, b);
    return c;
}
