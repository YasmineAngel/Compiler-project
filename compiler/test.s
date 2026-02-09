.text
testSwitch:
    pushq %rbp
    movq %rsp, %rbp
    subq $16, %rsp
    movq %rdi, -8(%rbp)
    movq -8(%rbp), %rax
    pushq %rax
    movq $12, %rax
    movq %rax, %rcx
    movq (%rsp), %rax
    cmpq %rcx, %rax
    je .CASE_01
    movq $15, %rax
    movq %rax, %rcx
    movq (%rsp), %rax
    cmpq %rcx, %rax
    je .CASE_12
    movq $1234, %rax
    movq %rax, %rcx
    movq (%rsp), %rax
    cmpq %rcx, %rax
    je .CASE_23
    jmp .CASE_34
.CASE_01:
    movq $0, %rax
            movq %rbp, %rsp
            popq %rbp
            ret
.CASE_12:
    movq $1, %rax
            movq %rbp, %rsp
            popq %rbp
            ret
.CASE_23:
    movq $2, %rax
            movq %rbp, %rsp
            popq %rbp
            ret
.CASE_34:
    movq $3, %rax
            movq %rbp, %rsp
            popq %rbp
            ret
.SWITCH_END0:
    addq $8, %rsp
    movq $12345678, %rax
            movq %rbp, %rsp
            popq %rbp
            ret
    # Default exit if no return statement is hit
    movq %rbp, %rsp
    popq %rbp
    ret
neg:
    pushq %rbp
    movq %rsp, %rbp
    subq $16, %rsp
    movq %rdi, -8(%rbp)
    movq -8(%rbp), %rax
    negq %rax
            movq %rbp, %rsp
            popq %rbp
            ret
    # Default exit if no return statement is hit
    movq %rbp, %rsp
    popq %rbp
    ret
testSwitchEvil:
    pushq %rbp
    movq %rsp, %rbp
    subq $16, %rsp
    movq %rdi, -8(%rbp)
    movq -8(%rbp), %rax
    pushq %rax
    movq $12, %rax
    movq %rax, %rcx
    movq (%rsp), %rax
    cmpq %rcx, %rax
    je .CASE_06
    movq x(%rip), %rax
    pushq %rax
    movq $1, %rax
    movq %rax, %rcx
    popq %rax
    addq %rcx, %rax
    movq %rax, %rcx
    movq (%rsp), %rax
    cmpq %rcx, %rax
    je .CASE_17
    movq x(%rip), %rax
    movq %rax, %rdi
    call neg
    movq %rax, %rcx
    movq (%rsp), %rax
    cmpq %rcx, %rax
    je .CASE_28
    jmp .CASE_39
.CASE_06:
    movq $0, %rax
            movq %rbp, %rsp
            popq %rbp
            ret
.CASE_17:
    movq $1, %rax
            movq %rbp, %rsp
            popq %rbp
            ret
.CASE_28:
    movq $2, %rax
            movq %rbp, %rsp
            popq %rbp
            ret
.CASE_39:
    movq $3, %rax
            movq %rbp, %rsp
            popq %rbp
            ret
.SWITCH_END5:
    addq $8, %rsp
    movq $12345678, %rax
            movq %rbp, %rsp
            popq %rbp
            ret
    # Default exit if no return statement is hit
    movq %rbp, %rsp
    popq %rbp
    ret
.data
x: .quad 123
print: .quad 0
.section .rodata
.LC_PRINT_INT: .string "%d\n"
.text
.global main
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $32, %rsp


    movq $1234, %rax
    movq %rax, %rdi
    call testSwitch
    movq %rax, %rdx
    leaq .LC_PRINT_INT(%rip), %rcx
    call printf
    movq $1235, %rax
    movq %rax, %rdi
    call testSwitch
    movq %rax, %rdx
    leaq .LC_PRINT_INT(%rip), %rcx
    call printf
    movq $124, %rax
    movq %rax, %rdi
    call testSwitchEvil
    movq %rax, %rdx
    leaq .LC_PRINT_INT(%rip), %rcx
    call printf
    movq $123, %rax
    negq %rax
    movq %rax, %rdi
    call testSwitchEvil
    movq %rax, %rdx
    leaq .LC_PRINT_INT(%rip), %rcx
    call printf
    movq $0, %rax
    addq $32, %rsp
    popq %rbp
    ret
