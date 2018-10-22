

class Environment:
    """Local env class"""
    def __init__(self, parent=None, initial=None):
        self.vars = []
        if initial:
           for k, v in initial:
               self.vars.append([k, v])
        self.parent = parent

    def update(self, dic, **kw):
        self.vars.update(dic, **kw)

    def _lookup(self, name):
        for i, (k, v) in enumerate(self.vars):
            if k == name: return i
        return -1

    def define(self, name):
        if self._lookup(name) >= 0: return False
        self.vars.append([name, None])
        return True

    def lookupEnv(self, name, raiseError=True, depth=None):
        env = self
        if depth is None:
            while env:
                if env._lookup(name) >= 0: return env
                env = env.parent
            if raiseError: raise KeyError(name)
            return None
        else:
            for i in range(depth):
                env = env.parent
                if not env: raise KeyError(name)
            if raiseError: assert(env._lookup(name) >= 0)
            return env

    def defined(self, name, depth=None):
        env = self.lookupEnv(name, raiseError=False, depth=depth)
        return env and env._lookup(name) >= 0

    def assign(self, name, value, depth=None):
        env = self.lookupEnv(name, depth=depth)
        idx = env._lookup(name)
        assert(env.vars[idx][0] == name)
        env.vars[idx][1] = value
        return value

    def value(self, name, depth=None):
        env = self.lookupEnv(name, depth=depth)
        idx = env._lookup(name)
        assert(env.vars[idx][0] == name)
        return env.vars[idx][1]
