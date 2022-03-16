#ifndef _BUILTINS_H
#define _BUILTINS_H 1

#include "matrix.h"

descriptor *copy(descriptor *m);
descriptor *shape(descriptor *m);
descriptor *reshape(descriptor *m, descriptor *shape);
double dimensions(descriptor *m);

#endif
