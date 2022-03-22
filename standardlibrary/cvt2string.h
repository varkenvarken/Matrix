#ifndef _CVT2STRING_H
#define _CVT2STRING_H 1

#include "matrix.h"

char *cvt_double(double d);
char *cvt_descriptor(descriptor *m);
char *concat_strings(char **list, long n);

#endif