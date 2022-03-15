#include <stdio.h>

#include "../../standardlibrary/matrixutil.h"
#include "../../standardlibrary/matrix.h"
#include "../../standardlibrary/matrixmath.h"

void test_index()
{
    long shape[3] = {4, 4, 4};
    double value = 1.0;
    descriptor *m = new_descriptor(TYPE_DOUBLE, 3, shape);
    matrix_fill_range(m);
    print_descriptor(m);
    puts("");
    descriptor *m2 = matrix_index(m, 1);
    print_descriptor(m2);
    puts("");
    descriptor *m3 = matrix_index(m2, 1);
    print_descriptor(m3);
    puts("");
    descriptor *m4 = matrix_index(m3, 1);
    print_descriptor(m4);
    puts("");
}

void test_index2()
{
    long shape[2] = {2, 2};
    descriptor *m = new_descriptor(TYPE_DOUBLE, 2, shape);
    matrix_fill_range(m);
    print_descriptor(m);
    descriptor *m2 = matrix_index(m, 0);
    descriptor *m3 = matrix_index(m, 1);
    print_descriptor(m2);
    puts("");
    print_descriptor(m3);
    puts("");
    descriptorcopy(m3, m2);
    print_descriptor(m);
    puts("");
}
int main(int argc, char **argv)
{
    test_index();
    test_index2();
    return 0;
}