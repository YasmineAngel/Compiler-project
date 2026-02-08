.text
factorial:
    pushq %rbp
    movq %rsp, %rbp
    subq $16, %rsp
    movq %rdi, -8(%rbp)
    movq -8(%rbp), %rax
    pushq %rax
    movq $0, %rax
    movq %rax, %rcx
    popq %rax
    cmpq %rcx, %rax
    sete %al
    movzbq %al, %rax
    cmpq $0, %rax
    jne .LOGIC_TRUE2
    movq -8(%rbp), %rax
    pushq %rax
    movq $1, %rax
    movq %rax, %rcx
    popq %rax
    cmpq %rcx, %rax
    sete %al
    movzbq %al, %rax
    cmpq $0, %rax
    jne .LOGIC_TRUE2
    movq $0, %rax
    jmp .LOGIC_END3
.LOGIC_TRUE2:
    movq $1, %rax
.LOGIC_END3:
    je .ELSE0
    movq $1, %rax
            movq %rbp, %rsp
            popq %rbp
            ret
.ELSE0:
    movq -8(%rbp), %rax
    pushq %rax
    movq -8(%rbp), %rax
    pushq %rax
    movq $1, %rax
    movq %rax, %rcx
    popq %rax
    subq %rcx, %rax
    movq %rax, %rdi
    call factorial
    movq %rax, %rcx
    popq %rax
    imulq %rcx, %rax
            movq %rbp, %rsp
            popq %rbp
            ret
    # Default exit if no return statement is hit
    movq %rbp, %rsp
    popq %rbp
    ret
.global main
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $16, %rsp

    movq $3, %rax
    movq %rax, %rdi
    call factorial
    movq $0, %rax
    addq $16, %rsp
    popq %rbp
    ret

