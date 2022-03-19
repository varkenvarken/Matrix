#ifndef _ARITHMATIC_H
#define _ARITHMATIC_H 1

void _add_double(void *c, void *a, void *b, long stride_c, long stride_a, long stride_b, long n);
void _add_double_contiguous(double *c, double *a, double *b, long n);

void _subtract_double(void *c, void *a, void *b, long stride_c, long stride_a, long stride_b, long n);
void _multiply_double(void *c, void *a, void *b, long stride_c, long stride_a, long stride_b, long n);
void _divide_double(void *c, void *a, void *b, long stride_c, long stride_a, long stride_b, long n);
void _modulo_double(void *c, void *a, void *b, long stride_c, long stride_a, long stride_b, long n);
void _notequal_double(void *c, void *a, void *b, long stride_c, long stride_a, long stride_b, long n);

void _negate_double(void *c, void *a, long stride_c, long stride_a, long n);

#endif