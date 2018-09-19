from contextlib import contextmanager
import Expr
from Scanner import *

class LispPrinter(Expr.Visitor):
    def __init__(self, file=None):
        super().__init__()
        self.file = file
        self.indent = 0
        self.linend = True

    def print(self, string):
        indent = ' ' * (2 * self.indent * self.linend)
        print(indent, string, sep='', end='', file=self.file)
        self.linend = (string[-1] == '\n')  # next print need indent

    def printProgram(self, prog):
        self.visit(prog)
        self.print('\n')

    @contextmanager
    def incIndent(self, n=1):
        self.indent += n
        yield
        self.indent -= n

    def visitProgram(self, prog):
        for i, stmt in enumerate(prog):
            if i != 0: self.print('\n')
            self.visit(stmt)
    def visitScopeStmt(self, stmt):
        self.print('(prog\n')
        with self.incIndent():
            self.visitProgram(stmt)
        self.print(')')
    def visitPrintStmt(self, stmt):
        self.print('(print ')
        self.visit(stmt.expr)
        self.print(')')
    def visitExprStmt(self, stmt):
        return self.visit(stmt.expr)
    def visitVarStmt(self, stmt):
        self.print('(declvar {}'.format(stmt.name.lexeme))
        if stmt.initial != None:
            self.print(' ')
            self.visit(stmt.initial)
        self.print(')')
    def visitFuncStmt(self, stmt):
        name = 'lambda' if stmt.name is None else 'defun {}'.format(stmt.name.lexeme)
        self.print('({} ({})\n'.format(name, ' '.join(tok.lexeme for tok in stmt.params)))
        with self.incIndent():
            self.visitProgram(stmt.block)
        self.print(')')
    def visitClassStmt(self, stmt):
        if not stmt.parent:
            self.print('(class {}\n'.format(stmt.name.lexeme))
        else:
            self.print('(class {} extends {}\n'.format(stmt.name.lexeme, stmt.parent.lexeme))
        with self.incIndent():
            self.visitProgram(stmt.members)
        self.print(')')
    def visitIfStmt(self, stmt):
        self.print('(if ')
        self.visit(stmt.condition)
        self.print('\n')
        with self.incIndent():
            self.visit(stmt.then_branch)
            if stmt.else_branch:
                self.print('\n')
                self.visit(stmt.else_branch)
        self.print(')')
    def visitWhileStmt(self, stmt):
        self.print('(while ')
        self.visit(stmt.condition)
        self.print('\n')
        with self.incIndent():
            self.visitProgram(stmt.loop)
            if stmt.iteration:
                self.print('\n')
                self.visit(stmt.iteration)
        self.print(')')
    def visitFlowStmt(self, stmt):
        self.print('({}'.format(stmt.type))
        if stmt.value:
            self.print(' ')
            self.visit(stmt.value)
        self.print(')')
    def visitBinaryExpr(self, expr):
        self.print('({} '.format(expr.operator))
        self.visit(expr.left)
        self.print(' ')
        self.visit(expr.right)
        self.print(')')
    def visitGroupingExpr(self, expr):
        self.print('(group ')
        self.visit(expr.expression)
        self.print(')')
    def visitLiteralExpr(self, expr):
        self.print(str(expr.value))
    def visitUnaryExpr(self, expr):
        self.print('({} '.format(expr.operator))
        self.visit(expr.right)
        self.print(')')
    def visitCallExpr(self, expr):
        self.print('(')
        self.visit(expr.callee)
        for v in expr.args:
            self.print(' ')
            self.visit(v)
        self.print(')')

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
