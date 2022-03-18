#include "../../standardlibrary/matrixutil.h"
#include "../../standardlibrary/matrix.h"
#include "../../standardlibrary/matrixmath.h"

void test_create()
{
    long shape[2] = {2, 2};
    double value = 1.0;
    descriptor *m = new_descriptor(TYPE_DOUBLE, 2, shape);
    matrix_fill(m, &value);
    print_descriptor(m);
    matrix_fill_range(m);
    print_descriptor(m);
}

void test_add()
{
    long shape[2] = {3, 3};
    double value_a = 1.0;
    descriptor *a = new_descriptor(TYPE_DOUBLE, 2, shape);
    matrix_fill(a, &value_a);
    double value_b = 2.0;
    descriptor *b = new_descriptor(TYPE_DOUBLE, 2, shape);
    matrix_fill(b, &value_b);
    print_descriptor(matrix_add(a, b));
}

void test_subtract()
{
    long shape[2] = {3, 3};
    double value_a = 1.0;
    descriptor *a = new_descriptor(TYPE_DOUBLE, 2, shape);
    matrix_fill(a, &value_a);
    double value_b = 2.0;
    descriptor *b = new_descriptor(TYPE_DOUBLE, 2, shape);
    matrix_fill(b, &value_b);
    print_descriptor(matrix_subtract(a, b));
}

void test_multiply()
{
    long shape[2] = {3, 3};
    double value_a = 2.0;
    descriptor *a = new_descriptor(TYPE_DOUBLE, 2, shape);
    matrix_fill(a, &value_a);
    double value_b = 2.0;
    descriptor *b = new_descriptor(TYPE_DOUBLE, 2, shape);
    matrix_fill(b, &value_b);
    print_descriptor(matrix_multiply(a, b));
}
void test_divide()
{
    long shape[2] = {3, 3};
    double value_a = 2.0;
    descriptor *a = new_descriptor(TYPE_DOUBLE, 2, shape);
    matrix_fill(a, &value_a);
    double value_b = 2.0;
    descriptor *b = new_descriptor(TYPE_DOUBLE, 2, shape);
    matrix_fill(b, &value_b);
    print_descriptor(matrix_divide(a, b));
}
void test_modulo()
{
    long shape[2] = {3, 3};
    double value_a = 3.0;
    descriptor *a = new_descriptor(TYPE_DOUBLE, 2, shape);
    matrix_fill(a, &value_a);
    double value_b = 2.0;
    descriptor *b = new_descriptor(TYPE_DOUBLE, 2, shape);
    matrix_fill(b, &value_b);
    print_descriptor(matrix_modulo(a, b));
}

void test_negate()
{
    long shape[2] = {3, 3};
    double value_a = 3.0;
    descriptor *a = new_descriptor(TYPE_DOUBLE, 2, shape);
    matrix_fill(a, &value_a);
    print_descriptor(matrix_negate(a));
}

int main(int argc, char **argv)
{
    test_create();
    test_add();
    test_subtract();
    test_multiply();
    test_divide();
    test_modulo();
    test_negate();
    return 0;
}