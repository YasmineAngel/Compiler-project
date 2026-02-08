import json 
import os
from LabelManager import LabelManager
from Environment import Environment

class Compiler:
    def __init__(self):
        self.data_section = []
        self.env = Environment()
        self.labels = LabelManager()
        self.loop_stack = []

    def compile(self, node):
        if node is None :
            return ""
        
        n_type = node.get("type")

        # 1. Start the Program
        if n_type == "File":
            return self.compile(node.get("program"))

        if n_type == "Program":
            funcs = []
            main_body = []
            for s in node.get("body", []):
                if s["type"] == "FunctionDeclaration":
                    funcs.append(self.compile(s))
                else:
                    # Compile body
                    main_body.append(self.compile(s))
            header = [".text"] + funcs

            # Header instructions
            if self.data_section:
                header.append(".section .rodata")
                header.extend(self.data_section)
                header.append(".text")

            # Calculate total space needed (number of vars * 8)
            total_space = len(self.env.variables) * 8
            aligned_space = (total_space + 15) & ~15
            stack_size = max(aligned_space, 16)

            header.extend([
                ".global main",
                "main:",
                "    pushq %rbp", 
                "    movq %rsp, %rbp",
                f"    subq ${stack_size}, %rsp"
                ])
            
            
            # Footer: Clean up stack and return
            footer = [
                f"    addq ${stack_size}, %rsp",
                "    popq %rbp",
                "    ret"
            ]
            return "\n".join(header + main_body + footer)

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
            elif op =="-":
                asm.append("    subq %rcx, %rax")
            elif op == "*":
                asm.append("    imulq %rcx, %rax")
            elif op in ["<", ">", "<=", ">=", "==", "!="]:
                asm.append("    cmpq %rcx, %rax") # Compare left (%rax) and right (%rcx)
            
                # To make (n == 0) return a 1 or 0 result in %rax:
                set_instr = {
                    "==": "sete",  "!=": "setne",
                    "<":  "setl",  "<=": "setle",
                    ">":  "setg",  ">=": "setge"
                }[op]
                
                asm.append(f"    {set_instr} %al")  # Sets 8-bit %al to 1 or 0
                asm.append("    movzbq %al, %rax") # Clears the rest of %rax
            
            return "\n".join(asm)
        

        if n_type == "LogicalExpression":
            op = node.get("operator")
            if op == "||":
                true_label = self.labels.new_label("LOGIC_TRUE")
                end_label = self.labels.new_label("LOGIC_END")
                
                # Compile Left Side
                left_asm = self.compile(node["left"])
                # If left is True (not 0), jump to True
                asm = [left_asm, "    cmpq $0, %rax", f"    jne {true_label}"]
                
                # Compile Right Side
                right_asm = self.compile(node["right"])
                asm += [right_asm, "    cmpq $0, %rax", f"    jne {true_label}"]
                
                # If both fail
                asm += ["    movq $0, %rax", f"    jmp {end_label}"]
                
                # True Label
                asm += [f"{true_label}:", "    movq $1, %rax", f"{end_label}:"]
                return "\n".join(asm)
        
        # Handle Variable Declarations
        if n_type == "VariableDeclaration":
            asm = []
            for decl in node.get("declarations", []):
                var_name = decl["id"]["name"]
                offset = self.env.declare(var_name)               
                asm.append(self.compile(decl.get("init")))
                asm.append(f"    movq %rax, {offset}(%rbp)")
            
            return "\n".join(asm)
        
        if n_type == "FunctionDeclaration":
            func_name = node["id"]["name"]
            params = node.get("params", [])
            
            # 1. Save global env and start a FRESH local env
            global_env = self.env
            self.env = Environment() 
            
            # 2. Map POSIX registers to parameters
            arg_regs = ["%rdi", "%rsi", "%rdx", "%rcx", "%r8", "%r9"]
            param_asm = []
            for i, p in enumerate(params):
                offset = self.env.declare(p["name"])
                param_asm.append(f"    movq {arg_regs[i]}, {offset}(%rbp)")
                
            # 3. Compile the body
            body_asm = self.compile(node["body"])
            
            # 4. Determine stack size for this function
            stack_size = max((len(self.env.variables) * 8 + 15) & ~15, 16)

            asm = [
                f"{func_name}:",
                "    pushq %rbp",
                "    movq %rsp, %rbp",
                f"    subq ${stack_size}, %rsp",
                "\n".join(param_asm),
                body_asm,
                f"    # Default exit if no return statement is hit",
                "    movq %rbp, %rsp",
                "    popq %rbp",
                "    ret"
            ]
            
            # Restore global env for the next nodes
            self.env = global_env
            return "\n".join(asm)
        
        if n_type == "ReturnStatement":
            # 1. Compile the expression to return (result goes to %rax)
            value_asm = self.compile(node.get("argument"))
            
            # 2. Cleanup and return
            return f"""{value_asm}
            movq %rbp, %rsp
            popq %rbp
            ret"""
        
        if n_type == "Identifier":
            name = node.get("name")
            offset = self.env.get_offset(name)
            return f"    movq {offset}(%rbp), %rax"
        

        if n_type == "BreakStatement":
            if not self.loop_stack: return "    # Error: break outside loop"
            _, end_label = self.loop_stack[-1]
            return f"    jmp {end_label}"

        if n_type == "ContinueStatement":
            if not self.loop_stack: return "    # Error: continue outside loop"
            start_label, _ = self.loop_stack[-1]
            return f"    jmp {start_label}"
        
        if n_type == "WhileStatement":
            start_label = self.labels.new_label("WHILE_START")
            end_label = self.labels.new_label("WHILE_END")
            # Register this loop so break/continue know where to go
            self.loop_stack.append((start_label, end_label))
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
            self.loop_stack.pop() # Remove loop from stack when done
            return "\n".join(asm)


        if n_type == "IfStatement":
            label_else = self.labels.new_label("ELSE")
            label_end = self.labels.new_label("IF_END")
            
            # 1. Compile the test (e.g., x != 0)
            op = node["test"]["operator"]
            jump_map = {
                "<": "jge", ">": "jle", "==": "jne", 
                "!=": "je", "<=": "jg", ">=": "jl"
            }
            jump_instr = jump_map.get(op, "je")

            asm = [
                self.compile(node["test"]),     # Generates the cmpq
                f"    {jump_instr} {label_else}", # Jump to ELSE if condition is FALSE
                self.compile(node["consequent"]),
            ]

            if node.get("alternate"):
                asm.append(f"    jmp {label_end}")
                asm.append(f"{label_else}:")
                asm.append(self.compile(node["alternate"]))
                asm.append(f"{label_end}:")
            else:
                asm.append(f"{label_else}:") # Just a label to skip the 'if' body
            return "\n".join(asm)
        
        if n_type == "BlockStatement":
            return "\n".join([self.compile(s) for s in node.get("body", [])])
        
        if n_type == "AssignmentExpression":
            target_name = node["left"]["name"]
            offset = self.env.get_offset(target_name)
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
        

        # --- NEW: For Loop ---
        if n_type == "ForStatement":
            start_label = self.labels.new_label("FOR_START")
            update_label = self.labels.new_label("FOR_UPDATE") # Continue jumps here
            end_label = self.labels.new_label("FOR_END")
            self.loop_stack.append((update_label, end_label))
            # 1. Initialization (run once)
            init_code = self.compile(node.get("init"))
            
            # 2. Test (the condition)
            # Assuming BinaryExpression used for test
            test_op = node["test"]["operator"]
            jump_map = {
                "<": "jge", ">": "jle", "==": "jne", 
                "!=": "je", "<=": "jg", ">=": "jl"
            }
            jump_instr = jump_map.get(test_op, "jge")
            
            asm = [
                init_code,
                f"{start_label}:",
                self.compile(node.get("test")), # Generates the cmpq
                f"    {jump_instr} {end_label}",
                self.compile(node.get("body")),
                # 3. Update (run after body, before jumping back)
                self.compile(node.get("update")),
                f"    jmp {start_label}",
                f"{end_label}:"
            ]
            self.loop_stack.pop()
            return "\n".join(asm)

        if n_type == "EmptyStatement" or n_type == "FunctionDeclaration":
            return "" # Ignore these for now
        
        if n_type == "NumericLiteral":
            val = node.get("value")
            # In x86-64, %rax is where the program looks for the return value
            return f"    movq ${val}, %rax"
        
        if n_type == "UpdateExpression":
            name = node["argument"]["name"]
            offset = self.env.get_offset(name)
            op = "incq" if node["operator"] == "++" else "decq"
            return f"    {op} {offset}(%rbp)"
        
        if n_type == "CallExpression":
            callee = node["callee"]["name"]
            args = node.get("arguments", [])
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
            else :
                args = node.get("arguments", [])
                arg_regs = ["%rdi", "%rsi", "%rdx", "%rcx", "%r8", "%r9"]
                asm = []
                # 1. Evaluate arguments and move them to registers
                for i, arg in enumerate(args):
                    asm.append(self.compile(arg)) # Result in %rax
                    asm.append(f"    movq %rax, {arg_regs[i]}")
                    
                # 2. Call the function
                asm.append(f"    call {callee}") # Return value will be in %rax
                return "\n".join(asm)

        
        if n_type == "StringLiteral":
            label = self.labels.new_label("STR")
            val = node.get("value")
            # Store the string definition for the .data section
            self.data_section.append(f'{label}: .string "{val}"')
            # Load the ADDRESS of the string into %rax
            return f"    leaq {label}(%rip), %rax"
        
        if n_type == "NullLiteral":
            return "    movq $0, %rax"

        return f"/* Missing: {n_type} */"

script_dir = os.path.dirname(__file__) 
file_path = os.path.join(script_dir, '12-fact.json')

with open(file_path, 'r') as f:
    ast = json.load(f)

compiler = Compiler()
print(compiler.compile(ast))