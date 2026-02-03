.text
.section .rodata
.LC_PRINT_INT: .string "%d\n"
.text
.global main
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $48, %rsp
    movq $0, %rax
    movq %rax, -8(%rbp)
    movq $8, %rax
    movq %rax, -16(%rbp)


.L0:
    movq -8(%rbp), %rax
    pushq %rax
    movq $10, %rax
    movq %rax, %rcx
    popq %rax
    cmpq %rcx, %rax
    jge .L1
    movq -8(%rbp), %rax
    pushq %rax
    movq -16(%rbp), %rax
    movq %rax, %rcx
    popq %rax
    cmpq %rcx, %rax
    jne .L2
    jmp .L1
.L2:
    incq -8(%rbp)
    movq -8(%rbp), %rax
    pushq %rax
    movq $2, %rax
    movq %rax, %rcx
    popq %rax
    cmpq %rcx, %rax
    jge .L4
    jmp .L0
.L4:
    movq -8(%rbp), %rax
    movq %rax, %rdx
    leaq .LC_PRINT_INT(%rip), %rcx
    call printf
    jmp .L0
.L1:
    addq $48, %rsp
    popq %rbp
    ret
