import json

with open("01-expressions.json", "r") as f:
    data = json.load(f)

body = data["program"]["body"]
comments = data["comments"]

# Print comment
for comment in comments:
    print(f"/*{comment['value']}*/\n")


# Operator precedence
precedence = {
    "+": 1,
    "*": 2
}

def print_expression(expr, parent_op=None):
    # Numeric literal
    if expr["type"] == "NumericLiteral":
        return str(expr["value"])

    # Binary expression
    if expr["type"] == "BinaryExpression":
        op = expr["operator"]

        left = print_expression(expr["left"], op)
        right = print_expression(expr["right"], op)

        expr_str = f"{left} {op} {right}"

        # Add parentheses ONLY if required by AST grouping
        if parent_op and precedence[op] < precedence[parent_op]:
            return f"({expr_str})"

        return expr_str


# Print expressions
for stmt in body:
    expr = stmt["expression"]
    print(f"{print_expression(expr)};")
