# Matrix, a simple programming language
# (c) 2022 Michel Anders
# License: MIT, see License.md
# Version: 20220319110310

from re import compile, match, search

from sly import Lexer
from sly.lex import Token


class MatrixToken(Token):
    def __init__(self) -> None:
        super().__init__()
        self.line = ""
        self.filename = ""

    @staticmethod
    def fromToken(tok):
        token = MatrixToken()
        token.type = tok.type
        token.value = tok.value
        token.lineno = tok.lineno
        token.index = tok.index
        return token

    def __str__(self):
        return f"{self.type} {self.value} {self.filename}:{self.lineno}:{self.index}"


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
        APLUS,
        AMINUS,
        AMUL,
        ADIV,
        AMOD,
        ASSERT,
    }

    ignore = " \t"
    ignore_comment = r"((\#)|(//)).*"
    literals = {"=", "*", "/", "(", ")", ","}

    STRINGLITERAL = r'f?"[^"\\\r\n]*(?:\\.[^"\\\r\n]*)*"'  # see: https://www.regular-expressions.info/examplesprogrammer.html

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
    NAME["assert"] = ASSERT

    @_(r"[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?")
    # @_(r"[0-9]+")
    def NUMBER(self, t):
        t.value = float(t.value)
        return t

    # longest first!
    APLUS = r"\+="
    AMINUS = r"\-="
    AMUL = r"\*="
    ADIV = r"/="
    AMOD = r"%="
    PLUS = r"\+"
    MINUS = r"-"
    POWER = r"\*\*"
    EQUAL = r"=="
    NOTEQUAL = r"!="
    LESSOREQUAL = r"\<="
    GREATEROREQUAL = r"\>="
    LESS = r"\<"
    GREATER = r"\>"
    MATMUL = r"@"
    MODULO = r"%"
    DOT = r"\."
    ROOT = r"???"
    CROSS = r"??"
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

    empty_line_pattern = compile(r"\s*(((\#)|(//)).*)?$")

    @staticmethod
    def is_empty(line):
        m = match(MatrixLexer.empty_line_pattern, line)
        return m is not None

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

        filename = "<unknown>"
        indent = [""]
        level = 0
        holdback = None
        inside_list = 0

        for lineno, line in enumerate(stream):

            if inside_list == 0:  # no indent/dedent processing inside lists
                if MatrixLexer.is_empty(line):
                    tok = MatrixToken()
                    tok.type = "NEWLINE"
                    tok.value = "\n"
                    tok.lineno = lineno
                    tok.index = 0
                    tok.line = line
                    tok.filename = filename
                    holdback = tok
                    continue

                space = leading_space(line)
                lineno -= 1
                try:
                    filename = stream.filename()
                    lineno = stream.filelineno()
                except AttributeError as e:
                    print(e)
                    pass

                if len(space) == 0:
                    while level > 0:
                        level -= 1
                        indent.pop()
                        tok = MatrixToken()
                        tok.type = "DEDENT"
                        tok.value = ""
                        tok.lineno = lineno
                        tok.index = 0
                        tok.line = line
                        tok.filename = filename
                        yield tok
                elif space != indent[-1]:
                    tok = MatrixToken()
                    tok.value = space
                    tok.lineno = lineno
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
                    tok.line = line
                    tok.filename = filename
                    yield tok

                if holdback is not None:
                    yield holdback
                    holdback = None

            for token in self.tokenize(line, lineno=lineno):
                tok = MatrixToken.fromToken(token)
                tok.line = line
                tok.filename = filename
                if token.type == "LBRACKET":
                    inside_list += 1
                elif token.type == "RBRACKET":
                    inside_list -= 1
                if inside_list > 0 and token.type == "NEWLINE":
                    continue
                yield tok

        # return any number of missing DEDENT tokens at the end of the stream
        for i in range(level):
            tok = MatrixToken()
            tok.type = "DEDENT"
            tok.value = ""
            tok.lineno = lineno
            tok.index = 0
            tok.line = line
            tok.filename = filename
            yield tok

        # and yield an extra newline
        tok = MatrixToken()
        tok.type = "NEWLINE"
        tok.value = "\n"
        tok.lineno = lineno
        tok.index = 0
        tok.line = line
        tok.filename = filename
        yield tok
