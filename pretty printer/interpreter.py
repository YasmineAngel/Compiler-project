import json


class BreakException(Exception):
    pass


class ContinueException(Exception):
    pass


class ReturnException(Exception):
    def __init__(self, value):
        self.value = value


class Environment:
    def __init__(self, parent=None):
        self.variables = {}  # Local dictionary for this scope
        self.parent = parent  # Link to global/outer dictionary

    def set(self, name, value):
        """Always sets the variable in the CURRENT local scope."""
        self.variables[name] = value

    def get(self, name, default=None):
        """Look in local scope first, then parent."""
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name, default)
        return default if default is not None else "undefined"

    def update(self, name, value):
        if name in self.variables:
            self.variables[name] = value
        elif self.parent:
            self.parent.update(name, value)
        else:
            self.variables[name] = value  # Fallback to local if not found


class Interpreter:
    def __init__(self, indent_size=4, verbose=False):
        self.env = Environment()
        self.verbose = verbose
        self.indent_size = indent_size
        self.indent_level = 0
        self.env.set("console", {"log": "built-in-print"})
        self.precedence = {
            "||": 1,
            "&&": 2,
            "|": 3,
            "^": 4,
            "&": 5,
            "==": 6,
            "!=": 6,
            "===": 6,
            "!==": 6,
            "<": 7,
            "<=": 7,
            ">": 7,
            ">=": 7,
            "+": 8,
            "-": 8,
            "*": 9,
            "/": 9,
            "%": 9,
        }

    def get_indent(self):
        return " " * (self.indent_level * self.indent_size)

    def interpret(self, node, parent_prec=0):
        if node is None:
            return None
        n_type = node.get("type")

        # Roots
        if n_type == "File":
            return self.interpret(node.get("program"))

        # Declarations
        if n_type == "VariableDeclaration":
            for decl in node.get("declarations", []):
                self.interpret(decl)
            return None

        if n_type == "VariableDeclarator":
            var_name = node.get("id").get("name")
            init_node = node.get("init")
            val = self.interpret(init_node) if init_node is not None else "undefined"
            self.env.set(var_name, val)
            trace_val = "function" if isinstance(val, dict) and "body" in val else val
            if self.verbose:
                print(f"  [Verbose] Declaring {var_name} as {trace_val}")
            print(f"VariableDeclaration: {var_name} {trace_val}")
            return val

        if n_type == "FunctionDeclaration":
            func_name = node.get("id").get("name")
            self.env.set(
                func_name,
                {
                    "params": node.get("params", []),
                    "body": node.get("body"),
                    "closure_env": self.env,  # Store the current scope
                },
            )
            print(f"FunctionDeclaration: {func_name}")
            return None

        # Control Flow
        if n_type == "IfStatement":
            if self.interpret(node.get("test")):
                return self.interpret(node.get("consequent"))
            elif node.get("alternate"):
                return self.interpret(node.get("alternate"))
            return None

        if n_type == "WhileStatement":
            result = None
            try:
                while self.interpret(node.get("test")):
                    try:
                        result = self.interpret(node.get("body"))
                    except ContinueException:
                        continue
            except BreakException:
                pass
            return result

        if n_type == "ForStatement":
            if node.get("init"):
                self.interpret(node.get("init"))
                result = None
            while True:
                if node.get("test"):
                    if not self.interpret(node.get("test")):
                        break
                result = self.interpret(node.get("body"))
                if node.get("update"):
                    self.interpret(node.get("update"))

            return result

        if n_type == "SwitchStatement":
            disc_val = self.interpret(node.get("discriminant"))

            result = None
            matched = False
            default_case = None

            for case in node.get("cases", []):
                test_node = case.get("test")

                if test_node is None:
                    default_case = case
                    continue

                case_val = self.interpret(test_node)

                if matched or disc_val == case_val:
                    matched = True
                    try:
                        for stmt in case.get("consequent", []):
                            result = self.interpret(stmt)
                    except BreakException:
                        return result
                    except ReturnException as e:
                        raise e

            if not matched and default_case:
                for stmt in default_case.get("consequent", []):
                    result = self.interpret(stmt)

            return result

        if n_type == "SwitchCase":
            test = self.interpret(node.get("test"))
            prefix = f"case {test}:" if test else "default:"
            self.indent_level += 1
            indent = self.get_indent()
            cons = f"\n{indent}".join(
                self.interpret(s) for s in node.get("consequent", [])
            )
            self.indent_level -= 1
            return f"{self.get_indent()}{prefix}\n{indent}{cons}"

        # Basic Blocks & Expressions
        if n_type == "Program" or n_type == "BlockStatement":
            last_val = None
            for statement in node.get("body", []):
                last_val = self.interpret(statement)
            return last_val

        if n_type == "ExpressionStatement":
            expr = node.get("expression")
            res = self.interpret(expr)

            is_print_func = expr.get("type") == "CallExpression" and expr.get(
                "callee", {}
            ).get("name") in ["print", "console.log"]

            if self.verbose:
                print(f"  [Verbose] Expression Result: {res}")

            if self.indent_level == 0 and res is not None and not is_print_func:
                if expr.get("type") in [
                    "BinaryExpression",
                    "CallExpression",
                    "NumericLiteral",
                    "StringLiteral",
                ]:
                    if (
                        expr.get("type") in ["NumericLiteral", "StringLiteral"]
                        and self.indent_level == 0
                    ):
                        print(f"ExpressionStatement: {res}")
                    elif expr.get("type") not in ["NumericLiteral", "StringLiteral"]:
                        print(f"ExpressionStatement: {res}")

            return res

        if n_type in ["BinaryExpression", "AssignmentExpression", "LogicalExpression"]:
            op = node.get("operator")

            if n_type != "AssignmentExpression":
                curr_prec = self.precedence.get(op, 0)
                left = self.interpret(node.get("left"), curr_prec)
                right = self.interpret(node.get("right"), curr_prec)

            if self.verbose and n_type != "AssignmentExpression":
                print(f"  [Verbose] BinaryOp: {left} {op} {right}")

            match op:
                case "=":
                    left_node = node.get("left")
                    val = self.interpret(node.get("right"))

                    if left_node.get("type") == "MemberExpression":
                        obj = self.interpret(left_node.get("object"))
                        if isinstance(obj, dict):
                            if left_node.get("computed"):
                                prop = self.interpret(left_node.get("property"))
                            else:
                                prop = left_node.get("property").get("name")

                            obj[prop] = val
                        return val
                    else:
                        var_name = left_node.get("name")
                        self.env.update(var_name, val)
                        return val

                case "+=":
                    var_name = node.get("left").get("name")
                    right_val = self.interpret(node.get("right"))
                    old_val = self.env.get(var_name, 0)
                    new_val = old_val + right_val

                    if self.verbose:
                        print(
                            f"  [Verbose] Assignment: {var_name} += {right_val} (Result: {new_val})"
                        )

                    self.env.set(var_name, new_val)
                    return new_val

                case "-=":
                    var_name = node.get("left").get("name")
                    right_val = self.interpret(node.get("right"))
                    old_val = self.env.get(var_name, 0)
                    new_val = old_val - right_val

                    if self.verbose:
                        print(
                            f"  [Verbose] Assignment: {var_name} -= {right_val} (Result: {new_val})"
                        )

                    self.env.set(var_name, new_val)
                    return new_val

                case "+":
                    res = left + right
                case "-":
                    res = left - right
                case "*":
                    res = left * right
                case "/":
                    res = left / right
                case "==":
                    res = left == right
                case "<":
                    res = left < right
                case "&&":
                    res = left and right
                case "||":
                    res = left or right
                case "<":
                    res = left < right
                case ">":
                    res = left > right
                case "<=":
                    res = left <= right
                case ">=":
                    res = left >= right
                case "!==":
                    res = left != right
                case "!=":
                    res = left != right

            return res

        if n_type == "UpdateExpression":
            var_name = node.get("argument").get("name")
            current_val = self.env.get(var_name, 0)
            op = node.get("operator")
            if op == "++":
                new_val = current_val + 1
            elif op == "--":
                new_val = current_val - 1
            else:
                new_val = current_val

            if self.verbose:
                print(
                    f"  [Verbose] Update: {var_name} {op} (from {current_val} to {new_val})"
                )

            self.env.set(var_name, new_val)
            return new_val

        if n_type == "UnaryExpression":
            arg = self.interpret(node.get("argument"))
            return f"({node.get('operator')}{arg})"

        if n_type == "CallExpression":
            callee_node = node.get("callee")
            func = self.interpret(callee_node)
            args = [self.interpret(a) for a in node.get("arguments", [])]

            if self.verbose:
                func_name = (
                    callee_node.get("name")
                    if callee_node.get("type") == "Identifier"
                    else "anonymous"
                )
                print(f"  [Verbose] Calling '{func_name}' with arguments: {args}")

            # 2. Check for built-ins first
            if callee_node.get("type") == "Identifier" and callee_node.get("name") in [
                "print",
                "console.log",
            ]:
                print(f"Print: {args[0]}")
                return args[0]

            # 3. Execute the function stored in 'func'
            if isinstance(func, dict) and "body" in func:
                old_env = self.env

                if self.verbose:
                    print(f"  [Verbose] Swapping to function scope (Static Scoping)")

                # Use static scoping via closure_env
                self.env = Environment(parent=func.get("closure_env", old_env))

                for i, param in enumerate(func.get("params", [])):
                    self.env.set(param.get("name"), args[i])

                result = None
                try:
                    result = self.interpret(func["body"])
                except ReturnException as e:
                    result = e.value

                self.env = old_env
                return result

        # Objects & Classes
        if n_type == "MemberExpression":
            obj = self.interpret(node.get("object"))
            if obj == "undefined":
                return "undefined"

            if node.get("computed"):
                prop = self.interpret(node.get("property"))
            else:
                prop = node.get("property").get("name")

            if isinstance(obj, dict):
                return obj.get(prop, "undefined")
            return "undefined"

        if n_type == "ObjectExpression":
            obj = {}
            for prop in node.get("properties", []):
                key_node = prop.get("key")
                if key_node.get("type") == "Identifier":
                    key = key_node.get("name")
                else:
                    key = self.interpret(key_node)

                value = self.interpret(prop.get("value"))
                obj[key] = value
            return obj

        if n_type == "ObjectProperty":
            return f"{self.interpret(node.get('key'))}: {self.interpret(node.get('value'))}"

        if n_type == "NewExpression":
            callee_name = node.get("callee").get("name")
            args = [self.interpret(a) for a in node.get("arguments", [])]
            func = self.env.get(callee_name)

            if isinstance(func, dict):
                new_instance = {}

                old_env = self.env
                self.env = Environment(parent=old_env)
                self.env.set("this", new_instance)

                for i, param in enumerate(func.get("params", [])):
                    self.env.set(param.get("name"), args[i])

                try:
                    self.interpret(func.get("body"))
                except ReturnException as e:
                    if isinstance(e.value, dict):
                        new_instance = e.value

                self.env = old_env
                return new_instance

        # Leaves
        if n_type == "Identifier":
            val = self.env.get(node.get("name"))
            if self.verbose:
                display_val = (
                    "[Function]" if isinstance(val, dict) and "body" in val else val
                )
                print(
                    f"  [Verbose] Resolve Identifier: '{node.get('name')}' -> {display_val}"
                )
            return val
        if n_type == "NumericLiteral":
            return node.get("value")
        if n_type == "StringLiteral":
            return node.get("value")
        if n_type == "BooleanLiteral":
            return node.get("value")
        if n_type == "NullLiteral":
            return None
        if n_type == "ThisExpression":
            return self.env.get("this")
        if n_type == "ReturnStatement":
            val = self.interpret(node.get("argument"))
            raise ReturnException(val)
        if n_type == "BreakStatement":
            print("BreakStatement")
            raise BreakException()

        if n_type == "ContinueStatement":
            print("ContinueStatement")
            raise ContinueException()

        if n_type == "EmptyStatement":
            return ";"

        return f"/* Missing: {n_type} */"


# usage function
def run_interpreter(path, verbose=False):
    try:
        with open(path, "r") as f:
            data = json.load(f)
            Interpreter(verbose=verbose).interpret(data)
    except Exception as e:
        print(f"Error: {e}")


# Running
# run_interpreter("01-expressions.json")
# run_interpreter("02-declarations.json")
# run_interpreter("03-while.json")
# run_interpreter("04-if-while.json")
# run_interpreter("05-fors.json")
# run_interpreter("06-while-break.json")
# run_interpreter("11-func.json")
# run_interpreter("12-fact.json")
# run_interpreter("13-switch.json")
# run_interpreter("14-obj.json")
# run_interpreter("15-new.json")
# run_interpreter("16-funcs.json")
# run_interpreter("17-double-parenth-func.json")
# run_interpreter("18-func-in-func.json")

import sys
import json

if __name__ == "__main__":

    verbose_mode = "-verbose" in sys.argv

    args = [a for a in sys.argv[1:] if a != "-verbose"]

    if args:
        run_interpreter(args[0], verbose=verbose_mode)
    else:
        print("Usage: py interpreter.py [-verbose] filename.json")
