#include <stdio.h>

#include "../../standardlibrary/matrixutil.h"
#include "../../standardlibrary/matrix.h"
#include "../../standardlibrary/matrixmath.h"

void test_index()
{
    long shape_a[3] = {4, 4};
    long shape_b[3] = {4};
    descriptor *a = new_descriptor(TYPE_DOUBLE, 2, shape_a);
    descriptor *b = new_descriptor(TYPE_DOUBLE, 1, shape_b);
    matrix_fill_range(a);
    matrix_fill_range(b);
    descriptor *c = broadcast(a, b);
    puts("");
    print_descriptor(c);
    puts("");
    print_descriptor(a);
    print_descriptor(matrix_add(a, c));

    print_descriptor(matrix_add(a, b));
}

int main(int argc, char **argv)
{
    test_index();
    return 0;
}