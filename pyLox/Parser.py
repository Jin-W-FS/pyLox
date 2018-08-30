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

    def nextToken(self):
        tok = self.currToken()
        self.current += 1
        return tok

    def parse(self):
        try:
            exp = self.expression()
            if not self.match(TokenType.EOF):
                tok = self.currToken()
                raise self.errUnexpToken('EOF')
            return exp
        except LoxError as ex:
            print(ex)

    def errUnexpToken(self, exp):
        tok = self.currToken()
        return ParserError(tok.line, "expect {}, got {}".format(exp, tok))

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
        elif self.match(TokenType.LEFT_PAREN):
            self.nextToken()
            ast = self.expression()
            if not self.match(TokenType.RIGHT_PAREN):
                raise self.errUnexpToken(')')
            self.nextToken()
            return Expr.Grouping(ast)
        else:
            raise self.errUnexpToken("primary expr")
