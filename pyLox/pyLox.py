from LoxError import *
from Parser import Parser
from Scanner import Scanner
from AstPrinter import LispPrinter

hadError = False

def run(data):
    global hadError
    try:
        tokens = Scanner(data).scanTokens()
        ast = Parser(tokens).parse()
        if ast: print(LispPrinter().visit(ast))
    except LoxError as ex:
        print(ex)
        hadError = True

def runFile(path):
    global hadError
    data = open(path).read()
    run(data)
    if hadError: exit(65)

def runPrompt():
    global hadError
    try:
        while True:
            print("> ", end='', flush=True)
            run(input())
            hadError = False
    except EOFError:
        return

if __name__ == "__main__":
    from sys import argv
    if len(argv) == 2:
        runFile(argv[1])
    elif len(argv) == 1:
        runPrompt()
    else:
        print("usage: %s [script]" % argv[0])
