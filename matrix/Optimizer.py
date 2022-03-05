from .Node import ParseNode


class Optimizer:
    def __init__(self, tree):
        self.tree = tree

    def optimize(self):
        return 0, 0


class Simplify(Optimizer):
    def __init__(self, tree):
        super().__init__(tree)
        self.removed = 0
        self.passes = 0

    @staticmethod
    def singleLine(node):
        if isinstance(node, ParseNode):
            if (
                node.token in ("unit", "program", "suite", "simpleunit")
                and node.e0 is not None
                and node.e1 is None
                and node.e2 is None
            ):
                child = node.e0
                if child.e0 is not None and child.e1 is None and child.e2 is None:
                    return child

        return None

    @staticmethod
    def simplifyNode(node):
        removed = 0
        if isinstance(node, ParseNode):
            s0 = Simplify.singleLine(node.e0)
            s1 = Simplify.singleLine(node.e1)
            s2 = Simplify.singleLine(node.e2)
            if s0:
                node.e0 = s0
                removed += 1
            if s1:
                node.e1 = s1
                removed += 1
            if s2:
                node.e0 = s2
                removed += 1
            else:
                removed += Simplify.simplifyNode(node.e0)
                removed += Simplify.simplifyNode(node.e1)
                removed += Simplify.simplifyNode(node.e2)
        return removed

    def optimize(self):
        self.removed = 0
        self.passes = 0
        while True:
            removed = Simplify.simplifyNode(self.tree)
            self.removed += removed
            self.passes += 1
            if removed <= 0:
                break
        return self.removed, self.passes
