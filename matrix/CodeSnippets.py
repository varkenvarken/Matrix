# Matrix, a simple programming language
# (c) 2022 Michel Anders
# License: MIT, see License.md
# Version: 20220309133451

from argparse import ArgumentError
from cProfile import label
from dataclasses import dataclass
from xml.etree.ElementTree import Comment

import opcode


@dataclass
class CodeLine:
    label: str = ""
    opcode: str = ""
    operands: str = ""
    comment: str = None

    def __str__(self):
        if self.comment is None or self.comment == "":
            comment = ""
        else:
            comment = " # " + self.comment.rstrip("\n")
        label = self.label + ":" if self.label is not None and self.label != "" else ""
        return f"{label:15s} {self.opcode:8s} {self.operands:16s}{comment}"


class CodeChunk:
    def __init__(self, intro=None, lines=None) -> None:
        self.lines = lines if lines else []
        self.intro = intro

    def __iter__(self):
        self.showintro = True
        self.index = 0
        return self

    def __next__(self):
        if self.showintro:
            self.showintro = False
            if self.intro:
                return "\n".join("# " + i for i in self.intro.split("\n"))
        if self.index < len(self.lines):
            self.index += 1
            return str(self.lines[self.index - 1])
        raise StopIteration

    def __str__(self):
        print("&&&&&&&&&&&&", self.intro)
        code = "\n".join(map(str, self.lines) if self.lines else "")
        if self.intro:
            return "# " + self.intro + "\n" + code
        return code

    def __add__(self, other):
        if type(other) != CodeChunk:
            raise ArgumentError
        if self.intro:
            intro = self.intro + (("\n" + other.intro) if other.intro else "")
        else:
            intro = other.intro
        return CodeChunk(intro=intro, lines=self.lines + other.lines)


def program_preamble():
    return CodeChunk(
        intro="main preamble",
        lines=[
            CodeLine(opcode=".text"),
            CodeLine(opcode=".globl", operands="main"),
            CodeLine(opcode=".type", operands="main, @function"),
            CodeLine(label="main"),
            CodeLine(opcode="pushq", operands="%rbp"),
            CodeLine(opcode="movq", operands="%rsp, %rbp"),
        ],
    )


def program_postamble():
    return CodeChunk(
        intro="main postamble",
        lines=[
            CodeLine(opcode=".globl", operands="end_main"),
            CodeLine(opcode="xor", operands="%rax,%rax", comment="zero exit code"),
            CodeLine(label="end_main"),
            CodeLine(opcode="popq", operands="%rbp"),
            CodeLine(opcode="ret"),
            CodeLine(opcode=".size", operands="main, .-main"),
        ],
    )


def convenience_constants():
    return CodeChunk(
        intro="convenience constants",
        lines=[
            CodeLine(opcode=".p2align", operands="3"),
            CodeLine(label=".DOUBLENEGATE", comment="to negate a double with xorpd"),
            CodeLine(opcode=".long", operands="0"),
            CodeLine(opcode=".long", operands="-2147483648"),
            CodeLine(opcode=".long", operands="0"),
            CodeLine(opcode=".long", operands="0"),
        ],
    )


def pop_quad(reg, intro=None, linecomment=None):
    return CodeChunk(
        intro=intro,
        lines=[
            CodeLine(opcode="pop", operands="%rax"),
            CodeLine(opcode="movq", operands=f"%rax, {reg}", comment=linecomment),
        ],
    )


def push_quad(reg, intro=None, linecomment=None):
    return CodeChunk(
        intro=intro,
        lines=[
            CodeLine(opcode="movq", operands=f"{reg}, %rax", comment=linecomment),
            CodeLine(opcode="push", operands="%rax"),
        ],
    )


def store_quad(reg, intro=None, linecomment=None):
    return CodeChunk(
        intro=intro,
        lines=[
            CodeLine(opcode="pop", operands="%rax"),
            CodeLine(opcode="movq", operands=f"%rax, {reg}", comment=linecomment),
        ],
    )


def load_quad(reg, intro=None, linecomment=None):
    return CodeChunk(
        intro=intro,
        lines=[
            CodeLine(opcode="movq", operands=f"{reg}, %rax", comment=linecomment),
            CodeLine(opcode="push", operands="%rax"),
        ],
    )


def load_address(reg, intro=None, linecomment=None):
    return CodeChunk(
        intro=intro,
        lines=[
            CodeLine(opcode="leaq", operands=f"{reg}, %rax", comment=linecomment),
            CodeLine(opcode="push", operands="%rax"),
        ],
    )


def unop_double_negate(intro=None, linecomment=None):
    return CodeChunk(
        intro=intro,
        lines=[
            CodeLine(opcode="movq", operands=f"(%rsp), %xmm0", comment=linecomment),
            CodeLine(
                opcode="movq",
                operands=".DOUBLENEGATE(%rip), %xmm1",
                comment="flip sign bit of xmm0",
            ),
            CodeLine(opcode="xorpd", operands="%xmm1, %xmm0"),
            CodeLine(opcode="movq", operands="%xmm0, (%rsp)"),
        ],
    )


