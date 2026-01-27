.text
.global main

main:
    movq $0, %rcx           # %rcx will be our loop counter

loop:
    # --- Start of Arithmetic (3 * 5 % 12) ---
    movq $3, %rax           # Load 3
    imulq $5, %rax          # %rax = 15
    
    movq $12, %rbx          # Load divisor 12
    cqto                    # Sign-extend %rax into %rdx:%rax
    idivq %rbx              # Divide 15 by 12. Remainder (3) goes to %rdx
    # --- End of Arithmetic ---

    addq $1, %rcx           # Increment our counter
    cmpq $1000000000, %rcx  # Compare counter to 1 billion
    jne loop                # Repeat if not equal

    movq %rdx, %rax         # Move the last modulo result (3) to %rax for return
    ret
    