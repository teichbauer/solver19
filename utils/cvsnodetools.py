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
    return Sequencer(node) # returna generator

def fill_missing(node1, node2):
    nvs1 = sorted(node1)
    nvs2 = sorted(node2)
    if nvs1 == nvs2: return
    if len(nvs1) > len(nvs2):
        for nv in nvs1:
            if nv not in node2: node2[nv] = {'*'}
    if len(nvs2) > len(nvs1):
        for nv in nvs2:
            if nv not in node1: node1[nv] = {'*'}

def node1_C_node2(n1, n2):
    fill_missing(n1, n2)
    for nv, cvs in n1.items():
        if not cvs1_C_cvs2(n1[nv], n2[nv]):
            return False
    return True

def node_intersect(n1, n2):
    fill_missing(n1, n2)
    dic = {}
    for nv in n1:
        intrsct = cvs1_I_cvs2(n1[nv], n2[nv])
        if len(intrsct) == 0: return None
        dic[nv] = intrsct
    return dic

def node_to_lst(node, lst): # add node to lst, if node is not contained in it.
    for nd in lst:
        if node1_C_node2(nd, node): return False
    lst.append(node)
    return True


