import json 
import os

class Compiler:
    def __init__(self):
        self.code = []

    def emit(self, line):
        """Helper to add a line of assembly."""
        self.code.append(f"    {line}")

    def compile(self, node):
        if node is None :
            return ""
        
        n_type = node.get("type")

        # 1. Start the Program
        if n_type == "File":
            return self.compile(node.get("program"))

        if n_type == "Program":
            # Header instructions
            header = [".text", ".global main", "main:"]
            body = [self.compile(s) for s in node.get("body", [])]
            # Final step: ensure the last value is in %rax and return
            footer = ["    ret"]
            return "\n".join(header + body + footer)

        # 2. Handle a single number (The Leaf)
        if n_type == "ExpressionStatement":
            return self.compile(node.get("expression"))
        
        # 3. Handle Binary Expressions (Addition, Multiplication, etc.)
        if n_type == "BinaryExpression":
            left = node.get("left")
            right = node.get("right")
            op = node.get("operator")

            # Step 1: Compile left side (result goes to %rax)
            asm = [self.compile(left)]
            # Step 2: Push left result onto the stack
            asm.append("    pushq %rax")
            # Step 3: Compile right side (result goes to %rax)
            asm.append(self.compile(right))
            # Step 4: Move right result to %rcx, pop left result back to %rax
            asm.append("    movq %rax, %rcx")
            asm.append("    popq %rax")

            # Step 5: Perform the operation
            if op == "+":
                asm.append("    addq %rcx, %rax")
            elif op == "*":
                asm.append("    imulq %rcx, %rax")
            
            return "\n".join(asm)

        if n_type == "NumericLiteral":
            val = node.get("value")
            # In x86-64, %rax is where the program looks for the return value
            return f"    movq ${val}, %rax"

        return f"/* Missing: {n_type} */"

script_dir = os.path.dirname(__file__) 
file_path = os.path.join(script_dir, '01-expressions.json')

with open(file_path, 'r') as f:
    ast = json.load(f)

compiler = Compiler()
print(compiler.compile(ast))