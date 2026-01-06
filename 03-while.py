import json

with open("03-while.json", "r") as f:
    data = json.load(f)

body = data["program"]["body"]

for node in body:
    # Handle: var x = 0;
    if node["type"] == "VariableDeclaration":
        decl = node["declarations"][0]
        name = decl["id"]["name"]
        value = decl["init"]["value"]
        print(f"var {name} = {value};")

    # Handle: while loop
    elif node["type"] == "WhileStatement":
        left = node["test"]["left"]["name"]
        operator = node["test"]["operator"]
        right = node["test"]["right"]["value"]

        print(f"while ({left} {operator} {right}) {{")

        for stmt in node["body"]["body"]:
            # x ++ ;
            if stmt["expression"]["type"] == "UpdateExpression":
                var = stmt["expression"]["argument"]["name"]
                op = stmt["expression"]["operator"]
                print(f"    {var} {op} ;")

            # print(x);
            elif stmt["expression"]["type"] == "CallExpression":
                func = stmt["expression"]["callee"]["name"]
                arg = stmt["expression"]["arguments"][0]["name"]
                print(f"    {func}({arg});")

        print("}")
