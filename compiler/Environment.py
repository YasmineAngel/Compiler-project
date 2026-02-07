class Environment:
    def __init__(self, start_offset=-8):
        self.variables = {}
        self.current_offset = start_offset

    def declare(self, name):
        """Allocates a new 8-byte slot on the stack."""
        if name not in self.variables:
            self.variables[name] = self.current_offset
            self.current_offset -= 8
        return self.variables[name]

    def get_offset(self, name):
        """Returns the %rbp offset for a variable."""
        return self.variables.get(name)