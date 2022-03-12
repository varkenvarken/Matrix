#include "matrix.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

void matrixcopy(matrix_descriptor **src, matrix_descriptor **dst)
{
    long size = (*src)->size;
    long dim = (*src)->dimensions;
    long *shape = (*src)->shape;
    double *srcdata = (*src)->data;
    double *dstdata = (*dst)->data;

    for (int i = 0; i < dim; i++)
    {
        size *= shape[i];
    }

    memcpy(dstdata, srcdata, size);
}

matrix_descriptor *matrix_malloc_desc(matrix_descriptor *src)
{
    long size = (src)->size;
    long dim = (src)->dimensions;
    long *shape = (src)->shape;

    for (int i = 0; i < dim; i++)
    {
        size *= shape[i];
    }

    matrix_descriptor *newdesc = malloc((1 + 1 + 1 + dim) * 8);
    newdesc->size = src->size;
    newdesc->dimensions = src->dimensions;
    for (int i = 0; i < dim; i++)
    {
        newdesc->shape[i] = src->shape[i];
    }
    newdesc->data = malloc(size);

    return newdesc;
}

long matrix_data_elements(matrix_descriptor *m)
{
    long size = 1;
    long dim = m->dimensions;
    long *shape = m->shape;

    for (int i = 0; i < dim; i++)
    {
        size *= shape[i];
    }

    return size;
}

void print_row(double *data, long len, long dim)
{
    printf("%*s", (int)dim, "[");
    while (len--)
    {
        printf("%9.4f ", *data++);
    }
    puts(" ]");
}

void print_matrix(matrix_descriptor *m)
{
    long dim = m->dimensions;
    long *shape = m->shape;
    double *data = m->data;

    long strides[32];
    long rows = 1;
    long nelements = matrix_data_elements(m);

    for (long i = 0; i < dim - 1; i++)
    {
        rows *= shape[i];
    }

    for (long i = dim - 1, stride = 1; i >= 0; i--)
    {
        strides[i] = stride;
        stride *= shape[1];
    }

    for (long i = 0; i < rows; i++)
    {
        // printf(">>> %ld [%ld,%ld]\n",i,strides[0],strides[1]);
        for (int d = 0; d < dim - 1; d++)
        {
            if (i % strides[d] == 0)
            {
                printf("%*s\n", d + 1, "[");
            }
        }
        print_row(data, shape[dim - 1], dim);
        for (int d = dim - 2; d >= 0; d--)
        {
            if ((i + 1) % strides[d] == 0)
            {
                printf("%*s\n", d + 1, "]");
            }
        }
        data += shape[dim - 1];
    }
}

matrix_descriptor *matrix_index(matrix_descriptor *m, long index)
{
    long size = (m)->size;
    long dim = (m)->dimensions;
    long *shape = (m)->shape;
    double *data = m->data;

    long strides[32];
    for (long i = dim - 1, stride = 1; i >= 0; i--)
    {
        strides[i] = stride;
        stride *= shape[1];
    }
    long newdim = dim;
    if (dim > 1)
    {
        newdim = dim - 1;
    }
    matrix_descriptor *newdesc = malloc((1 + 1 + 1 + newdim) * 8);
    newdesc->size = size;
    newdesc->dimensions = newdim;
    if (dim > 1)
    {
        for (int i = 1; i < dim; i++)
        {
            newdesc->shape[i - 1] = shape[i];
        }
        newdesc->data = data + index * strides[0];
    }
    else
    {
        newdesc->shape[0] = 1;
        newdesc->data = data + index;
    }

    return newdesc;
}