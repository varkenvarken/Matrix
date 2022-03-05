# Matrix, a simple programming language
# (c) 2022 Michel Anders
# License: MIT, see License.md
# Version: 20220304172024

from math import expm1

from .Node import SyntaxNode


class Symbol:
    def __init__(self, name, typ, const=False, rtype=None, parameters=None):
        self.name = name
        self.type = typ
        self.const = const
        self.constoverride = False
        self.value = None
        self.rtype = rtype
        self.parameters = parameters
        self.scope = None

    def __str__(self):
        if self.type != "function":
            return f"{self.name:12s} {'const' if self.const else 'var  '}:{self.type} = {self.value}"
        return f"{self.name:12s} fun  :{self.rtype} ({','.join(self.parameters)})"


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
        return "\n".join(f"{value}" for key, value in self.symbols.items())


class SyntaxTree:
    def __init__(self, parsetree):
        self.symbols = Scope(scope="global")
        self.tree = self.process(parsetree)

    def process(self, node):
        print(node)
        if node is None:
            return node
        elif node.token == "program":
            return SyntaxNode("program", "start", e0=self.process(node.e1))
        elif node.token == "unit":
            return SyntaxNode(
                "unit",
                "",
                e0=self.process(node.e0),
                e1=self.process(node.e1),
                level=node.level + 1,
            )
        elif node.token == "vardeclist":
            const = node.value != "var"
            typ = node.e0.value
            vardecls = node.e1
            dnodes = dnode = SyntaxNode("initialize", typ)
            while vardecls:
                vardecl = vardecls.e0
                name = vardecl.value
                # TODO: check if name already defined
                dnode.e0 = SyntaxNode("assign", (self.symbols.scope, name))
                self.symbols[name] = Symbol(name, typ, const)
                if vardecl.e0 is None:
                    dnode.e1 = (
                        SyntaxNode("stringliteral", "")
                        if type == "stringliteral"
                        else SyntaxNode("number", 0)
                    )
                else:
                    dnode.e1 = self.process(vardecl.e0)
                vardecls = vardecls.e1
                if vardecls is not None:
                    dnode.e1 = SyntaxNode("initialize", typ)
                    dnode = dnode.e1
            return dnodes
        elif node.token == "number":
            return SyntaxNode("number", node.value)
        elif node.token == "plus":
            sn = SyntaxNode(
                "binop",
                {"op": "plus"},
                e0=self.process(node.e0),
                e1=self.process(node.e1),
            )
            return sn
        elif node.token == "function declaration":
            name = node.value
            plist = node.e1
            parameters = []
            while plist is not None:
                parameter = plist.e1
                plist = plist.e0
                parameters.append(parameter.e0.value)
            self.symbols[name] = Symbol(
                name, "function", True, rtype=node.e0.value, parameters=parameters
            )
        elif node.token == "function call":
            name = node.value
            if name not in self.symbols:
                print(f"unknown function {name}")
                return None
            else:
                fun = self.symbols[name]
                alist = node.e0
                sn = snret = SyntaxNode("call", {"name": name, "type": fun.rtype})
                na = 0
                print(snret, sn)
                while alist is not None:
                    sn.e0 = self.process(alist.e0)
                    sn = sn.e0
                    print(
                        f"TODO: match type of expr {sn} againts param {fun.parameters[na]}"
                    )
                    alist = alist.e1
                    na += 1
                    print(snret, sn)
                if na != len(fun.parameters):
                    print(
                        f"length of argument list {na} does not match length of parameter list {len(fun.parameters)}"
                    )
                return snret
        elif node.token == "name":
            name = node.value
            if name not in self.symbols:
                print(f"unknown variable {name}")
                return None
            var = self.symbols[name]
            return SyntaxNode(
                "var reference", {"name": name, "scope": var.scope, "type": var.type}
            )
        elif node.token == "function definition":
            name = node.value
            # check if name already defined
            # add an entry in the global scope just like a function declaration
            # push a new local scope
            # add the parameters to the local scope
            # process the body
            # pop the local scope 
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
            self.tree, lambda x: print(f"{x.id:3d}", "  " * x.level, str(x), file=f)
        )
