# Matrix, a simple programming language
# (c) 2022 Michel Anders
# License: MIT, see License.md
# Version: 20220308145355

from sly.yacc import YaccSymbol


class ParseNode:

    _id = 0  # redefine this one in a derived class to get a unique counter

    @classmethod
    def generateId(cls):
        cls._id += 1
        return cls._id

    @staticmethod
    def getLine(production):
        for tok in production._slice:
            if isinstance(tok, YaccSymbol):
                continue
            line = getattr(tok, "line", None)
            if line:
                return line
        return ""

    def __init__(
        self, token, value=None, e0=None, e1=None, e2=None, level=0, prod=None
    ) -> None:
        self.id = self.generateId()
        self.token = token
        self.value = value
        self.e0 = e0
        self.e1 = e1
        self.e2 = e2
        self.level = level
        if prod:
            self.lineno = getattr(prod, "lineno", None)
            self.line = ParseNode.getLine(prod)
            self.index = getattr(prod, "index", 0)
        else:
            self.lineno = None
            self.line = ""
            self.index = 0

    def src(self):
        return dict(lineno=self.lineno, index=self.index, line=self.line)

    def __str__(self):
        lineno = f"@{self.lineno:4d}:{self.index:3d}" if self.lineno else ""
        enmap = ", ".join(
            f"e{n} -> [{en.id:4d}]"
            for n, en in enumerate((self.e0, self.e1, self.e2))
            if en
        )
        line = self.line.rstrip("\n")
        return (
            f"({self.token}:{self.value if self.value else ''}) {enmap} {lineno}:{line}"
        )

    def walk(self, level=0):
        self.level = level
        yield self
        if self.e0:
            for node in self.e0.walk(level + 1):
                yield node
        if self.e1:
            for node in self.e1.walk(level + 1):
                yield node
        if self.e2:
            for node in self.e2.walk(level + 1):
                yield node


class SyntaxNode:
    _id = 0

    @classmethod
    def generateId(cls):
        cls._id += 1
        return cls._id

    def __init__(
        self, typ, info, e0=None, e1=None, e2=None, level=0, lineno=0, index=0, line=""
    ):
        self.id = self.generateId()
        self.typ = typ
        self.info = info
        self.e0 = e0
        self.e1 = e1
        self.e2 = e2
        self.level = level
        self.lineno = lineno
        self.index = index
        self.line = line

    def __str__(self):
        enmap = ", ".join(
            f"e{n} -> [{en.id:4d}]"
            for n, en in enumerate((self.e0, self.e1, self.e2))
            if en
        )
        newline = "\n"
        lineinfo = (
            ""
            if self.lineno is None or self.index == 0
            else f"@|{self.lineno}:{self.index}:{self.line.rstrip(newline)}"
        )
        return f"({self.typ}:{self.info}) {enmap} {lineinfo}"
