# main preamble
                .text
                .globl   main
                .type    main, @function
main:
                pushq    %rbp
                movq     %rsp, %rbp
                .file    1 "myfunc.mat"
                .loc     1 3 13
                .loc     1 5 11
                .loc     1 9 11
# function call printdouble
# calculate argument 0
                .loc     1 9 12
# function call myfunc
# calculate argument 0
                .loc     1 9 21
                .loc     1 9 19
                movq     .LDN0(%rip), %rax
                push     %rax
                .loc     1 9 22
                movq     .LDN1(%rip), %rax
                push     %rax
# add two doubles
                pop      %rax
                movq     %rax, %xmm0
                pop      %rax
                movq     %rax, %xmm1
                addsd    %xmm1, %xmm0
                movq     %xmm0, %rax
                push     %rax
# calculate argument 1
                .loc     1 9 26
                .loc     1 9 24
                movq     .LDN2(%rip), %rax
                push     %rax
                .loc     1 9 27
                movq     .LDN3(%rip), %rax
                push     %rax
# add two doubles
                pop      %rax
                movq     %rax, %xmm0
                pop      %rax
                movq     %rax, %xmm1
                addsd    %xmm1, %xmm0
                movq     %xmm0, %rax
                push     %rax
# popping 2 arguments using the x64 convention
                pop      %rax
                movq     %rax, %xmm1
                pop      %rax
                movq     %rax, %xmm0
                movq     $2,%rax          # number of arguments, only needed when calling varargs
                call     myfunc
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
# function definition myfunc
                .text
                .globl   myfunc
                .type    myfunc, @function
myfunc:
                pushq    %rbp             # stack will now be 16 byte aligned (because of return address)
                movq     %rsp, %rbp
                subq     $32, %rsp        # reserve space for automatic (local) vars
                movq     %xmm0, -8(%rbp)  # moving argument a (double) to local stack frame
                movq     %xmm1, -16(%rbp) # moving argument b (double) to local stack frame
                .loc     1 6 20
                .loc     1 6 17
                .loc     1 6 15
                movq     -8(%rbp), %rax   # local var reference double:a
                push     %rax
                .loc     1 6 19
                movq     -16(%rbp), %rax  # local var reference double:b
                push     %rax
# add two doubles
                pop      %rax
                movq     %rax, %xmm0
                pop      %rax
                movq     %rax, %xmm1
                addsd    %xmm1, %xmm0
                movq     %xmm0, %rax
                push     %rax
# store in local var c
                pop      %rax
                movq     %rax, -24(%rbp)
                .loc     1 7 4
                .loc     1 7 11
                movq     -24(%rbp), %rax  # local var reference double:c
                push     %rax
                pop      %rax
                movq     %rax, %xmm0
        jmp end_myfunc
end_myfunc:     leave
                ret
                .size    myfunc, .-myfunc
# local constants defined in .text section
                .p2align 3
.LDN0:          .double  10.0
                .p2align 3
.LDN1:          .double  7.0
                .p2align 3
.LDN2:          .double  20.0
                .p2align 3
.LDN3:          .double  5.0
# global constants
# <no items>
# global variables
                .global c                 
                .section .data           
                .p2align 3                 
                .type    c, @object      
                .size    c, 8            
c:                                       
                .double  12.0            

