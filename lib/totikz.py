'''Utilities for translating a digraph dot-string to tikz code 
that can be edited by Tikzit (https://tikzit.github.io/).
This script uses dot2tex (https://dot2tex.readthedocs.io/).

Use `totikz` function:
    - `dot-input`:        the input dot string
    - `math_symbol_map`:  a dictionary that maps special symbols to
                          latex math commands
    - `coef`:             raw tikz code generated by dot2tex measures
                          length in bp; specify `coef` to rescale to
                          a number suitable for cm.
'''

import re
import dot2tex as d2t


BP_TO_CM = 25
MATH_SYMBOL_MAP = {'ρ': '$\\rho$',
                   'σ': '$\\sigma$',
                   'ι': '$\\iota$',
                   'λ': '$\\lambda$',
                   'κ': '$\\kappa$',
                   '¬': '$\\neg$',
                   '∀': '$\\forall$',
                   'every': '$\\forall$',
                   'most': '$\\%$',
                   '∈': '$\\in$',
                   '⊇': '$\\supseteq$',
                   '⊒': '$\\sqsupseteq$',
                   '⊂': '$\\subset$',
                   '⊃': '$\\supset$',
                   '\\\\#': '$\\#$',
                   '(?<=\\{)no(?=\\})': '$\\neg$'}


def make_math_trans(math_symbol_map=MATH_SYMBOL_MAP):
    def lookup(m):
        s = m.group(0)
        if s == '\\#':
            s = '\\\\#'
        elif s == 'no':
            s = '(?<=\\{)no(?=\\})'
        return math_symbol_map.get(s)
    def math_trans(s, pattern=re.compile('|'.join(math_symbol_map))):
        return pattern.sub(lookup, s)
    return math_trans


def coord_adjust(s, coef,
    pattern=re.compile(r'\((.+)bp,(.+)bp\)')):
    x, y = map(float, pattern.search(s).groups())
    return '(%.2f,%.2f)' % (x / coef, y / coef)
    

def head_adjust(s):
    return s if 'u' not in s else '(%s.center);' % s[1:-2]


def node_line_transform(s, coef):
    parts = s.strip().split()
    parts[3] = coord_adjust(parts[3], coef)
    parts = parts[:4] + parts[5:]
    parts[1:1] = ['[style=none]'] if 'u' in parts[1] else \
                 ['[style=node]']
    return '\t' + ' '.join(parts)


def label_line_transform(s, num, coef):
    parts = s.strip().split()
    return '\t\\node [style=none] (%s) at %s %s' % (
        num, coord_adjust(parts[1], coef), parts[3]) 


def edge_line_transform(s):
    parts = s.strip().split()
    return '\t\\draw [style=arrow] %s to %s' % (
        parts[2], head_adjust(parts[-1]))


def in_frame(node_lines, edge_lines, template=
    '\\begin{tikzpicture}\n'
    '\\begin{pgfonlayer}{nodelayer}\n'
    '%s\n'
    '\\end{pgfonlayer}\n'
    '\\begin{pgfonlayer}{edgelayer}\n'
    '%s\n'
    '\\end{pgfonlayer}\n'
    '\\end{tikzpicture}'):
    return template %('\n'.join(node_lines),
                      '\n'.join(edge_lines))


def totikz(dot_input:str, math_trans=make_math_trans(), 
                          coef=BP_TO_CM) -> str:
    '''Translate a dot-string into `tikz` code editable by Tikzit.'''
    raw = d2t.dot2tex(dot_input, format='tikz', 
                      prog='neato', codeonly='True')

    code = math_trans(raw).split('\n')
    label_count = 0
    node_lines, edge_lines = [], []

    for line in code[1:-1]:
        if line.strip().startswith('\\node'):
            node_lines.append(node_line_transform(line, coef))        
        elif line.strip().startswith('\\draw') and 'node' in line:
            node_lines.append(label_line_transform(line, label_count, coef))
            label_count += 1
        elif line.strip().startswith('\\draw') and 'node' not in line:
            edge_lines.append(edge_line_transform(line))
        
    return in_frame(node_lines, edge_lines)
