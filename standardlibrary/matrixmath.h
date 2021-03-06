#ifndef _MATRIXMATH_H
#define _MATRIXMATH_H 1

#include "matrix.h"

descriptor *matrix_add(descriptor *, descriptor *);
descriptor *matrix_subtract(descriptor *a, descriptor *b);
descriptor *matrix_multiply(descriptor *, descriptor *);
descriptor *matrix_divide(descriptor *a, descriptor *b);
descriptor *matrix_modulo(descriptor *a, descriptor *b);
descriptor *matrix_notequal(descriptor *a, descriptor *b);

descriptor *matrix_negate(descriptor *a);

double matrix_notequalany(descriptor *a, descriptor *b);

#endif
