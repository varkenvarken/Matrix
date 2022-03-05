# Matrix, a simple programming language
# (c) 2022 Michel Anders
# License: MIT, see License.md
# Version: 20220305105607

from re import compile, search

from sly import Lexer
from sly.lex import Token


class MatrixLexer(Lexer):
    tokens = {
        NAME,
        NUMBER,
        STRINGLITERAL,
        FUN,
        LONG,
        FLOAT,
        DOUBLE,
        STRING,
        MATRIX,
        VECTOR,
        FLOATMATRIX,
        FLOATVECTOR,
        VOID,
        NEWLINE,
        IF,
        ELSE,
        EXTERN,
        RETURN,
        WHILE,
        BREAK,
        CONTINUE,
        INDENT,
        DEDENT,
        PLUS,
        MINUS,
        EQUAL,
        NOTEQUAL,
        LESS,
        GREATER,
        LESSOREQUAL,
        GREATEROREQUAL,
        MATMUL,
        MODULO,
        DOT,
        POWER,
        ROOT,
        CROSS,
        LBRACKET,
        RBRACKET,
        COLON,
        FOR,
        IN,
        CONST,
    }

    ignore = " \t"
    ignore_comment = r"((\#)|(//)).*"
    literals = {"=", "*", "/", "(", ")", ","}

    # Tokens
    NAME = r"[a-zA-Z_][a-zA-Z0-9_]*"
    NAME["fun"] = FUN
    NAME["long"] = LONG
    NAME["extern"] = EXTERN
    NAME["return"] = RETURN
    NAME["if"] = IF
    NAME["else"] = ELSE
    NAME["while"] = WHILE
    NAME["break"] = BREAK
    NAME["continue"] = CONTINUE
    NAME["float"] = FLOAT
    NAME["double"] = DOUBLE
    NAME["str"] = STRING
    NAME["mat"] = MATRIX
    NAME["vec"] = VECTOR
    NAME["matf"] = FLOATMATRIX
    NAME["vecf"] = FLOATVECTOR
    NAME["void"] = VOID
    NAME["in"] = IN
    NAME["for"] = FOR
    NAME["const"] = CONST

    @_(r"[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?")
    # @_(r"[0-9]+")
    def NUMBER(self, t):
        t.value = float(t.value)
        return t

    STRINGLITERAL = r'"[^"\\\r\n]*(?:\\.[^"\\\r\n]*)*"'  # see: https://www.regular-expressions.info/examplesprogrammer.html
    PLUS = r"\+"
    MINUS = r"-"
    EQUAL = r"=="
    NOTEQUAL = r"!="
    LESS = r"\<"
    GREATER = r"\>"
    LESSOREQUAL = r"\<="
    GREATEROREQUAL = r"\>="
    MATMUL = r"@"
    MODULO = r"%"
    DOT = r"\."
    POWER = r"\*\*"
    ROOT = r"√"
    CROSS = r"×"
    LBRACKET = r"\["
    RBRACKET = r"\]"
    COLON = r":"

    @_(r"\n+")
    def NEWLINE(self, t):
        self.lineno += t.value.count("\n")
        return t

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1

    def tokenizeFromInputStream(self, stream):
        """
        Tokenize from an iterator that yields lines.
        """

        def leading_space(s):
            """
            Return leading whitespace part from s.

            Whitespace is defined as space or tab
            """
            nonws = compile(r"[^ \t]")
            if m := search(nonws, s):
                return s[: m.start()]
            return ""

        indent = [""]
        level = 0
        for lineno, line in enumerate(stream):
            space = leading_space(line)

            # print(f"\nspace{len(space)}:>>>{line}")
            # print(level)
            # for l, s in enumerate(indent):
            #    print(l, f"[{s}]")

            if len(space) == 0:
                while level > 0:
                    level -= 1
                    indent.pop()
                    tok = Token()
                    tok.type = "DEDENT"
                    tok.value = ""
                    tok.lineno = lineno + 1
                    tok.index = 0
                    yield tok
                    # tok = Token()
                    # tok.type = "NEWLINE"
                    # tok.value = "\n"
                    # tok.lineno = lineno + 1
                    # tok.index = 0
                    # yield tok
            elif space != indent[-1]:
                tok = Token()
                tok.value = space
                tok.lineno = lineno + 1
                tok.index = 0
                if len(space) > len(indent[-1]):
                    tok.type = "INDENT"
                    level += 1
                    indent.append(space)
                elif len(space) < len(indent[-1]):
                    tok.type = "DEDENT"
                    level -= 1
                    indent.pop()
                else:  # same length but mixed spaces and tabes
                    tok.type = "ERROR"
                yield tok
            for token in self.tokenize(line, lineno=lineno + 1):
                lastline = token.lineno
                yield token

        # return any number of missing DEDENT tokens at the end of the stream
        for i in range(level):
            tok = Token()
            tok.type = "DEDENT"
            tok.value = ""
            tok.lineno = lineno + 1
            tok.index = 0
            yield tok

        # and yield an extra newline
        tok = Token()
        tok.type = "NEWLINE"
        tok.value = "\n"
        tok.lineno = lineno + 1
        tok.index = 0
        yield tok
