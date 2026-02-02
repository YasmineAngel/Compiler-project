class Compiler:
    def __init__(self):
        self.code = []

    def emit(self, line):
        """Helper to add a line of assembly."""
        self.code.append(f"    {line}")

    def compile(self, node):
        n_type = node.get("type")

        # 1. Start the Program
        if n_type == "File":
            return self.compile(node.get("program"))

        if n_type == "Program":
            # Header instructions
            header = [".text", ".global main", "main:"]
            full_asm = header + [self.compile(s) for s in node.get("body", [])]
            # Final step: ensure the last value is in %rax and return
            full_asm.append("    ret")
            return "\n".join(full_asm)

        # 2. Handle a single number (The Leaf)
        if n_type == "ExpressionStatement":
            return self.compile(node.get("expression"))

        if n_type == "NumericLiteral":
            val = node.get("value")
            # In x86-64, %rax is where the program looks for the return value
            return f"    movq ${val}, %rax"

        return f"/* Missing: {n_type} */"

# Quick test with a dummy AST representing "42;"
dummy_ast = {
    "type": "File",
    "program": {
        "type": "Program",
        "body": [
            {"type": "ExpressionStatement", "expression": {"type": "NumericLiteral", "value": 42}}
        ]
    }
}

compiler = Compiler()
print(compiler.compile(dummy_ast))