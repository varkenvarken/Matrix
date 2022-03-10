#ifndef _MATRIX_H
#define _MATRIX_H	1

typedef struct {
     long dimensions;
     long size;
     double * data;
     long shape[];
} matrix_descriptor;

#endif
