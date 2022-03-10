#include "matrix.h"
#include <string.h>

void matrixcopy(matrix_descriptor **src, matrix_descriptor **dst){
    long size = (*src)->size;
    long dim = (*src)->dimensions;
    long *shape = (*src)->shape;
    double *srcdata = (*src)->data;
    double *dstdata = (*dst)->data;

    for(int i=0; i<dim; i++){
        size *= shape[i]; 
    }

    memcpy (dstdata, srcdata, size);
}
