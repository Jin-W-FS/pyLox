
'''helpers and buildin functions for Interpreter'''

from LoxError import *

def stringify(v):
    'parse interpreter value to string as in Lox program'
    fn = __stringify_fns.get(type(v))
    if not fn: return str(v)
    return fn(v)

__stringify_fns = {
    type(None)  : (lambda v: 'nil'),
    type(stringify) : (lambda v: '<buildin {}>'.format(v.__name__.split('loxfn_', 2)[-1])),
    bool        : (lambda v: str(v).lower()),
    float       : (lambda v: str(v).split('.0', 2)[0]),
    str         : (lambda v: v),
}

def checkArity(name, n, args):
    if len(args) != n:
        raise LoxFuncArgc(0, 'funcion {} takes {} args, got {}'.format(name, n, len(args)))

# buildin functions
def loxfn_printf(interp, args):
    if len(args) < 1:
        checkArity('printf', '>1', args)    # hack: len(args) != '>1' is always true
    fmt, arg = args[0], tuple(args[1:])
    print(fmt % arg, end='', flush=True)

def loxfn_typeof(interp, args):
    checkArity('typeof', 1, args)
    typenames = {
        bool  : 'Boolean',
        float : 'Number',
        str   : 'String',
    }
    tp = type(args[0])
    return typenames.get(tp, tp.__name__)

def loxfn_clock(interp, args):
    checkArity('clock', 0, args)
    from time import time
    return time()

# user defined funtions
class LoxFunc:
    ANONYMOUS = '<anonymous>'
    def __init__(self, stmt, env=None):
        self.name = stmt.name.lexeme if stmt.name else LoxFunc.ANONYMOUS
        self.params = [ p.lexeme for p in stmt.params ]
        self.block = stmt.block
        self.env = env  # closure
    def __str__(self):
        return '<function {}>'.format(self.name)
    def __call__(self, interp, args, **kw):
        checkArity(self.name, len(self.params), args)
        binding = { k : v for k, v in zip(self.params, args) }
        binding.update(kw)
        with interp.subEnv(env=self.env, initial=binding):
            return interp.visitProgram(self.block)

class LoxMethod:
    def __init__(self, obj, func):
        self.obj, self.func = obj, func
    def __str__(self):
        return '<method {} of {}>'.format(self.func.name, self.obj.cls.name)
    def __call__(self, interp, args):
        return self.func(interp, args, this=self.obj, super=self.obj.super())

# user defined classes
class LoxClass:
    def __init__(self, stmt, env):
        if stmt is None:    # super base class: Object
            self.name, self.parent, self.methods = 'Object', None, {}
            return
        self.name = stmt.name.lexeme
        self.parent = env.value(stmt.parent.lexeme) if stmt.parent else LoxCls_Object
        self.methods = { func.name.lexeme : LoxFunc(func, env) for func in stmt.members }
    def __str__(self):
        return '<class {}>'.format(self.name)
    def __call__(self, interp, args):
        object = LoxInstance(self)
        object.getattr('init', default=(lambda *args: None))(interp, args)
        return object
    def getattr(self, name):
        fn = self.methods.get(name)
        if not fn and self.parent:
            fn = self.parent.getattr(name)
        return fn

LoxCls_Object = LoxClass(None, None)

class LoxInstance:
    def __init__(self, cls, attr=None):
        self.cls = cls
        self.attr = attr if attr is not None else {}
    def __str__(self):
        return '<instance of class {}>'.format(self.cls.name)
    def super(self):
        'shift self to a super class object'
        return LoxInstance(self.cls.parent, self.attr)
    def getattr(self, name, default=KeyError):
        # 1) obj.attr
        if name in self.attr: return self.attr[name]
        # 2) cls.method
        fn = self.cls.getattr(name)
        if fn: return LoxMethod(self, fn)
        # 3) default value
        if default != KeyError: return default
        # 4) report error
        raise KeyError(name)
    def setattr(self, name, value):
        self.attr[name] = value
    def hasattr(self, name):
        try:
            self.getattr(name)
            return True
        except KeyError:
            return False

# buildins
lox_builtins = {
    'printf' : loxfn_printf,
    'typeof' : loxfn_typeof,
    'clock'  : loxfn_clock,
    'Object' : LoxCls_Object,
}
