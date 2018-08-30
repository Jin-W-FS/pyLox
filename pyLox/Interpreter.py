import Expr
from Scanner import *
from LoxError import *

class Interpreter(Expr.Visitor):
    BinFns = {
        TokenType.EQUAL_EQUAL   :   (lambda l, r: l == r),
        TokenType.BANG_EQUAL    :   (lambda l, r: l != r),
        TokenType.GREATER       :   (lambda l, r: l > r),
        TokenType.GREATER_EQUAL :   (lambda l, r: l >= r),
        TokenType.LESS          :   (lambda l, r: l < r),
        TokenType.LESS_EQUAL    :   (lambda l, r: l <= r),
        TokenType.MINUS         :   (lambda l, r: l - r),
        TokenType.PLUS          :   (lambda l, r: l + r),
        TokenType.SLASH         :   (lambda l, r: l / r),
        TokenType.STAR          :   (lambda l, r: l * r),
    }
    def visitBinaryExpr(self, expr):
        fn = self.BinFns[expr.operator.type]
        return fn(self.visit(expr.left), self.visit(expr.right))
    def visitGroupingExpr(self, expr):
        return self.visit(expr.expression)
    def visitUnaryExpr(self, expr):
        if expr.operator.type == TokenType.MINUS:
            return - self.visit(expr.right)
        if expr.operator.type == TokenType.BANG:
            return not self.visit(expr.right)
    def visitLiteralExpr(self, expr):
        if expr.value.type in (TokenType.TRUE, TokenType.FALSE):
           return expr.value.type == TokenType.TRUE
        if expr.value.type in (TokenType.STRING, TokenType.NUMBER, TokenType.NIL):
            return expr.value.literal
        raise LoxError(expr.value.line, "unsupported literal type {}".format(repr(expr.value)))
