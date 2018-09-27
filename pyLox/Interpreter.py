from contextlib import contextmanager
import Expr
from Scanner import *
from LoxError import *
from Functions import *
from Resolver import Resolver
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
        self.env = self.globalEnv = Environment(initial=lox_builtins)
        self.ids = None

    def interpret(self, ast, ids=None):
        self.ids = ids
        if self.ids is None:
            self.getval, self.setval = self.getval0, self.setval0
        else:
            self.getval, self.setval = self.getval1, self.setval1
        return self.visit(ast)

    @contextmanager
    def subEnv(self, env=None, initial=None):
        if env is None: env = self.env
        saved = self.env    # save
        self.env = Environment(env, initial)    # extend
        try:
            yield   # run user code
        finally:
            self.env = saved    # recover

    def setval0(self, name, valueExpr):
        env = self.env
        if not env.defined(name.lexeme):
            raise InterpError(name.line, "var {} used without being declared".format(name.lexeme))
        return env.assign(name.lexeme, self.visit(valueExpr))

    def getval0(self, name):
        env = self.env
        if not env.defined(name.lexeme):
            if name.type == TokenType.IDENTIFIER:
                raise InterpError(name.line, "var {} used without being declared".format(name.lexeme))
            else:
                raise InterpError(name.line, "keyword '{}' should be used inside a class".format(name.lexeme))
        if name.type == TokenType.SUPER: # trick here
            parent = env.value('super')    # super class
            if not env.defined('this'): return parent    # class method
            return env.value('this').super(parent)
        return env.value(name.lexeme)

    def setval1(self, name, valueExpr):
        depth = None if self.ids is None else self.ids[name]
        env = self.globalEnv if depth == -1 else self.env
        if not env.defined(name.lexeme, depth=depth):
            raise InterpError(name.line, "var {} used without being declared".format(name.lexeme))
        return env.assign(name.lexeme, self.visit(valueExpr), depth=depth)

    def getval1(self, name):
        depth = None if self.ids is None else self.ids[name]
        env = self.globalEnv if depth == -1 else self.env
        if not env.defined(name.lexeme, depth=depth):
            if name.type == TokenType.IDENTIFIER:
                raise InterpError(name.line, "var {} used without being declared".format(name.lexeme))
            else:
                raise InterpError(name.line, "keyword '{}' should be used inside a class".format(name.lexeme))
        if name.type == TokenType.SUPER: # trick here
            parent = env.value('super', depth=depth)    # super class
            updepth = None if self.ids is None else (depth - 1)
            if not env.defined('this', depth=updepth): return parent    # class method
            return env.value('this', depth=updepth).super(parent)
        return env.value(name.lexeme, depth=depth)

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

    def visitAssertStmt(self, stmt):
        value = InterpType.Boolean(self.visit(stmt.expr))
        if value == InterpType.INV:
            raise InterpError(stmt.op.line, "assert statement requires a boolean condition")
        if not value:
            from io import StringIO
            from AstPrinter import LispPrinter
            sp = LispPrinter(file=StringIO()).printProgram(stmt.expr, end='').getvalue()
            raise AssertError(stmt.op.line, "assertion {} failed".format(sp))

    def visitExprStmt(self, stmt):
        value = self.visit(stmt.expr)
        return None if stmt.semicolon else value

    def visitVarStmt(self, stmt):
        name = stmt.name
        if not self.env.define(name.lexeme):
            raise InterpError(name.line, "duplicated declaration of var {}".format(name.lexeme))
        if stmt.initial is not None:
            self.env.assign(name.lexeme, self.visit(stmt.initial), depth=0)

    def visitFuncStmt(self, stmt):
        func = LoxFunc(stmt, env=self.env)  # lexical scope
        if func.name != LoxFunc.ANONYMOUS:
            self.env.define(func.name)    # allow function redefine
            self.env.assign(func.name, func, depth=0)
        return func

    def visitClassStmt(self, stmt):
        self.env.define(stmt.name.lexeme)
        cls = LoxClass(stmt, env=self.env, lookup=self.getval)
        self.env.assign(cls.name, cls, depth=0)
        return cls

    def visitIfStmt(self, stmt):
        condition = InterpType.Boolean(self.visit(stmt.condition))
        if condition == InterpType.INV:
            raise InterpError(stmt.condition.line, "if statement requires a boolean condition")
        if condition:
            return self.visit(stmt.then_branch)
        else:
            if not stmt.else_branch: return None
            return self.visit(stmt.else_branch)

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
            if stmt.iteration:
                self.visit(stmt.iteration)

    def visitFlowStmt(self, stmt):
        raise LoxFlowCtrl(stmt.type, stmt.value and self.visit(stmt.value))

    def visitBinaryExpr(self, expr):
        if expr.operator.type == TokenType.EQUAL:
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

    def visitAttribExpr(self, expr):
        return self._visitGetAttribExpr(expr)

    def _visitAssignExpr(self, expr):
        if isinstance(expr.left, Expr.Identifier):
            name = expr.left.value
            return self.setval(name, expr.right)
        if isinstance(expr.left, Expr.Attrib):
            return self._visitSetAttribExpr(expr.left, expr.right)
        raise InterpError(expr.operator.line, "left value required before operator {}".format(expr.operator))

    def _visitGetAttribExpr(self, expr):
        object = self.visit(expr.object)
        getter = getattr(object, 'getattr', None)
        if not getter:
            raise InterpError(expr.operator.line, "left of operator '.' should be a gettable object")
        attr = expr.attribute.lexeme
        try:
            return getter(attr)
        except KeyError:
            raise InterpError(expr.operator.line, "{} doesn't have attr '{}'".format(object, attr))

    def _visitSetAttribExpr(self, expr, valueExpr):
        object = self.visit(expr.object)
        setter = getattr(object, 'setattr', None)
        if not setter:
            raise InterpError(expr.operator.line, "left of operator '.' should be a settable object")
        attr = expr.attribute.lexeme
        value = self.visit(valueExpr)
        setter(attr, value)

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
        raise InterpError(tok.line, "unsupported literal {}".format(repr(tok)))

    def visitIdentifierExpr(self, expr):
        return self.getval(expr.value)

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
