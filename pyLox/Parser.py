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

    def consume(self, *args):
        if self.match(*args):
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

    def synchronize(self):
        'skip until next ';' or EOF when encounter error'
        while not self.isAtEnd():
            if self.nextToken().type == TokenType.SEMICOLON:
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
        def checkStmtEnd():
            cur = self.currToken()
            if cur.type == TokenType.EOF: return cur
            if cur.type == TokenType.SEMICOLON: return self.nextToken()
            raise self.errUnexpToken(';')

        if self.consume(TokenType.LEFT_BRACE):
            stmts = Expr.ScopeStmt()  # scope statement
            while not self.isAtEnd():
                if self.consume(TokenType.RIGHT_BRACE): break
                stmts.append(self.statement())
            else:   # is at end
                raise self.errUnexpToken('}')
            return stmts
        elif self.consume(TokenType.PRINT):
            ast = self.expression()
            checkStmtEnd()
            return Expr.PrintStmt(ast)
        elif self.consume(TokenType.VAR):
            name = self.consume(TokenType.IDENTIFIER)
            if not name:
                raise self.errUnexpToken('Identifier')
            if self.consume(TokenType.EQUAL):
                initial = self.expression()
            else:
                initial = None
            checkStmtEnd()
            return Expr.VarStmt(name, initial)
        elif self.consume(TokenType.SEMICOLON):
            pass    # allow null statement
        else:
            ast = self.expression()
            checkStmtEnd()
            return Expr.ExprStmt(ast)

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
