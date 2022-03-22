## Welcome to the webpages for Matrix

The supported [Syntax](https://github.com/varkenvarken/Matrix/Syntax) is documented (sort of).

# scopes and declarations

We have two scoped: global and local. The local scope is inside a function definition.

You cannot define functions inside functions and you cannot make forward references.

The *extern* keyword can be used to either declare external functions or a forward declaration.

# types

Currently only three types are supported (not counting *void* functions):

- double, a double precision floating point number
- str,    a string
- mat,    a double precision multidimensional matrix (i.e. a matrix of any rank, not just 2d)

More on matrices and string later.

# control structures

- if/else, your standard conditional
- while,   a unbounded loop
- for,     a bounded loop

Just like functions, control structures use indentation to mark there body, just like in Python. For example:

```
// return the n'th fibonnaci number
fun double fibonnaci(double n):
    if n == 0:
        return 1
    if n == 1:
        return 1
    double n0 = 1
    double n1 = 1
    double fib
    for i = 2 to n:
        fib = n1 + n0
        n0 = n1
        n1 = fib
    return fib
```

# strings

Both regular, double quoted strings are supported (with the backslash (\) as the escape character, as well as interpolated strings.

Interpolated strings are a bit like f-strings in Python:

```
str interpolated = f"a example with a mat {mymatrix:m} and a double {mydouble:f}\n"
```

because the focus of this language is on matrices, string operations are a bit limited: you can concatenate then with + or print them with the built-in function *printstring()*.

# matrices

*TODO*

# specials

*TODO*

- matrix multiplication
- root
- cross
- dot
- assert

# built-in functions

*TODO*

