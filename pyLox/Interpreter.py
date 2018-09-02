import Expr
from Scanner import *
from LoxError import *

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

def stringify(v):
    'parse interpreter value to string as in Lox program'
    if v == None: return 'nil'
    if isinstance(v, str):
        return repr(v)
    if isinstance(v, float):
        s = str(v)
        if s.endswith('.0'): return s[:-2]
        return s
    if isinstance(v, bool):
        return str(v).lower()
    return str(v)

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
        self.vars = {}

    def visitProgram(self, prog):
        for stmt in prog:
            rlt = self.visit(stmt)
        return rlt

    def visitPrintStmt(self, stmt):
        value = self.visit(stmt.expr)
        print(stringify(value))
        return None

    def visitExprStmt(self, stmt):
        value = self.visit(stmt.expr)
        return value

    def visitVarStmt(self, stmt):
        name = stmt.name
        if name.lexeme in self.vars:
            raise InterpError(name.line, "duplicated declaration of var {}".format(name.lexeme))
        self.vars[name.lexeme] = self.visit(stmt.initial)

    def visitBinaryExpr(self, expr):
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
            if tok.lexeme not in self.vars:
                raise InterpError(tok.line, "var {} used without being declared".format(tok.lexeme))
            return self.vars[tok.lexeme]
        raise InterpError(tok.line, "unsupported literal {}".format(repr(tok)))
