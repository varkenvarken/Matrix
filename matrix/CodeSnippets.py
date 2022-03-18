# Matrix, a simple programming language
# (c) 2022 Michel Anders
# License: MIT, see License.md
# Version: 20220318145822

from argparse import ArgumentError
from collections import defaultdict
from dataclasses import dataclass
from functools import reduce
from re import S


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


class Label:
    def __init__(self):
        self.labels = defaultdict(int)

    def __getitem__(self, key):
        self.labels[key] += 1
        return f"{key}{self.labels[key]}"


labels = Label()


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


def move_quad(reg, intro=None, linecomment=None):
    return CodeChunk(
        intro=intro,
        lines=[
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
    pop0 = pop_quad(reg="%xmm1", intro=intro)
    pop1 = pop_quad(reg="%xmm0")
    binop = CodeChunk(
        lines=[
            CodeLine(opcode=binop, operands=f"%xmm1, %xmm0", comment=linecomment),
        ],
    )
    push = push_quad(reg="%xmm0")
    return pop0 + pop1 + binop + push


def modulo_double():
    pop0 = pop_quad(reg="%xmm1", intro="modulo two doubles")
    pop1 = pop_quad(reg="%xmm0")
    binop = CodeChunk(
        lines=[
            CodeLine(opcode="movapd", operands="%xmm0, %xmm2"),
            CodeLine(opcode="divsd", operands="%xmm1, %xmm2"),
            CodeLine(opcode="cvttsd2sil", operands="%xmm2, %eax"),
            CodeLine(opcode="pxor", operands="%xmm2, %xmm2"),
            CodeLine(opcode="cvtsi2sdl", operands="%eax, %xmm2"),
            CodeLine(opcode="mulsd", operands="%xmm2, %xmm1"),
            CodeLine(opcode="subsd", operands="%xmm1, %xmm0"),
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


def binop_mat(binop, intro=None, linecomment=None):
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


def function_call(name, returntype, an=0, alignment=0, intro=None):
    nargs = CodeChunk(
        intro=intro,
        lines=[
            CodeLine(
                opcode="movq",
                operands=f"${an},%rax",
                comment="number of arguments, only needed when calling varargs",
            ),
            CodeLine(opcode="subq", operands=f"${alignment},%rsp"),
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
            ),
            CodeLine(opcode="addq", operands=f"${alignment},%rsp"),
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


def strides(shape, size):
    stride = []
    s = size
    for sh in reversed(shape):
        stride.append(int(s))
        s *= sh
    return reversed(stride)


rawdata = -1


def getDataLabel():
    global rawdata
    rawdata += 1
    return f".LRData{rawdata}"


descriptors = -1


def getDescriptor():
    global descriptors
    descriptors += 1
    return f".LMatDesc{descriptors}"


def matrix_var(v, desc):
    return CodeChunk(
        intro=f"global var {v.name}",
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
                opcode=".quad",
                operands=desc,
                comment="mat variables and constants are pointers to a data descriptor",
            ),
        ],
    )


def descriptor(shape, size, desc, data, scalar):
    nelements = 1 if scalar else reduce(lambda x, y: int(x) * int(y), shape, 1)
    code = CodeChunk(
        lines=[
            CodeLine(
                label=desc,
                opcode=".quad",
                operands=f"{len(shape)}",
                comment="number of dimensions",
            ),
            CodeLine(
                opcode=".quad",
                operands=str(size),
                comment="size of single data element",
            ),
            CodeLine(
                opcode=".quad",
                operands=f"{nelements}",
                comment="total number of elements",
            ),
            CodeLine(
                opcode=".quad",
                operands="0",
                comment="flags (not used)",
            ),
            CodeLine(
                opcode=".quad",
                operands="1",
                comment="type, always 1 (double) for now",
            ),
            CodeLine(
                opcode=".quad",
                operands=data,  # TODO: add null pointer for unspecified shape
                comment="pointer to consequetive data. if a shape was specified or an initialize present, data will follow",
            ),
            CodeLine(
                opcode=".quad",
                operands="0",
                comment="base (0 because this is not a view)",
            ),
            CodeLine(
                opcode=".quad",
                operands="0",
                comment="offset (0 because this is not a view)",
            ),
            CodeLine(
                opcode=".quad",
                operands=", ".join(["0"] * 32)
                if scalar
                else f"{', '.join(list(map(str,map(int,shape))) + ['0']*(32-len(shape)))}",
                comment="shape",
            ),
            CodeLine(
                opcode=".quad",
                operands=", ".join(["1"] * 32)
                if scalar
                else f"{', '.join(list(map(str,strides(shape,8))) + ['0']*(32-len(shape)))}",  # size always 8 (double)
                comment="stride",
            ),
        ],
    )
    return code


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
    elif v.type == "str":
        code = CodeChunk(
            lines=[
                CodeLine(opcode=f".global {v.name}"),
                CodeLine(
                    opcode=".section",
                    operands=".rodata" if v.const and not v.constoverride else ".data",
                ),
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
    elif v.type == "mat":
        data = getDataLabel()
        desc = getDescriptor()
        if type(v.shape) == int:
            assert v.shape == 0
            code = matrix_var(v, desc) + descriptor(
                [0], 8, desc, data, True
            )  # size always 8 (double)
            code.lines.append(
                CodeLine(
                    label=data,
                    opcode=".double",
                    operands="0.0",
                )
            )
        else:
            nelements = reduce(lambda x, y: int(x) * int(y), v.shape, 1)
            code = matrix_var(v, desc) + descriptor(
                v.shape, 8, desc, data, False
            )  # size always 8 (double)
            code.lines.append(
                CodeLine(
                    label=data,
                    opcode=".dcb.d",
                    operands=f"{nelements}, 0.0",
                )
            )
    else:
        print(f"unprocessed vardef {v.name}:{v.type}")
        return None
    return code


def flatten(
    nestedList,
):  # from https://wiki.python.org/moin/ProblemSets/99%20Prolog%20Problems%20Solutions#Problem_7:_Flatten_a_nested_list_structure
    result = []
    if not nestedList:
        return result
    stack = [list(nestedList)]
    while stack:
        current = stack.pop()
        next = current.pop()
        if current:
            stack.append(current)
        if isinstance(next, list):
            if next:
                stack.append(list(next))
        else:
            result.append(next)
    result.reverse()
    return result


matliterals = -1


def matLiteral(shape, values):
    global matliterals
    matliterals += 1
    name = f".MATLIT{matliterals}"
    data = getDataLabel()
    desc = getDescriptor()
    code = CodeChunk(
        lines=[CodeLine(label=name, opcode=".quad", operands=desc)]
    ) + descriptor(
        shape, 8, desc, data, False
    )  # size always 8 (double)
    code.lines.append(CodeLine(label=data))
    for val in flatten(values):
        code.lines.append(CodeLine(opcode=".double", operands=f"{val}"))
    return name, code


def matCopy(src, dst):
    return CodeChunk(
        intro=f"copy matrix {src} to {dst}",
        lines=[
            CodeLine(opcode="leaq", operands=f"{src}(%rip), %rdi"),
            CodeLine(opcode="leaq", operands=f"{dst}(%rip), %rsi"),
            CodeLine(opcode="call", operands="matrixcopy"),
        ],
    )


def matCopy2():
    return CodeChunk(
        intro=f"copy matrix [stack - 1] -> [stack] (both elements are pointers to descriptors)",
        lines=[
            CodeLine(
                opcode="movq",
                operands=f"(%rsp), %rdi",
                comment="top is src matrix (view) and goes into 1st argument (= %rdi) but we keep it on the stack",
            ),
            CodeLine(
                opcode="movq",
                operands=f"8(%rsp), %rsi",
                comment="top -1 is dst matrix (view) and goes into 2nd argument (= %rsi) but we keep it on the stack",
            ),
            CodeLine(opcode="call", operands="descriptorcopy"),
            CodeLine(
                opcode="add",
                operands="$8, %rsp",
                comment="discard destination address but keep src on top",
            ),
        ],
    )


def globalMatInit(symbol, info):
    return matLiteral(info["shape"], info["values"])


def local_matrix(info):
    return matLiteral(info["shape"], info["values"])


def index_matrix(alignment):
    return CodeChunk(
        intro="index a matrix",
        lines=[
            CodeLine(opcode="popq", operands="%rax"),
            CodeLine(opcode="movq", operands="%rax, %xmm0"),
            CodeLine(
                opcode="cvtsd2si",
                operands="%xmm0, %rsi",
                comment="convert single double to long",
            ),
            CodeLine(opcode="popq", operands="%rdi"),
            CodeLine(opcode="subq", operands=f"${alignment},%rsp"),
            CodeLine(opcode="call", operands="matrix_index"),
            CodeLine(opcode="addq", operands=f"${alignment},%rsp"),
            CodeLine(opcode="push", operands="%rax"),
        ],
    )


def slice_matrix(alignment, nslices):
    malloc = [
        CodeLine(
            opcode="subq",
            operands=f"${alignment},%rsp",
            comment="make sure stack is 16 byte aligned",
        ),
        CodeLine(
            opcode="mov",
            operands=f"${nslices*3*8}, %rdi",
            comment=f"room for {nslices} slice structs",
        ),
        CodeLine(opcode="call", operands="malloc"),
        CodeLine(opcode="movq", operands="%rax, %rdx"),
        CodeLine(opcode="addq", operands=f"${alignment},%rsp"),
    ]
    moveslices = []
    offset = nslices * 3 * 8 - 8
    for i in range(nslices - 1, -1, -1):
        moveslices.append(
            CodeLine(opcode="popq", operands="%rax", comment=f"slice[{i}].step")
        )
        moveslices.append(CodeLine(opcode="movq", operands="%rax, %xmm0"))
        moveslices.append(
            CodeLine(
                opcode="cvtsd2si",
                operands=f"%xmm0, %rax",
                comment="convert single double to long",
            )
        )
        moveslices.append(
            CodeLine(
                opcode="movq",
                operands=f"%rax, {offset}(%rdx)",
            )
        )
        offset -= 8
        moveslices.append(
            CodeLine(opcode="popq", operands="%rax", comment=f"slice[{i}].stop")
        )
        moveslices.append(CodeLine(opcode="movq", operands="%rax, %xmm0"))
        moveslices.append(
            CodeLine(
                opcode="cvtsd2si",
                operands=f"%xmm0, %rax",
                comment="convert single double to long",
            )
        )
        moveslices.append(
            CodeLine(
                opcode="movq",
                operands=f"%rax, {offset}(%rdx)",
            )
        )
        offset -= 8
        moveslices.append(
            CodeLine(opcode="popq", operands="%rax", comment=f"slice[{i}].start")
        )
        moveslices.append(CodeLine(opcode="movq", operands="%rax, %xmm0"))
        moveslices.append(
            CodeLine(
                opcode="cvtsd2si",
                operands=f"%xmm0, %rax",
                comment="convert single double to long",
            )
        )
        moveslices.append(
            CodeLine(
                opcode="movq",
                operands=f"%rax, {offset}(%rdx)",
            )
        )
        offset -= 8

    current_alignment = (
        alignment + nslices * 3 * 8 + 8
    ) % 16  # include the space for the rdx we will push
    slice = [
        CodeLine(opcode="popq", operands="%rdi", comment="the descriptor"),
        CodeLine(opcode="movq", operands=f"${nslices}, %rsi"),
        CodeLine(opcode="pushq", operands="%rdx", comment="save allocated pointer"),
        CodeLine(
            opcode="subq",
            operands=f"${current_alignment},%rsp",
            comment="make sure stack is 16 byte aligned",
        ),
        CodeLine(opcode="call", operands="matrix_slice"),
        CodeLine(opcode="addq", operands=f"${current_alignment},%rsp"),
        CodeLine(
            opcode="popq",
            operands="%rdi",
            comment="the pointer to the allocated slice array",
        ),
        CodeLine(opcode="pushq", operands="%rax"),
    ]

    free = [
        CodeLine(
            opcode="subq",
            operands=f"${alignment},%rsp",
            comment="make sure stack is 16 byte aligned",
        ),
        CodeLine(opcode="call", operands="free"),
        CodeLine(opcode="addq", operands=f"${alignment},%rsp"),
    ]

    return CodeChunk(
        intro=f"slice a matrix with {nslices} slices",
        lines=malloc + moveslices + slice + free,
    )


def fileref(filenumber, filename):
    return CodeChunk(
        lines=[CodeLine(opcode=".file", operands=f'{filenumber} "{filename}"')]
    )


def location(filenumber, lineno, index):
    return CodeChunk(
        lines=[CodeLine(opcode=".loc", operands=f"{filenumber} {lineno} {index}")]
    )


def stack_adjust(size):
    return CodeChunk(
        intro="adjust stack at end of unit",
        lines=[CodeLine(opcode="add", operands=f"${size}, %rsp")],
    )


def jump_if_false(label):
    return CodeChunk(
        lines=[
            CodeLine(opcode="popq", operands="%rax"),
            CodeLine(opcode="cmp", operands="$0, %rax"),
            CodeLine(opcode="jz", operands=label),
        ]
    )


def jump(label):
    return CodeChunk(lines=[CodeLine(opcode="jmp", operands=label)])


def labelCode(label):
    return CodeChunk(lines=[CodeLine(label=label)])


def scalar_to_mat(alignment):
    return CodeChunk(
        intro="convert double to 0 dim matrix",
        lines=[
            CodeLine(opcode="popq", operands="%rax"),
            CodeLine(
                opcode="subq",
                operands=f"${alignment+8},%rsp",
                comment="make sure stack is 16 byte aligned",
            ),
            CodeLine(opcode="movq", operands="%rax, %xmm0"),
            CodeLine(opcode="call", operands="scalar_to_mat"),
            CodeLine(opcode="addq", operands=f"${alignment+8},%rsp"),
            CodeLine(opcode="pushq", operands="%rax"),
        ],
    )


def scalar_to_mat_top1(alignment):
    return CodeChunk(
        intro="convert double on top[-1] to 0 dim matrix",
        lines=[
            CodeLine(opcode="movq", operands="8(%rsp), %rax", comment="we do not pop"),
            CodeLine(
                opcode="subq",
                operands=f"${alignment},%rsp",
                comment="make sure stack is 16 byte aligned",
            ),
            CodeLine(opcode="movq", operands="%rax, %xmm0"),
            CodeLine(opcode="call", operands="scalar_to_mat"),
            CodeLine(opcode="addq", operands=f"${alignment},%rsp"),
            CodeLine(opcode="movq", operands="%rax, 8(%rsp)"),
        ],
    )


def pushZero():
    return CodeChunk(
        lines=[
            CodeLine(
                opcode="pushq",
                operands="$0",
                comment="push zero (double or long are the same)",
            )
        ]
    )


# top is index (a long), top -1 is matrix
def getItemAndInc(alignment):
    convert = CodeChunk(
        intro="getItemAndInc",
        lines=[
            CodeLine(
                opcode="pushq",
                operands="8(%rsp)",
                comment="dup top[-1] (the matrix reference)",
            ),
            CodeLine(
                opcode="cvtsi2sdq",
                operands="8(%rsp), %xmm0",
                comment="convert the long index to a double",
            ),
            CodeLine(opcode="movq", operands="%xmm0, %rax"),
            CodeLine(opcode="pushq", operands="%rax"),
        ],
    )
    code = index_matrix(alignment)
    inc = CodeChunk(
        lines=[
            CodeLine(opcode="incq", operands="8(%rsp)", comment="increment the index"),
        ]
    )
    return convert + code + inc


# top is index (a long), top -1 is matrix. both stay on the stack
def jump_if_end_of_range(alignment, end_label):
    return CodeChunk(
        intro="check if index is beyond length of matrix",
        lines=[
            CodeLine(opcode="movq", operands="8(%rsp),%rdi"),
            CodeLine(opcode="movq", operands="(%rsp),%rsi"),
            CodeLine(
                opcode="call", operands="matrix_index_end"
            ),  # no floats, so we skip the stack alignment check
            CodeLine(opcode="and", operands="%rax, %rax"),
            CodeLine(opcode="jne", operands=end_label),
        ],
    )


def pop(n):
    return CodeChunk(
        intro=f"pop {n} items from the stack",
        lines=[CodeLine(opcode="addq", operands=f"${n*8}, %rsp")],
    )
