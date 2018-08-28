exprs = {
      "Binary"   : "left, operator, right",
      "Grouping" : "expression",                      
      "Literal"  : "value",                         
      "Unary"    : "operator, right",
}

print('''class Visitor:
    def visit(self, expr):
        return expr.accept(self)''')
for k in exprs.keys():
    print('''    def visit{type}Expr(self, expr):\n        pass'''.format(type=k))

for k, v in exprs.items():
    print('''
class {type}(namedtuple("{type}", "{fields}")):
    def accept(self, visitor):
        return visitor.visit{type}Expr(self)'''.format(type=k, fields=v))
