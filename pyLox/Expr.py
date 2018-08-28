from collections import namedtuple

class Visitor:
    def visit(self, expr):
        return expr.accept(self)
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