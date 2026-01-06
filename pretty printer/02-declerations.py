import json

# Open and read the JSON file
with open('02-declarations.json', 'r') as f:
    data = json.load(f) 

# Extract the 'body' from the program
program_body = data['program']['body']
comments = data['comments']

# Prepare to store the result
output = []

# Loop through the variable declarations
for idx, declaration in enumerate(program_body):
    kind = declaration['kind']  # 'var'
    vars_line = []
    
    for decl in declaration['declarations']:
        name = decl['id']['name']
        init_value = decl['init']
        
        # Check for the value of the initializer
        if init_value is None:
            init_str = f"{name};"
        elif init_value.get('type') == 'NumericLiteral':
            init_str = f"{name} = {init_value['value']};"
        elif init_value.get('type') == 'StringLiteral':
            init_str = f'{name} = "{init_value["value"]}";'
        elif init_value.get('type') == 'NullLiteral':
            init_str = f"{name} = null;"
        else:
            init_str = f"{name};"
        
        # Add the variable line to the list
        vars_line.append(init_str)
    
    # Join the variables into one line
    output.append(f"{kind} {' '.join(vars_line)}")

# Add the comments to the output
for idx, comment in enumerate(comments):
    output[idx] += f" //{comment['value']}"

# Print the formatted JavaScript code
for line in output:
    print(line)
