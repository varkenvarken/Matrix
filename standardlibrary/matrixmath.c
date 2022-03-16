#include <stdio.h>
#include "matrix.h"
#include "matrixutil.h"

// TODO: verify if operands are compatible
// TODO: check for malloc failures
descriptor *matrix_add(descriptor *a, descriptor *b)
{
    descriptor *c = duplicate_descriptor(a);

    puts("matrix_add\na:");
    dump_descriptor(a);
    puts("b:");
    dump_descriptor(b);
    puts("c:");
    dump_descriptor(c);

    switch (a->type)
    {
    case TYPE_DOUBLE:
        break;
    default:
        fputs("matrix addition only for doubles for now", stderr);
        exit(EXIT_FAILURE);
    }

    switch (broadcastable(a, b))
    {
    case -1:
        fputs("matrix addition cannot be broadcast", stderr);
        exit(EXIT_FAILURE);
    case 0: // no need to broadcast
        break;
    default: // create a broadcast descriptor from b that matches a
        b = broadcast(a, b);
        break;
    }

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
#ifdef DEBUG
    puts("a:");
    dump_descriptor(a);
    puts("b:");
    dump_descriptor(b);
    puts("c:");
    dump_descriptor(c);
#endif
    return c;
}