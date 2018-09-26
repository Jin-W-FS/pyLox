from contextlib import contextmanager
import Expr
from Scanner import *
from LoxError import *
from Functions import *


class Resolver(Expr.Visitor):
    """resolve variables"""
    def __init__(self):
        self.globalEnv = { k : True for k in lox_builtins }
        self.envs = [self.globalEnv]
        self.ids = {}
        self.errors = []
        self.currentLoop = self.currentFunction = 0

    @contextmanager
    def subEnv(self, initial=None):
        env = dict()
        if initial is not None: env.update(initial)
        self.envs.append(env)
        try:
            yield
        finally:
            self.envs.pop()

    def defineVar(self, name, inited=False, check=True):
        env = self.envs[-1]
        if check and name.lexeme in env:
            raise ResolveError(name.line, "duplicated declaration of var {}".format(name.lexeme))
        env[name.lexeme] = inited

    def resolveGet(self, name):
        for i, env in enumerate(reversed(self.envs)):
            if name.lexeme in env:
                if not env[name.lexeme]:
                    raise ResolveError(name.line, "var {} used without being initialized".format(name.lexeme))
                return -1 if env == self.globalEnv else i
        raise ResolveError(name.line, "var {} used without being defined".format(name.lexeme))

    def resolveSet(self, name):
        for i, env in enumerate(reversed(self.envs)):
            if name.lexeme in env:
                env[name.lexeme] = True
                return -1 if env == self.globalEnv else i
        raise ResolveError(name.line, "var {} used without being defined".format(name.lexeme))

    def resolve(self, ast):
        self.errors = []
        self.visit(ast)
        return self.ids, self.errors # return ids and errors

    def visitProgram(self, prog):
        for stmt in prog:
            try:
                self.visit(stmt)
            except LoxError as ex:
                self.errors.append(ex)

    def visitScopeStmt(self, stmt):
        with self.subEnv():
            self.visitProgram(stmt)

    def visitVarStmt(self, stmt):
        self.defineVar(stmt.name)
        if stmt.initial is not None:
            self.visit(stmt.initial)
            self.resolveSet(stmt.name)

    def visitFuncStmt(self, stmt, isMethod=False):
        if stmt.name:
            self.defineVar(stmt.name, inited=True, check=False)
        with self.subEnv(initial={'this':True}):
            for p in stmt.params: self.defineVar(p, inited=True)
            self.currentFunction += 1
            self.visitProgram(stmt.block)
            self.currentFunction -= 1

    def visitClassStmt(self, stmt):
        self.defineVar(stmt.name, inited=False, check=False)
        if stmt.parent:
            self.ids[stmt.parent] = self.resolveGet(stmt.parent)
        self.resolveSet(stmt.name)
        with self.subEnv(initial={ 'super' : True }):
            for method in stmt.members:
                self.visitFuncStmt(method, isMethod=True)

    def visitAttribExpr(self, expr):
        self.visit(expr.object)
        # for now, we know nothing about expr.attribute

    def visitIdentifierExpr(self, expr):
        tok = expr.value
        self.ids[tok] = self.resolveGet(tok)
        return

    def _visitAssignExpr(self, expr):
        if isinstance(expr.left, Expr.Identifier):
            self.visit(expr.right)
            tok = expr.left.value
            self.ids[tok] = self.resolveSet(tok)
        elif isinstance(expr.left, Expr.Attrib):
            self.visit(expr.left)
            self.visit(expr.right)
        else:
            raise ResolveError(expr.operator.line, "left value required before operator {}".format(expr.operator))

    def visitPrintStmt(self, stmt):
        self.visit(stmt.expr)

    def visitExprStmt(self, stmt):
        self.visit(stmt.expr)

    def visitIfStmt(self, stmt):
        self.visit(stmt.condition)
        self.visit(stmt.then_branch)
        if stmt.else_branch: self.visit(stmt.else_branch)

    def visitWhileStmt(self, stmt):
        self.visit(stmt.condition)
        self.currentLoop += 1
        self.visit(stmt.loop)
        if stmt.iteration: self.visit(stmt.iteration)
        self.currentLoop -= 1

    def visitFlowStmt(self, stmt):
        if stmt.type.type == TokenType.RETURN:
           if not self.currentFunction:
               raise ResolveError(stmt.type.line, "{} should be in a function".format(stmt.type.lexeme))
        else:
           if not self.currentLoop:
               raise ResolveError(stmt.type.line, "{} should be in a loop".format(stmt.type.lexeme))
        if stmt.value: self.visit(stmt.value)

    def visitBinaryExpr(self, expr):
        if expr.operator.type == TokenType.EQUAL:
            return self._visitAssignExpr(expr)
        self.visit(expr.left)
        self.visit(expr.right)

    def visitGroupingExpr(self, expr):
        self.visit(expr.expression)

    def visitLiteralExpr(self, expr):
        return

    def visitUnaryExpr(self, expr):
        self.visit(expr.right)

    def visitCallExpr(self, expr):
        self.visit(expr.callee)
        for v in expr.args:  self.visit(v) 
