void generate(Node *n) {
    if (n->type == LITERAL) {
        printf("    pushq $%d\n", n->value);
    } 
    else if (n->type == BINARY_OP) {
        generate(n->left);   // Recursive call
        generate(n->right);  // Recursive call
        
        printf("    popq %%rbx\n"); // Right operand
        printf("    popq %%rax\n"); // Left operand
        
        if (n->op == '+') printf("    addq %%rbx, %%rax\n");
        if (n->op == '-') printf("    subq %%rbx, %%rax\n");
        if (n->op == '*') printf("    imulq %%rbx, %%rax\n");
        
        printf("    pushq %%rax\n");
    }
}