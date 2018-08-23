from enum import Enum
from collections import namedtuple
from LoxError import *

class TokenType(Enum):
    LEFT_PAREN, RIGHT_PAREN, LEFT_BRACE, RIGHT_BRACE,\
    COMMA, DOT, MINUS, PLUS, SEMICOLON, SLASH, STAR, \
    BANG, BANG_EQUAL,                                \
    EQUAL, EQUAL_EQUAL,                              \
    GREATER, GREATER_EQUAL,                          \
    LESS, LESS_EQUAL,                                \
    AND, CLASS, ELSE, FALSE, FUN, FOR, IF, NIL, OR,  \
    PRINT, RETURN, SUPER, THIS, TRUE, VAR, WHILE,    \
    IDENTIFIER, STRING, NUMBER,                      \
    EOF = range(39)

TokenType.Keys = (
    '(', ')', '{', '}',
    ',', '.', '-', '+', ';', '/', '*',
    '!', '!=',
    '=', '==',
    '>', '>=',
    '<', '<=',
    'and', 'class', 'else', 'false', 'fun', 'for', 'if', 'nil', 'or',
    'print', 'return', 'super', 'this', 'true', 'var', 'while'
    )
TokenType.KeyMap = { k : TokenType(i) for i, k in enumerate(TokenType.Keys) }

class Token(namedtuple("Token", "type,lexeme,literal,line")):
    def __repr__(self):
        t = self.type.name
        if self.literal is not None:
            v = self.literal
            if isinstance(v, str): v = repr(v)
        else:
            v = self.lexeme
        return '<{}: {}>'.format(t, v)

class Scanner:

    def __init__(self, source):
        self.source = source
        self.start = self.current = 0
        self.line = 1
        self.tokens = []

    def curToken(self):
        return self.source[self.start:self.current]

    def addToken(self, type, literal=None):
        self.tokens.append(Token(type, self.curToken(), literal, self.line))

    def scanTokens(self):
        while not self.isAtEnd():
            self.scanToken()
        self.start = self.current
        self.addToken(TokenType.EOF)
        return self.tokens

    def scanToken(self):
        self.skipSpaces()
        self.start = self.current
        if self.isAtEnd(): return
        c = self.peek()
        if c.isalpha() or c == '_':
            self.scanIdentifier()
        elif c.isdigit():
            self.scanNumber()
        elif c == '"':
            self.scanString()
        else:
            self.scanSymbol()

    def skipSpaces(self):
        while self.peek().isspace() and not self.isAtEnd():
            self.advance()

    def scanIdentifier(self):
        c = self.peek()
        while c.isalnum() or c == '_':
            self.advance()
            c = self.peek()
        key = TokenType.KeyMap.get(self.curToken())
        if key is not None:
            self.addToken(key)
        else:
            self.addToken(TokenType.IDENTIFIER, None)

    def scanNumber(self):
        while self.peek().isdigit():
            self.advance()
        if self.peek() == '.' and self.peek(1).isdigit():
            self.advance()
            while self.peek().isdigit():
                self.advance()
        s = self.curToken()
        try:
            v = float(s)
        except ValueError:
            raise LoxError(self.line, 'parse "{}" as number failed'.format(s))
        self.addToken(TokenType.NUMBER, v)

    def scanString(self):
        self.advance()  # skip leading '"'
        escape, ended = False, False
        while not self.isAtEnd():
            c = self.advance()
            # if c == '\n': break # error: string not ended
            if not escape:
                if c == '"':
                    ended = True
                    break
                if c == '\\':   # escape
                    escape = True
            else:
                escape = False  # escape only one char
        if not ended:
            raise LoxError(self.line, 'string terminated at unexpected position')
        s = self.curToken()
        try:
            v = eval(s) # evaluate string as python string
        except SyntaxError:
            raise LoxError(self.line, 'parse "{}" as string failed'.format(s))
        self.addToken(TokenType.STRING, v)

    def scanSymbol(self):
        c = self.advance()
        if not self.isAtEnd():
            if c in ('!', '=', '>', '<'):
                if self.peek() == '=':
                    self.advance()
            elif c == '/':
                if self.peek() == '/':  # comment
                    while not self.isAtEnd() and self.advance() != '\n':
                        pass
                    return
        s = self.curToken()
        key = TokenType.KeyMap.get(s)
        if key is None:
            raise LoxError(self.line, 'unexpected character "{}"'.format(s))
        self.addToken(key)

    def isAtEnd(self):
        return self.current >= len(self.source)

    def peek(self, n = 0):
        idx = self.current + n
        if idx >= len(self.source): return '\0'
        return self.source[idx]

    def advance(self):
        c = self.source[self.current]
        if c == '\n': self.line += 1
        self.current += 1
        return c

    def ungetc(self):
        self.current -= 1
