# main preamble
                .text
                .globl   main
                .type    main, @function
main:
                pushq    %rbp
                movq     %rsp, %rbp
                .file    1 "indexing.mat"
                .loc     1 6 21
# copy matrix .MATLIT0 to m
                leaq     .MATLIT0(%rip), %rdi
                leaq     m(%rip), %rsi
                call     matrixcopy
                .loc     1 8 12
# function call print_matrix
# calculate argument 0
                .loc     1 8 13
                movq     m(%rip), %rax    # global var reference mat:m
                push     %rax
                .loc     1 8 15
                movq     .LDN0(%rip), %rax
                push     %rax
# index a matrix
                popq     %rax
                movq     %rax, %xmm0
                cvtsd2si %xmm0, %rsi      # convert single double to long
                popq     %rdi
                call     matrix_index
                push     %rax
# popping 1 arguments using the x64 convention
                pop      %rax
                movq     %rax, %rdi
                movq     $1,%rax          # number of arguments, only needed when calling varargs
                call     print_matrix     # void return type, nothing to push
                .loc     1 10 12
# function call print_matrix
# calculate argument 0
                .loc     1 10 13
                movq     m(%rip), %rax    # global var reference mat:m
                push     %rax
                .loc     1 10 15
                movq     .LDN1(%rip), %rax
                push     %rax
# index a matrix
                popq     %rax
                movq     %rax, %xmm0
                cvtsd2si %xmm0, %rsi      # convert single double to long
                popq     %rdi
                call     matrix_index
                push     %rax
                .loc     1 10 18
                movq     .LDN2(%rip), %rax
                push     %rax
# index a matrix
                popq     %rax
                movq     %rax, %xmm0
                cvtsd2si %xmm0, %rsi      # convert single double to long
                popq     %rdi
                call     matrix_index
                push     %rax
# popping 1 arguments using the x64 convention
                pop      %rax
                movq     %rax, %rdi
                movq     $1,%rax          # number of arguments, only needed when calling varargs
                call     print_matrix     # void return type, nothing to push
                .loc     1 12 8
# Assignment to index matrix
                movq     m(%rip), %rax    # global var reference m
                push     %rax
                .loc     1 12 2
                movq     .LDN3(%rip), %rax
                push     %rax
# index a matrix
                popq     %rax
                movq     %rax, %xmm0
                cvtsd2si %xmm0, %rsi      # convert single double to long
                popq     %rdi
                call     matrix_index
                push     %rax
                .loc     1 12 5
                movq     .LDN4(%rip), %rax
                push     %rax
# index a matrix
                popq     %rax
                movq     %rax, %xmm0
                cvtsd2si %xmm0, %rsi      # convert single double to long
                popq     %rdi
                call     matrix_index
                push     %rax
                .loc     1 12 10
                movq     .MATLIT1(%rip), %rax
                push     %rax
# copy matrix [stack - 1] -> [stack] (both elements are pointers to descriptors)
                movq     (%rsp), %rdi     # top is src matrix (view) and goes into 1st argument (= %rdi) but we keep it on the stack
                movq     8(%rsp), %rsi    # top -1 is dst matrix (view) and goes into 2nd argument (= %rsi) but we keep it on the stack
                call     descriptorcopy
                add      $8, %rsp         # discard destination address but keep src on top
# adjust stack at end of unit
                add      $8, %rsp
                .loc     1 14 12
# function call print_matrix
# calculate argument 0
                .loc     1 14 13
                movq     m(%rip), %rax    # global var reference mat:m
                push     %rax
# popping 1 arguments using the x64 convention
                pop      %rax
                movq     %rax, %rdi
                movq     $1,%rax          # number of arguments, only needed when calling varargs
                call     print_matrix     # void return type, nothing to push
                .loc     1 16 5
# Assignment to index matrix
                movq     m(%rip), %rax    # global var reference m
                push     %rax
                .loc     1 16 2
                movq     .LDN5(%rip), %rax
                push     %rax
# index a matrix
                popq     %rax
                movq     %rax, %xmm0
                cvtsd2si %xmm0, %rsi      # convert single double to long
                popq     %rdi
                call     matrix_index
                push     %rax
                .loc     1 16 7
                movq     m(%rip), %rax    # global var reference mat:m
                push     %rax
                .loc     1 16 9
                movq     .LDN6(%rip), %rax
                push     %rax
# index a matrix
                popq     %rax
                movq     %rax, %xmm0
                cvtsd2si %xmm0, %rsi      # convert single double to long
                popq     %rdi
                call     matrix_index
                push     %rax
# copy matrix [stack - 1] -> [stack] (both elements are pointers to descriptors)
                movq     (%rsp), %rdi     # top is src matrix (view) and goes into 1st argument (= %rdi) but we keep it on the stack
                movq     8(%rsp), %rsi    # top -1 is dst matrix (view) and goes into 2nd argument (= %rsi) but we keep it on the stack
                call     descriptorcopy
                add      $8, %rsp         # discard destination address but keep src on top
# adjust stack at end of unit
                add      $8, %rsp
                .loc     1 18 12
# function call print_matrix
# calculate argument 0
                .loc     1 18 13
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
                .p2align 3
.LDN0:          .double  0.0
                .p2align 3
.LDN1:          .double  0.0
                .p2align 3
.LDN2:          .double  1.0
                .p2align 3
.LDN3:          .double  1.0
                .p2align 3
.LDN4:          .double  1.0
                .section .data
                .p2align 3
.MATLIT1:
                .quad    .LMatDesc1       # mat variables and constants are pointers to a data descriptor
.LMatDesc1:     .quad    1                # number of dimensions
                .quad    8                # size of single data element
                .quad    .LRData1         # pointer to consequetive data
                .quad    1                # shape
.LRData1:
                .double  3.14
                .p2align 3
.LDN5:          .double  0.0
                .p2align 3
.LDN6:          .double  1.0
# global constants
# <no items>
# global variables
# global var m is not a scalar
                .global m                 
                .section .data           
                .p2align 3                 
                .type    m, @object      
                .size    m, 8            
m:                                       
                .quad    .LMatDesc2       # mat variables and constants are pointers to a data descriptor
.LMatDesc2:     .quad    2                # number of dimensions
                .quad    8                # size of single data element
                .quad    .LRData2         # pointer to consequetive data. if a shape was specified or an initialize present, data will follow
                .quad    2, 2             # shape
.LRData2:       .dcb.d   4 ,0.0          

