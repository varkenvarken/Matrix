#include <stdio.h>
#include "matrix.h"
#include "matrixutil.h"
#include "arithmatic.h"

void _recursive_add(void *cd, void *ad, void *bd, long *cstride, long *astride, long *bstride, long *shape, long dim);

// TODO: check for malloc failures
// check for compat and does broadcast
// returns a, b (possibly broadcasted)
void binop_common(char *op, descriptor *a, descriptor *b, descriptor **ab)
{
#ifdef DEBUG
    puts(op);
    puts("a:");
    dump_descriptor(a);
    puts("b:");
    dump_descriptor(b);
#endif

    switch (a->type)
    {
    case TYPE_DOUBLE:
        break;
    default:
        fprintf(stderr, "matrix %s: only for doubles for now", op);
        exit(EXIT_FAILURE);
    }

    ab[0] = a;
    ab[1] = b;

    switch (broadcastable(a, b))
    {
    case -1:
        if (broadcastable(b, a) < 0) // we don have to check for 0 because that would have been caught by the first test
            exit(EXIT_FAILURE);
        else
            ab[0] = broadcast(b, a);
        break;
    case 0: // no need to broadcast
        break;
    default: // create a broadcast descriptor from b that matches a
        ab[1] = broadcast(a, b);
        break;
    }
}

descriptor *matrix_add(descriptor *a, descriptor *b)
{
    // puts("in a");
    // dump_descriptor(a);
    // puts("in b");
    // dump_descriptor(b);

    descriptor *ab[2];
    binop_common("add", a, b, ab);
    a = ab[0];
    b = ab[1];
    descriptor *c = duplicate_descriptor(a);

    // puts("out a");
    // dump_descriptor(a);
    // puts("out b");
    // dump_descriptor(b);
    // puts("out c");
    // dump_descriptor(c);
    // puts("");

    if (a->dimensions == 0)
    { // a scalar
        *((double *)(c->data + c->offset)) = *((double *)(a->data + a->offset)) + *((double *)(b->data + b->offset));
    }
    else
    {
        long a_index[MAX_DIMENSIONS];
        long b_index[MAX_DIMENSIONS];
        long c_index[MAX_DIMENSIONS];
        for (int i = 0; i < a->dimensions; i++)
            a_index[i] = b_index[i] = c_index[i] = 0;
        void *ad = a->data + a->offset;
        void *bd = b->data + b->offset;
        void *cd = c->data + c->offset;
        switch (a->dimensions)
        {
        case 1:
            _add_double(cd, ad, bd, c->stride[0], a->stride[0], b->stride[0], a->shape[0]);
            break;
        case 2:
            for (long i = 0; i < a->shape[0]; i++)
            {
                _add_double(cd, ad, bd, c->stride[1], a->stride[1], b->stride[1], a->shape[1]);
                ad += a->stride[0];
                bd += b->stride[0];
                cd += c->stride[0];
            }
            break;
        default:
            for (long i = 0; i < a->shape[0]; i++)
            {
                _recursive_add(cd, ad, bd, c->stride + 1, a->stride + 1, b->stride + 1, a->shape + 1, a->dimensions - 1);
                ad += a->stride[0];
                bd += b->stride[0];
                cd += c->stride[0];
            }
            break;
        }
    }
    return c;
}

void _recursive_add(void *cd, void *ad, void *bd, long *cstride, long *astride, long *bstride, long *shape, long dim)
{
    // printf("recursive add: %p %p %p    %ld\n", cd, ad, bd, dim);
    if (dim == 2)
    {
        for (long i = 0; i < shape[0]; i++)
        {
            _add_double(cd, ad, bd, cstride[1], astride[1], bstride[1], shape[1]);
            ad += astride[0];
            bd += bstride[0];
            cd += cstride[0];
        }
    }
    else
    {
        for (long i = 0; i < shape[0]; i++)
        {
            _recursive_add(cd, ad, bd, cstride + 1, astride + 1, bstride + 1, shape + 1, dim - 1);
            ad += astride[0];
            bd += bstride[0];
            cd += cstride[0];
        }
    }
}

descriptor *matrix_add_old(descriptor *a, descriptor *b)
{
    // puts("in a");
    // dump_descriptor(a);
    // puts("in b");
    // dump_descriptor(b);

    descriptor *ab[2];
    binop_common("add", a, b, ab);
    a = ab[0];
    b = ab[1];
    descriptor *c = duplicate_descriptor(a);

    // puts("out a");
    // dump_descriptor(a);
    // puts("out b");
    // dump_descriptor(b);

    if (a->dimensions == 0)
    { // a scalar
        *((double *)(c->data + c->offset)) = *((double *)(a->data + a->offset)) + *((double *)(b->data + b->offset));
    }
    else
    {
        long a_index[MAX_DIMENSIONS];
        long b_index[MAX_DIMENSIONS];
        long c_index[MAX_DIMENSIONS];
        for (int i = 0; i < MAX_DIMENSIONS; i++)
            a_index[i] = b_index[i] = c_index[i] = 0;
        double *ad = a->data + a->offset;
        double *bd = b->data + b->offset;
        double *cd = c->data + c->offset;
        do
        {
            *cd = *ad + *bd;
            ad = step(a, a_index);
            bd = step(b, b_index);
            cd = step(c, c_index);

        } while (ad != NULL && bd != NULL && cd != NULL);
    }
    return c;
}

descriptor *matrix_subtract(descriptor *a, descriptor *b)
{
    descriptor *ab[2];
    binop_common("add", a, b, ab);
    a = ab[0];
    b = ab[1];
    descriptor *c = duplicate_descriptor(a);

    if (a->dimensions == 0)
    { // a scalar
        *((double *)(c->data + c->offset)) = *((double *)(a->data + a->offset)) - *((double *)(b->data + b->offset));
    }
    else
    {
        long a_index[MAX_DIMENSIONS];
        long b_index[MAX_DIMENSIONS];
        long c_index[MAX_DIMENSIONS];
        for (int i = 0; i < MAX_DIMENSIONS; i++)
            a_index[i] = b_index[i] = c_index[i] = 0;
        double *ad = a->data + a->offset;
        double *bd = b->data + b->offset;
        double *cd = c->data + c->offset;
        do
        {
            *cd = *ad - *bd;
            ad = step(a, a_index);
            bd = step(b, b_index);
            cd = step(c, c_index);

        } while (ad != NULL && bd != NULL && cd != NULL);
    }
    return c;
}