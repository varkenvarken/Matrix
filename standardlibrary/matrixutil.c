#include "matrix.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

// given an matrix descriptor with dimensions, shape
// and size set, calculate the stride assumming C-contigueous data
void calculate_strides(descriptor *m)
{
    long stride = m->size;
    if (m->dimensions == 0)
    {
        m->stride[0] = stride;
    }
    else
    {
        for (long d = m->dimensions - 1; d >= 0; d--)
        {
            m->stride[d] = stride;
            stride *= m->shape[d];
        }
    }
}

// for debugging
void dump_descriptor(descriptor *m)
{
    printf("data: @%p, base: @%p\n", m->data, m->base);
    printf("dim: %ld, type: %ld, size: %ld, elements: %ld offset: %ld(%ld elements of size %ld)\n",
           m->dimensions, m->type, m->size, m->elements, m->offset, m->offset / m->size, m->size);
    for (int i = 0; i < m->dimensions; i++)
    {
        printf("dim %d: %ld , stride %ld (%ld elements of size %ld)\n", i, m->shape[i], m->stride[i], m->stride[i] / m->size, m->size);
    }
}

// return a pointer to the next datapoint and update the index
// return NULL if there is no next datapoint
void *step(descriptor *m, long *index)
{
    if (m->type == TYPE_DOUBLE)
    {
        if (m->dimensions == 0)
        {
            return NULL;
        }
        // increment indices
        for (long d = m->dimensions - 1; d >= 0; d--)
        {
            // if there is no rollover, no other indices need to be incremented
            index[d]++;
            if (index[d] >= m->shape[d])
            {
                index[d] = 0;
                if (d == 0)
                {
                    return NULL; // if the highest index is rolled over we're done
                }
            }
            else
            {
                break;
            }
        }

        long strideoffset = 0;
        for (long d = m->dimensions - 1; d >= 0; d--)
        {
            strideoffset += index[d] * m->stride[d];
        }

        return (void *)(m->data + m->offset + strideoffset);
    }
    else
    {
        fputs("index only supports doubles for now", stderr);
        exit(EXIT_FAILURE);
    }
}

// return true if types and total number of elements are the same
int compatible(descriptor *a, descriptor *b)
{
    if (a->type != b->type)
        return 0;
    if (a->elements != b->elements)
        return 0;
    return 1;
}

// copy the data from one descriptor to the other
// the data type and the total number of elements should be the same
// dimensions and strides may be different
// if src and dst point to overlapping regions the behaviour is undefined
void descriptorcopy(descriptor *src, descriptor *dst)
{
    puts("descriptorcopy");
    puts("src:");
    dump_descriptor(src);
    puts("dst:");
    dump_descriptor(dst);
    if (!compatible(src, dst))
    {
        fputs("descriptor copy on incompatible types", stderr);
        exit(EXIT_FAILURE);
    }
    if (src->type != TYPE_DOUBLE)
    {
        fputs("descriptor copy only supports double for now", stderr);
        exit(EXIT_FAILURE);
    }

    if (src->dimensions == 0)
    { // copy a single value for scalars
        switch (src->type)
        {
        case TYPE_DOUBLE:
            *((double *)(dst->data + dst->offset)) = *((double *)(src->data + src->offset));
            break;
        }
    }
    else
    { // TODO: optimization opportunity: if stride[highestdim] == size we can memcopy whole dimensions
        long s_index[MAX_DIMENSIONS];
        long d_index[MAX_DIMENSIONS];
        double *d, *s;
        for (int i = 0; i < MAX_DIMENSIONS; i++)
            s_index[i] = d_index[i] = 0;
        switch (src->type)
        {
        case TYPE_DOUBLE:
            d = (double *)(dst->data + dst->offset);
            s = (double *)(src->data + src->offset);
            do
            {
                *d = *s;
                d = step(dst, d_index);
                s = step(src, s_index);
            } while (d != NULL && s != NULL);
            break;
        }
    }
}

void matrixcopy(descriptor **src, descriptor **dst)
{
    descriptorcopy(*src, *dst);
}

// malloc a new desciptor and allocate size for a contigeous number of elements
descriptor *duplicate_descriptor(descriptor *m)
{
    descriptor *newdesc = malloc(sizeof(descriptor));
    *newdesc = *m;
    calculate_strides(newdesc); // recalulate the stride for C-contigeous memory
    newdesc->base = NULL;       // we are NOT creating a view but a new matrix
    newdesc->offset = 0;
    newdesc->data = malloc(newdesc->size * newdesc->elements);
    return newdesc;
}

descriptor *new_empty_descriptor(long type, long dimensions, long shape[MAX_DIMENSIONS])
{
    long size = 0;
    switch (type)
    {
    case TYPE_DOUBLE:
        size = SIZE_DOUBLE;
        break;
    default:
        fputs("new descriptor only supports double for now", stderr);
        exit(EXIT_FAILURE);
        break;
    }
    descriptor *newdesc = malloc(sizeof(descriptor));
    newdesc->type = type;
    newdesc->dimensions = dimensions;
    newdesc->size = size;
    for (int i = 0; i < dimensions; i++)
    {
        newdesc->shape[i] = shape[i];
    }
    calculate_strides(newdesc);
    newdesc->elements = 1;
    for (int i = 0; i < dimensions; i++)
    {
        newdesc->elements *= shape[i];
    }
    newdesc->offset = 0;
    return newdesc;
}

