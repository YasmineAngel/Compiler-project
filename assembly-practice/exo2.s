.text
.global main

main:
    #(3+4)*12 modulo 5
    # 1 Calculate (3 + 4)
    movq $3, %rax      # Load 3 into %rax
    addq $4, %rax      # %rax = %rax + 4 (now 7)

    # 2 Multiply by 12
    movq $12, %rbx     # Load 12 into a temporary register
    imulq %rbx         # Multiplies %rax by %rbx. Result (84) in %rax

    # 3 Modulo 5 (requires division)
    movq $5, %rcx      # Load divisor (5) into %rcx
    idivq %rcx         # Divide %rdx:%rax by 5. 
                       # Quotient goes to %rax, Remainder goes to %rdx

    # 4 Prepare return value
    movq %rdx, %rax    # Move the remainder (84 % 5 = 4) into %rax for return
    ret
    