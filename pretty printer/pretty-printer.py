import json

class PrettyPrinter:
    def __init__(self, indent_size=4):
        self.indent_size = indent_size
        self.indent_level = 0

    def get_indent(self):
        return " " * (self.indent_level * self.indent_size)

    def print_node(self, node):
        if node is None: return ""
        n_type = node.get("type")

        # Roots
        if n_type == "File": return self.print_node(node.get("program"))
        if n_type == "Program":
            return "\n".join(self.print_node(s) for s in node.get("body", []))

        # Declarations
        if n_type == "VariableDeclaration":
            kind = node.get("kind", "var")
            decls = ", ".join(self.print_node(d) for d in node.get("declarations", []))
            return f"{kind} {decls};"

        if n_type == "VariableDeclarator":
            init = self.print_node(node.get("init"))
            return f"{self.print_node(node.get('id'))} = {init}" if init else self.print_node(node.get('id'))

        if n_type == "FunctionDeclaration":
            params = ", ".join(self.print_node(p) for p in node.get("params", []))
            return f"\nfunction {self.print_node(node.get('id'))}({params}) {self.print_node(node.get('body'))}\n"

        # Control Flow (Switch & If)
        if n_type == "SwitchStatement":
            disc = self.print_node(node.get("discriminant"))
            self.indent_level += 1
            cases = "\n".join(self.print_node(c) for c in node.get("cases", []))
            self.indent_level -= 1
            return f"switch ({disc}) {{\n{cases}\n{self.get_indent()}}}"

        if n_type == "SwitchCase":
            test = self.print_node(node.get("test"))
            prefix = f"case {test}:" if test else "default:"
            self.indent_level += 1
            indent = self.get_indent()
            # Consequent is a list of statements
            cons = f"\n{indent}".join(self.print_node(s) for s in node.get("consequent", []))
            self.indent_level -= 1
            return f"{self.get_indent()}{prefix}\n{indent}{cons}"

        if n_type == "IfStatement":
            code = f"if ({self.print_node(node.get('test'))}) {self.print_node(node.get('consequent'))}"
            if node.get("alternate"):
                code += f" else {self.print_node(node.get('alternate'))}"
            return code

        # Objects & Classes
        if n_type == "ObjectExpression":
            props = ", ".join(self.print_node(p) for p in node.get("properties", []))
            return f"{{ {props} }}"

        if n_type == "ObjectProperty":
            key = self.print_node(node.get("key"))
            val = self.print_node(node.get("value"))
            return f"{key}: {val}"

        if n_type == "NewExpression":
            callee = self.print_node(node.get("callee"))
            args = ", ".join(self.print_node(a) for a in node.get("arguments", []))
            return f"new {callee}({args})"

        if n_type == "MemberExpression":
            obj = self.print_node(node.get("object"))
            prop = self.print_node(node.get("property"))
            return f"{obj}.{prop}" if not node.get("computed") else f"{obj}[{prop}]"

        # Basic Blocks & Expressions
        if n_type == "BlockStatement":
            self.indent_level += 1
            lines = [f"{self.get_indent()}{self.print_node(s)}" for s in node.get("body", [])]
            self.indent_level -= 1
            return "{\n" + "\n".join(lines) + f"\n{self.get_indent()}}}"

        if n_type == "ExpressionStatement":
            return f"{self.print_node(node.get('expression'))};"

        if n_type in ["BinaryExpression", "AssignmentExpression", "LogicalExpression"]:
            return f"{self.print_node(node.get('left'))} {node.get('operator')} {self.print_node(node.get('right'))}"

        if n_type == "UnaryExpression":
            arg = self.print_node(node.get("argument"))
            return f"{node.get('operator')}{arg}" if node.get("prefix") else f"{arg}{node.get('operator')}"

        if n_type == "CallExpression":
            args = ", ".join(self.print_node(a) for a in node.get("arguments", []))
            return f"{self.print_node(node.get('callee'))}({args})"

        # Leaves
        if n_type == "Identifier": return node.get("name")
        if n_type == "NumericLiteral": return str(node.get("value"))
        if n_type == "StringLiteral": return f'"{node.get("value")}"'
        if n_type == "ThisExpression": return "this"
        if n_type == "EmptyStatement": return ";"
        if n_type == "ReturnStatement": return f"return {self.print_node(node.get('argument'))};"

        return f"/* Missing: {n_type} */"

# usage function
def run_pretty_printer(path):
    with open(path, "r") as f:
        print(PrettyPrinter().print_node(json.load(f)))



# Running
run_pretty_printer("11-func.json")
run_pretty_printer("12-fact.json")
run_pretty_printer("13-switch.json")
run_pretty_printer("14-obj.json")
run_pretty_printer("15-new.json")
run_pretty_printer("16-funcs.json")
run_pretty_printer("17-double-parenth-func.json")
run_pretty_printer("18-func-in-func.json")
run_pretty_printer("18-func-in-func.json")