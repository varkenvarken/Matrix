#include <stdio.h>
#include <math.h>
#include "matrix.h"
#include "matrixutil.h"
#include "arithmatic.h"

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

descriptor *unop_common(char *op, descriptor *a)
{
    switch (a->type)
    {
    case TYPE_DOUBLE:
        break;
    default:
        fprintf(stderr, "matrix unop %s: only for doubles for now", op);
        exit(EXIT_FAILURE);
    }
    return a;
}

#define RECURSIVE_BINOP(op)                                                                                                \
    void _recursive_##op(void *cd, void *ad, void *bd, long *cstride, long *astride, long *bstride, long *shape, long dim) \
    {                                                                                                                      \
        if (dim == 2)                                                                                                      \
        {                                                                                                                  \
            for (long i = 0; i < shape[0]; i++)                                                                            \
            {                                                                                                              \
                _##op##_double(cd, ad, bd, cstride[1], astride[1], bstride[1], shape[1]);                                  \
                ad += astride[0];                                                                                          \
                bd += bstride[0];                                                                                          \
                cd += cstride[0];                                                                                          \
            }                                                                                                              \
        }                                                                                                                  \
        else                                                                                                               \
        {                                                                                                                  \
            for (long i = 0; i < shape[0]; i++)                                                                            \
            {                                                                                                              \
                _recursive_##op(cd, ad, bd, cstride + 1, astride + 1, bstride + 1, shape + 1, dim - 1);                    \
                ad += astride[0];                                                                                          \
                bd += bstride[0];                                                                                          \
                cd += cstride[0];                                                                                          \
            }                                                                                                              \
        }                                                                                                                  \
    }

#define RECURSIVE_UNOP(op)                                                                        \
    void _recursive_##op(void *cd, void *ad, long *cstride, long *astride, long *shape, long dim) \
    {                                                                                             \
        if (dim == 2)                                                                             \
        {                                                                                         \
            for (long i = 0; i < shape[0]; i++)                                                   \
            {                                                                                     \
                _##op##_double(cd, ad, cstride[1], astride[1], shape[1]);                         \
                ad += astride[0];                                                                 \
                cd += cstride[0];                                                                 \
            }                                                                                     \
        }                                                                                         \
        else                                                                                      \
        {                                                                                         \
            for (long i = 0; i < shape[0]; i++)                                                   \
            {                                                                                     \
                _recursive_##op(cd, ad, cstride + 1, astride + 1, shape + 1, dim - 1);            \
                ad += astride[0];                                                                 \
                cd += cstride[0];                                                                 \
            }                                                                                     \
        }                                                                                         \
    }

#define MATRIX_BINOP(op, operator)                                                                                              \
    descriptor *matrix_##op(descriptor *a, descriptor *b)                                                                       \
    {                                                                                                                           \
        descriptor *ab[2];                                                                                                      \
        binop_common("add", a, b, ab);                                                                                          \
        a = ab[0];                                                                                                              \
        b = ab[1];                                                                                                              \
        descriptor *c = duplicate_descriptor(a);                                                                                \
                                                                                                                                \
        if (a->dimensions == 0)                                                                                                 \
        {                                                                                                                       \
            *((double *)(c->data + c->offset)) = *((double *)(a->data + a->offset)) operator*((double *)(b->data + b->offset)); \
        }                                                                                                                       \
        else                                                                                                                    \
        {                                                                                                                       \
            long a_index[MAX_DIMENSIONS];                                                                                       \
            long b_index[MAX_DIMENSIONS];                                                                                       \
            long c_index[MAX_DIMENSIONS];                                                                                       \
            for (int i = 0; i < a->dimensions; i++)                                                                             \
                a_index[i] = b_index[i] = c_index[i] = 0;                                                                       \
            void *ad = a->data + a->offset;                                                                                     \
            void *bd = b->data + b->offset;                                                                                     \
            void *cd = c->data + c->offset;                                                                                     \
            switch (a->dimensions)                                                                                              \
            {                                                                                                                   \
            case 1:                                                                                                             \
                _##op##_double(cd, ad, bd, c->stride[0], a->stride[0], b->stride[0], a->shape[0]);                              \
                break;                                                                                                          \
            case 2:                                                                                                             \
                for (long i = 0; i < a->shape[0]; i++)                                                                          \
                {                                                                                                               \
                    _##op##_double(cd, ad, bd, c->stride[1], a->stride[1], b->stride[1], a->shape[1]);                          \
                    ad += a->stride[0];                                                                                         \
                    bd += b->stride[0];                                                                                         \
                    cd += c->stride[0];                                                                                         \
                }                                                                                                               \
                break;                                                                                                          \
            default:                                                                                                            \
                for (long i = 0; i < a->shape[0]; i++)                                                                          \
                {                                                                                                               \
                    _recursive_##op(cd, ad, bd, c->stride + 1, a->stride + 1, b->stride + 1, a->shape + 1, a->dimensions - 1);  \
                    ad += a->stride[0];                                                                                         \
                    bd += b->stride[0];                                                                                         \
                    cd += c->stride[0];                                                                                         \
                }                                                                                                               \
                break;                                                                                                          \
            }                                                                                                                   \
        }                                                                                                                       \
        return c;                                                                                                               \
    }

