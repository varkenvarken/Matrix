# Matrix, a simple programming language
# (c) 2022 Michel Anders
# License: MIT, see License.md
# Version: 20220308175453

from dataclasses import dataclass


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
        return f"{label:11s} {self.opcode:8s} {self.operands:12s}{comment}"


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
                return "# " + self.intro + "\n"
        if self.index < len(self.lines):
            self.index += 1
            return str(self.lines[self.index - 1])
        raise StopIteration

    def __str__(self):
        code = "\n".join(map(str, self.lines) if self.lines else "")
        if self.intro:
            return "# " + self.intro + "\n" + code
        return code


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
        intro="pop quad\n#" + str(intro),
        lines=[
            CodeLine(opcode="pop", operands="%rax"),
            CodeLine(opcode="movq", operands=f"%rax, {reg}", comment=linecomment),
        ],
    )


def push_quad(reg, intro=None, linecomment=None):
    return CodeChunk(
        intro="push quad\n#" + str(intro),
        lines=[
            CodeLine(opcode="movq", operands=f"{reg}, %rax", comment=linecomment),
            CodeLine(opcode="push", operands="%rax"),
        ],
    )


def store_quad(reg, intro=None, linecomment=None):
    return CodeChunk(
        intro="store quad\n#" + str(intro),
        lines=[
            CodeLine(opcode="pop", operands="%rax"),
            CodeLine(opcode="movq", operands=f"%rax, {reg}", comment=linecomment),
        ],
    )


def load_quad(reg, intro=None, linecomment=None):
    return CodeChunk(
        intro="load quad\n#" + str(intro),
        lines=[
            CodeLine(opcode="movq", operands=f"{reg}, %rax", comment=linecomment),
            CodeLine(opcode="push", operands="%rax"),
        ],
    )


def load_address(reg, intro=None, linecomment=None):
    return CodeChunk(
        intro="load address\n#" + str(intro),
        lines=[
            CodeLine(opcode="leaq", operands=f"{reg}, %rax", comment=linecomment),
            CodeLine(opcode="push", operands="%rax"),
        ],
    )
