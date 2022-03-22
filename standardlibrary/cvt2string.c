#include <string.h>
#include <malloc.h>
#include <stdio.h>
#include <stdlib.h>
#include "matrix.h"
#include "matrixutil.h"

#define MAX_DOUBLE_WIDTH 20
#define MAX_COLS 10
#define MAX_ROWS 10

char *cvt_double(double d)
{
    char *result = malloc(MAX_DOUBLE_WIDTH);
    snprintf(result, MAX_DOUBLE_WIDTH, "%9.4f", d);
    return result;
}

char *cvt_descriptor(descriptor *m)
{
    if (m->type != TYPE_DOUBLE)
    {
        fputs("cvt_descriptor only supports double for now", stderr);
        exit(EXIT_FAILURE);
    }

    char *result = NULL;
    if (m->dimensions == 0)
    { // copy a single value for scalars
        switch (m->type)
        {
        case TYPE_DOUBLE:
            result = malloc(MAX_DOUBLE_WIDTH);
            snprintf(result, MAX_DOUBLE_WIDTH, "%9.4f", *((double *)(m->data + m->offset)));
            return result;
        }
    }
    else
    {
        double *d;
        long index[MAX_DIMENSIONS], old_index[MAX_DIMENSIONS];
        for (int i = 0; i < MAX_DIMENSIONS; i++)
            index[i] = old_index[i] = 0;
        switch (m->type)
        {
        case TYPE_DOUBLE:
            result = malloc((MAX_DOUBLE_WIDTH + 1) * MAX_COLS * MAX_ROWS + 128);
            d = (double *)(m->data + m->offset);
            char *cursor = result;
            int rows = 0;
            int cols = 0;
            do
            {
                if (cols < MAX_COLS && rows < MAX_ROWS)
                {
                    int len = snprintf(cursor, MAX_DOUBLE_WIDTH, "%9.4f ", *d);
                    cursor += len;
                }
                if (cols >= MAX_COLS && rows < MAX_ROWS)
                {
                    strcpy(cursor, "...");
                    cursor += 3;
                    *cursor = 0;
                }
                if (rows >= MAX_ROWS)
                {
                    strcpy(cursor, "\n...\n");
                    return result;
                }
                cols++;
                d = step(m, index);
                // if the last dimension has rolled over, we print a newline
                if ((index[m->dimensions - 1] != old_index[m->dimensions - 1]) && index[m->dimensions - 1] == 0)
                {
                    *cursor++ = '\n';
                    *cursor = 0;
                    cols = 0;
                    rows++;
                }
                for (int i = 0; i < MAX_DIMENSIONS; i++)
                    old_index[i] = index[i];
            } while (d != NULL);
            break;
            return result;
        }
    }
}

char *concat_strings(char **list, long n)
{
    long total_length = 0;
    for (long i = 0; i < n; i++)
    {
        total_length += strlen(list[i]);
    }
    total_length++;
    char *result = malloc(total_length);
    char *cursor = result;
    for (long i = n - 1; i >= 0; i--)
    {
        cursor = stpcpy(cursor, list[i]);
    }
    return result;
}