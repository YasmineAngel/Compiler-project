# x86-64 JavaScript-to-Assembly Compiler

A compiler that translates JavaScript Abstract Syntax Trees (AST) in JSON format into optimized x86-64 assembly code. This project implements advanced features such as recursive function calls, global and local scoping, and complex control flow logic compliant with Posix and Windows x64 calling conventions.

## Features

* **Recursive Function Support**: Implements a standard stack frame using `%rbp` and `%rsp` to allow for deep recursion and nested calls.
* **Variable Scoping**: Supports both global variables (stored in the `.data` section via `%rip` addressing) and local variables (stored on the stack frame).
* **Complex Control Flow**: Implements `if-else`, `while` loops, `for` loops, and a sophisticated `switch` statement that supports dynamic case expressions.
* **Arithmetic & Logical Operations**: Full support for basic math (`+`, `-`, `*`), comparisons (`==`, `!=`, `<`, `>`, etc.), and logical unary operators (`-`, `!`).
* **System Integration**: Built-in support for a `print()` primitive that correctly aligns the stack to interface with the C library `printf` function.

---

## Requirements

* **Python 3.x**
* **GCC** (GNU Compiler Collection) for assembling and linking.

---

## Usage Instructions

### 1. Generate Assembly

Pass your JSON AST file as a command-line argument to the compiler. The script will output the assembly to the console and automatically generate a `test.s` file.

```bash
python Compiler.py input_ast.json

```

### 2. Assemble and Link

Use `gcc` to turn the generated assembly into an executable. On Windows, this ensures the correct linking of the C standard library.

```bash
gcc test.s -o test.exe

```

### 3. Run the Program

Execute your binary to see the results.

```bash
./test.exe

```

---

## Technical Implementation Details

### Stack Alignment

To maintain compatibility with the Windows x64 calling convention, the compiler ensures the stack is **16-byte aligned** before every function call. It provides the necessary **32-byte "Shadow Space"** required for calling external functions like `printf`.

### Switch Statement Logic

The `switch` implementation utilizes a "Discriminant-on-Stack" strategy:

1. The discriminant is evaluated and pushed to the stack.
2. Each `case` expression is evaluated individually.
3. The value is compared against the stack-stored discriminant, allowing for complex, non-static case tests.

### File Encoding

The compiler explicitly writes output in **UTF-8** with standard **LF (`\n`)** line endings. This prevents encoding errors (like UTF-16 BOM) that typically cause assembler failures in the GNU toolchain.
