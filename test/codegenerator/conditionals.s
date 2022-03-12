# main preamble
                .text
                .globl   main
                .type    main, @function
main:
                pushq    %rbp
                movq     %rsp, %rbp
                .file    1 "conditionals.mat"
                .loc     1 6 4
                .loc     1 6 3
                movq     .LDN0(%rip), %rax
                push     %rax
                popq     %rax
                cmp      $0, %rax
                jz       endif1
                .loc     1 7 4
# function call printstring
# calculate argument 0
                .loc     1 7 16
                leaq     .LS0(%rip), %rax
                push     %rax
# popping 1 arguments using the x64 convention
                pop      %rax
                movq     %rax, %rdi
                movq     $1,%rax          # number of arguments, only needed when calling varargs
                call     printstring      # void return type, nothing to push
endif1:
                .loc     1 9 4
                .loc     1 9 3
                movq     .LDN1(%rip), %rax
                push     %rax
                popq     %rax
                cmp      $0, %rax
                jz       else2
                .loc     1 10 4
# function call printstring
# calculate argument 0
                .loc     1 10 16
                leaq     .LS1(%rip), %rax
                push     %rax
# popping 1 arguments using the x64 convention
                pop      %rax
                movq     %rax, %rdi
                movq     $1,%rax          # number of arguments, only needed when calling varargs
                call     printstring      # void return type, nothing to push
                jmp      endif2
else2:
                .loc     1 12 4
# function call printstring
# calculate argument 0
                .loc     1 12 16
                leaq     .LS2(%rip), %rax
                push     %rax
# popping 1 arguments using the x64 convention
                pop      %rax
                movq     %rax, %rdi
                movq     $1,%rax          # number of arguments, only needed when calling varargs
                call     printstring      # void return type, nothing to push
endif2:
                .loc     1 14 4
                .loc     1 14 3
                movq     .LDN2(%rip), %rax
                push     %rax
                popq     %rax
                cmp      $0, %rax
                jz       else3
                .loc     1 15 4
                .loc     1 15 7
                movq     .LDN3(%rip), %rax
                push     %rax
                popq     %rax
                cmp      $0, %rax
                jz       endif4
                .loc     1 16 8
# function call printstring
# calculate argument 0
                .loc     1 16 20
                leaq     .LS3(%rip), %rax
                push     %rax
# popping 1 arguments using the x64 convention
                pop      %rax
                movq     %rax, %rdi
                movq     $1,%rax          # number of arguments, only needed when calling varargs
                call     printstring      # void return type, nothing to push
                .loc     1 17 8
# function call printstring
# calculate argument 0
                .loc     1 17 20
                leaq     .LS4(%rip), %rax
                push     %rax
# popping 1 arguments using the x64 convention
                pop      %rax
                movq     %rax, %rdi
                movq     $1,%rax          # number of arguments, only needed when calling varargs
                call     printstring      # void return type, nothing to push
endif4:
                jmp      endif3
else3:
                .loc     1 19 4
# function call printstring
# calculate argument 0
                .loc     1 19 16
                leaq     .LS5(%rip), %rax
                push     %rax
# popping 1 arguments using the x64 convention
                pop      %rax
                movq     %rax, %rdi
                movq     $1,%rax          # number of arguments, only needed when calling varargs
                call     printstring      # void return type, nothing to push
endif3:
                .loc     1 21 4
                .loc     1 21 3
                movq     .LDN4(%rip), %rax
                push     %rax
                popq     %rax
                cmp      $0, %rax
                jz       else5
                .loc     1 22 4
# function call printstring
# calculate argument 0
                .loc     1 22 16
                leaq     .LS6(%rip), %rax
                push     %rax
# popping 1 arguments using the x64 convention
                pop      %rax
                movq     %rax, %rdi
                movq     $1,%rax          # number of arguments, only needed when calling varargs
                call     printstring      # void return type, nothing to push
                jmp      endif5
else5:
                .loc     1 24 4
                .loc     1 24 7
                movq     .LDN5(%rip), %rax
                push     %rax
                popq     %rax
                cmp      $0, %rax
                jz       endif6
                .loc     1 25 8
# function call printstring
# calculate argument 0
                .loc     1 25 20
                leaq     .LS7(%rip), %rax
                push     %rax
# popping 1 arguments using the x64 convention
                pop      %rax
                movq     %rax, %rdi
                movq     $1,%rax          # number of arguments, only needed when calling varargs
                call     printstring      # void return type, nothing to push
                .loc     1 26 8
# function call printstring
# calculate argument 0
                .loc     1 26 20
                leaq     .LS8(%rip), %rax
                push     %rax
# popping 1 arguments using the x64 convention
                pop      %rax
                movq     %rax, %rdi
                movq     $1,%rax          # number of arguments, only needed when calling varargs
                call     printstring      # void return type, nothing to push
endif6:
endif5:
                .loc     1 28 11
# function call printstring
# calculate argument 0
                .loc     1 28 12
                leaq     .LS9(%rip), %rax
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
.LS0:           .string  "one"
                .p2align 3
.LDN1:          .double  0.0
.LS1:           .string  "one"
.LS2:           .string  "zero"
                .p2align 3
.LDN2:          .double  1.0
                .p2align 3
.LDN3:          .double  1.0
.LS3:           .string  "one"
.LS4:           .string  "one"
.LS5:           .string  "zero"
                .p2align 3
.LDN4:          .double  0.0
.LS6:           .string  "one"
                .p2align 3
.LDN5:          .double  1.0
.LS7:           .string  "zero"
.LS8:           .string  "one"
.LS9:           .string  "done"
# global constants
# <no items>
# global variables
# <no items>

