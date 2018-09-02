
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