# main preamble
                .text
                .globl   main
                .type    main, @function
main:
                pushq    %rbp
                movq     %rsp, %rbp
                .file    1 "print_sine_plus_1.mat"
                .loc     1 4 24
                .loc     1 6 11
# function call printdouble
# calculate argument 0
                .loc     1 6 20
                .loc     1 6 12
# function call sin
# calculate argument 0
                .loc     1 6 16
                movq     pi2(%rip), %rax  # global var reference double:pi2
                push     %rax
# popping 1 arguments using the x64 convention
                pop      %rax
                movq     %rax, %xmm0
                movq     $1,%rax          # number of arguments, only needed when calling varargs
                call     sin
                movq     %xmm0, %rax
                push     %rax
                .loc     1 6 21
                movq     .LDN0(%rip), %rax
                push     %rax
# add two doubles
                pop      %rax
                movq     %rax, %xmm0
                pop      %rax
                movq     %rax, %xmm1
                addsd    %xmm1, %xmm0
                movq     %xmm0, %rax
                push     %rax
# popping 1 arguments using the x64 convention
                pop      %rax
                movq     %rax, %xmm0
                movq     $1,%rax          # number of arguments, only needed when calling varargs
                call     printdouble      # void return type, nothing to push
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
.LDN0:          .double  1.0
# global constants
# <no items>
# global variables
                .global pi2                 
                .section .data           
                .p2align 3                 
                .type    pi2, @object    
                .size    pi2, 8          
pi2:                                     
                .double  1.570796327     

