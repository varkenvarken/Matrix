# Matrix, a simple programming language
# (c) 2022 Michel Anders
# License: MIT, see License.md
<<<<<<< HEAD
# Version: 20220308114331
=======
# Version: 20220305170303
>>>>>>> 5a43078... added a small standard library

from struct import pack, unpack


def program_preamble():
    return """

# main preamble
        .text
        .globl  main
        .type   main, @function
main:
        pushq   %rbp
        movq    %rsp, %rbp
"""


def program_postamble():
    return """
# main postamble
        .globl endmain
        xor %rax,%rax
endmain:
        popq    %rbp
        ret
        .size   main, .-main
.DOUBLENEGATE:     # to negate a double with xorpd
        .long   0
        .long   -2147483648
        .long   0
        .long   0
"""


def pop_double(reg):
    return f"""
        pop %rax
        movq %rax, {reg}
"""


def push_quad(reg):
    return f"""
        movq {reg}, %rax
        push %rax
"""


def pop_quad(reg):
    return f"""
        pop %rax
        movq %rax, {reg}
"""


def push_double(reg):
    return f"""
        movq {reg}, %rax
        push %rax
"""


def load_quad(reg):
    return f"""
        movq {reg}, %rax
        push %rax
"""


def load_address(reg):
    return f"""
        leaq {reg}, %rax
        push %rax
"""


def store_quad(reg):
    return f"""
# store a double
        pop %rax
        movq %rax, {reg}
"""


def store_string(reg):
    return f"""
# store a (pointer to a) string
        pop %rax
        movq %rax, {reg}
"""


local_doubles = -1


def local_double_number(number):
    # bytes = pack("<d", number)
    # longs = unpack("<LL", bytes)
    global local_doubles
    local_doubles += 1
    label = f".LDN{local_doubles}"
    return (
        label,
        f"""
{label}:
        .double {number if number is not None else 0.0}
""",
    )


# TODO: escape any embedded quotes
local_strings = -1


# note that string literals have already quotes arounf them
def local_string(s):
    global local_strings
    local_strings += 1
    label = f".LS{local_strings}"
    return (
        label,
        f"""
{label}:
        .string {s if s is not None else ''}
""",
    )


def pop(n):
    return f"        addq ${n}, %rsp"


def print_top_float():
    return f"""
        leaq  .pfloat(%rip), %rdi
        movsd (%rsp), %xmm0
        movl $1,%eax
        call printf
"""


def vardef(v):
    tab = "        "
    lines = [f"{v.name} not processed"]
    if v.type == "double":
        lines = [
            f"\n{tab}.global {v.name}",
            f"{tab}{'.section .rodata' if v.const and not v.constoverride else '.data'}",
            f"{tab}.p2align 3",
            f"{tab}.type {v.name}, @object",
            f"{tab}.size {v.name}, 8",
            f"{v.name}:",
            f"{tab}.double {v.value if v.value is not None else 0.0}",
            #            f"{tab}.long {longs[0]:d}",
            #            f"{tab}.long {longs[1]:d}",
        ]
    if v.type == "str":
        lines = [
            f"\n{tab}.global {v.name}",
            f"{tab}.section .rodata",
            f"{tab}.type {v.name}, @object",
            f"{v.name}:",
            f"{tab}.quad . + 8",
            f"{tab}.string {v.value}",
            f"{tab}.size   {v.name}, .-{v.name}",
        ]
    elif v.type == "function":
        lines = [""]

    print(">>>>>", v.name, v.type)
    return "\n".join(lines)


def vardefs(scope, defs):
    return "\n".join(vardef(v) for v in defs)


def symbol_defs(scope):
    consts = [
        val for key, val in scope.symbols.items() if val.const and not val.constoverride
    ]
    var = [
        val
        for key, val in scope.symbols.items()
        if (not val.const) or val.constoverride
    ]

    for key, val in scope.symbols.items():
        print(f"{key}: {val.type} {val.const} override {val.constoverride}")

    return (
        "# global constants\n"
        + vardefs(scope.scope, consts)
        + "\n\n# global variables\n"
        + vardefs(scope.scope, var)
    )


