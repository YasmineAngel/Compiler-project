import json

with open("04-if-while.json", "r") as f:
    data = json.load(f)

body = data["program"]["body"]

for node in body:

    # var x = 0;
    if node["type"] == "VariableDeclaration":
        decl = node["declarations"][0]
        name = decl["id"]["name"]
        value = decl["init"]["value"]
        print(f"var {name} = {value};")

    # if / else
    elif node["type"] == "IfStatement":
        left = node["test"]["left"]["name"]
        op = node["test"]["operator"]
        right = node["test"]["right"]["value"]

        print(f"if ({left} {op} {right}) {{")

        for stmt in node["consequent"]["body"]:
            expr = stmt["expression"]

            # x++ ;
            if expr["type"] == "UpdateExpression":
                var = expr["argument"]["name"]
                op2 = expr["operator"]
                print(f"    {var}{op2} ;")

            # x-=2 ;
            elif expr["type"] == "AssignmentExpression":
                var = expr["left"]["name"]
                op2 = expr["operator"]
                val = expr["right"]["value"]
                print(f"    {var}{op2}{val} ;")

        print("}")

        # else block (if exists)
        if node["alternate"] is not None:
            print("else {")
            for stmt in node["alternate"]["body"]:
                expr = stmt["expression"]
                var = expr["left"]["name"]
                op2 = expr["operator"]
                val = expr["right"]["value"]
                print(f"    {var} {op2} {val};")
            print("}")

    # while loop
    elif node["type"] == "WhileStatement":
        left = node["test"]["left"]["name"]
        op = node["test"]["operator"]
        right = node["test"]["right"]["value"]

        print(f"while ({left} {op} {right}) {{")

        for stmt in node["body"]["body"]:
            expr = stmt["expression"]

            # print(x);
            if expr["type"] == "CallExpression":
                func = expr["callee"]["name"]
                arg = expr["arguments"][0]["name"]
                print(f"    {func}({arg});")

            # x ++ ;
            elif expr["type"] == "UpdateExpression":
                var = expr["argument"]["name"]
                op2 = expr["operator"]
                print(f"    {var} {op2} ;")

        print("}")
