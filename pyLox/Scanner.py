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
    AND, ASSERT, BREAK, CLASS, CONTINUE, ELSE, FALSE, FUN, FOR, IF,    \
    LAMBDA, NIL, OR, PRINT, RETURN, SUPER, THIS, TRUE, VAR, WHILE,    \
    IDENTIFIER, STRING, NUMBER,                      \
    EOF = range(43)

TokenType.Keys = (
    '(', ')', '{', '}',
    ',', '.', '-', '+', ';', '/', '*',
    '!', '!=',
    '=', '==',
    '>', '>=',
    '<', '<=',
    'and', 'assert', 'break', 'class', 'continue', 'else', 'false', 'fun', 'for', 'if',
    'lambda', 'nil', 'or', 'print', 'return', 'super', 'this', 'true', 'var', 'while',
    )
TokenType.KeyMap = { k : TokenType(i) for i, k in enumerate(TokenType.Keys) }

class Token(namedtuple("Token", "type,lexeme,literal,line,char")):
    def __repr__(self):
        return '<{}: {}>'.format(self.type.name, str(self))
    def __str__(self):
        if isinstance(self.literal, str):
            return repr(self.literal)
        else:
            return self.lexeme

class Scanner:

    def __init__(self, source):
        self.source = source
        self.start = self.current = 0
        self.line, self.linebeg = 1, -1
        self.tokens = []

    def curToken(self):
        return self.source[self.start:self.current]

    def addToken(self, type, literal=None):
        self.tokens.append(Token(type, self.curToken(), literal, self.line, self.start - self.linebeg))

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
            raise ParserError(self.line, 'parse "{}" as number failed'.format(s))
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
            raise ParserError(self.line, 'string terminated at unexpected position')
        s = self.curToken()
        try:
            v = eval(s) # evaluate string as python string
        except SyntaxError:
            raise ParserError(self.line, 'parse "{}" as string failed'.format(s))
        self.addToken(TokenType.STRING, v)

    def scanSymbol(self):
        c = self.advance()
        if not self.isAtEnd():
            if c in ('!', '=', '>', '<'):
                if self.peek() == '=':
                    self.advance()
            elif c == '/':
                if self.peek() == '/':  # inline comment
                    while not (self.isAtEnd() or self.advance() == '\n'):
                        pass
                    return
                elif self.peek() == '*':  # crossline comments
                    while not self.isAtEnd():
                        if self.advance() == '*' and self.peek() == '/':
                            self.advance()
                            return
                    raise ParserError(self.line, 'unterminated block comment')
        s = self.curToken()
        key = TokenType.KeyMap.get(s)
        if key is None:
            raise ParserError(self.line, 'unexpected character "{}"'.format(s))
        self.addToken(key)

    def isAtEnd(self):
        return self.current >= len(self.source)

    def peek(self, n = 0):
        idx = self.current + n
        if idx >= len(self.source): return '\0'
        return self.source[idx]

    def advance(self):
        c = self.source[self.current]
        if c == '\n':
            self.line += 1
            self.linebeg = self.current
        self.current += 1
        return c

    def ungetc(self):
        self.current -= 1

    @staticmethod
    def checkParen(tokens):
        '''returns: =0: left/right paren match; >0: left > right; <0: left < right(error)'''
        checking = (TokenType.LEFT_PAREN, TokenType.RIGHT_PAREN, TokenType.LEFT_BRACE, TokenType.RIGHT_BRACE)
        counter = { k : 0 for k in checking }
        for tok in tokens:
            if tok.type in checking:
                counter[tok.type] += 1
        return ((counter[TokenType.LEFT_PAREN] - counter[TokenType.RIGHT_PAREN]) or
                (counter[TokenType.LEFT_BRACE] - counter[TokenType.RIGHT_BRACE]))
