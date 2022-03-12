# main preamble
                .text
                .globl   main
                .type    main, @function
main:
                pushq    %rbp
                movq     %rsp, %rbp
                .file    1 "while.mat"
                .loc     1 6 17
                .loc     1 7 49
                .loc     1 7 13
                .loc     1 7 14
                movq     .LDN0(%rip), %rax
                push     %rax
                movq     (%rsp), %xmm0
                movq     .DOUBLENEGATE(%rip), %xmm1 # flip sign bit of xmm0
                xorpd    %xmm1, %xmm0
                movq     %xmm0, (%rsp)
# store in global var dec
                pop      %rax
                movq     %rax, dec(%rip)
                .loc     1 9 11
while1:
                .loc     1 9 6
                movq     count(%rip), %rax # global var reference double:count
                push     %rax
                popq     %rax
                cmp      $0, %rax
                jz       endwhile1
                .loc     1 10 4
# function call printdouble
# calculate argument 0
                .loc     1 10 16
                movq     count(%rip), %rax # global var reference double:count
                push     %rax
# popping 1 arguments using the x64 convention
                pop      %rax
                movq     %rax, %xmm0
                movq     $1,%rax          # number of arguments, only needed when calling varargs
                call     printdouble      # void return type, nothing to push
                .loc     1 11 10
                .loc     1 11 18
                .loc     1 11 12
                movq     count(%rip), %rax # global var reference double:count
                push     %rax
                .loc     1 11 20
                movq     dec(%rip), %rax  # global var reference double:dec
                push     %rax
# add two doubles
                pop      %rax
                movq     %rax, %xmm0
                pop      %rax
                movq     %rax, %xmm1
                addsd    %xmm1, %xmm0
                movq     %xmm0, %rax
                push     %rax
# store in global var count
                movq     %rax, count(%rip)
# adjust stack at end of unit
                add      $8, %rsp
                jmp      while1
endwhile1:
                .loc     1 13 11
# function call printstring
# calculate argument 0
                .loc     1 13 12
                leaq     .LS0(%rip), %rax
                push     %rax
# popping 1 arguments using the x64 convention
                pop      %rax
                movq     %rax, %rdi
                movq     $1,%rax          # number of arguments, only needed when calling varargs
                call     printstring      # void return type, nothing to push
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
.LS0:           .string  "done"
# global constants
# <no items>
# global variables
                .global count                 
                .section .data           
                .p2align 3                 
                .type    count, @object  
                .size    count, 8        
count:                                   
                .double  10.0            
                .global dec                 
                .section .data           
                .p2align 3                 
                .type    dec, @object    
                .size    dec, 8          
dec:                                     
                .double  0.0             

