"""
    Lispy Python (Pythonic Lisp?)
"""
import ply.lex as lex
import ply.yacc as yacc
import traceback

DEBUG = False

#### LEXER ####

reserved = {
    'and' : 'AND',
    'or' : 'OR',
    'let' : 'LET'
}

# Must be present
tokens = [
    'SYMBOL',
    'NUMBER',
    'TIMES',
    'DIVIDE',
    'PLUS',
    'MINUS',
    'POW',
    'MOD',
    'EQUALS',
    'LT',
    'GT',
    'LE',
    'GE',
    'LPAREN',
    'RPAREN'
] + list(reserved.values())

# Tokens
# Each definition must be of the form t_<token name defined above>

def t_error(t):
    print "Illegal character \'str(t.value[0])\'"
    t.lexer.skip(1)

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_SYMBOL(t):
    r'[a-zA-Z_][a-zA-Z0-9]*'
    t.type = reserved.get(t.value, 'SYMBOL')
    return t

def t_NUMBER(t):
    r'[-]?(([0-9]+\.[0-9]+)|(\.[0-9]+)|([0-9]+\.?))'
    if '.' in t.value:
        try:
            t.value = float(t.value)
        except ValueError:
            print "Float value too large: " + str(t.value)
            t.value = 0.0
    else:
        try:
            t.value = int(t.value)
        except ValueError:
            print "Integer value too large: " + str(t.value)
            t.value = 0
    return t

t_ignore = ' \t'

t_TIMES = r'\*'
t_DIVIDE = r'/'
t_PLUS = r'\+'
t_MINUS = r'-'
t_POW = r'\^'
t_MOD = r'%'
t_EQUALS = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LE = r'<='
t_GE = r'>='
t_LT = r'<'
t_GT = r'>'

lex.lex()

#### PARSER ####

# Symbols
SYMBOLS = {}

def p_result(p):
    '''
    result : statement
    '''
    print p[1]

### Statements
def p_statement_expression(p):
    '''
    statement : LPAREN expression RPAREN
    '''
    p[0] = p[2]

### Expressions
def p_expression_let(p):
    '''
    expression : LET SYMBOL operand
    '''
    SYMBOLS[p[2]] = p[3]
    p[0] = p[3]

# Mathematical expressions
def p_expression_plus(p):
    '''
    expression : PLUS operands
    '''
    if operand_check(p, 2, '+'):
        p[0] = reduce(lambda x, y: x + y, p[2])

def p_expression_minus(p):
    '''
    expression : MINUS operands
    '''
    if operand_check(p, 2, '-'):
        p[0] = reduce(lambda x, y: x - y, p[2])

def p_expression_times(p):
    '''
    expression : TIMES operands
    '''
    if operand_check(p, 2, '*'):
        p[0] = reduce(lambda x, y: x * y, p[2])

def p_expression_divide(p):
    '''
    expression : DIVIDE operands
    '''
    if operand_check(p, 2, '/'):
        p[0] = reduce(lambda x, y: x / y, p[2])

def p_expression_pow(p):
    '''
    expression : POW operands
    '''
    if operand_check(p, 2, '^'):
        p[0] = reduce(lambda x, y: x ** y, p[2])

def p_expression_mod(p):
    '''
    expression : MOD operands
    '''
    if operand_check(p, 2, '%'):
        p[0] = reduce(lambda x, y: x % y, p[2])

# Boolean expressions
def p_expression_gt(p):
    '''
    expression : GT operands
    '''
    if operand_check(p, 2, '>'):
        p[0] = reduce(lambda x, y: x > y, p[2])

def p_expression_ge(p):
    '''
    expression : GE operands
    '''
    if operand_check(p, 2, '>='):
        p[0] = reduce(lambda x, y: x >= y, p[2])

def p_expression_lt(p):
    '''
    expression : LT operands
    '''
    if operand_check(p, 2, '<'):
        p[0] = reduce(lambda x, y: x < y, p[2])

def p_expression_le(p):
    '''
    expression : LE operands
    '''
    if operand_check(p, 2, '<='):
        p[0] = reduce(lambda x, y: x <= y, p[2])

def p_expression_and(p):
    '''
    expression : AND operands
    '''
    if operand_check(p, 2, 'and'):
        p[0] = reduce(lambda x, y: x and y, p[2])

def p_expression_or(p):
    '''
    expression : OR operands
    '''
    if operand_check(p, 2, 'or'):
        p[0] = reduce(lambda x, y: x or y, p[2])

def p_expression_equals(p):
    '''
    expression : EQUALS operands
    '''
    if operand_check(p, 2, '='):
        p[0] = reduce(lambda x, y: x == y, p[2])

### Operands
def p_operands(p):
    '''
    operands : operand
             | operand operands
    '''
    p[0] = []
    for i in p[1:]:
        p[0] += [j for j in i] if isinstance(i, list) else [i]

def p_operand(p):
    '''
    operand : statement
            | NUMBER
    '''
    p[0] = p[1]

def p_operand_symbol(p):
    '''
    operand : SYMBOL
    '''
    if p[1] in SYMBOLS:
        p[0] = SYMBOLS[p[1]]
    else:
        raise Exception, "Unknown symbol \'" + p[1] + "\' at position " + \
            str(p.lexpos(1))

def operand_check(p, size, op):
    if len(p[2]) < size:
        raise Exception, "Operator \'" + op + "\' at position " + \
            str(p.lexpos(1)) + "requires at least " + str(size) + " operands"
    else:
        return True

### Error
def p_error(p):
    if p:
        print "Syntax error at \'" + p.value + "\'"
    else:
        print "Malformed expression (missing closing parenthesis?)"

yacc.yacc()

while 1:
    try:
        s = raw_input('> ')
    except EOFError:
        break
    s = s.strip()
    if not s:
        continue
    if s == "quit" or s == "exit":
        break
    try:
        yacc.parse(s)
    except Exception as e:
        print e
        if DEBUG:
            print traceback.format_exc()
