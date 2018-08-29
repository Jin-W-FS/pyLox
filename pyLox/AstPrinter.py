import Expr
from Scanner import *

class LispPrinter(Expr.Visitor):
    def visitBinaryExpr(self, expr):
        return '({} {} {})'.format(expr.operator, self.visit(expr.left), self.visit(expr.right))
    def visitGroupingExpr(self, expr):
        return '(group {})'.format(self.visit(expr.expression))
    def visitLiteralExpr(self, expr):
        return str(expr.value)
    def visitUnaryExpr(self, expr):
        return '({} {})'.format(expr.operator, self.visit(expr.right))

class RevPolPrinter(Expr.Visitor):
    def visitBinaryExpr(self, expr):
        return '{1} {2} {0}'.format(expr.operator, self.visit(expr.left), self.visit(expr.right))
    def visitGroupingExpr(self, expr):
        return '{} group'.format(self.visit(expr.expression))
    def visitLiteralExpr(self, expr):
        return str(expr.value)
    def visitUnaryExpr(self, expr):
        return '{1} {0}'.format(expr.operator, self.visit(expr.right))

def _test():
    ast = Expr.Binary(
        Expr.Unary(                                    
            Token(TokenType.MINUS, "-", None, 1),
            Expr.Literal(123)),
        Token(TokenType.STAR, "*", None, 1),
        Expr.Grouping(
            Expr.Literal(45.67)));
    print(LispPrinter().visit(ast))

if __name__ == "__main__":
    _test()