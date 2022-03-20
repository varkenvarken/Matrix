# Matrix

A programming language with a focus on easy matrix calculations.

- Compiles to GNU Assembler
- Python like syntax
- Matrix object will be very similar to a Numpy ndarray object
- Easy to extend (uses the Sly lexer/parser framework)
- MIT license

Very much a work in progress and intended as a personal exercise in creating something a little bit more complete than your average toy language.

Documentation (if any) will be on [https://varkenvarken.github.io/Matrix/]

An example of the kind of syntax is accepts:

```
// calculate the sum of the elements on the main diagonal
// the trace is only define for square nxn matrices

fun double trace(mat m):
    mat s = shape(m)

    double l = length(s)

    if l != 2:
        error("trace: input not a 2D matrix")
    if s[0] != s[1]:
        error("trace: input not a square matrix")

    mat i
    double sum

    for i in range(0,s[0],1):
        sum += m[i][i]

    return sum

mat test =[[1,2,3],
           [2,3,4],
           [3,4,5]]

double t = trace(test)

printdouble(t)

assert t == 9, f"trace of \n{test:m}\nwas {t:.4f}, expected 9"
```
