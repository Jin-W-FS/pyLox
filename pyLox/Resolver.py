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

    @contextmanager
    def subEnv(self, initial=None):
        env = dict()
        if initial is not None: env.update(initial)
        self.envs.append(env)
        try:
            yield
        finally:
            self.envs.pop()

    def defineVar(self, name, inited = False, check=True):
        env = self.envs[-1]
        if check and name.lexeme in env:
            raise ResolverError(name.line, "duplicated declaration of var {}".format(name.lexeme))
        env[name.lexeme] = inited

    def resolveGet(self, name):
        for i, env in enumerate(reversed(self.envs)):
            if name.lexeme in env:
                if not env[name.lexeme]:
                    raise ResolverError(name.line, "var {} used without being initialized".format(name.lexeme))
                return -1 if env == self.globalEnv else i
        raise ResolverError(name.line, "var {} used without being defined".format(name.lexeme))

    def resolveSet(self, name):
        for i, env in enumerate(reversed(self.envs)):
            if name.lexeme in env:
                env[name.lexeme] = True
                return -1 if env == self.globalEnv else i
        raise ResolverError(name.line, "var {} used without being defined".format(name.lexeme))

    def resolve(self, ast):
        old, self.ids = self.ids, {}
        self.visit(ast)
        self.ids, new = old, self.ids
        self.ids.update(new)
        return new # return newly updated ids

    def visitProgram(self, prog):
        for stmt in prog:
            self.visit(stmt)

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
        params = { p.lexeme:True for p in stmt.params }
        if isMethod: params['this'] = True
        with self.subEnv(initial=params):
            self.visitProgram(stmt.block)

    def visitClassStmt(self, stmt):
        self.defineVar(stmt.name, inited=True, check=False)
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
            raise ResolverError(expr.operator.line, "left value required before operator {}".format(expr.operator))

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
        self.visit(stmt.loop)
        if stmt.iteration: self.visit(stmt.iteration)

    def visitFlowStmt(self, stmt):
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
