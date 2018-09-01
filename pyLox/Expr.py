from collections import namedtuple

class Visitor:
    def visit(self, obj):
        return obj.accept(self)
    def visitProgram(self, prog):
        pass
    def visitPrintStmt(self, stmt):
        pass
    def visitExprStmt(self, stmt):
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
    def accept(self, visitor):
        return visitor.visitGroupingExpr(self)


# Statements:

class PrintStmt(namedtuple("Print", "expr")):
    def accept(self, visitor):
        return visitor.visitPrintStmt(self)

class ExprStmt(namedtuple("Expr", "expr")):
    def accept(self, visitor):
        return visitor.visitExprStmt(self)

class Program(list):
    def accept(self, visitor):
        return visitor.visitProgram(self)
