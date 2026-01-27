.text
.global main

main:
    movq $0, %rax           # Initialize counter %rax to 0

loop:                       # Label for the start of the loop
    addq $1, %rax           # Increment the counter
    cmpq $1000000000, %rax  # Compare the counter with 1,000,000,000
    jne loop                # If %rax != 1,000,000,000, jump back to 'loop'

    movq $0, %rax           # Standard exit code 0
    ret                     # Return to the operating system
    