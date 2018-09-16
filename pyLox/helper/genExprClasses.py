exprs = {
    "Binary"    : "left, operator, right",
    "Grouping"  : "expression",                      
    "Literal"   : "value",                         
    "Unary"     : "operator, right",
    "Call"      : "callee, paran, args"
}

stmts = {
    "Print"     : "expr",
    "Expr"      : "expr",
    "Var"       : "name, initial",
    'Func'      : "name, params, block",
    "If"        : "condition, then_branch, else_branch",
    "While"     : "condition, loop, iteration", # support both while and for loop
    "Flow"      : "type, value", # break, continue, return
}

print("from collections import namedtuple\n\n")
print('''class Visitor:
    def visit(self, obj):
        return obj.accept(self)
    def visitProgram(self, prog):
        pass
    def visitScopeStmt(self, stmt):
        pass''')
for k in stmts.keys():
    print('''    def visit{type}Stmt(self, stmt):\n        pass'''.format(type=k))
for k in exprs.keys():
    print('''    def visit{type}Expr(self, expr):\n        pass'''.format(type=k))

for k, v in exprs.items():
    print('''
class {type}(namedtuple("{type}", "{fields}")):
    def accept(self, visitor):
        return visitor.visit{type}Expr(self)'''.format(type=k, fields=v))

print("\n\n# Statements:")
for k, v in stmts.items():
    print('''
class {type}Stmt(namedtuple("{type}Stmt", "{fields}")):
    def accept(self, visitor):
        return visitor.visit{type}Stmt(self)'''.format(type=k, fields=v))

print('''
class ScopeStmt(list):
    def accept(self, visitor):
        return visitor.visitScopeStmt(self)

class Program(list):
    def accept(self, visitor):
        return visitor.visitProgram(self)
''')
