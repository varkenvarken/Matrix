# main preamble
                .text
                .globl   main
                .type    main, @function
main:
                pushq    %rbp
                movq     %rsp, %rbp
                .file    1 "mixedfunc.mat"
                .loc     1 4 19
                .loc     1 6 9
                .loc     1 12 6
# function call myfunc
# calculate argument 0
                .loc     1 12 7
                movq     hello(%rip), %rax # global var reference str:hello
                push     %rax
# calculate argument 1
                .loc     1 12 14
                .loc     1 12 15
                movq     .LDN1(%rip), %rax
                push     %rax
                movq     (%rsp), %xmm0
                movq     .DOUBLENEGATE(%rip), %xmm1 # flip sign bit of xmm0
                xorpd    %xmm1, %xmm0
                movq     %xmm0, (%rsp)
# popping 2 arguments using the x64 convention
                pop      %rax
                movq     %rax, %xmm0
                pop      %rax
                movq     %rax, %rdi
                movq     $2,%rax          # number of arguments, only needed when calling varargs
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
                movq     %rdi, -8(%rbp)   # moving argument a (str) to local stack frame
                movq     %xmm0, -16(%rbp) # moving argument b (double) to local stack frame
                .loc     1 7 80
                .loc     1 7 22
                .loc     1 7 17
                movq     .LDN0(%rip), %rax
                push     %rax
                .loc     1 7 24
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
# store in local var bbb
                pop      %rax
                movq     %rax, -24(%rbp)
                .loc     1 8 63
                .loc     1 8 16
                .loc     1 8 14
                movq     -8(%rbp), %rax   # local var reference str:a
                push     %rax
                .loc     1 8 18
                leaq     .LS0(%rip), %rax
                push     %rax
# add two strings
                pop      %rax
                movq     %rax, %rsi
                pop      %rax
                movq     %rax, %rdi
                call     addstring
                movq     %rax, %rax
                push     %rax
# store in local var aaa
                pop      %rax
                movq     %rax, -32(%rbp)
                .loc     1 9 4
# function call printdouble
# calculate argument 0
                .loc     1 9 16
                movq     -24(%rbp), %rax  # local var reference double:bbb
                push     %rax
# popping 1 arguments using the x64 convention
                pop      %rax
                movq     %rax, %xmm0
                movq     $1,%rax          # number of arguments, only needed when calling varargs
                call     printdouble      # void return type, nothing to push
                .loc     1 10 4
# function call printstring
# calculate argument 0
                .loc     1 10 16
                movq     -32(%rbp), %rax  # local var reference str:aaa
                push     %rax
# popping 1 arguments using the x64 convention
                pop      %rax
                movq     %rax, %rdi
                movq     $1,%rax          # number of arguments, only needed when calling varargs
                call     printstring      # void return type, nothing to push
end_myfunc:     leave
                ret
                .size    myfunc, .-myfunc
# local constants defined in .text section
                .p2align 3
.LDN0:          .double  3.14
.LS0:           .string  " world"
                .p2align 3
.LDN1:          .double  3.14
# global constants
# <no items>
# global variables
                .global hello                 
                .section .data           
                .p2align 3               
                .type    hello, @object  
                .size    hello, 8        
hello:                                   
                .quad    . + 8            # string variables and constants are pointers
                .string  "Hello"         
                .size    hello, .-hello  

