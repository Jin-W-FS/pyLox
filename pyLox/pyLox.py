from LoxError import *
from Parser import Parser
from Scanner import Scanner
from AstPrinter import LispPrinter
from Interpreter import Interpreter, stringify

class Lox:

    def __init__(self):
        self.hadError = False
        self.tokens = []            # saved tokens from previous uncompleted lines
        self.interp = Interpreter() # for retain inner statements when runPrompt()

    def run(self, data, prompt=False):
        try:
            tokens = Scanner(data).scanTokens()
            if prompt:
                tokens = self.continueLines(tokens)
                if not tokens: return
            ast, errors = Parser(tokens).parse()
            if errors:
                for ex in errors: print(ex)
                print("skip interpret dure to parser errors")
                self.hadError = True
            LispPrinter().printProgram(ast)
            rlt = self.interp.visit(ast)
            if rlt is not None: print(stringify(rlt))
        except LoxError as ex:
            print(ex)
            self.hadError = True

    def runFile(self, path):
        data = open(path).read()
        self.run(data)
        if self.hadError: exit(65)

    def runPrompt(self):
        try:
            while True:
                if not self.tokens:
                    print(">>> ", end='', flush=True)
                else:
                    print("... ", end='', flush=True)
                self.run(input(), prompt=True)
                self.hadError = False
        except EOFError:
            return
        except KeyboardInterrupt:
            return

    def continueLines(self, tokens):
        self.tokens.extend(tokens)
        if Scanner.checkParen(self.tokens) > 0:  # uncompleted
            tokens = []
            self.tokens.pop()   # pop EOF
        else:   # matched or error
            tokens = self.tokens
            self.tokens = []
        return tokens


if __name__ == "__main__":
    from sys import argv
    lox = Lox()
    if len(argv) == 2:
        lox.runFile(argv[1])
    elif len(argv) == 1:
        lox.runPrompt()
    else:
        print("usage: %s [script]" % argv[0])
