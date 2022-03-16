#include <stdio.h>
#include "matrix.h"
#include "matrixutil.h"

// TODO: check for malloc failures
// check for compat and does broadcast
// returns b (possibly broadcasted)
descriptor *binop_common(char *op, descriptor *a, descriptor *b)
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

    switch (broadcastable(a, b))
    {
    case -1:
        fprintf(stderr, "matrix %s: right hand matrix cannot be broadcast", op);
        exit(EXIT_FAILURE);
    case 0: // no need to broadcast
        break;
    default: // create a broadcast descriptor from b that matches a
        b = broadcast(a, b);
        break;
    }

    return b;
}

descriptor *matrix_add(descriptor *a, descriptor *b)
{
    descriptor *c = duplicate_descriptor(a);

    b = binop_common("add", a, b);

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
    descriptor *c = duplicate_descriptor(a);

    b = binop_common("subtract", a, b);

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