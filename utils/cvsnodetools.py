import copy
from utils.sequencer import Sequencer
from hashlib import md5
# --------- cvs tools ------------
# C: contains, I: intersection
def cvs1_contains_cvs2(c1, c2):
    return c1 == {'*'} or c1.issuperset(c2)

def cvs1_intersect_cvs2(c1, c2):
    if c1 == {'*'}: return c2
    if c2 == {'*'}: return c1
    return c1.intersection(c2)

def cvs1_minus_cvs2(c1, c2, chvdict):
    pass

def po_cvs(cvs):
    m = '('
    for v in sorted(cvs):
        m += str(v)
    m += ')'
    return m


#------------ node tools -----------
def clone_node(nd): # nd : {<nov>:<cvs-set>,..}
    return copy.deepcopy(nd)

def signature(obj):
    sig = md5(str(obj).encode('utf-8'))
    return sig.digest().hex()

def is_single(node):
    for cvs in node.values():
        if len(cvs) > 1: return False
    return True

def node_seq(node):
    return Sequencer(node) # return a generator

def missing_nv2star(node1, node2, steps):
    if len(steps) == len(node1) and len(steps)  == len(node2): 
        return
    for nv in steps:
        if type(node1) == list:
            for nd in node1:
                if nv not in nd: nd[nv] = {'*'}
        else:
            if nv not in node1: node1[nv] = {'*'}
        if nv not in node2: node2[nv] = {'*'}

def node_valid(node):
    for nv, v in node.items():
        if len(v) == 0: return False
    return True

def node1_C_node2(n1, n2, steps):
    if steps:
        missing_nv2star(n1, n2, steps)
    for nv, cvs in n1.items():
        if not cvs1_contains_cvs2(n1[nv], n2[nv]):
            return False
    return True

def node_intersect(n1, n2):
    dic = {}
    for nv in n1:
        intrsct = cvs1_intersect_cvs2(n1[nv], n2[nv])
        if len(intrsct) == 0: return None
        dic[nv] = intrsct
    return dic

def node_to_lst(node, lst, steps=None): 
    # add node to lst, if not contained in it. 
    for nd in lst:
        if node1_C_node2(nd, node, steps):
            # node is in one of nd in self.nodes: node not added
            return False 
    lst.append(node) # node not contained in any of self.nodes: add it
    return True

def expand_star(node, chvdict):
    if type(node) == list:
        ind = 0
        while ind < len(node):
            expand_star(node[ind], chvdict)
            ind += 1
    elif type(node) == dict:
        for nv in chvdict:
            if (nv not in node) or (node[nv] == {'*'}):
                node[nv] = chvdict[nv]

def subtract_delta_node(node, delta_node):
    if node == delta_node: return {}
    cmm = node_intersect(node, delta_node)
    if not cmm: return node
    res = []
    seq1 = Sequencer(cmm)
    seq2 = Sequencer(node)
    while not seq1.done:
        n1 = seq1.get_next()
        while not seq2.done:
            n2 = seq2.get_next()
            if n1 != n2:
                res.append(n2)
    return res

def check_spouse(bb_dic):
    if len(bb_dic) > 1:
        bb_dic[0].spouse = bb_dic[1]
        bb_dic[1].spouse = bb_dic[0]
        bb_dic[0].spousal_conflict(bb_dic[1])

