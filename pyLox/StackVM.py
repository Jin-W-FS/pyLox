
class StackVM:
    # operators
    NOP, JMPTO, JMP, JZ, JNZ,                       \
    LOAD, SAVE, INST, DUP, POP,                     \
    NOT, NEGATIVE,                                  \
    PLUS, MINUS, MULTIPLY, DIVIDE,                  \
    EQUAL, NOT_EQUAL,                               \
    GREATER, GREATER_EQUAL, LESS, LESS_EQUAL,       \
    PRINT, TERM,                                    \
    OPS_COUNT_N = range(25)
    # functions
    Funcs = [
        ('NOP', lambda s: None),
        ('JMPTO', lambda s: s.jump(s.pop())),
        ('JMP', lambda s: s.access('jump')),
        ('JZ', lambda s: s.access(s.pop() and 'none' or 'jump')),
        ('JNZ', lambda s: s.access(s.pop() and 'jump' or 'none')),
        ('LOAD', lambda s: s.access('load')),
        ('SAVE', lambda s: s.access('save')),
        ('INST', lambda s: s.access('inst')),
        ('DUP', lambda s: s.push(s.value())),
        ('POP', lambda s: s.pop()),
        ('NOT', lambda s: s.push(s.pop() == 0)),
        ('NEGATIVE', lambda s: s.push(-s.pop())),
        ('PLUS', lambda s: s.push(s.pop() + s.pop())),
        ('MINUS', lambda s: s.push(s.pop() - s.pop())),
        ('MULTIPLY', lambda s: s.push(s.pop() * s.pop())),
        ('DIVIDE', lambda s: s.push(s.pop() / s.pop())),
        ('EQUAL', lambda s: s.push(s.pop() == s.pop())),
        ('NOT_EQUAL', lambda s: s.push(s.pop() != s.pop())),
        ('GREATER', lambda s: s.push(s.pop() > s.pop())),
        ('GREATER_EQUAL', lambda s: s.push(s.pop() >= s.pop())),
        ('LESS', lambda s: s.push(s.pop() < s.pop())),
        ('LESS_EQUAL', lambda s: s.push(s.pop() <= s.pop())),
        ('PRINT', lambda s: print(s.pop())),
        ('TERM', lambda s: s.term()),
    ]

    def __init__(self, code=b'', data=[]):
        self.code = bytearray(code)
        self.data = data
        self.stack = []
        self.pc = 0
        self.error = ""

    def extend(self, code, data=[]):
        self.code.extend(code)
        self.data.extend(data)

    def replace(self, code, data=[]):
        self.code.extend(code[len(self.code):])
        self.data.extend(data[len(self.data):])

    def terminated(self):
        if self.error: return True
        if self.pc >= len(self.code): return True
        return False

    def term(self, msg="user terminated"):
        self.error = msg

    def operand(self, pc):
        end = pc + 2
        if end > len(self.code):
            raise IndexError("operand", pc)
        return int.from_bytes(self.code[pc:end], 'little', signed=True)

    def access(self, op, value=None):
        '"load" or "save" value at operand'
        end = self.pc + 2
        if end > len(self.code):
            return self.term("{} without operands".format(op))
        idx = int.from_bytes(self.code[self.pc:end], 'little', signed=True)
        self.pc = end
        if op == 'load':
            if not 0 <= idx < len(self.data): return self.term("wrong address to {}".format(op))
            self.push(self.data[idx])
        elif op == 'save':
            if not 0 <= idx < len(self.data): return self.term("wrong address to {}".format(op))
            self.data[idx] = self.pop()
        elif op == 'inst':
            self.push(idx)
        elif op == 'jump':
            self.jump(self.pc + idx)
        else:   # 'none'
            pass

    def jump(self, pc):
        self.pc = pc

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        return self.stack.pop()

    def value(self):
        return self.stack[-1] if self.stack else None

    def runOnce(self):
        if self.terminated():
            return False
        op = self.code[self.pc]
        self.pc += 1
        StackVM.Funcs[op][-1](self)
        return True

    def run(self, debug=False):
        while True:
            if debug: self.printOnce(self.pc)
            if not self.runOnce(): break

    def printOnce(self, pc):
        if not 0 <= pc < len(self.code): return pc
        op = self.code[pc]
        contents = [ '%04d' % pc, StackVM.Funcs[op][0] ]
        pc += 1
        if op in (StackVM.JMP, StackVM.JZ, StackVM.JNZ, StackVM.LOAD, StackVM.SAVE, StackVM.INST):
            opd = self.operand(pc)
            pc += 2
            if op in (StackVM.JMP, StackVM.JZ, StackVM.JNZ):
                contents.append('%+d(=%04d)' % (opd, pc + opd))
            elif op in (StackVM.LOAD, StackVM.SAVE):
                contents.append('#%d(%s)' % (opd, repr(self.data[opd])))
            else: # if op in (StackVM.INST,):
                contents.append('%d(0x%x)' % (opd, opd))
        print(*contents, sep='\t')
        return pc

    def print(self):
        print('.CODE')
        pc = self.pc
        while pc < len(self.code):
            pc = self.printOnce(pc)
        print('.DATA')
        for i, d in enumerate(self.data):
            print('%04d' % i, d, sep='\t')

assert(len(StackVM.Funcs) == StackVM.OPS_COUNT_N)

if __name__ == "__main__":
    vm = StackVM([StackVM.INST, 3, 0,
                  StackVM.INST, 2, 0,
                  StackVM.PLUS,
                  StackVM.LOAD, 2, 0,
                  StackVM.MINUS,
                  StackVM.LOAD, 3, 0,
                  StackVM.EQUAL,
                  StackVM.DUP,
                  StackVM.PRINT,
                  StackVM.JZ, 7, 0,
                  # then phase
                  StackVM.LOAD, 4, 0,
                  StackVM.PRINT,
                  StackVM.JMP, 4, 0,
                  # else phase
                  StackVM.LOAD, 5, 0,
                  StackVM.PRINT,
                  # terminate
                  StackVM.TERM,
                  ], [3, 2, 5, 0, 'true', 'false'])
    print("Disassemble:")
    vm.print()
    print("Running:")
    vm.run(debug=True)