def binop_double(binop, intro=None, linecomment=None):
    pop0 = pop_quad(reg="%xmm0", intro=intro)
    pop1 = pop_quad(reg="%xmm1")
    binop = CodeChunk(
        lines=[
            CodeLine(opcode=binop, operands=f"%xmm1, %xmm0", comment=linecomment),
        ],
    )
    push = push_quad(reg="%xmm0")
    return pop0 + pop1 + binop + push


def binop_str(binop, intro=None, linecomment=None):
    pop0 = pop_quad(reg="%rsi", intro=intro)
    pop1 = pop_quad(reg="%rdi")
    binop = CodeChunk(
        lines=[
            CodeLine(opcode="call", operands=f"{binop}", comment=linecomment),
        ],
    )
    push = push_quad(reg="%rax")
    return pop0 + pop1 + binop + push


local_doubles = -1


def local_double_number(number):
    global local_doubles
    local_doubles += 1
    label = f".LDN{local_doubles}"
    code = CodeChunk(
        lines=[
            CodeLine(opcode=".p2align", operands="3"),
            CodeLine(
                label=label,
                opcode=".double",
                operands=str(number if number is not None else 0.0),
            ),
        ]
    )
    return label, code


# TODO: escape any embedded quotes?
local_strings = -1

# note that string literals have already quotes around them
def local_string(s):
    global local_strings
    local_strings += 1
    label = f".LS{local_strings}"
    code = CodeChunk(
        lines=[
            CodeLine(label=label, opcode=".string", operands=s if s is not None else "")
        ]
    )
    return label, code


def function_call(name, returntype, an=0, intro=None):
    nargs = CodeChunk(
        intro=intro,
        lines=[
            CodeLine(
                opcode="movq",
                operands=f"${an},%rax",
                comment="number of arguments, only needed when calling varargs",
            )
        ],
    )
    call = CodeChunk(
        lines=[
            CodeLine(
                opcode="call",
                operands=name,
                comment="void return type, nothing to push"
                if returntype == "void"
                else None,
            )
        ]
    )
    if an >= 0:
        call = nargs + call
    if returntype != "void":
        call = call + push_quad(reg="%xmm0" if returntype == "double" else "%rax")
    return call


def function_preamble(name, size):
    return CodeChunk(
        intro=f"function definition {name}",
        lines=[
            CodeLine(opcode=".text"),
            CodeLine(opcode=".globl", operands=name),
            CodeLine(opcode=".type", operands=f"{name}, @function"),
            CodeLine(label=name),
            CodeLine(
                opcode="pushq",
                operands="%rbp",
                comment="stack will now be 16 byte aligned (because of return address)",
            ),
            CodeLine(opcode="movq", operands="%rsp, %rbp"),
            CodeLine(
                opcode="subq",
                operands=f"${size}, %rsp",
                comment="reserve space for automatic (local) vars",
            ),
        ],
    )


def function_postamble(name):
    return CodeChunk(
        lines=[
            CodeLine(label=f"end_{name}", opcode="leave"),
            CodeLine(opcode="ret"),
            CodeLine(opcode=".size", operands=f"{name}, .-{name}"),
        ]
    )


def store_argument(reg, offset, name, type):
    return CodeChunk(
        lines=[
            CodeLine(
                opcode="movq",
                operands=f"{reg}, -{offset}(%rbp)",
                comment=f"moving argument {name} ({type}) to local stack frame",
            )
        ]
    )


def vardef(v):
    if v.type == "double":
        code = CodeChunk(
            lines=[
                CodeLine(opcode=f".global {v.name}"),
                CodeLine(
                    opcode=".section",
                    operands=".rodata" if v.const and not v.constoverride else ".data",
                ),
                CodeLine(opcode=".p2align 3"),
                CodeLine(opcode=".type", operands=f"{v.name}, @object"),
                CodeLine(opcode=".size", operands=f"{v.name}, 8"),
                CodeLine(label=v.name),
                CodeLine(
                    opcode=".double",
                    operands=f"{v.value if v.value is not None else 0.0}",
                ),
            ]
        )
    if v.type == "str":
        code = CodeChunk(
            lines=[
                CodeLine(opcode=f".global {v.name}"),
                CodeLine(opcode=".section", operands=".rodata"),
                CodeLine(opcode=".p2align", operands="3"),
                CodeLine(opcode=".type", operands=f"{v.name}, @object"),
                CodeLine(opcode=".size", operands=f"{v.name}, 8"),
                CodeLine(label=v.name),
                CodeLine(
                    opcode=".quad",
                    operands=f". + 8",
                    comment="string variables and constants are pointers",
                ),
                CodeLine(opcode=".string", operands=f"{v.value}"),
                CodeLine(opcode=".size", operands=f"{v.name}, .-{v.name}"),
            ]
        )
    elif v.type == "function":
        return None
    return code
