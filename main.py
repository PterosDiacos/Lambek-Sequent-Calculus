import json
import sys
import displace as dsp
import lbnoprod as npr
from lbnoprod import parseProof
from cmll import ProofNet
from cntccg import Cntccg
from cindex import indexSeq


LinkSearch = []
def registerLinkSearch(f):
    LinkSearch.append(f)
    return f


@registerLinkSearch
def pnLinks(con: str, pres: list):
    (con, *pres), _ = indexSeq(con, pres)
    pn = ProofNet.fromLambekSeq(con, pres)
    pn.buildProofs()
    if pn.proofCount:
        print('%s\n%s <= %s\n' % ('-' * 10, con, ' '.join(pres)))
        pn.printProofLinks(symbolOnly=True)
        print('Total: %d\n' % pn.proofCount)
    
    return pn.proofCount


@registerLinkSearch
def noprodLinks(con, pres):
    (con, *pres), _ = indexSeq(con, pres)
    proofs = npr.findproof(con, *pres)
    links = parseProof(proofs)
    if links:
        print('%s\n%s <= %s\n' % ('-' * 10, con, ' '.join(pres)))
        print(*links, sep='\n', end='\n\n')
        print('Total: %d\n' % len(links))
    
    return len(links)


@registerLinkSearch
def ccgLinks(con, pres):
    (con, *pres), _ = indexSeq(con, pres)
    ccg = Cntccg(pres)
    ccg.parse()
    if ccg.proofCount(con):
        print('%s\n%s <= %s\n' % ('-' * 10, con, ' '.join(pres)))
        ccg.printProofs(con)
        print('Total: %d\n' % ccg.proofCount(con))
    
    return ccg.proofCount(con)


@registerLinkSearch
def dspLinks(con, pres):
    (con, *pres), _ = indexSeq(con, pres)
    proofs = dsp.findproof(con, *pres)
    links = parseProof(proofs)
    if links:
        print('%s\n%s <= %s\n' % ('-' * 10, con, ' '.join(pres)))
        print(*links, sep='\n', end='\n\n')
        print('Total: %d\n' % len(links))
    
    return len(links)    


def deAbbr(con: str, pres: list, abbr: dict):
    def gen(L):
        if L:
            head, *tail = L
            for hopt in abbr.get(head, [head]):
                for topt in gen(tail): 
                    yield [hopt] + topt
        else:
            yield []
    for con, *pres in gen([con] + pres):
        yield con, pres


if __name__ == '__main__':
    con, *pres = json.load(open('input.json'))[0]
    abbr = json.load(open('abbr.json'))

    # defaults to ccgLinks
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    f = LinkSearch[n]
    print(f)

    f.count = 0
    for con, pres in deAbbr(con, pres, abbr):
        f.count += f(con, pres)

    if not f.count:
        print('Total: 0\n')
