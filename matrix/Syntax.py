# Matrix, a simple programming language
# (c) 2022 Michel Anders
# License: MIT, see License.md
# Version: 20220311104235

from ast import While
from math import expm1

from .Node import SyntaxNode


class Symbol:
    def __init__(
        self, name, typ, const=False, rtype=None, parameters=None, isparameter=False
    ):
        self.name = name
        self.type = typ
        self.const = const
        self.constoverride = False
        self.isparameter = isparameter
        self.parameterindex = -1
        self.offset = 0
        self.value = None
        self.rtype = rtype
        self.parameters = parameters
        self.scope = None
        self.shape = 0  # a scalar

    def __repr__(self):
        if self.type != "function":
            return f"{self.scope:6s} {self.name:12s}{'p' if self.isparameter else ' '}({self.parameterindex:2d}) {'const' if self.const else 'var  '}:{self.type} {self.shape if self.type == 'mat' else ''} = {self.value}"
        return f"{self.scope:6s} {self.name:12s}    fun  :{self.rtype} ({','.join(self.parameters)})"


class Scope:
    def __init__(self, outer=None, scope="local"):
        self.outer = outer
        self.symbols = dict()
        self.scope = scope

    def __getitem__(self, key):
        if key in self.symbols:
            return self.symbols[key]
        if self.outer is not None and key in self.outer:
            return self.outer[key]
        raise KeyError(f"{key} not found in scope")

    def __setitem__(self, key, value):
        value.scope = self.scope
        self.symbols[key] = value

    def __contains__(self, key):
        if key in self.symbols:
            return True
        if self.outer and key in self.outer:
            return True
        return False

    def __str__(self):
        a = "\n".join(f"{value}" for key, value in self.symbols.items())
        b = (
            "\n" + "\n".join(f"{value}" for key, value in self.outer.symbols.items())
            if self.outer
            else ""
        )
        return a + b


def inner(node):
    assert node.token == "elist"
    assert node.e0.token == "number"
    values = [node.e0.value]
    while node.e1:
        node = node.e1
        assert node.e0.token == "number"
        values.append(node.e0.value)
    return values


def elist(node):
    items = list()
    assert node.token == "elist"
    if node.e0.token == "matrixliteral":
        items.append(elist(node.e0.e0))
        while node.e1:
            node = node.e1
            assert node.e0.token == "matrixliteral"
            items.append(elist(node.e0.e0))
            # print(">>", items)

    elif node.e0.token == "number":
        newitems = inner(node)
        return newitems
    else:
        assert False
    return items


def shape(mat):
    if type(mat) == list:
        shape0 = shape(mat[0])
        for item in mat[1:]:
            assert shape0 == shape(item)
        return [len(mat)] + shape0
    return []


def getShape(node):
    shape = []
    assert node.token == "elist"
    assert node.e0.token == "number"
    while node is not None:
        shape.append(node.e0.value)
        node = node.e1
    return shape


