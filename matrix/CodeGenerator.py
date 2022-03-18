# Matrix, a simple programming language
# (c) 2022 Michel Anders
# License: MIT, see License.md
# Version: 20220318154604

from sys import stderr

from .CodeSnippets import *
from .Syntax import Scope


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
            self.code.append(stack_adjust(self.stack))
            self.stack = 0

    def align_stack(self):
        if self.stack % 16:
            return 8
        return 0

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
                                intro=f"store in global var {name}",
                            )
                        )
                        self.stack -= 8
                else:
                    self.process(node.e1)
                    self.code.append(
                        store_quad(
                            reg=f"-{self.symbols[name].offset}(%rbp)",
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
                            reg=f"-{self.symbols[name].offset}(%rbp)",
                            intro=f"store in local var {name}",
                        )
                    )
                    self.stack -= 8
            elif node.info == "mat":
                what = node.e0.info
                name = what[1]
                scope = what[0]
                if scope == "global":
                    if node.e1.typ == "matrixliteral":
                        litname, chunk = globalMatInit(self.symbols[name], node.e1.info)
                        self.locals.append(chunk)
                        self.code.append(matCopy(litname, name))
                    else:  # initializer expression
                        self.symbols[name].constoverride = True
                        typ = self.process(node.e1)
                        if typ == "double":
                            print(
                                f"mat initializer expression of type {typ} ignored for now"
                            )
                        elif typ == "mat":
                            self.code.append(
                                store_quad(
                                    reg=f"{name}(%rip)",
                                    intro=f"store in global var {name}",
                                )
                            )
                            self.stack -= 8
                        else:
                            print(f"illegal mat intializer expression of type {typ}")
                else:
                    self.process(node.e1)
                    self.code.append(
                        pop_quad(
                            reg=f"-{self.symbols[name].offset}(%rbp)",
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
            elif type0 == "mat":
                if node.info["op"] == "uminus":
                    self.code.append(
                        unop_mat(unop="matrix_negate", intro="negate a matrix")
                    )
            else:
                print(f"unprocessed unop {node.info['op']} for type {type0}")
        elif node.typ == "binop":
            type0 = self.process(node.e0)
            type1 = self.process(node.e1)
            if type0 != type1 or type0 is None or type1 is None:
                if type0 == "mat" and type1 == "double":
                    self.code.append(scalar_to_mat(self.align_stack()))
                    type1 = "mat"
                elif type0 == "double" and type1 == "mat":
                    self.code.append(scalar_to_mat_top1(self.align_stack()))
                    type0 = "mat"
                else:
                    print(f"Incompatible types {type0} {type1} in node {node}")
                    return
            if type0 == "double":
                if node.info["op"] == "plus":
                    self.code.append(
                        binop_double(binop="addsd", intro="add two doubles")
                    )
                elif node.info["op"] == "minus":
                    self.code.append(
                        binop_double(binop="subsd", intro="subtract two doubles")
                    )
                elif node.info["op"] == "*":
                    self.code.append(
                        binop_double(binop="mulsd", intro="subtract two doubles")
                    )
                elif node.info["op"] == "/":
                    self.code.append(
                        binop_double(binop="divsd", intro="subtract two doubles")
                    )
                elif node.info["op"] == "%":
                    self.code.append(modulo_double())
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
            elif type0 == "mat":
                if node.info["op"] == "plus":
                    self.code.append(
                        binop_mat(binop="matrix_add", intro="add two matrices")
                    )
                elif node.info["op"] == "minus":
                    self.code.append(
                        binop_mat(
                            binop="matrix_subtract", intro="subtract two matrices"
                        )
                    )
                elif node.info["op"] == "*":
                    self.code.append(
                        binop_mat(
                            binop="matrix_multiply", intro="multiply two matrices"
                        )
                    )
                elif node.info["op"] == "/":
                    self.code.append(
                        binop_mat(binop="matrix_divide", intro="divide two matrices")
                    )
                elif node.info["op"] == "%":
                    self.code.append(
                        binop_mat(binop="matrix_modulo", intro="divide two matrices")
                    )
                else:
                    print("unprocessed binop for two matrices", node.info["op"])
                self.stack -= 8
                return "mat"
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
        elif node.typ == "matrixliteral":
            label, code = local_matrix(node.info)
            self.code.append(
                load_quad(reg=f"{label}(%rip)")
            )  # not load_address because we need to dereference the pointer to the matrix decriptor
            self.stack += 8
            self.locals.append(code)
            return "mat"
        elif node.typ == "call":
            returntype = node.info["type"]
            name = node.info["name"]
            self.code.append(f"# function call {name}")
            an = 0
            arg = node.e0
            if arg is not None:  # empty parameter list is allowed
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
                self.code.append(f"# popping {an} arguments using the x64 convention")
                for i in range(an):
                    self.code.append(pop_quad(reg=argregisters.pop()))
                    self.stack -= 8
                # TODO: this should align the stack, NOT remove anything
            self.code.append(function_call(name, returntype, an, self.align_stack()))
            if returntype in ("double", "str", "mat"):
                self.stack += 8
            elif returntype == "void":
                pass
            else:
                print(f"return type {returntype} ignored for now")
            return returntype
        elif node.typ == "var reference":
            if (
                node.info["type"] in ("double", "str", "mat")
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
                if node.e0 is not None:
                    assert node.e0.typ == "indexlist"
                    indexlist = node.e0
                    last_was_slice = 0
                    while indexlist is not None:
                        index_or_slice = indexlist.e0
                        indexlist = indexlist.e1
                        if index_or_slice.typ == "index":
                            if last_was_slice > 0:
                                self.code.append(
                                    slice_matrix(self.align_stack(), last_was_slice)
                                )
                                self.stack -= 8 * last_was_slice * 3
                                last_was_slice = 0
                            self.process(index_or_slice.e0)
                            self.code.append(index_matrix(self.align_stack()))
                            self.stack -= 8
                        elif index_or_slice.typ == "slice":
                            self.process(index_or_slice.e0)
                            self.process(index_or_slice.e1)
                            self.process(index_or_slice.e2)
                            last_was_slice += 1
                        else:
                            print(
                                f"index type of {index_or_slice.typ} ignored on {name}"
                            )
                    if last_was_slice > 0:
                        self.code.append(
                            slice_matrix(self.align_stack(), last_was_slice)
                        )
                        self.stack -= 8 * last_was_slice * 3
                        last_was_slice = 0

            elif (
                node.info["type"] in ("double", "str", "mat")
                and node.info["scope"] == "local"
            ):
                name = node.info["name"]
                self.code.append(
                    load_quad(
                        reg=f"-{self.symbols[name].offset}(%rbp)",
                        linecomment=f"local var reference {node.info['type']}:{name}",
                    )
                )
                self.stack += 8
                if node.e0 is not None:
                    assert node.e0.typ == "indexlist"
                    print(f"unprocessed local slice/index {name}")
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
            self.symbols = Scope(outer=self.symbols)
            self.symbols.symbols.update(node.info["scope"])
            # calculate space for local vars and calc their offsets
            size = self.processScope()
            self.code.append(function_preamble(self.function, size))
            self.moveArgumentsToStack()
            # process the function body
            self.process(node.e0)
            self.symbols = self.symbols.outer
            self.code.append(function_postamble(self.function))
            self.code, self.fdefinitions = self.fdefinitions, self.code
        elif node.typ == "return":
            rtype = self.process(node.e0)
            self.code.append(pop_quad(reg=f"{'%xmm0' if rtype=='double' else '%rax'}"))
            self.stack -= 8
            self.code.append(f"        jmp end_{self.function}")
        elif node.typ == "assign":
            symbol = self.symbols[node.info]
            # Note that assignment is an expression so we do not pop the stack
            if (
                symbol.type == "mat" and node.e0 is not None and node.e0.e0 is not None
            ):  # assignment to indexed matrix
                symbol = self.symbols[node.info]
                if symbol.scope == "global":
                    assert node.e0.e0.typ == "indexlist"
                    indexlist = node.e0.e0
                    last_was_slice = 0
                    self.code.append(
                        load_quad(
                            intro="Assignment to index matrix",
                            reg=f"{symbol.name}(%rip)",
                            linecomment=f"global var reference {symbol.name}",
                        )
                    )
                    self.stack += 8
                    while indexlist is not None:
                        index_or_slice = indexlist.e0
                        indexlist = indexlist.e1
                        if index_or_slice.typ == "index":
                            if last_was_slice > 0:
                                self.code.append(
                                    slice_matrix(self.align_stack(), last_was_slice)
                                )
                                self.stack -= 8 * last_was_slice * 3
                                last_was_slice = 0
                            self.process(index_or_slice.e0)
                            self.code.append(index_matrix(self.align_stack()))
                            self.stack -= 8
                        elif index_or_slice.typ == "slice":
                            self.process(index_or_slice.e0)
                            self.process(index_or_slice.e1)
                            self.process(index_or_slice.e2)
                            last_was_slice += 1
                        else:
                            print(
                                f"index type of {index_or_slice.typ} ignored on {symbol.name}"
                            )
                    if last_was_slice > 0:
                        self.code.append(
                            slice_matrix(self.align_stack(), last_was_slice)
                        )
                        self.stack -= 8 * last_was_slice * 3
                        last_was_slice = 0
                    typ = self.process(node.e1)
                    assert symbol.type == typ
                    # at this point we have a matrixliteral on the top of the stack
                    # and a view into the destination matrix just below it (TODO: check if dimensions match)
                    self.code.append(matCopy2())
                    self.stack -= 8
                else:
                    print(
                        f"local indexed matrix assignment to {symbol.name} ignored for now"
                    )
            else:
                typ = self.process(node.e1)
                assert symbol.type == typ
                if symbol.scope == "global":
                    self.code.append(
                        move_quad(
                            reg=f"{symbol.name}(%rip)",
                            intro=f"store in global var {symbol.name}",
                        )
                    )
                else:
                    self.code.append(
                        move_quad(
                            reg=f"-{self.symbols[symbol.name].offset}(%rbp)",
                            intro=f"store in local var {symbol.name}",
                        )
                    )
        elif node.typ == "if":
            etype = self.process(node.e0)
            # TODO: verify etype is double
            else_label = labels["else"]
            end_label = labels["endif"]
            self.code.append(
                jump_if_false(else_label if node.e2 is not None else end_label)
            )
            self.stack -= 8
            self.process(node.e1)
            if node.e2 is not None:
                self.code.append(jump(end_label))
                self.code.append(labelCode(else_label))
                self.process(node.e2)
            self.code.append(labelCode(end_label))
        elif node.typ == "while":
            while_label = labels["while"]
            end_label = labels["endwhile"]
            self.code.append(labelCode(while_label))
            etype = self.process(node.e0)
            # TODO: verify etype is double
            self.code.append(jump_if_false(end_label))
            self.stack -= 8
            self.process(node.e1)
            self.code.append(jump(while_label))
            self.code.append(labelCode(end_label))
        elif node.typ == "for":
            for_label = labels["for"]
            end_label = labels["endfor"]
            etype = self.process(node.e0)  # get the range
            self.code.append(pushZero())  # start index
            self.stack -= 8  # we discount the expression result pushed by node.e0 because we keep the two on stack across the body
            # self.stack += 16  we do NOT count these because that would mess up stack corrections in units inside the body
            self.code.append(labelCode(for_label))
            self.code.append(jump_if_end_of_range(self.align_stack(), end_label))
            self.code.append(getItemAndInc(self.align_stack()))
            self.stack += 8
            # assign to variable
            symbol = self.symbols[node.info["name"]]
            if symbol.scope == "global":
                self.code.append(
                    move_quad(
                        reg=f"{symbol.name}(%rip)",
                        intro=f"store in global var {symbol.name}",
                    )
                )
            else:
                self.code.append(
                    move_quad(
                        reg=f"-{self.symbols[symbol.name].offset}(%rbp)",
                        intro=f"store in local var {symbol.name}",
                    )
                )
            self.code.append(
                pop(1)
            )  # this assignment inside a for loop is NOT an expression that stays on the stack
            self.stack -= 8
            self.process(node.e1)
            self.code.append(jump(for_label))
            self.code.append(labelCode(end_label))
            self.code.append(pop(2))
            # self.stack -=8  no correction we didn count the 2 arguments (and they are 16 bytes together)
        else:
            print("unprocessed syntax node", node)

    def processScope(self):
        """calculate offsets if automatic (local) variables
        and return the total amount of space to reserve on the stack."""
        size = 0
        for name, symbol in self.symbols.symbols.items():
            if symbol.type in ("double", "str", "mat"):
                size += 8
                symbol.offset = size
            else:
                print(f"unprocessed size for local symbol {name} ({symbol.type})")
        if size % 16:
            size += 8
        return size

    def moveArgumentsToStack(self):
        args = [
            symbol
            for name, symbol in self.symbols.symbols.items()
            if symbol.isparameter
        ]
        args.sort(key=lambda s: s.parameterindex)
        xmms = [f"%xmm{i}" for i in range(8)]
        regs = ["%rdi", "%rsi", "%rdx", "%rcx", "%r8", "%r9"]
        for symbol in args:
            if symbol.type == "double":
                reg = xmms.pop(0)
                self.code.append(
                    store_argument(reg, symbol.offset, symbol.name, symbol.type)
                )
            elif symbol.type in ("str", "mat"):
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
