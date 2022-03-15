#ifndef _MATRIXUTIL_H
#define _MATRIXUTIL_H 1

#include "matrix.h"
#include <stdlib.h>
#include <string.h>

void calculate_strides(descriptor *m);
void *step(descriptor *m, long *index);
void descriptorcopy(descriptor *src, descriptor *dst);
void matrixcopy(descriptor **src, descriptor **dst);
descriptor *duplicate_descriptor(descriptor *m);
descriptor *new_descriptor(long type, long dimensions, long shape[MAX_DIMENSIONS]);
void print_descriptor(descriptor *m);
descriptor *matrix_index(descriptor *m, long index);

void matrix_fill(descriptor *m, void *data);
void matrix_fill_range(descriptor *m);

void dump_descriptor(descriptor *m);
#endif
