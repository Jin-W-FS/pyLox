import Expr
from Scanner import *
from LoxError import *

class Interpreter(Expr.Visitor):

    def visitBinaryExpr(self, expr):
        tl, tr, fn = self.BinFns[expr.operator.type]
        return fn(tl(self, expr.left), tr(self, expr.right))

    def visitGroupingExpr(self, expr):
        return self.visit(expr.expression)

    def visitUnaryExpr(self, expr):
        if expr.operator.type == TokenType.MINUS:
            return - self.Double(expr.right)
        if expr.operator.type == TokenType.BANG:
            return not self.Boolean(expr.right)

    def visitLiteralExpr(self, expr):
        tok = expr.value
        if tok.type in (TokenType.TRUE, TokenType.FALSE):
            return tok.type == TokenType.TRUE
        if tok.type in (TokenType.STRING, TokenType.NUMBER, TokenType.NIL):
            return tok.literal
        raise InterpError(tok.line, "unsupported literal {}".format(repr(tok)))

    def Any(self, expr):
        return self.visit(expr)

    def Boolean(self, expr):
        v = self.visit(expr)
        if v == None: return False
        if isinstance(v, bool): return v
        if isinstance(v, float): return v != 0
        raise InterpError(expr[0].line, "cannot eval to Boolean: {}".format(repr(v)))

    def Number(self, expr):
        v = self.visit(expr)
        if isinstance(v, float): return v
        if isinstance(v, bool): return float(v)
        raise InterpError(expr[0].line, 'cannot eval to Number: {}'.format(repr(v)))

    def String(self, expr):
        v = self.visit(expr)
        if isinstance(val, str): return v 
        raise InterpError(expr[0].line, 'cannot eval to String: {}'.format(repr(v)))

Interpreter.BinFns = {
    TokenType.EQUAL_EQUAL   :   (Interpreter.Any, Interpreter.Any, lambda l, r: l == r),
    TokenType.BANG_EQUAL    :   (Interpreter.Any, Interpreter.Any, lambda l, r: l != r),
    TokenType.GREATER       :   (Interpreter.Number, Interpreter.Number, lambda l, r: l > r),
    TokenType.GREATER_EQUAL :   (Interpreter.Number, Interpreter.Number, lambda l, r: l >= r),
    TokenType.LESS          :   (Interpreter.Number, Interpreter.Number, lambda l, r: l < r),
    TokenType.LESS_EQUAL    :   (Interpreter.Number, Interpreter.Number, lambda l, r: l <= r),
    TokenType.MINUS         :   (Interpreter.Number, Interpreter.Number, lambda l, r: l - r),
    TokenType.PLUS          :   (Interpreter.Number, Interpreter.Number, lambda l, r: l + r),
    TokenType.SLASH         :   (Interpreter.Number, Interpreter.Number, lambda l, r: l / r),
    TokenType.STAR          :   (Interpreter.Number, Interpreter.Number, lambda l, r: l * r),
}
