from .cterm import towerSplit
from .tobuss import trans_term


def trans_cat(cat, inMath):
    c, a, b = towerSplit(cat)
    if a:
        return '$\\dfrac{%s|%s}{%s}$' % (
            trans_cat(a, True),
            trans_cat(b, True),
            trans_cat(c, True))
    else:
        return trans_term(cat, inMath)


def axiom_line(cat, indent=''):
    return '%s\\AXC{%s}\n' %  (
        indent, trans_cat(cat, False))


def binary_infer(above1, above2, cat, indent=''):
    return '%s%s%s\\BIC{%s}\n' % (
        above1, above2, indent, trans_cat(cat, False))


def toBussCcg(tree, proofs, 
              indent='', space=' ' * 4):
    res = ''
    for r in proofs:
        if not indent:
            s = sorted('(%s, %s)' % (i, j) for (i, j) in r.links)
            res += ', '.join(s) + '\n' + '-' * 10 + '\n'
            res += '\\begin{prooftree}\n\\EnableBpAbbreviations\n'
        
        if r in tree:
            sub1, sub2 = tree[r]
            res += binary_infer(
                toBussCcg(tree, [sub1], indent + space),
                toBussCcg(tree, [sub2], indent + space), 
                r.cat, indent)
        else:
            res += axiom_line(r.cat, indent)
        
        if not indent:
            res += '\\end{prooftree}\n\n\n'
    
    return res
