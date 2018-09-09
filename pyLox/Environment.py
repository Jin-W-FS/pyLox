

class Environment:
    """description of class"""
    def __init__(self):
        self.vars = {}
    def defined(self, name):
        return name in self.vars
    def define(self, name):
        if self.defined(name): return False
        self.vars[name] = None
        return True
    def assign(self, name, value):
        self.vars[name] = value
        return value
    def value(self, name):
        return self.vars[name]
    def delete(self, name):
        del self.vars[name]
