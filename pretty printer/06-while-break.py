import json

with open("06-while-break.json", "r") as f:
    data = json.load(f)

body = data["program"]["body"]

for node in body:

    # var x = 0; / var y = 8;
    if node["type"] == "VariableDeclaration":
        name = node["declarations"][0]["id"]["name"]
        value = node["declarations"][0]["init"]["value"]
        print(f"var {name} = {value};")

    # function print(i) { }
    elif node["type"] == "FunctionDeclaration":
        fname = node["id"]["name"]
        param = node["params"][0]["name"]
        print(f"\nfunction {fname}({param}) {{")
        print("} ;\n")

    # skip empty statement
    elif node["type"] == "EmptyStatement":
        pass

    # while loop
    elif node["type"] == "WhileStatement":
        left = node["test"]["left"]["name"]
        op = node["test"]["operator"]
        right = node["test"]["right"]["value"]

        print(f"while ({left} {op} {right}) {{")

        for stmt in node["body"]["body"]:

            # if (x == y) { break; }
            if stmt["type"] == "IfStatement":
                l = stmt["test"]["left"]["name"]
                o = stmt["test"]["operator"]
                r = stmt["test"]["right"]["name"] if stmt["test"]["right"]["type"] == "Identifier" else stmt["test"]["right"]["value"]

                print(f"    if ({l} {o} {r}) {{")

                inner = stmt["consequent"]["body"][0]["type"]
                if inner == "BreakStatement":
                    print("        break;")
                elif inner == "ContinueStatement":
                    print("        continue;")

                print("    }")

            # x ++ ;
            elif stmt["expression"]["type"] == "UpdateExpression":
                var = stmt["expression"]["argument"]["name"]
                op2 = stmt["expression"]["operator"]
                print(f"    {var} {op2} ;")

            # print(x);
            elif stmt["expression"]["type"] == "CallExpression":
                func = stmt["expression"]["callee"]["name"]
                arg = stmt["expression"]["arguments"][0]["name"]
                print(f"    {func}({arg});")

        print("}")
