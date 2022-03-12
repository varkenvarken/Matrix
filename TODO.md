TODO
====

x code generation for functions
x always store argument count in %rax even for functions that don require it (i.e. non-vargargs function)
x propagate line numbers, filenames and actual lines trough parsenode, ast to codegenerator
- error handling and proper return codes
    - 0 OK
    - 1 parse failed
    - 2 syntax failed
    - 3 code generation failed 
- initialization of (local) variables should check type compat

BUGS
====

- a completely empty line should not generate dedents


IDEAS
=====

- allow functions with same name but different parameter types
- ::NAME to refer to functions