descriptor *new_descriptor(long type, long dimensions, long shape[MAX_DIMENSIONS])
{
    descriptor *newdesc = new_empty_descriptor(type, dimensions, shape);
    newdesc->data = malloc(newdesc->elements * newdesc->size);
    return newdesc;
}

void matrix_fill(descriptor *m, void *data)
{
#ifdef DEBUG
    dump_descriptor(m);
#endif
    switch (m->type)
    {
    case TYPE_DOUBLE:
        break;
    default:
        fputs("matrix fill only supports double for now", stderr);
        exit(EXIT_FAILURE);
        break;
    }
    if (m->dimensions == 0)
    { // fill a single value for scalars
        switch (m->type)
        {
        case TYPE_DOUBLE:
            *((double *)(m->data + m->offset)) = *((double *)data);
            break;
        }
    }
    else
    {
        double *d;
        long index[MAX_DIMENSIONS], old_index[MAX_DIMENSIONS];
        for (int i = 0; i < MAX_DIMENSIONS; i++)
            index[i] = old_index[i] = 0;
        switch (m->type)
        {
        case TYPE_DOUBLE:
            d = (double *)(m->data + m->offset);
            do
            {
                *d = *((double *)data);
                // printf("%.3f @ %p [%ld,%ld]\n", *d, d, index[0], index[1]);
                d = step(m, index);
            } while (d != NULL);
            break;
        }
    }
}

void matrix_fill_range(descriptor *m)
{
    switch (m->type)
    {
    case TYPE_DOUBLE:
        break;
    default:
        fputs("matrix fill range only supports double for now", stderr);
        exit(EXIT_FAILURE);
        break;
    }
    if (m->dimensions == 0)
    { // fill a single value for scalars
        switch (m->type)
        {
        case TYPE_DOUBLE:
            *((double *)(m->data + m->offset)) = 0.0;
            break;
        }
    }
    else
    {
        double value = 0.0;
        double *data = (double *)(m->data + m->offset);
        long index[MAX_DIMENSIONS], old_index[MAX_DIMENSIONS];
        for (int i = 0; i < MAX_DIMENSIONS; i++)
            index[i] = old_index[i] = 0;
        switch (m->type)
        {
        case TYPE_DOUBLE:
            do
            {
                *data = value++;
                data = step(m, index);
            } while (data != NULL);
            break;
        }
    }
}

void print_descriptor(descriptor *m)
{

    puts("print_descriptor");
    dump_descriptor(m);

    if (m->type != TYPE_DOUBLE)
    {
        fputs("print descriptor only supports double for now", stderr);
        exit(EXIT_FAILURE);
    }

    if (m->dimensions == 0)
    { // copy a single value for scalars
        switch (m->type)
        {
        case TYPE_DOUBLE:
            printf("%9.4f\n", *((double *)(m->data + m->offset)));
            break;
        }
    }
    else
    {
        double *d;
        long index[MAX_DIMENSIONS], old_index[MAX_DIMENSIONS];
        for (int i = 0; i < MAX_DIMENSIONS; i++)
            index[i] = old_index[i] = 0;
        switch (m->type)
        {
        case TYPE_DOUBLE:
            d = (double *)(m->data + m->offset);
            printf("PTR m:%p data:%p = %f\n", m, d, *d);
            do
            {
                printf("%9.4f ", *d);
                d = step(m, index);
                // if the last dimension has rolled over, we print a newline
                if ((index[m->dimensions - 1] != old_index[m->dimensions - 1]) && index[m->dimensions - 1] == 0)
                {
                    fputs("\n", stdout);
                }
                for (int i = 0; i < MAX_DIMENSIONS; i++)
                    old_index[i] = index[i];
            } while (d != NULL);
            puts("");
            break;
        }
    }
}

// create a new view based on a single index into the highest dimension
descriptor *matrix_index(descriptor *m, long index)
{
    printf("matrix_index [%ld]\n", index);
    dump_descriptor(m);
    // print_descriptor(m);

    if (m->dimensions)
    {
        descriptor *newdesc = new_descriptor(m->type, m->dimensions - 1, m->shape + 1);
        printf("INTERMEDIATE matrix_index [%ld]\n", index);
        dump_descriptor(newdesc);

        for (int j = 0, i = 1; i < m->dimensions; i++, j++)
        {
            printf("j:%d i:%d mdim:%ld\n", j, i, m->dimensions);
            newdesc->stride[j] = m->stride[i];
        }
        newdesc->base = m->base ? m->base : m->data;
        newdesc->data = m->data + m->offset;
        newdesc->offset = index * m->stride[0];

        printf("RESULT matrix_index [%ld]\n", index);
        dump_descriptor(newdesc);
        print_descriptor(newdesc);

        return newdesc;
    }

    return NULL;
}