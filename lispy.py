#tutorial from http://norvig.com/lispy.html
#BUILD THE LISP INTERPRETER AND UNDERSTAND WHAT ALEN KAY CALLED:   "Maxwell's Equatoins of Software" 
#http://www.righto.com/2008/07/maxwells-equations-of-software-examined.html
import math
import operator as op 

################## Types #######################
Symbol = str
List = list
Number = (int, float)

################## Parser ######################

def tokenize(chars: str) -> list:
    "convert string of values into a list of tokens. Add white space to parentesis " 
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()


def parse(program: str): 
    "set temporary variable for the tokenized list"
    return read_from_tokens(tokenize(program)) 


def read_from_tokens(tokens: list):
    "Read an expression from a sequence of tokens." 
    if len(tokens) == 0: 
        raise SyntaxError("unexprected EDF")
    token = tokens.pop(0) 
    if token == '(': 
         L = []
         while tokens[0] != ')': 
             L.append(read_from_tokens(tokens))
         tokens.pop(0) # pop off ')' 
         return L 
    elif token == ')': 
        raise SyntaxError('unexpected )')
    else: 
        return atom(token)

def atom(token: str): 
    "Number become numbers: every other token is a symbol." 
    try:
        return int(token)
    except ValueError: 
        try:
            return float(token)
        except ValueError: 
            return Symbol(token)
 
 ##################### Enviroments #######################

def standard_Env(): 
    "An enviroment with some Scheme standrard procedures." 
    env = Env()
    env.update(vars(math)) #sin, cos, sqrt, pi, ...
    env.update({
        '+': op.add, '-':op.sub, '*':op.mul, '/':op.truediv,
        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq, 
        'abs': abs, 
        'append': op.add, 
        'apply': lambda proc, args: proc(*args), 
        'begin': lambda *x: x[-1],
        'car':   lambda x: x[0], 
        'cdr':   lambda x: x[1], 
        'cons':  lambda x,y: [x] + y,
        'eq?' :  op.is_, 
        'expt':  pow, 
        'equal?': op.eq, 
        'length': len, 
        'list':  lambda *x: list(x), 
        'list?': lambda x: isinstance(x, list), 
        'map': map, 
        'max': max, 
        'min': min, 
        'not': op.not_, 
        'null?': lambda x:x == [], 
        'number?' : lambda x: isinstance(x, Number), 
        'print': print, 
        'procedure?': callable, 
        'round': round, 
        'symbol?' : lambda x: isinstance(x, Symbol),
    })
    return env

################## Define Env #########################

class Env(dict):
    "An environment: a dict of {'var': val} pairs , with outer Env."
    def __init__(self, parms=(), args = (), outer=None):
        self.update(zip(parms, args))
        self.outer = outer
    def find(self, var):
        "Find the innermost Env where var appears."
        return self if (var in  self) else self.outer.find(var)
        
global_env = standard_Env()

################ Procedues

class Procedure(object):
    "A user-defined Scheme procedure"
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env
    def __call__(self, *args):
        return eval(self.body, Env(self.parms, args, self.env))

################ The eval Function ###################

def eval(x, env=global_env):
    "Evaluate an expression in an environment."
    if isinstance(x, Symbol):   # variable reference 
        return env.find(x)[x]
    elif not isinstance(x, List):      # constant
        return x
    op, *args = x
    if op == 'quote':                  # quotation
        return args[0]
    elif isinstance(x, Number):
        return x
    elif x[0] =='if':                  # conditionals
        (_, test, conseq, alt) = x
        exp = (conseq if  eval (test, env) else alt)
        return eval(exp, env)
    elif x[0] == 'define':             # definition
        (_, symbol, exp) = x 
        env[symbol] = eval(exp, env)
    elif op =='set':                   # assignmnet
        (symbol, exp) = args
        env.find(symbol)[symbol] = eval(exp, env)
    elif op == 'lambda':               # procedure
        (parms, body) = args
        return Procedure(parms, body , env)
    else:                              # procedure call 
        proc = eval(x[0], env)
        args = [eval(arg, env) for arg in x[1:]]
        return proc(*args)

################## Interaction ####################

def repl(prompt='lispy.py>'):
    "A prompt-read-eval-print loop."
    while True:
        val = eval(parse(input(prompt)))
        if val is not None:
            print(schemestr(val))
def schemestr(exp):
    "Convert a python object back into s Scheme-readable string."
    if isinstance(exp, List):
        return '(' + ' '.join(map(schemestr, exp)) + ')'
    else: 
        return str(exp)