#define MATRIX_BINOPF(op, operator)                                                                                                \
    descriptor *matrix_##op(descriptor *a, descriptor *b)                                                                          \
    {                                                                                                                              \
        descriptor *ab[2];                                                                                                         \
        binop_common("add", a, b, ab);                                                                                             \
        a = ab[0];                                                                                                                 \
        b = ab[1];                                                                                                                 \
        descriptor *c = duplicate_descriptor(a);                                                                                   \
                                                                                                                                   \
        if (a->dimensions == 0)                                                                                                    \
        {                                                                                                                          \
            *((double *)(c->data + c->offset)) = operator(*((double *)(a->data + a->offset)), *((double *)(b->data + b->offset))); \
        }                                                                                                                          \
        else                                                                                                                       \
        {                                                                                                                          \
            long a_index[MAX_DIMENSIONS];                                                                                          \
            long b_index[MAX_DIMENSIONS];                                                                                          \
            long c_index[MAX_DIMENSIONS];                                                                                          \
            for (int i = 0; i < a->dimensions; i++)                                                                                \
                a_index[i] = b_index[i] = c_index[i] = 0;                                                                          \
            void *ad = a->data + a->offset;                                                                                        \
            void *bd = b->data + b->offset;                                                                                        \
            void *cd = c->data + c->offset;                                                                                        \
            switch (a->dimensions)                                                                                                 \
            {                                                                                                                      \
            case 1:                                                                                                                \
                _##op##_double(cd, ad, bd, c->stride[0], a->stride[0], b->stride[0], a->shape[0]);                                 \
                break;                                                                                                             \
            case 2:                                                                                                                \
                for (long i = 0; i < a->shape[0]; i++)                                                                             \
                {                                                                                                                  \
                    _##op##_double(cd, ad, bd, c->stride[1], a->stride[1], b->stride[1], a->shape[1]);                             \
                    ad += a->stride[0];                                                                                            \
                    bd += b->stride[0];                                                                                            \
                    cd += c->stride[0];                                                                                            \
                }                                                                                                                  \
                break;                                                                                                             \
            default:                                                                                                               \
                for (long i = 0; i < a->shape[0]; i++)                                                                             \
                {                                                                                                                  \
                    _recursive_##op(cd, ad, bd, c->stride + 1, a->stride + 1, b->stride + 1, a->shape + 1, a->dimensions - 1);     \
                    ad += a->stride[0];                                                                                            \
                    bd += b->stride[0];                                                                                            \
                    cd += c->stride[0];                                                                                            \
                }                                                                                                                  \
                break;                                                                                                             \
            }                                                                                                                      \
        }                                                                                                                          \
        return c;                                                                                                                  \
    }

#define MATRIX_UNOP(op, operator)                                                                           \
    descriptor *matrix_##op(descriptor *a)                                                                  \
    {                                                                                                       \
        a = unop_common("add", a);                                                                          \
        descriptor *c = duplicate_descriptor(a);                                                            \
                                                                                                            \
        if (a->dimensions == 0)                                                                             \
        {                                                                                                   \
            *((double *)(c->data + c->offset)) = operator(*((double *)(a->data + a->offset)));              \
        }                                                                                                   \
        else                                                                                                \
        {                                                                                                   \
            long a_index[MAX_DIMENSIONS];                                                                   \
            long c_index[MAX_DIMENSIONS];                                                                   \
            for (int i = 0; i < a->dimensions; i++)                                                         \
                a_index[i] = c_index[i] = 0;                                                                \
            void *ad = a->data + a->offset;                                                                 \
            void *cd = c->data + c->offset;                                                                 \
            switch (a->dimensions)                                                                          \
            {                                                                                               \
            case 1:                                                                                         \
                _##op##_double(cd, ad, c->stride[0], a->stride[0], a->shape[0]);                            \
                break;                                                                                      \
            case 2:                                                                                         \
                for (long i = 0; i < a->shape[0]; i++)                                                      \
                {                                                                                           \
                    _##op##_double(cd, ad, c->stride[1], a->stride[1], a->shape[1]);                        \
                    ad += a->stride[0];                                                                     \
                    cd += c->stride[0];                                                                     \
                }                                                                                           \
                break;                                                                                      \
            default:                                                                                        \
                for (long i = 0; i < a->shape[0]; i++)                                                      \
                {                                                                                           \
                    _recursive_##op(cd, ad, c->stride + 1, a->stride + 1, a->shape + 1, a->dimensions - 1); \
                    ad += a->stride[0];                                                                     \
                    cd += c->stride[0];                                                                     \
                }                                                                                           \
                break;                                                                                      \
            }                                                                                               \
        }                                                                                                   \
        return c;                                                                                           \
    }

RECURSIVE_BINOP(add)

RECURSIVE_BINOP(subtract)

RECURSIVE_BINOP(multiply)

RECURSIVE_BINOP(divide)

RECURSIVE_BINOP(modulo)

RECURSIVE_UNOP(negate)

MATRIX_BINOP(add, +)

MATRIX_BINOP(subtract, -)

MATRIX_BINOP(multiply, *)

MATRIX_BINOP(divide, /)

MATRIX_BINOPF(modulo, fmod)

MATRIX_UNOP(negate, -)
