# main preamble
                .text
                .globl   main
                .type    main, @function
main:
                pushq    %rbp
                movq     %rsp, %rbp
                .file    1 "assignment.mat"
                .loc     1 6 8
                .loc     1 7 5
                .loc     1 8 5
                .loc     1 8 5
                movq     .LDN0(%rip), %rax
                push     %rax
# adjust stack at end of unit
                add      $8, %rsp
                .loc     1 10 2
                .loc     1 10 6
                .loc     1 10 4
                movq     .LDN1(%rip), %rax
                push     %rax
                .loc     1 10 8
                movq     .LDN2(%rip), %rax
                push     %rax
# add two doubles
                pop      %rax
                movq     %rax, %xmm0
                pop      %rax
                movq     %rax, %xmm1
                addsd    %xmm1, %xmm0
                movq     %xmm0, %rax
                push     %rax
# store in global var c
                movq     %rax, c(%rip)
# adjust stack at end of unit
                add      $8, %rsp
                .loc     1 11 2
                .loc     1 11 14
                .loc     1 11 4
                leaq     .LS0(%rip), %rax
                push     %rax
                .loc     1 11 16
                leaq     .LS1(%rip), %rax
                push     %rax
# add two strings
                pop      %rax
                movq     %rax, %rsi
                pop      %rax
                movq     %rax, %rdi
                call     addstring
                movq     %rax, %rax
                push     %rax
# store in global var s
                movq     %rax, s(%rip)
# adjust stack at end of unit
                add      $8, %rsp
                .loc     1 12 2
                .loc     1 12 4
                movq     .MATLIT0(%rip), %rax
                push     %rax
# store in global var m
                movq     %rax, m(%rip)
# adjust stack at end of unit
                add      $8, %rsp
                .loc     1 14 11
# function call printdouble
# calculate argument 0
                .loc     1 14 12
                movq     c(%rip), %rax    # global var reference double:c
                push     %rax
# popping 1 arguments using the x64 convention
                pop      %rax
                movq     %rax, %xmm0
                movq     $1,%rax          # number of arguments, only needed when calling varargs
                call     printdouble      # void return type, nothing to push
                .loc     1 15 11
# function call printstring
# calculate argument 0
                .loc     1 15 12
                movq     s(%rip), %rax    # global var reference str:s
                push     %rax
# popping 1 arguments using the x64 convention
                pop      %rax
                movq     %rax, %rdi
                movq     $1,%rax          # number of arguments, only needed when calling varargs
                call     printstring      # void return type, nothing to push
                .loc     1 16 12
# function call print_matrix
# calculate argument 0
                .loc     1 16 13
                movq     m(%rip), %rax    # global var reference mat:m
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
# local constants defined in .text section
                .p2align 3
.LDN0:          .double  0
                .p2align 3
.LDN1:          .double  1.0
                .p2align 3
.LDN2:          .double  3.0
.LS0:           .string  "Hello, "
.LS1:           .string  "world!"
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
                .global c                 
                .section .data           
                .p2align 3                 
                .type    c, @object      
                .size    c, 8            
c:                                       
                .double  0               
                .global s                 
                .section .data           
                .p2align 3               
                .type    s, @object      
                .size    s, 8            
s:                                       
                .quad    . + 8            # string variables and constants are pointers
                .string  ""              
                .size    s, .-s          
# global var m is a scalar (i.e not yet initialized or given a shape)
                .global m                 
                .section .data           
                .p2align 3                 
                .type    m, @object      
                .size    m, 8            
m:                                       
                .quad    .LMatDesc1       # mat variables and constants are pointers to a data descriptor
.LMatDesc1:     .quad    0                # number of dimensions (zero, because not initialized)
                .quad    8                # size of single data element
                .quad    0                # pointer to consequetive data (zero, because not initialized)
                .quad    0                # shape (a single, 0 dimension, because not initialized)

