
class LoxError(RuntimeError):
    def __init__(self, line, message):
        super().__init__(line, message)
    def __str__(self):
        line, message = self.args
        return '[line %d] Error: %s' % (line, message)

class ParserError(LoxError):
    pass

class InterpError(LoxError):
    pass