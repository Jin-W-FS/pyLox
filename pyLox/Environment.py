

class Environment:
    """description of class"""
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def define(self, name):
        if name in self.vars: return False
        self.vars[name] = None
        return True

    def lookupEnv(self, name, raiseError=True):
        env = self
        while env:
            if name in env.vars: return env
            env = env.parent
        if raiseError: raise KeyError(name)
        return None

    def defined(self, name):
        env = self.lookupEnv(name, raiseError=False)
        return env is not None

    def assign(self, name, value):
        env = self.lookupEnv(name)
        env.vars[name] = value
        return value

    def value(self, name):
        env = self.lookupEnv(name)
        return env.vars[name]

    def delete(self, name):
        env = self.lookupEnv(name)
        del env.vars[name]
