# Matrix, a simple programming language
# (c) 2022 Michel Anders
# License: MIT, see License.md
# Version: 20220305152954

from sys import stderr

from sly import Parser

from .Lexer import MatrixLexer
from .Node import ParseNode


class MatrixParser(Parser):
    # debugfile = "parser.out"
    tokens = MatrixLexer.tokens

    precedence = (
        (
            "left",
            "LESS",
            "GREATER",
            "LESSOREQUAL",
            "GREATEROREQUAL",
            "EQUAL",
            "NOTEQUAL",
        ),
        ("left", "PLUS", "MINUS"),
        ("left", "*", "/", "MATMUL", "DOT", "MODULO", "CROSS"),
        ("right", "POWER"),
        ("right", "UMINUS", "ROOT"),
        ("right", "CAST"),
    )

    def __init__(self, names=None):
        super().__init__()
        self.names = dict() if names is None else names

    def error(self, token):
        if token:
            lineno = getattr(token, "lineno", 0)
            if lineno:
                stderr.write(
                    f"MatrixParser: Syntax error at line {lineno}, token={token.type}:{token.value}\n"
                )
            else:
                stderr.write(
                    f"MatrixParser: Syntax error, token={token.type}:{token.value}"
                )
        else:
            stderr.write("MatrixParser: Parse error in input. EOF\n")

    # program : { unit }

    @_("{ unit }")
    def program(self, p):
        ln = pn = ParseNode("program")
        for u in p.unit:
            if u is not None:
                pn.e1 = ParseNode("unit", e0=u)
                pn = pn.e1
        return ln

    # suite : { simpleunit }

    @_("{ simpleunit }")
    def suite(self, p):
        ln = pn = ParseNode("suite")
        for u in p.simpleunit:
            if u is not None:
                pn.e1 = ParseNode("simpleunit", e0=u)
                pn = pn.e1
        return ln

    # unit : function NEWLINE
    #      | external NEWLINE
    #      | simpleunit

    @_("function NEWLINE")
    @_("external NEWLINE")
    def unit(self, p):
        return p[0]

    @_("simpleunit")
    def unit(self, p):
        return p.simpleunit

    # simpleunit:expression NEWLINE
    #      | compound
    #      | RETURN [expression] NEWLINE
    #      | BREAK NEWLINE
    #      | CONTINUE NEWLINE
    #      | NEWLINE

    @_("expression NEWLINE")
    @_("compound")
    def simpleunit(self, p):
        return p[0]

    @_("NEWLINE")
    def simpleunit(self, p):
        pass

    @_("RETURN expression NEWLINE")
    def simpleunit(self, p):
        return ParseNode("return", e0=p.expression)

    @_("RETURN NEWLINE")
    def simpleunit(self, p):
        return ParseNode("return")

    @_("BREAK NEWLINE")
    def simpleunit(self, p):
        return ParseNode("break")

    @_("CONTINUE NEWLINE")
    def simpleunit(self, p):
        return ParseNode("continue")

    # variable declarations
    @_("ptype vardecls NEWLINE")
    def simpleunit(self, p):
        return ParseNode("vardeclist", "var", e0=p.ptype, e1=p.vardecls)

    # variable declarations
    @_("CONST ptype vardecls NEWLINE")
    def simpleunit(self, p):
        return ParseNode("vardeclist", "const", e0=p.ptype, e1=p.vardecls)

    @_("vardecl")
    def vardecls(self, p):
        return ParseNode("vardecls", e0=p.vardecl)

    @_('vardecl "," vardecls')
    def vardecls(sefl, p):
        return ParseNode("vardecls", e0=p.vardecl, e1=p.vardecls)

    @_("NAME")
    def vardecl(self, p):
        return ParseNode("vardecl", p.NAME)

    @_('NAME "=" expr')
    def vardecl(self, p):
        return ParseNode("vardecl", p.NAME, e0=p.expr)

    # expression : reference = expr
    #            | expr

    @_('reference "=" expr')
    def expression(self, p):
        return ParseNode("assignment", e0=p.reference, e1=p.expr)

    @_("expr")
    def expression(self, p):
        return p.expr

    # expr : expr + expr
    #      | expr - expr
    #      | expr * expr
    #      | expr / expr
    #      | - expr
    #      | ( expr )
    #      | reference
    #      | NUMBER

    @_("expr PLUS expr")
    def expr(self, p):
        return ParseNode("plus", e0=p.expr0, e1=p.expr1)

    @_("expr MINUS expr")
    def expr(self, p):
        return ParseNode("minus", e0=p.expr0, e1=p.expr1)

    @_('expr "*" expr')
    @_("expr MATMUL expr")
    @_("expr DOT expr")
    @_("expr CROSS expr")
    def expr(self, p):
        return ParseNode(p[1], e0=p.expr0, e1=p.expr1)

    @_('expr "/" expr')
    @_("expr MODULO expr")
    def expr(self, p):
        return ParseNode(p[1], e0=p.expr0, e1=p.expr1)

    @_("expr POWER expr")
    def expr(self, p):
        return ParseNode(p[1], e0=p.expr0, e1=p.expr1)

    # comparisions
    @_("expr EQUAL expr")
    def expr(self, p):
        return ParseNode("equal", e0=p.expr0, e1=p.expr1)

    @_("expr NOTEQUAL expr")
    def expr(self, p):
        return ParseNode("notequal", e0=p.expr0, e1=p.expr1)

    @_("expr LESS expr")
    def expr(self, p):
        return ParseNode("less", e0=p.expr0, e1=p.expr1)

    @_("expr GREATER expr")
    def expr(self, p):
        return ParseNode("greater", e0=p.expr0, e1=p.expr1)

    @_("expr LESSOREQUAL expr")
    def expr(self, p):
        return ParseNode("lessorequal", e0=p.expr0, e1=p.expr1)

    @_("expr GREATEROREQUAL expr")
    def expr(self, p):
        return ParseNode("greaterorequal", e0=p.expr0, e1=p.expr1)

    # unary operations incl. casts
    @_("MINUS expr %prec UMINUS")
    def expr(self, p):
        return ParseNode("uminus", e0=p.expr)

    @_("ROOT expr")
    def expr(self, p):
        return ParseNode("root", e0=p.expr)

    @_('"(" ptype ")" expr %prec CAST')
    def expr(self, p):
        return ParseNode("cast", p.ptype, e0=p.expr)

    # grouping
    @_('"(" expression ")"')
    def expr(self, p):
        return p.expression

    # var reference
    @_("reference")
    def expr(self, p):
        return p.reference

    @_("NAME")
    def reference(self, p):
        return ParseNode("name", value=p.NAME)

    @_("NAME indexlist")
    def reference(self, p):
        return ParseNode("indexed name", e0=p.indexlist)

    @_("LBRACKET slice RBRACKET")
    def indexlist(self, p):
        return ParseNode("indexlist", e0=p.slice)

    @_("LBRACKET slice RBRACKET indexlist")
    def indexlist(self, p):
        return ParseNode("indexlist", e0=p.slice, e1=p.indexlist)

    @_("vexpr COLON vexpr COLON vexpr")
    def slice(self, p):
        return ParseNode(
            "slice", "start:stop:step", e0=p.vexpr0, e1=p.vexpr1, e2=p.vexpr2
        )

    @_("vexpr COLON vexpr")
    def slice(self, p):
        return ParseNode("slice", "start:stop", e0=p.vexpr0, e1=p.vexpr1)

    @_("expr")
    def slice(self, p):
        return ParseNode("slice", "index", e0=p.expr)

    @_("expr")
    def vexpr(self, p):
        return p.expr

    @_("empty")
    def vexpr(self, p):
        return ParseNode("default")

    # literals
    @_("NUMBER")
    def expr(self, p):
        return ParseNode("number", p.NUMBER)

    @_("STRINGLITERAL")
    def expr(self, p):
        return ParseNode("stringliteral", p.STRINGLITERAL)

    @_("LBRACKET elist RBRACKET")
    def expr(self, p):
        return ParseNode("matrixliteral", e0=p.elist)

    @_("expr")
    def elist(self, p):
        return ParseNode("elist", e0=p.expr)

    @_('expr "," elist')
    def elist(self, p):
        return ParseNode("elist", e0=p.expr, e1=p.elist)

    # function call
    @_('NAME "(" arguments ")"')
    def expr(self, p):
        return ParseNode("function call", p.NAME, e0=p.arguments)

    @_("alist")
    def arguments(self, p):
        return p.alist

    @_("empty")
    def arguments(self, p):
        pass

    @_("expression")
    def alist(self, p):
        return ParseNode("alist", e0=p.expression)

    @_('alist "," expression')
    def alist(self, p):
        return ParseNode("alist", e0=p.alist, e1=p.expression)

    # function definition
    @_('FUN rtype NAME "(" parameters ")" COLON NEWLINE INDENT suite DEDENT ')
    def function(self, p):
        return ParseNode(
            "function definition",
            value=p.NAME,
            e0=ParseNode("return type", p.rtype),
            e1=p.parameters,
            e2=p.suite,
        )

    # function declaration
    @_('EXTERN FUN rtype NAME "(" parameters ")"')
    def external(self, p):
        return ParseNode(
            "function declaration",
            value=p.NAME,
            e0=ParseNode("return type", p.rtype.value),
            e1=p.parameters,
        )

    @_("VOID")
    @_("LONG")
    @_("FLOAT")
    @_("DOUBLE")
    @_("STRING")
    @_("MATRIX")
    @_("VECTOR")
    @_("FLOATMATRIX")
    @_("FLOATVECTOR")
    def rtype(self, p):
        return ParseNode("rtype", p[0])

    @_("LONG")
    @_("FLOAT")
    @_("DOUBLE")
    @_("STRING")
    @_("MATRIX")
    @_("VECTOR")
    @_("FLOATMATRIX")
    @_("FLOATVECTOR")
    def ptype(self, p):
        return ParseNode("ptype", p[0])

    @_("plist")
    def parameters(self, p):
        return p.plist

    @_("empty")
    def parameters(self, p):
        return ParseNode("plist")

    @_("ptype NAME")
    def plist(self, p):
        return ParseNode("plist", e1=ParseNode("parameter", value=p.NAME, e0=p.ptype))

    @_('plist "," ptype NAME')
    def plist(self, p):
        return ParseNode(
            "plist", e0=p.plist, e1=ParseNode("parameter", value=p.NAME, e0=p.ptype)
        )

    # compound statements, i.e. control structures
    @_(
        "IF expression COLON NEWLINE INDENT suite DEDENT [ ELSE COLON NEWLINE INDENT  suite DEDENT ]"
    )
    def compound(self, p):
        p.suite0.token = "then"
        if p.suite1:
            p.suite1.token = "else"
        return ParseNode("if", e0=p.expression, e1=p.suite0, e2=p.suite1)

    @_("WHILE expression COLON NEWLINE INDENT suite DEDENT")
    def compound(self, p):
        return ParseNode("while", e0=p.expression, e1=p.suite)

    @_("FOR NAME IN expr COLON NEWLINE INDENT suite DEDENT")
    def compound(self, p):
        return ParseNode("for", p.NAME, e0=p.expr, e1=p.suite)

    # empty production, used in many optional bits and {}* repeats as EBNF notation is buggy (?)
    @_("")
    def empty(self, p):
        pass
