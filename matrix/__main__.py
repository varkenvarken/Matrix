import argparse
import fileinput
from sys import stderr, stdout


def outputfile(filename, ext):
    if filename == "-":
        f = stdout
    else:
        f = open(filename + ext, "w")
    return f


def printParseTree(filename, ext, parsetree):
    f = outputfile(filename, ext)
    print("Parsetree\n\n id  node\n---------", file=f)
    for node in parsetree.walk():
        print(f"{node.id:3d}", "  " * node.level, node, file=f)
    print(file=f)
    if f != stdout:
        f.close()


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "files",
        metavar="FILE",
        nargs="*",
        help="files to read, if empty, stdin is used",
    )
    argparser.add_argument("-o", "--output", type=str, default="out")
    argparser.add_argument(
        "-t",
        "--tokenize",
        default=False,
        action="store_true",
        help="tokenize then stop & show tokens ",
    )
    argparser.add_argument(
        "-p",
        "--parse",
        default=False,
        action="store_true",
        help="parse then stop & show parse tree",
    )
    argparser.add_argument(
        "-O",
        "--optimize",
        default=False,
        action="store_true",
        help="optimize then stop & show parse tree",
    )
    argparser.add_argument(
        "-d",
        "--debug",
        default=False,
        action="store_true",
        help="print additional debug info to stderr",
    )
    argparser.add_argument(
        "-s",
        "--syntax",
        default=False,
        action="store_true",
        help="build the syntax tree then stop & show the syntax tree",
    )
    argparser.add_argument(
        "-v",
        "--verbose",
        default=False,
        action="store_true",
        help="print additional debug info to stderr",
    )
    args = argparser.parse_args()

    from .CodeGenerator import CodeGenerator
    from .Lexer import MatrixLexer
    from .Optimizer import Simplify
    from .Parser import MatrixParser
    from .Syntax import SyntaxTree

    lexer = MatrixLexer()
    parser = MatrixParser()

    inputstream = fileinput.input(files=args.files if len(args.files) > 0 else ("-",))
    if args.verbose:
        print(
            f"input stream opened on file {', '.join(args.files) if len(args.files) else 'stdin'}",
            file=stderr,
        )

    if args.tokenize:
        f = outputfile(args.output, ".tok")
        for token in lexer.tokenizeFromInputStream(inputstream):
            f.write(str(token) + "\n")
        if f != stdout:
            f.close()
        exit(0)

    parsetree = parser.parse(lexer.tokenizeFromInputStream(inputstream))
    if args.verbose:
        print("parse tree complete", file=stderr)

    if args.debug:
        f = outputfile(args.output, ".grammar")
        print(parser._grammar, file=f)
        if f != stdout:
            f.close()
        printParseTree(args.output, ".parse", parsetree)
    if args.parse:
        exit(0)

    #    opt = Simplify(parsetree)
    #    removed, passes = opt.optimize()
    #    parsetree = opt.tree
    #    if args.verbose:
    #        print(
    #            f"Simplified parse tree. Removed {removed} nodes in {passes} passes",
    #            file=stderr,
    #        )
    #    if args.debug:
    #        printParseTree(args.output, ".optimized", parsetree)
    #    if args.optimize:
    #        exit(0)

    syntaxtree = SyntaxTree(parsetree)
    if args.verbose:
        print(f"Created a syntax tree", file=stderr)
    if args.debug:
        f = outputfile(args.output, ".ast")
        syntaxtree.print(f)
        if f != stdout:
            f.close()
    if args.syntax:
        exit(0)

    code = CodeGenerator(syntaxtree)
    if args.verbose:
        print(f"Created assembly code", file=stderr)
    f = outputfile(args.output, ".s")
    code.print(f)
    if f != stdout:
        f.close()
