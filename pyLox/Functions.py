
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
    str         : (lambda v: repr(v)),
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

lox_builtin_functions = {
    'printf' : loxfn_printf,
    'typeof' : loxfn_typeof,
    'clock'  : loxfn_clock,
}

# user defined funtions
class LoxFunc:
    ANONYMOUS = '<anonymous>'
    def __init__(self, stmt, env=None):
        self.name = stmt.name.lexeme if stmt.name else LoxFunc.ANONYMOUS
        self.params = [ p.lexeme for p in stmt.params ]
        self.block = stmt.block
        self.env = env
    def __str__(self):
        return '<function {}>'.format(self.name)
    def __call__(self, interp, args):
        checkArity(self.name, len(self.params), args)
        binding = { k : v for k, v in zip(self.params, args) }
        with interp.subEnv(env=self.env, initial=binding):
            return interp.visitProgram(self.block)
