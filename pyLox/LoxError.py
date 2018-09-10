
class LoxError(RuntimeError):
    def __init__(self, line, message):
        super().__init__(line, message)
    def __str__(self):
        line, message = self.args
        if line is not None:
            return '[line %d] Error: %s' % (line, message)
        else:
            return 'Error: %s' % (message)

class ParserError(LoxError):
    pass

class InterpError(LoxError):
    pass

class RunningError(LoxError):
    pass

class LoxFlowCtrl(RunningError):
    def __init__(self, token):
        self.type = token.type
        super().__init__(token.line, 'unexpected {} statement'.format(token.lexeme))
