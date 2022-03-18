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
descriptor *matrix_slice(descriptor *m, long n, slice *s);
descriptor *broadcast(descriptor *a, descriptor *b);
int broadcastable(descriptor *a, descriptor *b);

void matrix_fill(descriptor *m, void *data);
void matrix_fill_range(descriptor *m);

void dump_descriptor(descriptor *m);

int is_contiguous(descriptor *m);
int matrix_index_end(descriptor *m, long index);
#endif
