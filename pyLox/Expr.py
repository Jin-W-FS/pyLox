from collections import namedtuple


class Visitor:
    def visit(self, obj):
        return obj.accept(self)
    def visitProgram(self, prog):
        pass
    def visitScopeStmt(self, stmt):
        pass
    def visitPrintStmt(self, stmt):
        pass
    def visitAssertStmt(self, stmt):
        pass
    def visitExprStmt(self, stmt):
        pass
    def visitVarStmt(self, stmt):
        pass
    def visitFuncStmt(self, stmt):
        pass
    def visitClassStmt(self, stmt):
        pass
    def visitIfStmt(self, stmt):
        pass
    def visitWhileStmt(self, stmt):
        pass
    def visitFlowStmt(self, stmt):
        pass
    def visitBinaryExpr(self, expr):
        pass
    def visitGroupingExpr(self, expr):
        pass
    def visitLiteralExpr(self, expr):
        pass
    def visitIdentifierExpr(self, expr):
        pass
    def visitAttribExpr(self, expr):
        pass
    def visitUnaryExpr(self, expr):
        pass
    def visitCallExpr(self, expr):
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

class Identifier(namedtuple("Identifier", "value")):
    def accept(self, visitor):
        return visitor.visitIdentifierExpr(self)

class Attrib(namedtuple("Attrib", "object, dot, attribute")):
    def accept(self, visitor):
        return visitor.visitAttribExpr(self)

class Unary(namedtuple("Unary", "operator, right")):
    def accept(self, visitor):
        return visitor.visitUnaryExpr(self)

class Call(namedtuple("Call", "callee, paran, args")):
    def accept(self, visitor):
        return visitor.visitCallExpr(self)


# Statements:

class PrintStmt(namedtuple("PrintStmt", "expr")):
    def accept(self, visitor):
        return visitor.visitPrintStmt(self)

class AssertStmt(namedtuple("AssertStmt", "op, expr")):
    def accept(self, visitor):
        return visitor.visitAssertStmt(self)

class ExprStmt(namedtuple("ExprStmt", "expr, semicolon")):
    def accept(self, visitor):
        return visitor.visitExprStmt(self)

class VarStmt(namedtuple("VarStmt", "name, initial")):
    def accept(self, visitor):
        return visitor.visitVarStmt(self)

class FuncStmt(namedtuple("FuncStmt", "name, params, block")):
    def accept(self, visitor):
        return visitor.visitFuncStmt(self)

class ClassStmt(namedtuple("ClassStmt", "name, parent, members")):
    def accept(self, visitor):
        return visitor.visitClassStmt(self)

class IfStmt(namedtuple("IfStmt", "condition, then_branch, else_branch")):
    def accept(self, visitor):
        return visitor.visitIfStmt(self)

class WhileStmt(namedtuple("WhileStmt", "condition, loop, iteration")):
    def accept(self, visitor):
        return visitor.visitWhileStmt(self)

class FlowStmt(namedtuple("FlowStmt", "type, value")):
    def accept(self, visitor):
        return visitor.visitFlowStmt(self)

class ScopeStmt(list):
    def accept(self, visitor):
        return visitor.visitScopeStmt(self)

class Program(list):
    def accept(self, visitor):
        return visitor.visitProgram(self)