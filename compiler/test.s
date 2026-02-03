.text
.section .rodata
.LC0: .string "Hello, World!"
.text
.global main
main:
    pushq %rbp
    movq %rsp, %rbp
    movq $0, %rax
    subq $8, %rsp
    movq %rax, -8(%rbp)
    movq $2, %rax
    subq $8, %rsp
    movq %rax, -16(%rbp)
    leaq .LC0(%rip), %rax
    subq $8, %rsp
    movq %rax, -24(%rbp)
    movq $1, %rax
    subq $8, %rsp
    movq %rax, -32(%rbp)
    movq $0, %rax
    subq $8, %rsp
    movq %rax, -40(%rbp)
    movq $0, %rax
    subq $8, %rsp
    movq %rax, -48(%rbp)
    movq %rbp, %rsp
    popq %rbp
    ret
    