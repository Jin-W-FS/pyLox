

class Environment:
    """description of class"""
    def __init__(self, parent=None, initial=None):
        self.vars = initial or {}
        self.parent = parent

    def update(self, dic, **kw):
        self.vars.update(dic, **kw)

    def define(self, name):
        if name in self.vars: return False
        self.vars[name] = None
        return True

    def lookupEnv(self, name, raiseError=True, depth=None):
        env = self
        if depth is None:
            while env:
                if name in env.vars: return env
                env = env.parent
            if raiseError: raise KeyError(name)
            return None
        else:
            for i in range(depth):
                env = env.parent
                if not env: raise KeyError(name)
            if raiseError: assert(name in env.vars)
            return env

    def defined(self, name, depth=None):
        env = self.lookupEnv(name, raiseError=False, depth=depth)
        return env and name in env.vars

    def assign(self, name, value, depth=None):
        env = self.lookupEnv(name, depth=depth)
        env.vars[name] = value
        return value

    def value(self, name, depth=None):
        env = self.lookupEnv(name, depth=depth)
        return env.vars[name]

    def delete(self, name, depth=None):
        env = self.lookupEnv(name, depth=depth)
        del env.vars[name]
