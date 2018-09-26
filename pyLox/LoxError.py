
class LoxError(RuntimeError):
    def __init__(self, line, message):
        super().__init__(line, message)
    def __str__(self):
        line, message = self.args
        if line is not None:
            return '[line %d] %s: %s' % (line, self.__class__.__name__, message)
        else:
            return '%s: %s' % (self.__class__.__name__, message)

class ParserError(LoxError):
    pass

class InterpError(LoxError):
    pass

class ResolveError(LoxError):
    pass

class RunningError(LoxError):
    pass

class LoxFuncArgc(RunningError):
    pass

class LoxFlowCtrl(RunningError):
    def __init__(self, token, ret=None):
        self.type = token.type
        self.ret = ret
        super().__init__(token.line, 'unexpected {} statement'.format(token.lexeme))
