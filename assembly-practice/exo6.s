.text
.global main

# The "do nothing" subroutine
dummy_subroutine:
    ret

main:
    movq $0, %rax           # Initialize counter %rax to 0

loop:
    call dummy_subroutine   # Replaced arithmetic with a function call
    addq $1, %rax           # Increment the counter
    cmpq $1000000000, %rax 
    jne loop                

    movq $0, %rax           
    ret
