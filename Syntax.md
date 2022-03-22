Recognized syntax
-----------------

A slighly truncated syntax (some parameter and arglist definitions are ommited for brevity)

```
    # program : { unit }          ( zero or more units )
    
    # suite : { simpleunit }      ( zero or more simple units )
    
    # unit : function NEWLINE     ( we can only define/declare functions globally )
    #      | external NEWLINE
    #      | simpleunit
    
    # function : FUN rtype NAME "(" parameters ")" COLON NEWLINE INDENT suite DEDENT
 
    # external : EXTERN FUN rtype NAME "(" parameters ")"
    
    # simpleunit:expression NEWLINE
    #      | compound
    #      | RETURN [expression] NEWLINE
    #      | BREAK NEWLINE
    #      | CONTINUE NEWLINE
    #      | NEWLINE
    #      | ptype vardecls NEWLINE
    #      | CONST ptype vardecls NEWLINE
    
    # vardecls : vardecl
    #          | vardecl "," vardecls
    #          | NAME
    #          | NAME "=" expr
    #          | NAME LBRACKET elist RBRACKET
    
    # expression : reference = expr         ( an expression is an assignment or a simple expression )
    #            | reference APLUS expr     ( a += b )
    #            | reference AMINUS expr    ( a -= b )
    #            | reference AMUL expr      ( a *= b )
    #            | reference ADIV expr      ( a /= b )
    #            | reference AMOD expr      ( a %= b )
    #            | expr
    
    # expr : expr + expr
    #      | expr - expr
    #      | expr * expr
    #      | expr / expr
    #      | expr MODULO expr           a % b
    #      | expr POWER expr            a ** b
    #      | expr MATMUL expr           a @ b
    #      | expr DOT expr              a . b
    #      | expr CROSS expr            a ⨯ b   (that's a Unicode ⨯ U+2A2F vector or cross product)
    #      | expr EQUAL expr            a == b
    #      | expr NOTEQUAL expr         a != b
    #      | expr LESS expr             a < b
    #      | expr GREATER expr          a > b
    #      | expr LESSOREQUAL expr      a <= b
    #      | expr GREATEROREQUAL expr   a >= b
    #      | - expr
    #      | ROOT expr                  √ a     (that's a Unicode √ U+221A square root)
    #      | "(" ptype ")" expr %prec CAST      (an explicit cast to a type)
    #      | ( expr )
    #      | reference                          (a reference to a variable (possibly indexed))
    #      | NUMBER                             (a double )
    #      | STRINGLITERAL                      (a string "" or an interpolated string f"")
    #      | LBRACKET elist RBRACKET            (a matrix literal)
    #      | NAME "(" arguments ")"             (a function call)

    # reference : NAME
    #           | NAME indexlist
 
    # indexlist : LBRACKET slice RBRACKET
    #           | LBRACKET slice RBRACKET indexlist
 
    # slice     : vexpr COLON vexpr COLON vexpr
    #           | vexpr COLON vexpr
    #           | expr
 
    # vexpr     : expr
    #           | empty

    # compound : IF expression COLON NEWLINE INDENT suite DEDENT [ ELSE COLON NEWLINE INDENT  suite DEDENT ]
    #          | WHILE expression COLON NEWLINE INDENT suite DEDENT
    #          | FOR NAME IN expr COLON NEWLINE INDENT suite DEDENT"
    #          | ASSERT expr "," STRINGLITERAL

```
