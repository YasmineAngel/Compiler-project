.text
.global main
main:
    pushq %rbp
    movq %rsp, %rbp
    movq $0, %rax
    subq $8, %rsp
    movq %rax, -8(%rbp)
.L0:
    movq -8(%rbp), %rax
    pushq %rax
    movq $10, %rax
    movq %rax, %rcx
    popq %rax
    cmpq %rcx, %rax
    jge .L1
    incq -8(%rbp)
    # print(x) - System call or printf would go here
    jmp .L0
.L1:
    movq %rbp, %rsp
    popq %rbp
    ret
