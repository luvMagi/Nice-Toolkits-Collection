svf_grammar = r"""
start: expr

?expr: logic

# 逻辑层（优先级最低）
?logic: logic AND compare      -> and_expr
      | logic OR  compare      -> or_expr
      | NOT compare            -> not_expr
      | compare

# 比较层
?compare: arith
        | arith "="  arith     -> eq
        | arith "<>" arith     -> ne
        | arith "!=" arith     -> ne
        | arith "<"  arith     -> lt
        | arith ">"  arith     -> gt
        | arith "<=" arith     -> le
        | arith ">=" arith     -> ge

# 算术层
?arith: arith "+" term         -> add
      | arith "-" term         -> sub
      | term

# 乘除层（可选，如果需要 * /）
?term: term "*" factor         -> mul
     | term "/" factor         -> div
     | factor

# 原子
?factor: func_call
       | NAME                  -> name
       | NUMBER                -> number
       | STRING                -> string
       | "(" expr ")"
       | "-" factor            -> neg   // 一元负号

# 函数调用
func_call: NAME "(" [args] ")"
args: expr ("," expr)*

# 词法
NAME   : /[A-Za-z_][A-Za-z0-9_]*/
NUMBER : /\d+(\.\d+)?/

// 同时支持 '...' 或 "..." 字符串
STRING : ESCAPED_STRING_SQ
       | ESCAPED_STRING_DQ
ESCAPED_STRING_SQ : /'([^'\\]|\\.)*'/
ESCAPED_STRING_DQ : /"([^"\\]|\\.)*"/

AND    : /(?i:AND)/
OR     : /(?i:OR)/
NOT    : /(?i:NOT)/

%import common.WS
%ignore WS
"""