class CodeGenerator:
    def __init__(self, syntaxtree):
        self.ast = syntaxtree.tree
        self.symbols = syntaxtree.symbols
        self.code = []
        self.fdefinitions = []
        self.locals = []  # bit of a misnomer, static would prob. be better
        self.process(self.ast)
        self.code.extend(self.locals)
        self.code.append(symbol_defs(syntaxtree.symbols))
        self.stack = 0

    def adjust_stack(self):
        print(f"adjust stack {self.stack}")
        if self.stack != 0:
            self.code.append(f"        add ${self.stack}, %rsp")
            self.stack = 0

    def process(self, node):
        if node is None:
            return
        elif node.typ == "program":
            self.code.append(program_preamble())
            self.process(node.e0)
            self.code.append(program_postamble())
            self.code.extend(self.fdefinitions)
        elif node.typ == "unit":
            print("begin unit")
            self.code.append(f"# unit (node id: {node.id})")
            self.stack = 0
            self.process(node.e0)
            self.adjust_stack()
            print("end unit")
            self.process(node.e1)
        elif node.typ == "initialize":
            # TODO: check that type of expresion matches type of variable being initialized (or actually do this in Syntax.py)
            if node.info == "double":
                what = node.e0.info
                name = what[1]
                scope = what[0]
                if scope == "global":
                    if node.e1.typ == "number":  # single constant initializer
                        self.symbols[name].value = node.e1.info
                    else:  # initializer expression
                        self.symbols[name].constoverride = True
                        self.process(node.e1)
                        self.code.append(f"# store in global var {name}")
                        self.code.append(store_quad(f"{name}(%rip)"))
                        self.stack -= 8
                else:
                    self.process(node.e1)
                    self.code.append(f"# store in local var {name}")
                    self.code.append(store_quad(f"-{self.scope[name].offset}(%rbp)"))
                    self.stack -= 8
            elif node.info == "str":
                what = node.e0.info
                name = what[1]
                scope = what[0]
                if scope == "global":
                    if node.e1.typ == "stringliteral":  # single constant initializer
                        self.symbols[name].value = node.e1.info
                    else:  # initializer expression
                        self.symbols[name].constoverride = True
                        self.process(node.e1)
                        self.code.append(f"# store in global var {name}")
                        self.code.append(store_string(f"{name}(%rip)"))
                        self.stack -= 8
                else:
                    self.process(node.e1)
                    self.code.append(f"# store in local var {name}")
                    self.code.append(store_string(f"-{self.scope[name].offset}(%rbp)"))
                    self.stack -= 8
            else:
                print("unprocessed initializer for", node.info)
        elif node.typ == "unop":
            type0 = self.process(node.e0)
            if type0 == "double":
                self.code.append(
                    f"""
        movq (%rsp),%xmm0
        movq    .DOUBLENEGATE(%rip), %xmm1
        xorpd   %xmm1, %xmm0
        movq %xmm0, (%rsp)
"""
                )
                return type0
            else:
                print(f"unprocessed unop {node.info['op']} for type {type0}")
        elif node.typ == "binop":
            type0 = self.process(node.e0)
            type1 = self.process(node.e1)
            if type0 != type1 or type0 is None or type1 is None:
                print(f"Incompatible type {type0} {type1} in node {node}")
                return
            if type0 == "double":
                self.code.append(pop_double("%xmm0"))
                self.stack -= 8
                print(f"stack: {self.stack}")
                self.code.append(pop_double("%xmm1"))
                self.stack -= 8
                print(f"stack: {self.stack}")
                if node.info["op"] == "plus":
                    self.code.append("        addsd %xmm1, %xmm0")
                else:
                    print("unprocessed binop", node.info["op"])
                self.code.append(push_double("%xmm0"))
                self.stack += 8
                print(f"stack: {self.stack}")
                return "double"
            elif type0 == "str":
                self.code.append(pop_quad("%rsi"))
                self.stack -= 8
                print(f"stack: {self.stack}")
                self.code.append(pop_quad("%rdi"))
                self.stack -= 8
                print(f"stack: {self.stack}")
                if node.info["op"] == "plus":
                    self.code.append("        call addstring")
                else:
                    print("unprocessed binop", node.info["op"])
                self.code.append(push_quad("%rax"))
                self.stack += 8
                print(f"stack: {self.stack}")
                return "str"
        elif node.typ == "number":
            label, code = local_double_number(node.info)
            self.code.append(load_quad(f"{label}(%rip)"))
            self.stack += 8
            print(f"stack: {self.stack}")
            self.locals.append(code)
            return "double"
        elif node.typ == "stringliteral":
            label, code = local_string(node.info)
            self.code.append(load_address(f"{label}(%rip)"))
            self.stack += 8
            print(f"stack: {self.stack}")
            self.locals.append(code)
            return "str"
        elif node.typ == "call":
            returntype = node.info["type"]
            name = node.info["name"]
            an = 0
            arg = node.e0
            assert arg.typ == "argument"
            argtypes = []
            while arg:
                self.code.append(f"# argument {an}")
                argtypes.append(self.process(arg.e1))
                arg = arg.e0
                an += 1
            ndoubles = 0
            nothers = 0
            argregisters = []
            regs = ["%rdi", "%rsi", "%rdx", "%rcx", "%r8", "%r9"]
            for t in argtypes:
                if t == "double":
                    argregisters.append(f"%xmm{ndoubles}")
                    ndoubles += 1
                else:
                    argregisters.append(regs.pop(0))
                    nothers += 1
            print("!!!!!!!!", argtypes, argregisters, an)
            for i in range(an):
                self.code.append(pop_quad(argregisters.pop()))
                self.stack -= 8
            self.code.append(
                f"        movq ${an},%rax  # number of arguments, only needed when calling varargs"
            )
            self.adjust_stack()
            self.code.append(f"        call {name}")
            if returntype == "double":
                self.code.append(push_double("%xmm0"))
                self.stack += 8
            elif returntype == "void":
                self.code.append("# void return type, nothing to push")
            elif returntype == "str":
                self.code.append(push_quad("%rax"))
                self.stack += 8
            else:
                print(f"return type {returntype} ignored for now")
            return returntype
        elif node.typ == "var reference":
            if (
                node.info["type"] in ("double", "str")
                and node.info["scope"] == "global"
            ):
                name = node.info["name"]
                self.code.append(f"# global var reference {node.info['type']}:{name}")
                self.code.append(load_quad(f"{name}(%rip)"))
                self.stack += 8
                print(f"stack: {self.stack}")
            elif (
                node.info["type"] in ("double", "str") and node.info["scope"] == "local"
            ):
                name = node.info["name"]
                self.code.append(f"# local var reference {node.info['type']}:{name}")
                self.code.append(load_quad(f"-{self.scope[name].offset}(%rbp)"))
                self.stack += 8
                print(f"stack: {self.stack}")
            else:
                print(
                    f'unprocessed var reference {node.info["scope"]} {node.info["type"]} {node.info["name"]}'
                )
            return node.info["type"]
        elif node.typ == "function definition":
            self.function = node.info["name"]
            self.code, self.fdefinitions = self.fdefinitions, self.code
            self.code.append(
                f"""
# fundef {node.info['name']}
        .text
        .globl {node.info['name']}
        .type   {node.info['name']}, @function
{node.info['name']}:
        pushq   %rbp         # stack is now 16 byte aligned (because of return address)
        movq    %rsp, %rbp
"""
            )
            print("]]]]]]]", node)
            self.scope = node.info["scope"]
            # reserve space for local vars and move args to stack
            size = self.processScope()
            self.code.append(
                f"""
        subq ${size},%rsp
"""
            )
            self.moveArgumentsToStack()

            self.process(node.e0)

            self.scope = {}
            self.code.append(
                f"""
end_{node.info['name']}:
        leave
        ret
        .size   {node.info['name']}, .-{node.info['name']}
"""
            )
            self.code, self.fdefinitions = self.fdefinitions, self.code
        elif node.typ == "return":
            self.process(node.e0)
            self.code.append(pop_double(f"%xmm0"))
            self.stack -= 8
            self.code.append(f"        jmp end_{self.function}")
        else:
            print("unprocessed syntax node", node)

    def processScope(self):
        print("]]]]]]]]]]]]]", list(self.scope.items()))
        size = 0
        for name, symbol in self.scope.items():
            if symbol.type in ("double", "str"):
                size += 8
                symbol.offset = size
                print("@@@@", name, symbol, symbol.offset, size)
            else:
                print(f"unprocessed size for local symbol {name} ({symbol.type})")
        if size % 16:
            size += 8
        return size

    def moveArgumentsToStack(self):
        args = [symbol for name, symbol in self.scope.items() if symbol.isparameter]
        args.sort(key=lambda s: s.parameterindex)
        xmms = [f"%xmm{i}" for i in range(8)]
        regs = ["%rdi", "%rsi", "%rdx", "%rcx", "%r8", "%r9"]
        for symbol in args:
            print(">>>>>", symbol, symbol.offset)
            if symbol.type == "double":
                reg = xmms.pop(0)
                self.code.append(
                    f"""
# moving double argument {symbol.name} ({symbol.type}) to local stack frame
        movq {reg}, -{symbol.offset}(%rbp)
"""
                )
            elif symbol.type == "str":
                reg = regs.pop(0)
                self.code.append(
                    f"""
# moving string argument {symbol.name} ({symbol.type}) to local stack frame
        movq {reg}, -{symbol.offset}(%rbp)
"""
                )
            else:
                print(f"unprocessed argument {symbol.name} ({symbol.type})")

    def print(self, f):
        print("\n".join(self.code), file=f)
