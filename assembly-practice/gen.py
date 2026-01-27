import json
import sys

class AsmGenerator:
    def __init__(self):
        self.output = []

    def emit(self, line):
        self.output.append(f"    {line}")

    def generate(self, node):
        n_type = node.get("type")

        # 1. Handle the Root Structure
        if n_type == "File":
            self.generate(node.get("program"))
        elif n_type == "Program":
            print(".text\n.global main\nmain:")
            for stmt in node.get("body", []):
                self.generate(stmt)
                # The result of the expression is now in %rax because 
                # ExpressionStatement just did a popq %rax.
            
            # No extra pop needed here anymore!
            print("    ret")


            # Handle Expressions
        elif n_type == "ExpressionStatement":
            self.generate(node.get("expression"))
            # CLEANUP: Pop the result of this expression so it doesn't 
            # sit on the stack and break the return address.
            print("    popq %rax")

        elif n_type == "BinaryExpression":
            # Post-order traversal: Evaluate children first
            self.generate(node.get("left"))
            self.generate(node.get("right"))

            # BinaryOp Rule: Pop right into %rbx, pop left into %rax
            print("    popq %rbx")
            print("    popq %rax")

            op = node.get("operator")
            if op == "+":   print("    addq %rbx, %rax")
            elif op == "-": print("    subq %rbx, %rax")
            elif op == "*": print("    imulq %rbx, %rax")
            elif op == "%" or op == "/":
                print("    cqto")
                print("    idivq %rbx")
                if op == "%":
                    print("    movq %rdx, %rax") # Modulo is in %rdx

            # Push result back onto stack
            print("    pushq %rax")

        # 3. Handle Literals (Leaves)
        elif n_type == "NumericLiteral":
            print(f"    pushq ${node.get('value')}")

# Execution
if __name__ == "__main__":
    with open("test.json", "r") as f:
        data = json.load(f)
        AsmGenerator().generate(data)