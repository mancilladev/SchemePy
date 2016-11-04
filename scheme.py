#!/usr/bin/env python
import sys
import math
import readline
import operator as op
from functools import reduce


readline.parse_and_bind('tab: complete')
readline.parse_and_bind('set editing-mode vi')


class Env(dict):
    """Diccionario Python con Env exterior"""
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer
    def find(self, var):
        '''Buscar variable del Env más profundo al menos'''
        return self if (var in self) else self.outer.find(var)


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
        'car':     lambda x: x[0],
        'cdr':     lambda x: x[1:], 
        'cons':    lambda x,y: [x] + y,
        'eq?':     op.is_, 
        'equal?':  op.eq, 
        'length':  len, 
        'list':    lambda *x: list(x), 
        'list?':   lambda x: isinstance(x,list), 
        'map':     lambda f, l: list(map(f, l)),
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [], 
        'number?': lambda x: isinstance(x, Number),   
        'procedure?': callable,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
        'true': True,
        'false': False,
    })
    return env


class Procedure(object):
    """Función creada por el usuario"""
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env
    def __call__(self, *args):
        return eval(self.body, Env(self.parms, args, self.env))
        

global_env = standard_env()


def eval(x, env=global_env):
    # Variable reference
    if isinstance(x, Symbol):
        return env.find(x)[x]
    # Constant literal
    elif not isinstance(x, List):
        return x
    # Quotation
    elif x[0] == 'quote':
        _, exp = x
        return exp
    # Conditional
    elif x[0] == 'if':
        _, test, conseq, alt = x
        exp = conseq if eval(test, env) else alt
        return eval(exp, env)
    # Variable or function definition
    elif x[0] == 'define':
        _, var, exp = x
        env[var] = eval(exp, env)
    # Variable or function assignment
    elif x[0] == 'set!':
        _, var, exp = x
        env.find(var)[var] = eval(exp, env)
    # Procedure creation
    elif x[0] == 'lambda':
        _, parms, body = x
        return Procedure(parms, body, env)
    # Begin program
    elif x[0] == 'begin':
        return '\n'.join(filter(lambda x: x != 'None', [str(eval(exp, env)) for exp in x[1:]]))
    # Procedure call
    else:
        procedure = eval(x[0], env)
        args = [eval(arg, env) for arg in x[1:]]
        return procedure(*args)


# -----------------------------------------------------------------------------
# REPL
# -----------------------------------------------------------------------------
def repl(prompt='scm> '):
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


def main():
    if len(sys.argv) == 2:
        with open(sys.argv[1], 'r') as fin:
            val = eval(parse(fin.read()))
            if val is not None:
                print(schemestr(val))
            exit()
    else:
        try:
            repl()
        except (KeyboardInterrupt, EOFError):
            exit()
        except Exception as e:
            print(sys.exc_info()[0])
            main()


if __name__ == "__main__":
    main()
