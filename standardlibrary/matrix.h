#ifndef _MATRIX_H
#define _MATRIX_H 1

#define TYPE_DOUBLE 1
#define TYPE_FLOAT 2
#define TYPE_COMPLEX 9
#define TYPE_COMPLEX_FLOAT 10
#define TYPE_QUATERNION 17
#define TYPE_QUATERNION_FLOAT 18
#define TYPE_BOOL 64
#define TYPE_LONG 128

#define SIZE_DOUBLE 8
#define SIZE_FLOAT 4
#define SIZE_COMPLEX 16
#define SIZE_COMPLEX_FLOAT 8
#define SIZE_QUATERNION 32
#define SIZE_QUATERNION_FLOAT 16
#define SIZE_BOOL 128
#define SIZE_LONG 8

#define MAX_DIMENSIONS 32
typedef struct
{
     long dimensions; // zero for a scalar
     long size;       // size of the type in bytes
     long elements;   // total number of elements
     long flags;      // reserved
     long type;
     void *data;  // pointer to the start of the data
     void *base;  // points to underlying data if this is a view
     long offset; // offset into data where first element is located
     long shape[MAX_DIMENSIONS];
     long stride[MAX_DIMENSIONS];
} descriptor;

typedef struct{
     long start;
     long stop;
     long step;
} slice;
#endif
