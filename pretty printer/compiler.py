import json 
import os

class Compiler:
    def __init__(self):
        self.locals = {}
        self.stack_ptr = 0
        self.data_section = []
        self.string_count = 0
        self.label_count = 0

    def get_new_string_label(self):
        label = f".LC{self.string_count}"
        self.string_count += 1
        return label
    
    def get_new_label(self):
        label = f".L{self.label_count}"
        self.label_count += 1
        return label

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
            # Compile body
            body = [self.compile(s) for s in node.get("body", [])]
            # Header instructions
            header = [".text"]
            if self.data_section:
                header.append(".section .rodata")
                header.extend(self.data_section)
                header.append(".text")
            header.extend([
                ".global main",
                "main:",
                "    pushq %rbp", 
                "    movq %rsp, %rbp",
                "    subq $48, %rsp"
                ])
            
            
            # Footer: Clean up stack and return
            footer = [
                "    addq $48, %rsp",
                "    popq %rbp",
                "    ret"
            ]
            return "\n".join(header + body + footer)

        # Handle a single number (The Leaf)
        if n_type == "ExpressionStatement":
            return self.compile(node.get("expression"))
        
        #  Handle Binary Expressions (Addition, Multiplication, etc.)
        if n_type == "BinaryExpression":
            # Standard setup for all binary ops: Left in %rax, Right in %rcx
            asm = [
                self.compile(node["left"]), 
                "    pushq %rax", 
                self.compile(node["right"]), 
                "    movq %rax, %rcx", 
                "    popq %rax"
            ]
            op = node.get("operator")
            # Perform the operation
            if op == "+":
                asm.append("    addq %rcx, %rax")
            elif op == "*":
                asm.append("    imulq %rcx, %rax")
            elif op in ["<", ">", "<=", ">=", "==", "!="]:
                asm.append("    cmpq %rcx, %rax") # Compare left (%rax) and right (%rcx)
            
            return "\n".join(asm)
        
        # Handle Variable Declarations
        if n_type == "VariableDeclaration":
            asm = []
            for decl in node.get("declarations", []):
                var_name = decl["id"]["name"]
                # Allocate 8 bytes on our virtual stack for each variable
                self.stack_ptr -= 8
                self.locals[var_name] = self.stack_ptr
                
                # If there is an initial value, compile it and store it
                init = decl.get("init")
                if init and init.get("type") != "NullLiteral":
                    asm.append(self.compile(init)) # Result in %rax
                else:
                    asm.append("    movq $0, %rax") # Default to 0/undefined
                
                # Move value from %rax to the stack location
                asm.append(f"    movq %rax, {self.locals[var_name]}(%rbp)")
            
            return "\n".join(asm)
        
        if n_type == "Identifier":
            name = node.get("name")
            offset = self.locals.get(name)
            return f"    movq {offset}(%rbp), %rax"
        
        if n_type == "WhileStatement":
            start_label = self.get_new_label()
            end_label = self.get_new_label()
            # Use a map to choose the 'inverse' jump (jump if the condition is FALSE)
            op = node["test"]["operator"]
            jump_map = {
                "<": "jge",   # If not less than, jump to end
                ">": "jle",   # If not greater than, jump to end
                "==": "jne",  # If not equal, jump to end
                "!=": "je",   # If equal, jump to end
                "<=": "jg",
                ">=": "jl"
            }
            jump_instr = jump_map.get(op, "je")

            asm = [
                f"{start_label}:",
                self.compile(node["test"]),
                f"    {jump_instr} {end_label}",
                self.compile(node["body"]),
                f"    jmp {start_label}",
                f"{end_label}:"
            ]
            return "\n".join(asm)
        

        if n_type == "IfStatement":
            label_else = self.get_new_label()
            label_end = self.get_new_label()
            
            # 1. Compile the test (e.g., x != 0)
            op = node["test"]["operator"]
            jump_map = {
                "<": "jge", ">": "jle", "==": "jne", 
                "!=": "je", "<=": "jg", ">=": "jl"
            }
            jump_instr = jump_map.get(op, "je")

            asm = [
                self.compile(node["test"]),     # Generates the cmpq
                f"    {jump_instr} {label_else}", # Jump to else if false
                self.compile(node["consequent"]), # Then block
                f"    jmp {label_end}",           # Skip else block
                f"{label_else}:",
                self.compile(node.get("alternate")), # Else block (if any)
                f"{label_end}:"
            ]
            return "\n".join(asm)
        
        if n_type == "BlockStatement":
            return "\n".join([self.compile(s) for s in node.get("body", [])])
        
        if n_type == "AssignmentExpression":
            target_name = node["left"]["name"]
            offset = self.locals.get(target_name)
            op = node["operator"]
            
            # 1. Compile the right-hand side (value goes to %rax)
            asm = [self.compile(node["right"])]
            
            # 2. Apply the operation to the memory location
            if op == "=":
                asm.append(f"    movq %rax, {offset}(%rbp)")
            elif op == "+=":
                asm.append(f"    addq %rax, {offset}(%rbp)")
            elif op == "-=":
                asm.append(f"    subq %rax, {offset}(%rbp)")
            
            return "\n".join(asm)

        if n_type == "NumericLiteral":
            val = node.get("value")
            # In x86-64, %rax is where the program looks for the return value
            return f"    movq ${val}, %rax"
        
        if n_type == "UpdateExpression":
            name = node["argument"]["name"]
            offset = self.locals.get(name)
            op = "incq" if node["operator"] == "++" else "decq"
            return f"    {op} {offset}(%rbp)"
        
        if n_type == "CallExpression":
            callee = node["callee"]["name"]
            if callee == "print":
                # 1. Get the variable value into %rax (using Identifier logic)
                arg_asm = self.compile(node["arguments"][0])
                # 2. Add the format string to data section if not already there
                fmt_label = ".LC_PRINT_INT"
                if f'{fmt_label}: .string "%d\\n"' not in self.data_section:
                    self.data_section.append(f'{fmt_label}: .string "%d\\n"')
                
                asm = [
                    arg_asm,
                    f"    movq %rax, %rdx",      # Second argument: the number
                    f"    leaq {fmt_label}(%rip), %rcx", # First argument: format string
                    "    call printf"        # Call C library function
                ]
                return "\n".join(asm)
        
        if n_type == "StringLiteral":
            label = self.get_new_string_label()
            val = node.get("value")
            # Store the string definition for the .data section
            self.data_section.append(f'{label}: .string "{val}"')
            # Load the ADDRESS of the string into %rax
            return f"    leaq {label}(%rip), %rax"
        
        if n_type == "NullLiteral":
            return "    movq $0, %rax"

        return f"/* Missing: {n_type} */"

script_dir = os.path.dirname(__file__) 
file_path = os.path.join(script_dir, '04-if-while.json')

with open(file_path, 'r') as f:
    ast = json.load(f)

compiler = Compiler()
print(compiler.compile(ast))