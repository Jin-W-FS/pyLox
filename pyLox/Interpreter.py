from contextlib import contextmanager
import Expr
from Scanner import *
from LoxError import *
from Functions import *
from Environment import Environment


class InterpType:
    @staticmethod
    def INV(v):
        return InterpType.INV
    @staticmethod
    def Any(v):
        return v
    @staticmethod
    def Boolean(v):
        if v == None: return False
        if isinstance(v, bool): return v
        if isinstance(v, float): return v != 0
        return InterpType.INV
    @staticmethod
    def Number(v):
        if isinstance(v, float): return v
        if isinstance(v, bool): return float(v)
        return InterpType.INV
    @staticmethod
    def Integer(v):
        if isinstance(v, bool): return int(v)
        if isinstance(v, float) and int(v) == v: return int(v)
        return InterpType.INV
    @staticmethod
    def String(v):
        if isinstance(v, str): return v
        return InterpType.INV

class Interpreter(Expr.Visitor):
    BinFns = {
        TokenType.EQUAL_EQUAL   :   [(InterpType.Any, InterpType.Any, lambda l, r: l == r)],
        TokenType.BANG_EQUAL    :   [(InterpType.Any, InterpType.Any, lambda l, r: l != r)],
        TokenType.GREATER       :   [(InterpType.Number, InterpType.Number, lambda l, r: l > r)],
        TokenType.GREATER_EQUAL :   [(InterpType.Number, InterpType.Number, lambda l, r: l >= r)],
        TokenType.LESS          :   [(InterpType.Number, InterpType.Number, lambda l, r: l < r)],
        TokenType.LESS_EQUAL    :   [(InterpType.Number, InterpType.Number, lambda l, r: l <= r)],
        TokenType.MINUS         :   [(InterpType.Number, InterpType.Number, lambda l, r: l - r)],
        TokenType.PLUS          :   [(InterpType.Number, InterpType.Number, lambda l, r: l + r),
                                     (InterpType.String, InterpType.Any, lambda l, r: l + stringify(r)),
                                     (InterpType.Any, InterpType.String, lambda l, r: stringify(l) + r)],
        TokenType.SLASH         :   [(InterpType.Number, InterpType.Number, lambda l, r: l / r)],
        TokenType.STAR          :   [(InterpType.Number, InterpType.Number, lambda l, r: l * r),
                                     (InterpType.String, InterpType.Number, lambda l, r: l * int(r))],
        # dealing and/or operator is different: short circuit rules
        # TokenType.AND           :   [(InterpType.Boolean, InterpType.Boolean, lambda l, r: l and r)],
        # TokenType.OR            :   [(InterpType.Boolean, InterpType.Boolean, lambda l, r: l or r)],
    }
    UniFns = {
        TokenType.MINUS         :   [(InterpType.Number, lambda v: -v)],
        TokenType.BANG          :   [(InterpType.Boolean, lambda v: not v)],
    }
    
    def __init__(self):
        super().__init__()
        self.env = Environment(initial=lox_builtin_functions)

    @contextmanager
    def subEnv(self, env=None, initial=None):
        if env is None: env = self.env
        saved = self.env    # save
        self.env = Environment(env, initial)    # extend
        try:
            yield   # run user code
        finally:
            self.env = saved    # recover

    def visitProgram(self, prog):
        rlt = None
        for stmt in prog:
            rlt = self.visit(stmt)
        return rlt

    def visitScopeStmt(self, stmt):
        with self.subEnv():
            return self.visitProgram(stmt)

    def visitPrintStmt(self, stmt):
        value = self.visit(stmt.expr)
        print(stringify(value))

    def visitExprStmt(self, stmt):
        value = self.visit(stmt.expr)
        return value

    def visitVarStmt(self, stmt):
        name = stmt.name
        if not self.env.define(name.lexeme):
            raise InterpError(name.line, "duplicated declaration of var {}".format(name.lexeme))
        if stmt.initial is not None:
            self.env.assign(name.lexeme, self.visit(stmt.initial))

    def visitFuncStmt(self, stmt):
        func = LoxFunc(stmt, env=self.env)  # lexical scope
        if stmt.name:
            self.env.define(stmt.name.lexeme)    # allow function redefine
            self.env.assign(stmt.name.lexeme, func)
        return func

    def visitIfStmt(self, stmt):
        condition = InterpType.Boolean(self.visit(stmt.condition))
        if condition == InterpType.INV:
            raise InterpError(stmt.condition.line, "if statement requires a boolean condition")
        if condition:
            return self.visit(stmt.then_branch)
        else:
            if stmt.else_branch is not None:
                return self.visit(stmt.else_branch)
        return None

    def visitWhileStmt(self, stmt):
        while True:
            try:
                condition = InterpType.Boolean(self.visit(stmt.condition))
                if condition == InterpType.INV:
                    raise InterpError(stmt.condition.line, "while statement requires a boolean condition")
                if not condition: break
                self.visit(stmt.loop)
            except LoxFlowCtrl as ex:
                if ex.type == TokenType.BREAK:
                    break
                elif ex.type == TokenType.CONTINUE:
                    pass    # goto stmt.iteration
                else:
                    raise ex
            if (stmt.iteration):
                self.visit(stmt.iteration)

    def visitFlowStmt(self, stmt):
        raise LoxFlowCtrl(stmt.type, stmt.value and self.visit(stmt.value))

    def visitBinaryExpr(self, expr):
        if expr.operator.type in (TokenType.EQUAL,):
            return self._visitAssignExpr(expr)
        if expr.operator.type in (TokenType.AND, TokenType.OR):
            return self._visitAndOrExpr(expr)
        left, right = self.visit(expr.left), self.visit(expr.right)
        for tl, tr, fn in self.BinFns[expr.operator.type]:
            l, r = tl(left), tr(right)
            if l == InterpType.INV or r == InterpType.INV: continue
            try:
                return fn(l, r)
            except Exception as ex:
                raise RunningError(expr.operator.line, str(ex))
        else:
            raise InterpError(expr.operator.line, "invalid operand(s) for operator {}".format(expr.operator))

    def _visitAssignExpr(self, expr):
        if not (isinstance(expr.left, Expr.Literal) and expr.left.value.type == TokenType.IDENTIFIER):
            raise InterpError(expr.operator.line, "left value required before operator {}".format(expr.operator))
        name = expr.left.value
        if not self.env.defined(name.lexeme):
            raise InterpError(name.line, "Identifier {} used but not defined".format(expr.operator))
        return self.env.assign(name.lexeme, self.visit(expr.right))

    def _visitAndOrExpr(self, expr):
        shortcircuit = (expr.operator.type == TokenType.OR) # or short-circuited by True, and by False
        for opd in (expr.left, expr.right):
            v = InterpType.Boolean(self.visit(opd))
            if v == shortcircuit:
                return shortcircuit
            if v == InterpType.INV:
                raise InterpError(expr.operator.line, "invalid operand(s) for operator {}".format(expr.operator))
        return not shortcircuit

    def visitGroupingExpr(self, expr):
        return self.visit(expr.expression)

    def visitUnaryExpr(self, expr):
        val = self.visit(expr.right)
        for tp, fn in self.UniFns[expr.operator.type]:
            v = tp(val)
            if v == InterpType.INV: continue
            return fn(v)
        else:
            raise InterpError(expr.operator.line, "invalid operand(s) for operator {}".format(expr.operator))

    def visitLiteralExpr(self, expr):
        tok = expr.value
        if tok.type in (TokenType.TRUE, TokenType.FALSE):
            return tok.type == TokenType.TRUE
        if tok.type in (TokenType.STRING, TokenType.NUMBER, TokenType.NIL):
            return tok.literal
        if tok.type == TokenType.IDENTIFIER:
            if not self.env.defined(tok.lexeme):
                raise InterpError(tok.line, "var {} used without being declared".format(tok.lexeme))
            return self.env.value(tok.lexeme)
        raise InterpError(tok.line, "unsupported literal {}".format(repr(tok)))

    def visitCallExpr(self, expr):
        callee = self.visit(expr.callee)
        if not callable(callee):
            raise InterpError(expr.paran.line, "need a callable object before '(', got {}".format(stringify(callee)))
        args = [self.visit(v) for v in expr.args]
        try:
            return callee(self, args)
        except LoxFuncArgc as ex:
            ex.line = expr.paran.line
            raise ex
        except LoxFlowCtrl as ex:
            if ex.type == TokenType.RETURN:
                return ex.ret
            raise ex
