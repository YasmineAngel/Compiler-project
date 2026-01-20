# JavaScript AST Interpreter

A lightweight Python-based interpreter designed to execute JavaScript programs represented as **Abstract Syntax Trees (AST)** in JSON format. This project supports complex functional programming features including closures, static scoping, and recursion.

## Features

* **Variable Scoping**: Supports `var` declarations with a parent-linked environment system.
* **First-Class Functions**: Functions can be stored in variables and returned from other functions.
* **Closures (Static Scoping)**: Each function captures its definition-time environment (`closure_env`) to resolve variables correctly, regardless of where the function is called.
* **Control Flow**: Implements `if`, `while`, `for`, and `switch` statements with support for `break` and `continue`.
* **Deep Recursion**: Handles recursive calls such as factorial calculations.

---

## Usage

Run the interpreter from the terminal by passing a JSON AST file as an argument:

```bash
python interpreter.py filename.json

```

### Verbose Mode

To see the details including identifier resolutions, environment swaps, and binary operations—use the `-verbose` flag:

```bash
python interpreter.py -verbose 18-func-in-func.json

```

---

## Project Structure

* **`Environment` Class**: Manages variable storage. Uses a parent-pointer tree to implement lexical scoping.
* **`Interpreter` Class**: The `interpret()` method recursively traverses the AST nodes.
* **`Exceptions`**: Custom Python exceptions (`BreakException`, `ContinueException`, `ReturnException`) are used to control flow across the recursive visitor pattern.

---

### The Problem with Recursion

In my current implementation, the interpreter uses recursion to traverse the Abstract Syntax Tree (AST). This consumes space on the System Call Stack. On physical hardware with limited stack memory, deep recursion (like factorial(10000)) will cause a Stack Overflow, that's why for real interpreters, an iterative approach is required.

### The Iterative method:

 **Manual Stack**: In an iterative version we create a Control Stack in the heap to handle the "memory" of our program.
 - Every time we hit a nested node we create a new frame in a list .
 - We’d use a single while loop that keeps running as long as there are "tasks" left in a list. We just pop a task, process it, and move on.


 **Managing Values without "Returns"**: In an iterative loop, we can't just use a return statement to send a value back to a parent node. Instead, we have to use a Value Stack:
 - If we see something like 1 + 2, we push a "Plus Task" onto the stack, then push the numbers 1 and 2.
 - The Result: The interpreter resolves the numbers first, stores them in a separate values list, and then the "Plus Task" pops them later to do the final math.


 **Function Calls**: To handle functions like toto(3) without recursion, we have to manually simulate what the CPU does:
 - **Save**: When a function is called, we save our current position and the current environment to the stack.
 - **Jump**: We "jump" to the function's body and load its closure_env so it has the right scope.
 - **Return**: When we hit a ReturnStatement, we just pop the saved state back off the stack and pick up exactly where we left off.
