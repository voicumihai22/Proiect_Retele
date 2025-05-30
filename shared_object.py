class SharedObject:
    def _init_(self, data):
        self.data = data

    def _str_(self):
        return f"SharedObject: {self.data}"
