import json

with open("05-fors.json", "r") as f:
    data = json.load(f)

body = data["program"]["body"]

for node in body:

    # var i;
    if node["type"] == "VariableDeclaration":
        name = node["declarations"][0]["id"]["name"]
        print(f"var {name};\n")

    # function print(i) { }
    elif node["type"] == "FunctionDeclaration":
        fname = node["id"]["name"]
        param = node["params"][0]["name"]
        print(f"function {fname}({param}) {{")
        print("} ;\n")

    # Empty statement (just skip, but preserve spacing)
    elif node["type"] == "EmptyStatement":
        pass

    # for loops
    elif node["type"] == "ForStatement":

        # init
        if node["init"] is None:
            init = ""
        else:
            left = node["init"]["left"]["name"]
            right = node["init"]["right"]["value"]
            init = f"{left} = {right}"

        # test
        test_left = node["test"]["left"]["name"]
        test_op = node["test"]["operator"]
        test_right = node["test"]["right"]["value"]
        test = f"{test_left} {test_op} {test_right}"

        # update
        update_node = node["update"]
        if update_node["type"] == "UpdateExpression":
            update = f'{update_node["argument"]["name"]} ++'
        else:
            update = f'{update_node["left"]["name"]} {update_node["operator"]} {update_node["right"]["value"]}'

        print(f"for ({init}; {test}; {update}) {{")

        for stmt in node["body"]["body"]:
            expr = stmt["expression"]
            func = expr["callee"]["name"]
            arg = expr["arguments"][0]["name"]
            print(f"    {func}({arg});")

        print("}\n")
