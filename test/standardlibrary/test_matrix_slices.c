#include <stdio.h>

#include "../../standardlibrary/matrixutil.h"
#include "../../standardlibrary/matrix.h"
#include "../../standardlibrary/matrixmath.h"

void test_1()
{
    long shape[3] = {6, 4};
    descriptor *m = new_descriptor(TYPE_DOUBLE, 2, shape);
    matrix_fill_range(m);
    print_descriptor(m);
    puts("");

    slice s = {1, 4, 1};

    descriptor *m2 = matrix_slice(m, 1, &s);
    print_descriptor(m2);
    puts("");

    slice s2 = {4, 1, -1};

    descriptor *m3 = matrix_slice(m, 1, &s2);
    print_descriptor(m3);
    puts("");

    slice s3 = {1, 2, 1};

    descriptor *m4 = matrix_slice(m3, 1, &s3);
    print_descriptor(m4);
    puts("");

    slice s4[2] = {{1, 4, 1}, {1, 3, 1}};
    descriptor *m5 = matrix_slice(m, 2, s4);
    print_descriptor(m5);
    puts("");

    slice s5[2] = {{4, 1, -1}, {1, 3, 1}};
    descriptor *m6 = matrix_slice(m, 2, s5);
    print_descriptor(m6);
    puts("");
}

int main(int argc, char **argv)
{
    test_1();
    return 0;
}