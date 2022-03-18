#include "arithmatic.h"
#include <stdio.h>

void _add_double(void *c, void *a, void *b, long stride_c, long stride_a, long stride_b, long n)
{
    while (n--)
    {
        *(double *)c = *(double *)a + *(double *)b;
        c += stride_c;
        b += stride_b;
        a += stride_a;
    }
}

void _add_double_contiguous(double *c, double *a, double *b, long n)
{
    for (long i = 0; i < n; i++)
    {
        c[i] = a[i] + b[i];
    }
}

void _subtract_double(void *c, void *a, void *b, long stride_c, long stride_a, long stride_b, long n)
{
    while (n--)
    {
        *(double *)c = *(double *)a - *(double *)b;
        c += stride_c;
        b += stride_b;
        a += stride_a;
    }
}

void _multiply_double(void *c, void *a, void *b, long stride_c, long stride_a, long stride_b, long n)
{
    while (n--)
    {
        *(double *)c = *(double *)a * *(double *)b;
        c += stride_c;
        b += stride_b;
        a += stride_a;
    }
}

void _divide_double(void *c, void *a, void *b, long stride_c, long stride_a, long stride_b, long n)
{
    while (n--)
    {
        *(double *)c = *(double *)a / *(double *)b;
        c += stride_c;
        b += stride_b;
        a += stride_a;
    }
}

void _modulo_double(void *c, void *a, void *b, long stride_c, long stride_a, long stride_b, long n)
{
    while (n--)
    {
        *(double *)c = *(double *)a - (long)(*(double *)a / *(double *)b) * *(double *)b;
        c += stride_c;
        b += stride_b;
        a += stride_a;
    }
}
