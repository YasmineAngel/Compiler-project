import json
class BreakException(Exception): pass
class ContinueException(Exception): pass
class ReturnException(Exception):
    def __init__(self, value):
        self.value = value
class Environment:
    def __init__(self, parent=None):
        self.variables = {}  # Local dictionary for this scope
        self.parent = parent # Link to global/outer dictionary

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
            self.variables[name] = value # Fallback to local if not found
class Interpreter:
    def __init__(self, indent_size=4):
        self.env = Environment()
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

    def interpret(self, node, parent_prec=0):
        if node is None: return None
        n_type = node.get("type")

        # Roots
        if n_type == "File": return self.interpret(node.get("program"))
    
        
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
            print(f"VariableDeclaration: {var_name} {repr(val) if val != 'undefined' else 'undefined'}")
            return val

        if n_type == "FunctionDeclaration":
            func_name = node.get('id').get('name')
            self.env.set(func_name,  {
                "params": node.get("params", []),
                "body": node.get("body")
            })
            print(f"FunctionDeclaration: {func_name}")
            return None

        # Control Flow
        if n_type == "IfStatement":
            if self.interpret(node.get('test')):
              return self.interpret(node.get('consequent'))
            elif node.get("alternate"):
              return self.interpret(node.get('alternate'))
            return None

        if n_type == "WhileStatement":
            result = None
            try:
                while self.interpret(node.get('test')):
                    try:
                        result = self.interpret(node.get('body'))
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
            disc = self.interpret(node.get("discriminant"))
            self.indent_level += 1
            cases = "\n".join(self.interpret(c) for c in node.get("cases", []))
            self.indent_level -= 1
            return f"switch ({disc}) {{\n{cases}\n{self.get_indent()}}}"

        if n_type == "SwitchCase":
            test = self.interpret(node.get("test"))
            prefix = f"case {test}:" if test else "default:"
            self.indent_level += 1
            indent = self.get_indent()
            cons = f"\n{indent}".join(self.interpret(s) for s in node.get("consequent", []))
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
            is_print = (expr.get("type") == "CallExpression" and 
                expr.get("callee", {}).get("name") in ["print", "console.log"])
    
            if res is not None and not is_print:
                print(f"ExpressionStatement: {res}")
            return res

        if n_type in ["BinaryExpression", "AssignmentExpression", "LogicalExpression"]:
            op = node.get("operator")
            curr_prec = self.precedence.get(op, 0)
            left = self.interpret(node.get("left"), curr_prec)
            right = self.interpret(node.get("right"), curr_prec)
            res = None 
            match op:
                case "=":
                    var_name = node.get("left").get("name")
                    val = self.interpret(node.get("right"))
                    self.env.set(var_name, val)
                    return val
                case "+=":
                   var_name = node.get("left").get("name")
                   val = self.env.get(var_name, 0) + self.interpret(node.get("right"))
                   self.env.set(var_name, val)
                   return val
                case "-=":
                   var_name = node.get("left").get("name")
                   val = self.env.get(var_name, 0) - self.interpret(node.get("right"))
                   self.env.set(var_name, val)
                   return val
                case "+":   res = left + right
                case "-":   res = left - right
                case "*":   res = left * right
                case "/":   res = left / right
                case "==":  res = left == right
                case "<":   res = left < right
                case "&&":  res = left and right
                case "||":  res = left or right
                case "<":   res = left < right
                case ">":   res = left > right
                case "<=":  res = left <= right
                case ">=":  res = left >= right
                case "!==": res = left != right
                case "!=": res = left != right

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
        
    
           self.env.set(var_name,new_val)
           return new_val

        if n_type == "UnaryExpression":
            arg = self.interpret(node.get("argument"))
            return f"({node.get('operator')}{arg})"

        if n_type == "CallExpression":
            callee_name = node.get('callee').get('name')
            args = [self.interpret(a) for a in node.get("arguments", [])]

            if callee_name in ["print", "console.log"]:
                print(f"Print: {args[0]}")
                return args[0]

            func = self.env.get(callee_name)
            if isinstance(func, dict):
                old_env = self.env
                self.env = Environment(parent=old_env) # Create local environment
                
                for i, param in enumerate(func['params']):
                    self.env.set(param.get('name'), args[i]) # Map params to args
                    
                result = None
                try:
                    result = self.interpret(func['body']) # Execute body
                except ReturnException as e:
                    result = e.value # Capture the returned value
                
                self.env = old_env # Restore environment
                return result
        
        # Objects & Classes
        if n_type == "MemberExpression":
            obj = self.interpret(node.get("object"))
            prop = self.interpret(node.get("property"))
            return f"{obj}.{prop}" if not node.get("computed") else f"{obj}[{prop}]"

        if n_type == "ObjectExpression":
            props = ", ".join(self.interpret(p) for p in node.get("properties", []))
            return f"{{ {props} }}"

        if n_type == "ObjectProperty":
            return f"{self.interpret(node.get('key'))}: {self.interpret(node.get('value'))}"

        if n_type == "NewExpression":
            args = ", ".join(self.interpret(a) for a in node.get("arguments", []))
            return f"new {self.interpret(node.get('callee'))}({args})"

        # Leaves
        if n_type == "Identifier": return self.env.get(node.get("name"))
        if n_type == "NumericLiteral": return node.get("value")
        if n_type == "StringLiteral": return node.get("value")
        if n_type == "BooleanLiteral": return (node.get("value"))
        if n_type == "NullLiteral": return None
        if n_type == "ThisExpression": return "this"
        if n_type == "ReturnStatement": 
            val = self.interpret(node.get('argument'))
            raise ReturnException(val)
        if n_type == "BreakStatement":
            print("BreakStatement")
            raise BreakException()

        if n_type == "ContinueStatement":
            print("ContinueStatement")
            raise ContinueException()

        if n_type == "EmptyStatement": return ";"

        return f"/* Missing: {n_type} */"

# usage function
def run_interpreter(path):
    with open(path, "r") as f:
        Interpreter().interpret(json.load(f))



# Running
#run_interpreter("01-expressions.json")
#run_interpreter("02-declarations.json")
#run_interpreter("03-while.json")
#run_interpreter("04-if-while.json")
#run_interpreter("05-fors.json")
#run_interpreter("06-while-break.json")
run_interpreter("11-func.json")
#run_interpreter("12-fact.json")
#run_interpreter("13-switch.json")
#run_interpreter("14-obj.json")
#run_interpreter("15-new.json")
#run_interpreter("16-funcs.json")
#run_interpreter("17-double-parenth-func.json")
#run_interpreter("18-func-in-func.json")