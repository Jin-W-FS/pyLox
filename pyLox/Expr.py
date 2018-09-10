from collections import namedtuple


class Visitor:
    def visit(self, obj):
        return obj.accept(self)
    def visitProgram(self, prog):
        pass
    def visitScopeStmt(self, prog):
        pass
    def visitPrintStmt(self, stmt):
        pass
    def visitExprStmt(self, stmt):
        pass
    def visitVarStmt(self, stmt):
        pass
    def visitBinaryExpr(self, expr):
        pass
    def visitGroupingExpr(self, expr):
        pass
    def visitLiteralExpr(self, expr):
        pass
    def visitUnaryExpr(self, expr):
        pass

class Binary(namedtuple("Binary", "left, operator, right")):
    def accept(self, visitor):
        return visitor.visitBinaryExpr(self)

class Grouping(namedtuple("Grouping", "expression")):
    def accept(self, visitor):
        return visitor.visitGroupingExpr(self)

class Literal(namedtuple("Literal", "value")):
    def accept(self, visitor):
        return visitor.visitLiteralExpr(self)

class Unary(namedtuple("Unary", "operator, right")):
    def accept(self, visitor):
        return visitor.visitUnaryExpr(self)


# Statements:

class PrintStmt(namedtuple("PrintStmt", "expr")):
    def accept(self, visitor):
        return visitor.visitPrintStmt(self)

class ExprStmt(namedtuple("ExprStmt", "expr")):
    def accept(self, visitor):
        return visitor.visitExprStmt(self)

class VarStmt(namedtuple("VarStmt", "name, initial")):
    def accept(self, visitor):
        return visitor.visitVarStmt(self)

class ScopeStmt(list):
    def accept(self, visitor):
        return visitor.visitScopeStmt(self)

class Program(list):
    def accept(self, visitor):
        return visitor.visitProgram(self)
