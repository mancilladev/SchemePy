#!/usr/bin/env python
import sys
import math
import readline
import operator as op
from functools import reduce


readline.parse_and_bind('tab: complete')
readline.parse_and_bind('set editing-mode vi')


Env = dict            # An environment is a mapping of {variable: value}
Symbol = str          # A Scheme Symbol is implemented as a Python str
List   = list         # A Scheme List is implemented as a Python list
Number = (int, float) # A Scheme Number is implemented as a Python int or float


# -----------------------------------------------------------------------------
# PARSING
# -----------------------------------------------------------------------------
def tokenize(chars):
    '''Convierte un string de caractéres a una lista de tokens'''
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()


def atom(token):
    '''Convertir números a números, lo demás son símbolos'''
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)


def read_from_tokens(tokens):
    '''Leer expresión de una secuencia de tokens'''
    if len(tokens) == 0:
        raise SyntaxError('Unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0) # pop ')'
        return L
    elif ')' == token:
        raise SyntaxError('Unexpected character: )')
    else:
        return atom(token)


def parse(program):
    '''Lee expresión Scheme como string,
    convierte ello a un abstract syntax tree'''
    return read_from_tokens(tokenize(program))


# -----------------------------------------------------------------------------
# EXECUTING
# -----------------------------------------------------------------------------
def standard_env():
    ''' Definimos las funciones built-in del lenguaje, aquí también irán las
    variables y funciones que se creen durante la ejecución del programa '''
    env = Env()
    env.update(vars(math)) # sin, cos, sqrt, pi, ...
    env.update({
        '+':lambda *x: reduce(op.add, x), '-':lambda *x: reduce(op.sub, x),
        '*':lambda *x: reduce(op.mul, x), '/':lambda *x: reduce(op.truediv, x),
        '>':lambda *x: reduce(op.gt, x), '<':lambda *x: reduce(op.lt, x),
        '>=':lambda *x: reduce(op.ge, x), '<=':lambda *x: reduce(op.le, x),
        '=':lambda *x: reduce(op.eq, x), 'and':lambda *x: reduce(lambda a,b: a and b, x),
        'or':lambda *x: reduce(lambda a,b: a or b, x),
        'abs':      abs,
        'append':   op.add,
        'begin':    lambda *x: x[-1],
        'car':     lambda x: x[0],
        'cdr':     lambda x: x[1:], 
        'cons':    lambda x,y: [x] + y,
        'eq?':     op.is_, 
        'equal?':  op.eq, 
        'length':  len, 
        'list':    lambda *x: list(x), 
        'list?':   lambda x: isinstance(x,list), 
        'map':     map,
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [], 
        'number?': lambda x: isinstance(x, Number),   
        'procedure?': callable,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
    })
    return env


global_env = standard_env()


def eval(x, env=global_env):
    # Variable reference
    if isinstance(x, Symbol):
        return env[x]
    # Constant
    elif not isinstance(x, List):
        return x
    # Conditional
    elif x[0] == 'if':
        _, test, conseq, alt = x
        exp = conseq if eval(test, env) else alt
        return eval(exp, env)
    # Variable or function definition
    elif x[0] == 'define':
        _, var, exp = x
        env[var] = eval(exp, env)
    # Procedure call
    else:
        procedure = eval(x[0], env)
        args = [eval(arg, env) for arg in x[1:]]
        return procedure(*args)


# -----------------------------------------------------------------------------
# REPL
# -----------------------------------------------------------------------------
def repl(prompt='~> '):
    while True:
        line = input(prompt)
        if line == '': continue
        else:
            val = eval(parse(line))
            if val is not None:
                print(schemestr(val))


def schemestr(exp):
    if isinstance(exp, List):
        return '(' + ' '.join(map(schemestr, exp)) + ')'
    else:
        return str(exp)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        with open(sys.argv[1], 'r') as fin:
            val = eval(parse(fin.read()))
            if val is not None:
                print(schemestr(val))
            exit()
    try:
        repl()
    except EOFError:
        print('Goodbye')
