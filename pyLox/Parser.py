import Expr
from Scanner import *
from LoxError import *

class Parser(object):

    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        
    def currToken(self):
        return self.tokens[self.current]

    def match(self, *args):
        tok = self.currToken()
        return tok.type in args

    def consume(self, type):
        if self.match(type):
            return self.nextToken()
        return None

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

    def parse(self):
        stmts = []
        while not self.isAtEnd():
            stmts.append(self.statement())
        return Expr.Program(stmts)

    def statement(self):
        if self.consume(TokenType.PRINT):
            ast = self.expression()
            if not self.consume(TokenType.SEMICOLON):
                raise self.errUnexpToken(';')
            return Expr.PrintStmt(ast)
        else:
            ast = self.expression()
            if not self.consume(TokenType.SEMICOLON):
                raise self.errUnexpToken(';')
            return Expr.ExprStmt(ast)

    def expression(self):
        return self.equality()

    def equality(self):
        ast = self.comparison()
        while self.match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
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
            return self.primary()

    def primary(self):
        if self.match(TokenType.NIL, TokenType.NUMBER,
                      TokenType.STRING, TokenType.IDENTIFIER,
                      TokenType.TRUE, TokenType.FALSE):
            return Expr.Literal(self.nextToken())
        elif self.consume(TokenType.LEFT_PAREN):
            ast = self.expression()
            if not self.consume(TokenType.RIGHT_PAREN):
                raise self.errUnexpToken(')')
            return Expr.Grouping(ast)
        else:
            raise self.errUnexpToken("primary expr")
