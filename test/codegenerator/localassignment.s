# main preamble
                .text
                .globl   main
                .type    main, @function
main:
                pushq    %rbp
                movq     %rsp, %rbp
                .file    1 "localassignment.mat"
                .loc     1 6 9
                .loc     1 19 6
# function call myfunc
                movq     $0,%rax          # number of arguments, only needed when calling varargs
                call     myfunc           # void return type, nothing to push
# main postamble
                .globl   end_main
                xor      %rax,%rax        # zero exit code
end_main:
                popq     %rbp
                ret
                .size    main, .-main
# convenience constants
                .p2align 3
.DOUBLENEGATE:                            # to negate a double with xorpd
                .long    0
                .long    -2147483648
                .long    0
                .long    0
# function definition myfunc
                .text
                .globl   myfunc
                .type    myfunc, @function
myfunc:
                pushq    %rbp             # stack will now be 16 byte aligned (because of return address)
                movq     %rsp, %rbp
                subq     $32, %rsp        # reserve space for automatic (local) vars
                .loc     1 7 12
                .loc     1 7 12
                movq     .LDN0(%rip), %rax
                push     %rax
# store in local var d
                pop      %rax
                movq     %rax, -8(%rbp)
                .loc     1 8 9
                .loc     1 8 9
                leaq     .LS0(%rip), %rax
                push     %rax
# store in local var s
                pop      %rax
                movq     %rax, -16(%rbp)
                .loc     1 9 9
                .loc     1 9 9
                movq     .LDN1(%rip), %rax
                push     %rax
# store in local var m
                pop      %rax
                movq     %rax, -24(%rbp)
                .loc     1 10 6
                .loc     1 10 8
                movq     .LDN2(%rip), %rax
                push     %rax
# store in local var d
                movq     %rax, -8(%rbp)
# adjust stack at end of unit
                add      $8, %rsp
                .loc     1 11 4
# function call printdouble
# calculate argument 0
                .loc     1 11 16
                movq     -8(%rbp), %rax   # local var reference double:d
                push     %rax
# popping 1 arguments using the x64 convention
                pop      %rax
                movq     %rax, %xmm0
                movq     $1,%rax          # number of arguments, only needed when calling varargs
                call     printdouble      # void return type, nothing to push
                .loc     1 13 6
                .loc     1 13 8
                leaq     .LS1(%rip), %rax
                push     %rax
# store in local var s
                movq     %rax, -16(%rbp)
# adjust stack at end of unit
                add      $8, %rsp
                .loc     1 14 4
# function call printstring
# calculate argument 0
                .loc     1 14 16
                movq     -16(%rbp), %rax  # local var reference str:s
                push     %rax
# popping 1 arguments using the x64 convention
                pop      %rax
                movq     %rax, %rdi
                movq     $1,%rax          # number of arguments, only needed when calling varargs
                call     printstring      # void return type, nothing to push
                .loc     1 16 6
                .loc     1 16 8
                movq     .MATLIT0(%rip), %rax
                push     %rax
# store in local var m
                movq     %rax, -24(%rbp)
# adjust stack at end of unit
                add      $8, %rsp
                .loc     1 17 4
# function call print_matrix
# calculate argument 0
                .loc     1 17 17
                movq     -24(%rbp), %rax  # local var reference mat:m
                push     %rax
# popping 1 arguments using the x64 convention
                pop      %rax
                movq     %rax, %rdi
                movq     $1,%rax          # number of arguments, only needed when calling varargs
                call     print_matrix     # void return type, nothing to push
end_myfunc:     leave
                ret
                .size    myfunc, .-myfunc
# local constants defined in .text section
                .p2align 3
.LDN0:          .double  0
.LS0:           .string  ""
                .p2align 3
.LDN1:          .double  0
                .p2align 3
.LDN2:          .double  3.14
.LS1:           .string  "Hello, world!"
                .section .data
                .p2align 3
.MATLIT0:
                .quad    .LMatDesc0       # mat variables and constants are pointers to a data descriptor
.LMatDesc0:     .quad    2                # number of dimensions
                .quad    8                # size of single data element
                .quad    .LRData0         # pointer to consequetive data
                .quad    2, 2             # shape
.LRData0:
                .double  1.0
                .double  2.0
                .double  3.0
                .double  4.0
# global constants
# <no items>
# global variables
# <no items>

