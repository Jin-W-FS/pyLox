import Expr
from Scanner import *

class LispPrinter(Expr.Visitor):
    def visitProgram(self, prog):
        lst = [self.visit(stmt) for stmt in prog]
        return '\n'.join(lst)
    def visitScopeStmt(self, stmt):
        lst = [self.visit(v) for v in stmt]
        if sum(len(s) for s in lst) < 20:
            return '(prog {})'.format(' '.join(lst))
        else:
            return '(prog\n  {})'.format('\n  '.join(lst))
    def visitPrintStmt(self, stmt):
        return '(print {})'.format(self.visit(stmt.expr))
    def visitExprStmt(self, stmt):
        return self.visit(stmt.expr)
    def visitVarStmt(self, stmt):
        if stmt.initial == None:
            return '(declvar {})'.format(stmt.name.lexeme)
        else:
            return '(declvar {} {})'.format(stmt.name.lexeme, self.visit(stmt.initial))
    def visitIfStmt(self, stmt):
        if stmt.else_branch is None:
            return '(if {} {})'.format(self.visit(stmt.condition), self.visit(stmt.then_branch))
        else:
            return '(if {} {} {})'.format(self.visit(stmt.condition), self.visit(stmt.then_branch), self.visit(stmt.else_branch))
    def visitWhileStmt(self, stmt):
        if not stmt.iteration:
            return '(while {} {})'.format(self.visit(stmt.condition), self.visit(stmt.loop))
        else:
            return '(while {} {} {})'.format(self.visit(stmt.condition), self.visit(stmt.loop), self.visit(stmt.iteration))
    def visitBreakStmt(self, stmt):
        return str(stmt.type)
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
