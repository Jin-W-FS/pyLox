from LoxError import *
from Parser import Parser
from Scanner import Scanner
from AstPrinter import LispPrinter
from Interpreter import Interpreter, stringify

class Lox:

    def __init__(self):
        self.hadError = False
        self.interp = Interpreter() # for retain inner statements when runPrompt()

    def run(self, data):
        try:
            tokens = Scanner(data).scanTokens()
            ast, errors = Parser(tokens).parse()
            if errors:
                for ex in errors: print(ex)
                print("skip interpret dure to parser errors")
                self.hadError = True
            print(LispPrinter().visit(ast))
            print(stringify(self.interp.visit(ast)))
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
                print("> ", end='', flush=True)
                self.run(input())
                self.hadError = False
        except EOFError:
            return

if __name__ == "__main__":
    from sys import argv
    lox = Lox()
    if len(argv) == 2:
        lox.runFile(argv[1])
    elif len(argv) == 1:
        lox.runPrompt()
    else:
        print("usage: %s [script]" % argv[0])
