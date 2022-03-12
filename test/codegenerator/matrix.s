# main preamble
                .text
                .globl   main
                .type    main, @function
main:
                pushq    %rbp
                movq     %rsp, %rbp
                .file    1 "matrix.mat"
                .loc     1 1 48
# copy matrix .MATLIT0 to a
                leaq     .MATLIT0(%rip), %rdi
                leaq     a(%rip), %rsi
                call     matrixcopy
                .loc     1 3 10
                .loc     1 3 10
                movq     .LDN0(%rip), %rax
                push     %rax
# adjust stack at end of unit
                add      $8, %rsp
                .loc     1 5 13
                .loc     1 5 10
                .loc     1 5 8
                movq     a(%rip), %rax    # global var reference mat:a
                push     %rax
                .loc     1 5 12
                movq     a(%rip), %rax    # global var reference mat:a
                push     %rax
# add two matrices
                pop      %rax
                movq     %rax, %rsi
                pop      %rax
                movq     %rax, %rdi
                call     addmat
                movq     %rax, %rax
                push     %rax
# store in global var c
                pop      %rax
                movq     %rax, c(%rip)
                .loc     1 9 8
                .loc     1 13 12
# function call print_matrix
# calculate argument 0
                .loc     1 13 13
# function call mat_x2
# calculate argument 0
                .loc     1 13 20
                movq     c(%rip), %rax    # global var reference mat:c
                push     %rax
# popping 1 arguments using the x64 convention
                pop      %rax
                movq     %rax, %rdi
                movq     $1,%rax          # number of arguments, only needed when calling varargs
                call     mat_x2
                movq     %rax, %rax
                push     %rax
# popping 1 arguments using the x64 convention
                pop      %rax
                movq     %rax, %rdi
                movq     $1,%rax          # number of arguments, only needed when calling varargs
                call     print_matrix     # void return type, nothing to push
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
# function definition mat_x2
                .text
                .globl   mat_x2
                .type    mat_x2, @function
mat_x2:
                pushq    %rbp             # stack will now be 16 byte aligned (because of return address)
                movq     %rsp, %rbp
                subq     $16, %rsp        # reserve space for automatic (local) vars
                movq     %rdi, -8(%rbp)   # moving argument m (mat) to local stack frame
                .loc     1 10 18
                .loc     1 10 15
                .loc     1 10 13
                movq     -8(%rbp), %rax   # local var reference mat:m
                push     %rax
                .loc     1 10 17
                movq     -8(%rbp), %rax   # local var reference mat:m
                push     %rax
# add two matrices
                pop      %rax
                movq     %rax, %rsi
                pop      %rax
                movq     %rax, %rdi
                call     addmat
                movq     %rax, %rax
                push     %rax
# store in local var m2
                pop      %rax
                movq     %rax, -16(%rbp)
                .loc     1 11 4
                .loc     1 11 11
                movq     -16(%rbp), %rax  # local var reference mat:m2
                push     %rax
                pop      %rax
                movq     %rax, %rax
        jmp end_mat_x2
end_mat_x2:     leave
                ret
                .size    mat_x2, .-mat_x2
# local constants defined in .text section
                .section .data
                .p2align 3
.MATLIT0:
                .quad    .LMatDesc0       # mat variables and constants are pointers to a data descriptor
.LMatDesc0:     .quad    3                # number of dimensions
                .quad    8                # size of single data element
                .quad    .LRData0         # pointer to consequetive data
                .quad    2, 2, 3          # shape
.LRData0:
                .double  1.0
                .double  2.0
                .double  3.0
                .double  3.0
                .double  4.0
                .double  5.0
                .double  1.0
                .double  8.0
                .double  3.0
                .double  3.0
                .double  4.0
                .double  5.0
                .p2align 3
.LDN0:          .double  0
# global constants
# <no items>
# global variables
# global var a is not a scalar
                .global a                 
                .section .data           
                .p2align 3                 
                .type    a, @object      
                .size    a, 8            
a:                                       
                .quad    .LMatDesc1       # mat variables and constants are pointers to a data descriptor
.LMatDesc1:     .quad    3                # number of dimensions
                .quad    8                # size of single data element
                .quad    .LRData1         # pointer to consequetive data. if a shape was specified or an initialize present, data will follow
                .quad    2, 2, 3          # shape
.LRData1:       .dcb.d   12 ,0.0         
# global var b is not a scalar
                .global b                 
                .section .data           
                .p2align 3                 
                .type    b, @object      
                .size    b, 8            
b:                                       
                .quad    .LMatDesc2       # mat variables and constants are pointers to a data descriptor
.LMatDesc2:     .quad    2                # number of dimensions
                .quad    8                # size of single data element
                .quad    .LRData2         # pointer to consequetive data. if a shape was specified or an initialize present, data will follow
                .quad    3, 3             # shape
.LRData2:       .dcb.d   9 ,0.0          
# global var c is a scalar (i.e not yet initialized or given a shape)
                .global c                 
                .section .data           
                .p2align 3                 
                .type    c, @object      
                .size    c, 8            
c:                                       
                .quad    .LMatDesc3       # mat variables and constants are pointers to a data descriptor
.LMatDesc3:     .quad    0                # number of dimensions (zero, because not initialized)
                .quad    8                # size of single data element
                .quad    0                # pointer to consequetive data (zero, because not initialized)
                .quad    0                # shape (a single, 0 dimension, because not initialized)

