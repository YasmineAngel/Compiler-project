class LabelManager:
    def __init__(self):
        self.counter = 0

    def new_label(self, prefix="L"):
        label = f".{prefix}{self.counter}"
        self.counter += 1
        return label