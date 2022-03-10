#include "matrix.h"
#include "matrixutil.h"

// TODO: verify if operands are compatible
// TODO: check for malloc failures
matrix_descriptor *addmat(matrix_descriptor *a, matrix_descriptor *b){
    matrix_descriptor *c = matrix_malloc_desc(a);
    long elements = matrix_data_elements(c);

    double *ad = a->data;
    double *bd = b->data;
    double *cd = c->data;

    for(long i=0; i< elements; i++){
        *cd++ = *ad++ + *bd++;
    }

    return c;
}