import copy
from utils.sequencer import Sequencer
# --------- cvs tools ------------
# C: contains, I: intersection
def cvs1_C_cvs2(c1, c2):
    return c1 == {'*'} or c1.issuperset(c2)

def cvs1_I_cvs2(c1, c2):
    if c1 == {'*'}: return c2
    if c2 == {'*'}: return c1
    return c1.intersection(c2)

def po_cvs(cvs):
    m = '('
    for v in sorted(cvs):
        m += str(v)
    m += ')'
    return m

flip = lambda val: (val + 1) % 2

#------------ node tools -----------
def clone_node(nd): # nd : {<nov>:<cvs-set>,..}
    return copy.deepcopy(nd)

def is_single(node):
    for cvs in node.values():
        if len(cvs) > 1: return False
    return True

def node_seq(node):
    return Sequencer(node) # return a generator

def fill_nvs(node, nvs): # node can be a dict, or a BitBlocker-inst
    if type(node) == dict:
        for nv in nvs:
            if nv not in node:
                node[nv] = {'*'}
        return node
    # node is of class BitBlocker
    bb = node
    for nd in bb.nodes:
        nd = fill_nvs(nd, nvs)
    return bb

def fill_missing(node1, node2, steps):
    if len(steps) == len(node1) and len(steps)  == len(node2): 
        return
    for nv in steps:
        if nv not in node1: node1[nv] = {'*'}
        if nv not in node2: node2[nv] = {'*'}

def node1_C_node2(n1, n2, steps):
    fill_missing(n1, n2, steps)
    for nv, cvs in n1.items():
        if not cvs1_C_cvs2(n1[nv], n2[nv]):
            return False
    return True

def node_intersect(n1, n2, steps):
    fill_missing(n1, n2, steps)
    dic = {}
    for nv in n1:
        intrsct = cvs1_I_cvs2(n1[nv], n2[nv])
        if len(intrsct) == 0: return None
        dic[nv] = intrsct
    return dic

def node_to_lst(node, lst, steps): # add node to lst, if node is not contained in it.
    for nd in lst:
        if node1_C_node2(nd, node, steps): return False
    lst.append(node)
    return True

def subtract_delta_node(node, delta_node, chvdict):
    nvs = sorted(node)
    # for nv in nvs:
    #     if node[nv] == {'*'}:       node[nv] = set(chvdict[nv])
    #     if delta_node[nv] == {'*'}: delta_node[nv] = set(chvdict[nv])
    cmm = node_intersect(node, delta_node, chvdict)
    if not cmm: return node
    res = []
    seq1 = Sequencer(cmm)
    seq2 = Sequencer(node)
    while not seq1.done:
        while not seq2.done:
            n1 = seq1.get_next()
            n2 = seq2.get_next()
            if n1 != n2:
                res.append(n2)
    return res

def check_spouse(bb_dic):
    if len(bb_dic) > 1:
        bb_dic[0].spouse = bb_dic[1]
        bb_dic[1].spouse = bb_dic[0]
        bb_dic[0].spousal_conflict(bb_dic[1])