class SyntaxTree:
    def __init__(self, parsetree):
        self.symbols = Scope(scope="global")
        self.tree = self.process(parsetree)

    def process(self, node):
        if node is None:
            return node
        elif node.token == "program":
            return SyntaxNode(
                "program", "start", e0=self.process(node.e1), **node.src()
            )
        elif node.token in ("unit", "simpleunit"):
            return SyntaxNode(
                "unit",
                "",
                e0=self.process(node.e0),
                e1=self.process(node.e1),
                level=node.level + 1,
                **node.src(),
            )
        elif node.token == "suite":
            return self.process(node.e1)
        elif node.token == "return":
            return SyntaxNode(
                "return",
                "",
                e0=self.process(node.e0),
                level=node.level + 1,
                **node.src(),
            )
        elif node.token == "vardeclist":
            const = node.value != "var"
            typ = node.e0.value
            vardecls = node.e1
            dnodes = dnode = SyntaxNode(
                "initialize", typ, level=node.level + 1, **node.src()
            )
            while vardecls:
                vardecl = vardecls.e0
                name = vardecl.value
                # TODO: check if name already defined
                dnode.e0 = SyntaxNode(
                    "assign",
                    (self.symbols.scope, name),
                    level=node.level + 1,
                    **node.src(),
                )
                self.symbols[name] = Symbol(name, typ, const)
                if vardecl.e0 is None:
                    dnode.e1 = (
                        SyntaxNode(
                            "stringliteral", '""', level=node.level + 1, **node.src()
                        )
                        if typ == "str"
                        else SyntaxNode(
                            "number", 0, level=node.level + 1, **node.src()
                        )  # also added for an empty mat a[3,4] for example
                    )
                else:
                    dnode.e1 = self.process(vardecl.e0)
                    if type(dnode.e1.info) == dict and "shape" in dnode.e1.info:
                        self.symbols[name].shape = dnode.e1.info["shape"]
                if vardecl.e1 is not None:  # a matrix size spec
                    self.symbols[name].shape = getShape(vardecl.e1)
                vardecls = vardecls.e1
                if vardecls is not None:
                    dnode.e1 = SyntaxNode(
                        "initialize", typ, level=node.level + 1, **node.src()
                    )
                    dnode = dnode.e1
            return dnodes
        elif node.token in ("number", "stringliteral"):
            return SyntaxNode(
                node.token, node.value, level=node.level + 1, **node.src()
            )
        elif node.token in ("matrixliteral"):
            item = node.e0
            assert item.token == "elist"
            mat = elist(item)
            return SyntaxNode(
                node.token,
                {"values": mat, "shape": shape(mat)},
                level=node.level + 1,
                **node.src(),
            )
        elif node.token == "plus":
            sn = SyntaxNode(
                "binop",
                {"op": "plus"},
                e0=self.process(node.e0),
                e1=self.process(node.e1),
                level=node.level + 1,
                **node.src(),
            )
            return sn
        elif node.token == "uminus":
            return SyntaxNode(
                "unop",
                {"op": "uminus"},
                e0=self.process(node.e0),
                level=node.level + 1,
                **node.src(),
            )
        elif node.token == "function declaration":
            name = node.value
            plist = node.e1
            parameters = []
            while plist is not None:
                parameter = plist.e1
                plist = plist.e0
                parameters.append(parameter.e0.value)
            # TODO: warn if redefined (with same signature)
            self.symbols[name] = Symbol(
                name, "function", True, rtype=node.e0.value, parameters=parameters
            )
        elif node.token == "function call":
            name = node.value
            if name not in self.symbols:
                print(f"unknown function {name}")
                return None
            else:  # arguments are evaluated left to right
                fun = self.symbols[name]
                alist = node.e0
                snret = SyntaxNode(
                    "call",
                    {"name": name, "type": fun.rtype},
                    level=node.level + 1,
                    **node.src(),
                )
                arglist = []
                # e1 points to an expresssion
                # e0 points to any additional arguments to the left
                while alist is not None:
                    arglist.insert(0, self.process(alist.e1))
                    # TODO: match type of expr {sn} againts param {fun.parameters[na]}"
                    alist = alist.e0
                if len(arglist) != len(fun.parameters):
                    print(
                        f"length of argument list {len(arglist)} does not match length of parameter list {len(fun.parameters)}"
                    )
                sn = snret
                while arglist:
                    arg = SyntaxNode(
                        "argument",
                        "",
                        e1=arglist.pop(0),
                        level=node.level + 1,
                        **node.src(),
                    )
                    sn.e0 = arg
                    sn = arg
                return snret
        elif node.token == "name":
            name = node.value
            if name not in self.symbols:
                print(f"unknown variable {name}")
                return None
            var = self.symbols[name]
            return SyntaxNode(
                "var reference",
                {"name": name, "scope": var.scope, "type": var.type},
                level=node.level + 1,
                **node.src(),
            )
        elif node.token == "function definition":
            fname = node.value
            # check if name already defined
            if fname in self.symbols:
                print(f"function {fname} already defined")
                return None
            # add an entry in the global scope just like a function declaration
            plist = node.e1
            parameters = []
            while plist is not None:
                parameter = plist.e1
                plist = plist.e0
                if parameter is not None:
                    parameters.append(parameter.e0.value)
            # TODO: warn if redefined (with same signature)
            self.symbols[fname] = Symbol(
                fname, "function", True, rtype=node.e0.value, parameters=parameters
            )
            # push a new local scope
            self.symbols = Scope(outer=self.symbols)
            # add the parameters to the local scope
            plist = node.e1
            parameters = []
            while plist is not None:
                parameter = plist.e1
                plist = plist.e0
                if parameter is not None:
                    name = parameter.value
                    typ = parameter.e0.value
                    parameters.append(
                        Symbol(name, typ, False, isparameter=True)
                    )  # TODO: add option for const modifier to params?
            for n, p in enumerate(reversed(parameters)):
                p.parameterindex = n
                self.symbols[p.name] = p
            # process the body
            body = self.process(node.e2)
            # pop the local scope
            local = self.symbols.symbols.copy()
            self.symbols = self.symbols.outer
            # return to body for code generation
            sn = SyntaxNode(
                "function definition",
                {
                    "name": fname,
                    "scope": local,
                    "rtype": node.e0.value,
                    "ptypes": list(reversed(parameters)),
                },
                e0=body,
                level=node.level + 1,
                **node.src(),
            )
            return sn
        elif node.token == "assignment":
            return SyntaxNode(
                "assign",
                node.e0.value,
                level=node.level + 1,
                **node.src(),
                e0=self.process(node.e1),
            )
        else:
            print("unrecognized ParseNode", node)
            return None

    @staticmethod
    def walk(node, fie):
        if node is not None:
            fie(node)
            SyntaxTree.walk(node.e0, fie)
            SyntaxTree.walk(node.e1, fie)
            SyntaxTree.walk(node.e2, fie)

    def print(self, f):
        print("globals", file=f)
        print(self.symbols, file=f)
        print(file=f)
        SyntaxTree.walk(
            self.tree,
            lambda x: print(
                f"{x.id:3d}",
                "  " * x.level,
                str(x).replace("@|", "\n" + "  " * x.level + "     "),
                # ("   \n" + "  " * x.level).join(str(x).split("@|")),
                file=f,
                sep=" ",
            ),
        )
