from contextlib import contextmanager
import Expr
from Scanner import *
from LoxError import *
from StackVM import StackVM

class Compiler(Expr.Visitor):
    """description of class"""
    def __init__(self):
        super().__init__()
        self.code = bytearray()
        self.data = []

    def append(self, op, opd=None):
        pc = self.pc
        self.code.append(op)
        if opd is not None:
            self.code.extend(self.operand(opd))
        return pc

    def operand(self, opd):
        return [opd & 0xff, (opd >> 8) & 0xff]

    def filljmp(self, ins, target=None):
        if target is None: target = self.pc
        dist = target - (ins + 3)
        v = self.operand(dist)
        self.code[ins+1] = v[0]
        self.code[ins+2] = v[1]

    @property
    def pc(self):
        return len(self.code)

    def compile(self, prog):
        self.visit(prog)

    def visitProgram(self, prog):
        for stmt in prog:
            self.visit(stmt)

    def visitScopeStmt(self, stmt):
        self.visitProgram(stmt)

    def visitPrintStmt(self, stmt):
        self.visit(stmt.expr)
        self.append(StackVM.PRINT)

    def visitAssertStmt(self, stmt):
        pass

    def visitExprStmt(self, stmt):
        self.visit(stmt.expr)
        if stmt.semicolon: self.append(StackVM.POP)

    def visitVarStmt(self, stmt):
        self.data.append(stmt.name.lexeme)
        if stmt.initial:
            pos = len(self.data) - 1
            self.visit(stmt.initial)
            self.append(StackVM.SAVE, pos)

    def visitFuncStmt(self, stmt):
        pass

    def visitClassStmt(self, stmt):
        pass

    def visitIfStmt(self, stmt):
        self.visit(stmt.condition)
        cond = self.append(StackVM.JZ, 0)
        self.visit(stmt.then_branch)
        if not stmt.else_branch:
            self.filljmp(cond)
        else:
            end = self.append(StackVM.JMP, 0)
            self.filljmp(cond)
            self.visit(stmt.else_branch)
            self.filljmp(end)

    def visitWhileStmt(self, stmt):
        before = self.pc
        self.visit(stmt.condition)
        cond = self.append(StackVM.JNZ, 0)
        self.visitProgram(stmt.loop)
        if stmt.iteration:
            self.visit(stmt.iteration)
        self.append(StackVM.JMP, before - (self.pc + 3))
        self.filljmp(cond)

    def visitFlowStmt(self, stmt):
        pass

    def visitBinaryExpr(self, expr):
        if expr.operator.type == TokenType.EQUAL:
            return self._visitAssignExpr(expr)

        opmap = {
            TokenType.EQUAL_EQUAL   :   StackVM.EQUAL,
            TokenType.BANG_EQUAL    :   StackVM.NOT_EQUAL,
            TokenType.GREATER       :   StackVM.GREATER,
            TokenType.GREATER_EQUAL :   StackVM.GREATER_EQUAL,
            TokenType.LESS          :   StackVM.LESS,
            TokenType.LESS_EQUAL    :   StackVM.LESS_EQUAL,
            TokenType.MINUS         :   StackVM.MINUS,
            TokenType.PLUS          :   StackVM.PLUS,
            TokenType.SLASH         :   StackVM.DIVIDE,
            TokenType.STAR          :   StackVM.MULTIPLY,
        }
        op = opmap[expr.operator.type]
        self.visit(expr.left)
        self.visit(expr.right)
        self.append(op)

    def _visitAssignExpr(self, expr):
        if isinstance(expr.left, Expr.Identifier):
            name = expr.left.value
            idx = self.data.index(name.lexeme)
            self.visit(expr.right)
            self.append(StackVM.DUP)
            self.append(StackVM.SAVE, idx)

    def visitGroupingExpr(self, expr):
        self.visit(expr.expression)

    def visitLiteralExpr(self, expr):
        try:
            idx = self.data.index(expr.value.literal)
        except ValueError:
            self.data.append(expr.value.literal)
            idx = len(self.data) - 1
        self.append(StackVM.LOAD, idx)

    def visitIdentifierExpr(self, expr):
        idx = self.data.index(expr.value.lexeme)
        self.append(StackVM.LOAD, idx)

    def visitAttribExpr(self, expr):
        pass

    def visitUnaryExpr(self, expr):
        opmap = {
            TokenType.BANG  : StackVM.NOT,
            TokenType.MINUS : StackVM.NEGATIVE,
        }
        op = opmap[expr.operator.type]
        self.visit(expr.right)
        self.append(op)

    def visitCallExpr(self, expr):
        pass


