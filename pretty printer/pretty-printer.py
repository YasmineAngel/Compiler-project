import json

class PrettyPrinter:
    def __init__(self, indent_size=4):
        self.indent_size = indent_size
        self.indent_level = 0
        self.precedence = {
            "||": 1, "&&": 2, "|": 3, "^": 4, "&": 5,
            "==": 6, "!=": 6, "===": 6, "!==": 6,
            "<": 7, "<=": 7, ">": 7, ">=": 7,
            "+": 8, "-": 8, "*": 9, "/": 9, "%": 9
        }

    def get_indent(self):
        return " " * (self.indent_level * self.indent_size)

    def print_node(self, node, parent_prec=0):
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
            name = self.print_node(node.get('id'))
            params = ", ".join(self.print_node(p) for p in node.get("params", []))
            body = self.print_node(node.get('body'))
            return f"function {name}({params}) {body}"

        # Control Flow
        if n_type == "IfStatement":
            consequent = self.print_node(node.get('consequent'))
            code = f"if ({self.print_node(node.get('test'))}) {consequent}"
            if node.get("alternate"):
                code += f" else {self.print_node(node.get('alternate'))}"
            return code

        if n_type == "WhileStatement":
            return f"while ({self.print_node(node.get('test'))}) {self.print_node(node.get('body'))}"

        if n_type == "ForStatement":
            init = self.print_node(node.get("init")).rstrip(";")
            test = self.print_node(node.get("test"))
            update = self.print_node(node.get("update"))
            return f"for ({init}; {test}; {update}) {self.print_node(node.get('body'))}"

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
            cons = f"\n{indent}".join(self.print_node(s) for s in node.get("consequent", []))
            self.indent_level -= 1
            return f"{self.get_indent()}{prefix}\n{indent}{cons}"
        
        # Basic Blocks & Expressions
        if n_type == "BlockStatement":
            self.indent_level += 1
            lines = [f"{self.get_indent()}{self.print_node(s)}" for s in node.get("body", [])]
            self.indent_level -= 1
            return "{\n" + "\n".join(lines) + f"\n{self.get_indent()}}}"

        if n_type == "ExpressionStatement":
            return f"{self.print_node(node.get('expression'))};"

        if n_type in ["BinaryExpression", "AssignmentExpression", "LogicalExpression"]:
            op = node.get("operator")
            curr_prec = self.precedence.get(op, 0)
            left = self.print_node(node.get("left"), curr_prec)
            right = self.print_node(node.get("right"), curr_prec)
            res = f"{left} {op} {right}"
            return f"({res})" if parent_prec > curr_prec and curr_prec != 0 else res

        if n_type == "UpdateExpression":
            arg = self.print_node(node.get("argument"))
            op = node.get("operator")
            return f"{op}{arg}" if node.get("prefix") else f"{arg}{op}"

        if n_type == "UnaryExpression":
            arg = self.print_node(node.get("argument"))
            return f"({node.get('operator')}{arg})"

        if n_type == "CallExpression":
            args = ", ".join(self.print_node(a) for a in node.get("arguments", []))
            return f"{self.print_node(node.get('callee'))}({args})"
        
        # Objects & Classes
        if n_type == "MemberExpression":
            obj = self.print_node(node.get("object"))
            prop = self.print_node(node.get("property"))
            return f"{obj}.{prop}" if not node.get("computed") else f"{obj}[{prop}]"

        if n_type == "ObjectExpression":
            props = ", ".join(self.print_node(p) for p in node.get("properties", []))
            return f"{{ {props} }}"

        if n_type == "ObjectProperty":
            return f"{self.print_node(node.get('key'))}: {self.print_node(node.get('value'))}"

        if n_type == "NewExpression":
            args = ", ".join(self.print_node(a) for a in node.get("arguments", []))
            return f"new {self.print_node(node.get('callee'))}({args})"

        # Leaves
        if n_type == "Identifier": return node.get("name")
        if n_type == "NumericLiteral": return str(node.get("value"))
        if n_type == "StringLiteral": return f'"{node.get("value")}"'
        if n_type == "BooleanLiteral": return str(node.get("value")).lower()
        if n_type == "NullLiteral": return "null"
        if n_type == "ThisExpression": return "this"
        if n_type == "ReturnStatement": return f"return {self.print_node(node.get('argument'))};"
        if n_type == "BreakStatement": return "break;"
        if n_type == "ContinueStatement": return "continue;"
        if n_type == "EmptyStatement": return ";"

        return f"/* Missing: {n_type} */"

# usage function
def run_pretty_printer(path):
    with open(path, "r") as f:
        print(PrettyPrinter().print_node(json.load(f)))



# Running
run_pretty_printer("01-expressions.json")
run_pretty_printer("02-declarations.json")
run_pretty_printer("03-while.json")
run_pretty_printer("04-if-while.json")
run_pretty_printer("05-fors.json")
run_pretty_printer("06-while-break.json")
run_pretty_printer("11-func.json")
run_pretty_printer("12-fact.json")
run_pretty_printer("13-switch.json")
run_pretty_printer("14-obj.json")
run_pretty_printer("15-new.json")
run_pretty_printer("16-funcs.json")
run_pretty_printer("17-double-parenth-func.json")
run_pretty_printer("18-func-in-func.json")