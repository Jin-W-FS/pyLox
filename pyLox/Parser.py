import Expr
from Scanner import *
from LoxError import *
from Functions import *

class Parser(object):

    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def currToken(self):
        return self.tokens[self.current]

    def match(self, *args):
        tok = self.currToken()
        return tok.type in args

    def consume(self, *args, exp=None):
        if self.match(*args):
            return self.nextToken()
        if exp:
            raise self.errUnexpToken(exp)
        else:
            return None

    def lastToken(self):
        return self.tokens[self.current-1]

    def nextToken(self):
        tok = self.currToken()
        self.current += 1
        return tok

    def isAtEnd(self):
        return self.current >= len(self.tokens) - 1
        # return self.currToken().type == TokenType.EOF

    def errUnexpToken(self, exp):
        tok = self.currToken()
        return ParserError(tok.line, "expect {}, got {}".format(exp, tok))

    def synchronize(self):
        "skip until next ';' or '}' or EOF when encounter error"
        while not self.isAtEnd():
            if self.nextToken().type in (TokenType.SEMICOLON, TokenType.RIGHT_BRACE):
                break

    def parse(self):
        stmts, errors = Expr.Program(), []
        while not self.isAtEnd():
            try:
                stmts.append(self.statement())
            except ParserError as ex:
                errors.append(ex)
                self.synchronize()
        return stmts, errors

    def statement(self):
        if self.consume(TokenType.LEFT_BRACE): return self.scopeStmt()
        if self.consume(TokenType.PRINT): return self.printStmt()
        if self.consume(TokenType.VAR): return self.varStmt()
        if self.consume(TokenType.FUN): return self.funStmt()
        if self.consume(TokenType.IF): return self.ifStmt()
        if self.consume(TokenType.SEMICOLON): return self.voidStmt()
        if self.consume(TokenType.WHILE): return self.whileStmt()
        if self.consume(TokenType.FOR): return self.forStmt()
        if self.consume(TokenType.BREAK, TokenType.CONTINUE, TokenType.RETURN): return self.flowStmt()
        # else:
        return self.exprStmt()
    
    def scopeStmt(self):
        stmts = Expr.ScopeStmt()
        while not self.isAtEnd():
            if self.consume(TokenType.RIGHT_BRACE): break
            stmts.append(self.statement())
        else:   # is at end
            raise self.errUnexpToken('}')
        return stmts

    def printStmt(self):
        ast = self.expression()
        self.endStmt()
        return Expr.PrintStmt(ast)

    def varStmt(self):
        name = self.consume(TokenType.IDENTIFIER, exp='Identifier')
        if self.consume(TokenType.EQUAL):
            initial = self.expression()
        else:
            initial = None
        self.endStmt()
        return Expr.VarStmt(name, initial)

    def funStmt(self):
        name = self.consume(TokenType.IDENTIFIER, exp='Identifier')
        return self.funExpr(name)

    def funExpr(self, name=None):
        self.consume(TokenType.LEFT_PAREN, exp='(')
        params = []
        if not self.consume(TokenType.RIGHT_PAREN):
            while True:
                params.append(self.consume(TokenType.IDENTIFIER, exp='Identifier'))
                if self.consume(TokenType.RIGHT_PAREN): break
                self.consume(TokenType.COMMA, exp=',')
        self.consume(TokenType.LEFT_BRACE, exp='{')
        block = self.scopeStmt()
        return Expr.FuncStmt(name, params, block)

    def ifStmt(self):
        self.consume(TokenType.LEFT_PAREN, exp='(')
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, exp=')')
        then_branch = self.statement()
        if self.consume(TokenType.ELSE):
            else_branch = self.statement()
        else:
            else_branch = None
        return Expr.IfStmt(condition, then_branch, else_branch)

    def whileStmt(self):
        self.consume(TokenType.LEFT_PAREN, exp='(')
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, exp=')')
        loop = self.statement()
        return Expr.WhileStmt(condition, loop, None)

    def forStmt(self):
        self.consume(TokenType.LEFT_PAREN, exp='(')
        initial = self.statement()  # to support varStmt as (var i = 0; ...; ...)
        if not self.match(TokenType.SEMICOLON):
            condition = self.expression()
        else:
            condition = Expr.Literal(Token(type, lexeme, None, self.currToken().line))
        self.consume(TokenType.SEMICOLON, exp=';')
        iteration = self.expression() if not self.match(TokenType.RIGHT_PAREN) else None
        self.consume(TokenType.RIGHT_PAREN, exp=')')
        loop = self.statement()
        return Expr.ScopeStmt([initial, Expr.WhileStmt(condition, loop, iteration)])

    def flowStmt(self):
        tok, value = self.lastToken(), None
        if tok.type == TokenType.RETURN and not self.match(TokenType.COMMA):
            value = self.expression()
        self.endStmt()
        return Expr.FlowStmt(tok, value)

    def voidStmt(self):
        return Expr.Literal(Token(TokenType.NIL, 'nil', None, self.lastToken().line))

    def exprStmt(self):
        ast = self.expression()
        self.endStmt()
        return Expr.ExprStmt(ast)

    def endStmt(self):
        if self.match(TokenType.EOF, TokenType.RIGHT_BRACE): return True
        if self.consume(TokenType.SEMICOLON, exp=';'): return True
        return False

    def expression(self):
        return self.assign()

    def assign(self):
        ast = self.equality()
        while self.match(TokenType.EQUAL):
            ast = Expr.Binary(ast, self.nextToken(), self.assign())
        return ast

    def equality(self):
        ast = self.orexpr()
        while self.match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            ast = Expr.Binary(ast, self.nextToken(), self.orexpr())
        return ast

    def orexpr(self):
        ast = self.andexpr()
        while self.match(TokenType.OR):
            ast = Expr.Binary(ast, self.nextToken(), self.andexpr())
        return ast

    def andexpr(self):
        ast = self.comparison()
        while self.match(TokenType.AND):
            ast = Expr.Binary(ast, self.nextToken(), self.comparison())
        return ast

    def comparison(self):
        ast = self.addition()
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL,
                         TokenType.LESS, TokenType.LESS_EQUAL):
            ast = Expr.Binary(ast, self.nextToken(), self.addition())
        return ast

    def addition(self):
        ast = self.multiplication()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            ast = Expr.Binary(ast, self.nextToken(), self.multiplication())
        return ast

    def multiplication(self):
        ast = self.unary()
        while self.match(TokenType.SLASH, TokenType.STAR):
            ast = Expr.Binary(ast, self.nextToken(), self.unary())
        return ast

    def unary(self):
        if self.match(TokenType.BANG, TokenType.MINUS):
            return Expr.Unary(self.nextToken(), self.unary())
        else:
            return self.call()

    def call(self):
        ast = self.primary()
        while self.consume(TokenType.LEFT_PAREN):
            paran = self.lastToken()
            ast = Expr.Call(ast, paran, self.callArgs())
            self.consume(TokenType.RIGHT_PAREN, exp=')')
        return ast

    def callArgs(self):
        args = []
        if not self.match(TokenType.RIGHT_PAREN):
            while True:
                args.append(self.expression())
                if self.match(TokenType.RIGHT_PAREN): break
                self.consume(TokenType.COMMA, exp=',')
        return args

    def primary(self):
        if self.match(TokenType.NIL, TokenType.NUMBER,
                      TokenType.STRING, TokenType.IDENTIFIER,
                      TokenType.TRUE, TokenType.FALSE):
            return Expr.Literal(self.nextToken())
        elif self.consume(TokenType.LEFT_PAREN):
            ast = self.expression()
            self.consume(TokenType.RIGHT_PAREN, exp=')')
            return Expr.Grouping(ast)
        elif self.consume(TokenType.LAMBDA):
            return self.funExpr()
        else:
            raise self.errUnexpToken("primary expr")
