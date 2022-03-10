#ifndef _MATRIXUTIL_H
#define _MATRIXUTIL_H	1

#include "matrix.h"
#include <stdlib.h>
#include <string.h>

void matrixcopy(matrix_descriptor **src, matrix_descriptor **dst);
matrix_descriptor *matrix_malloc_desc(matrix_descriptor *src);
long matrix_data_elements(matrix_descriptor *m);
void print_matrix(matrix_descriptor *m);

#endif
