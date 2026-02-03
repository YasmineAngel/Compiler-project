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
    movq -8(%rbp), %rax
    pushq %rax
    movq $0, %rax
    movq %rax, %rcx
    popq %rax
    cmpq %rcx, %rax
    je .L0
    incq -8(%rbp)
    jmp .L1
.L0:
    movq $1, %rax
    addq %rax, -8(%rbp)
.L1:
    movq -8(%rbp), %rax
    pushq %rax
    movq $1, %rax
    movq %rax, %rcx
    popq %rax
    cmpq %rcx, %rax
    jne .L2
    movq $2, %rax
    subq %rax, -8(%rbp)
    jmp .L3
.L2:

.L3:
.L4:
    movq -8(%rbp), %rax
    pushq %rax
    movq $10, %rax
    movq %rax, %rcx
    popq %rax
    cmpq %rcx, %rax
    jge .L5
    movq -8(%rbp), %rax
    movq %rax, %rdx
    leaq .LC_PRINT_INT(%rip), %rcx
    call printf
    incq -8(%rbp)
    jmp .L4
.L5:
    addq $48, %rsp
    popq %rbp
    ret
