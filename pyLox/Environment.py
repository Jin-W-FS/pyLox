
class KVList(list):
    def append(self, kv):
        super().append(list(kv))
    def extend(self, kvs):
        super().extend([k, v] for k, v in kvs)
    def lookup(self, key):
        for i, (k, v) in enumerate(self):
            if k == key: return i
        return -1
    def index(self, key):
        i = self.lookup(key)
        if i < 0: raise KeyError(key)
        return i
    def __setitem__(self, k, v):
        # indexed
        if isinstance(k, int):
            super().__getitem__[k][1] = v
            return
        # else:
        try:
            self[self.index(k)][1] = v
        except KeyError:
            self.append([k, v])
    def __getitem__(self, k):
        # indexed
        if isinstance(k, int):
            return super().__getitem__(k)
        # else:
        return self[self.index(k)]


class Environment:
    """Local env class"""
    def __init__(self, parent=None, initial=None):
        self.vars = KVList()
        if initial: self.vars.extend(initial)
        self.parent = parent

    def define(self, name):
        if self.vars.lookup(name) >= 0: return False    # redefine
        self.vars.append([name, None])
        return True

    def lookup(self, name, depth=None):
        '''lookup [name, ?] at (optionally) depth'''
        env = self
        if depth is None:
            while env:
                try:
                    return env.vars[name]
                except KeyError:
                    env = env.parent
            raise KeyError(name)
        # else
        if isinstance(depth, int):
            depth, idx = depth, None
        else:
            depth, idx = depth
        for i in range(depth):
            env = env.parent
            assert(env is not None)
        if idx is None:
            return env.vars[name]
        else:
            kv = env.vars[idx]
            assert(kv[0] == name)
            return kv

    def defined(self, name, depth=None):
        try:
            if self.lookup(name, depth=depth): return True
        except KeyError:
            pass
        return False

    def assign(self, name, value, depth=None):
        self.lookup(name, depth=depth)[1] = value

    def value(self, name, depth=None):
        return self.lookup(name, depth=depth)[1]
