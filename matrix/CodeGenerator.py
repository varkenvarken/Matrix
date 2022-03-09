# Matrix, a simple programming language
# (c) 2022 Michel Anders
# License: MIT, see License.md
# Version: 20220309144832

from .CodeSnippets import *


def vardefs(scope, defs):
    vars = "\n".join(
        "\n".join(line for line in v)
        for v in (vardef(d) for d in defs)
        if v is not None
    )
    if len(vars):
        return vars + "\n"
    return "# <no items>\n"


def symbol_defs(scope):
    consts = [
        val for key, val in scope.symbols.items() if val.const and not val.constoverride
    ]
    var = [
        val
        for key, val in scope.symbols.items()
        if (not val.const) or val.constoverride
    ]

    return (
        "# global constants\n"
        + vardefs(scope.scope, consts)
        + "# global variables\n"
        + vardefs(scope.scope, var)
    )


class CodeGenerator:
    def __init__(self, syntaxtree):
        self.ast = syntaxtree.tree
        self.symbols = syntaxtree.symbols
        self.code = []
        self.fdefinitions = []
        self.locals = []  # bit of a misnomer, static would prob. be better
        self.stack = 0
        self.filename = None
        self.filenumber = 0
        self.process(self.ast)
        self.code.append("# local constants defined in .text section")
        self.code.extend(self.locals)
        self.code.append(symbol_defs(syntaxtree.symbols))

    def adjust_stack(self):
        if self.stack != 0:
            self.code.append(f"        add ${self.stack}, %rsp")
            self.stack = 0

    def process(self, node):
        if node is None:
            return
        if node.filename is not None:
            if node.filename != self.filename:
                self.filename = node.filename
                self.filenumber += 1
                self.code.append(fileref(self.filenumber, self.filename))
            self.code.append(location(self.filenumber, node.lineno, node.index))
        if node.typ == "program":
            self.code.append(program_preamble())
            self.process(node.e0)
            self.code.append(program_postamble())
            self.code.append(convenience_constants())
            self.code.extend(self.fdefinitions)
        elif node.typ == "unit":
            self.stack = 0
            self.process(node.e0)
            self.adjust_stack()
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
                        self.code.append(
                            store_quad(
                                reg=f"{name}(%rip)",
                                intro="store in global var {name}",
                            )
                        )
                        self.stack -= 8
                else:
                    self.process(node.e1)
                    self.code.append(
                        store_quad(
                            reg=f"-{self.scope[name].offset}(%rbp)",
                            intro=f"store in local var {name}",
                        )
                    )
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
                        self.code.append(
                            pop_quad(
                                reg=f"{name}(%rip)",
                                intro=f"store in global var {name}",
                            )
                        )
                        self.stack -= 8
                else:
                    self.process(node.e1)
                    self.code.append(
                        pop_quad(
                            reg=f"-{self.scope[name].offset}(%rbp)",
                            intro=f"store in local var {name}",
                        )
                    )
                    self.stack -= 8
            else:
                print("unprocessed initializer for", node.info)
        elif node.typ == "unop":
            type0 = self.process(node.e0)
            if type0 == "double" and node.info["op"] == "uminus":
                self.code.append(unop_double_negate())
                return type0
            else:
                print(f"unprocessed unop {node.info['op']} for type {type0}")
        elif node.typ == "binop":
            type0 = self.process(node.e0)
            type1 = self.process(node.e1)
            if type0 != type1 or type0 is None or type1 is None:
                print(f"Incompatible types {type0} {type1} in node {node}")
                return
            if type0 == "double":
                if node.info["op"] == "plus":
                    self.code.append(
                        binop_double(binop="addsd", intro="add two doubles")
                    )
                else:
                    print("unprocessed binop for two doubles", node.info["op"])
                self.stack -= 8
                return "double"
            elif type0 == "str":
                if node.info["op"] == "plus":
                    self.code.append(
                        binop_str(binop="addstring", intro="add two strings")
                    )
                else:
                    print("unprocessed binop for two strings", node.info["op"])
                self.stack -= 8
                return "str"
        elif node.typ == "number":
            label, code = local_double_number(node.info)
            self.code.append(load_quad(reg=f"{label}(%rip)"))
            self.stack += 8
            self.locals.append(code)
            return "double"
        elif node.typ == "stringliteral":
            label, code = local_string(node.info)
            self.code.append(load_address(reg=f"{label}(%rip)"))
            self.stack += 8
            self.locals.append(code)
            return "str"
        elif node.typ == "call":
            returntype = node.info["type"]
            name = node.info["name"]
            self.code.append(f"# function call {name}")
            an = 0
            arg = node.e0
            assert arg.typ == "argument"
            argtypes = []
            while arg:
                self.code.append(f"# calculate argument {an}")
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
            self.code.append(f"# popping {an} arguments usign x64 convention")
            for i in range(an):
                self.code.append(pop_quad(reg=argregisters.pop()))
                self.stack -= 8
            self.adjust_stack()
            self.code.append(function_call(name, returntype, an))
            if returntype in ("double", "str"):
                self.stack += 8
            elif returntype == "void":
                pass
            else:
                print(f"return type {returntype} ignored for now")
            return returntype
        elif node.typ == "var reference":
            if (
                node.info["type"] in ("double", "str")
                and node.info["scope"] == "global"
            ):
                name = node.info["name"]
                self.code.append(
                    load_quad(
                        reg=f"{name}(%rip)",
                        linecomment=f"global var reference {node.info['type']}:{name}",
                    )
                )
                self.stack += 8
            elif (
                node.info["type"] in ("double", "str") and node.info["scope"] == "local"
            ):
                name = node.info["name"]
                self.code.append(
                    load_quad(
                        reg=f"-{self.scope[name].offset}(%rbp)",
                        linecomment=f"local var reference {node.info['type']}:{name}",
                    )
                )
                self.stack += 8
            else:
                print(
                    f'unprocessed var reference {node.info["scope"]} {node.info["type"]} {node.info["name"]}'
                )
            return node.info["type"]
        elif node.typ == "function definition":
            self.function = node.info["name"]
            # function definitions should not appear in the middel of the main code
            # so we keep separate sets of generated code lines
            self.code, self.fdefinitions = self.fdefinitions, self.code
            self.scope = node.info["scope"]
            # calculate space for local vars and calc their offsets
            size = self.processScope()
            self.code.append(function_preamble(self.function, size))
            self.moveArgumentsToStack()
            # process the function body
            self.process(node.e0)
            self.scope = {}
            self.code.append(function_postamble(self.function))
            self.code, self.fdefinitions = self.fdefinitions, self.code
        elif node.typ == "return":
            self.process(node.e0)
            self.code.append(pop_quad(reg=f"%xmm0"))
            self.stack -= 8
            self.code.append(f"        jmp end_{self.function}")
        else:
            print("unprocessed syntax node", node)

    def processScope(self):
        """calculate offsets if automatic (local) variables
        and return the total amount of space to reserve on the stack."""
        size = 0
        for name, symbol in self.scope.items():
            if symbol.type in ("double", "str"):
                size += 8
                symbol.offset = size
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
            if symbol.type == "double":
                reg = xmms.pop(0)
                self.code.append(
                    store_argument(reg, symbol.offset, symbol.name, symbol.type)
                )
            elif symbol.type == "str":
                reg = regs.pop(0)
                self.code.append(
                    store_argument(reg, symbol.offset, symbol.name, symbol.type)
                )
            else:
                print(f"unprocessed argument {symbol.name} ({symbol.type})")

    def print(self, f):
        for c in self.code:
            if type(c) == str:
                print(c, file=f)
            elif type(c) == CodeChunk:
                for line in c:
                    print(line.rstrip(), file=f)
            else:
                print("unknown code line", c)
