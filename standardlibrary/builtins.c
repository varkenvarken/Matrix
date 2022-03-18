#include <stdio.h>
#include "matrix.h"
#include "matrixutil.h"

descriptor *copy(descriptor *m)
{
    descriptor *newdesc = duplicate_descriptor(m);
    descriptorcopy(m, newdesc);
    return newdesc;
}

descriptor *shape(descriptor *m)
{
    long shape = m->dimensions;
    descriptor *shape_as_desc = new_descriptor(TYPE_DOUBLE, 1, &shape);
    for (long i = 0; i < m->dimensions; i++)
    {
        ((double *)(shape_as_desc->data))[i] = (double)(m->shape[i]);
    }
    return shape_as_desc;
}

double dimensions(descriptor *m)
{
    return (double)(m->dimensions);
}

descriptor *reshape(descriptor *m, descriptor *shape)
{
    // puts("reshape m");
    // dump_descriptor(m);
    // puts("to shape");
    // dump_descriptor(shape);

    if (shape->dimensions != 1)
    {
        fputs("reshape: shape argument must be 1 dimensional", stderr);
        exit(EXIT_FAILURE);
    }
    if (shape->shape[0] > MAX_DIMENSIONS)
    {
        fprintf(stderr, "reshape: shape argument length %ld > %d", shape->shape[0], MAX_DIMENSIONS);
        exit(EXIT_FAILURE);
    }
    if (!is_contiguous(m))
    {
        fputs("reshape: cannot reshape non-contiguous matrix", stderr);
        exit(EXIT_FAILURE);
    }
    long nelements = 1;
    for (long i = 0; i < shape->shape[0]; i++)
    {
        nelements *= (long)(((double *)(shape->data + shape->offset))[i]);
    }
    if (m->elements != nelements)
    {
        fprintf(stderr, "reshape: shape argument number of elements does not match (%ld)\n", nelements);
        exit(EXIT_FAILURE);
    }
    m->dimensions = shape->shape[0];
    for (long i = 0; i < shape->shape[0]; i++)
    {
        m->shape[i] = (long)(((double *)(shape->data + shape->offset))[i]);
    }
    calculate_strides(m);
    return m;
}

descriptor *fill(descriptor *m, double d)
{
    matrix_fill(m, &d);
    return m;
}

descriptor *arange(descriptor *m)
{
    matrix_fill_range(m);
    return m;
}

// fill a 'square' matrix with the identity.
// square = size of all dimensions is the same
descriptor *eye(descriptor *m)
{
    for (long i = 0; i < m->dimensions; i++)
    {
        if (m->shape[i] != m->shape[0])
        {
            fprintf(stderr, "eye matrix is not a regular hypercube\n");
            exit(EXIT_FAILURE);
        }
    }
    if (m->dimensions == 0)
    {
        *((double *)(m->data + m->offset)) = 1.0;
    }
    else
    {
        double zero = 0.0;
        matrix_fill(m, &zero);
        long index[MAX_DIMENSIONS];
        for (int i = 0; i < MAX_DIMENSIONS; i++)
        {
            index[i] = 0;
        }
        void *data = m->data + m->offset;
        // dump_descriptor(m);
        for (long i = 0; i < m->shape[0]; i++)
        {
            long offset = 0;
            for (long j = 0; j < m->dimensions; j++)
            {
                offset += index[j] * m->stride[j];
            }
            for (long k = 0; k < m->dimensions; k++)
            {
                // printf("%ld ", index[k]);
                index[k]++;
            }
            // printf("\n");
            *((double *)(data + offset)) = 1.0;
        }
    }
    return m;
}

double length(descriptor *m)
{
    return (double)(m->shape[0]);
}

descriptor *range(double start, double stop, double step)
{
    if (step == 0)
    {
        step = 1;
    }
    long shape = 1;
    if (start > stop)
    {
        if (step < 0)
        {
            shape = (long)((start - stop) / -step);
        }
    }
    else if (stop > start)
    {
        if (step > 0)
        {
            shape = (long)((stop - start) / step);
        }
    } // if start == stop shape stays 1
    // fprintf(stderr, "start %.4f stop %.4f step %.4f shape %ld\n", start, stop, step, shape);
    descriptor *r = new_descriptor(TYPE_DOUBLE, 1, &shape);
    double *d = (double *)(r->data + r->offset);
    for (long i = 0; i < shape; i++, d++, start += step)
    {
        *d = start;
    }
    return r;
}