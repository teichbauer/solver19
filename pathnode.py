
import copy
from utils.sequencer import Sequencer
from utils.cvsnodetools import *

def _is_single(node):
    for nv in node:
        if len(node[nv]) != 1: return False
    return True

def _split_single(node, sngl): # node: single or compound. sngl: sure single
    # return True: node is single, and node == sngl
    # return [..]: node is compound. After subtract sngl from it
    #              returned list of single-nds: the rest of node
    # return : False - node and sngl don't touch
    if _is_single(node):
        return node == sngl
    # node is not single - 
    res = []
    seq = Sequencer(node)
    is_subset = False
    while not seq.done:
        nd = seq.get_next()
        if nd == sngl:
            is_subset = True
        else:
            res.append(nd)
    if is_subset: return res
    return False

def _node_intersect(n1, n2): # both n1 and n2 can be compound or single
    # n1 and n2 must have the same novs
    lst = []
    n1seq = Sequencer(n1)
    n2seq = Sequencer(n2)
    while not n1seq.done:
        n1s = n1seq.get_next()
        while not n2seq.done:
            n2s = n2seq.get_next()
            if n1s == n2s:
                lst.append(n1s)
        else:
            n2seq.reset()
    return lst  # list of single nds that are the intersection-nodes

def _node_subtract(src, delta): 
    # delta is a subset of src, subtract it from src
    # both drlta/src are dict: k/v - nov/cvs(set)
    res = {}
    for nv in src:
        res[nv] = src[nv] - delta[nv]
    return res

class PathNode:
    def __init__(self, path, nodes=None):
        self.path = path
        if nodes: 
            self.nodes = [copy.deepcopy(n) for n in nodes]
        else:
            self.nodes = [] #
        self.srcdic = {}

    def clone(self):
        ninst = PathNode(self.path, self.nodes)
        ninst.srcdic = copy.deepcopy(self.srcdic)
        return ninst

    def expand(self, new_nov=None): # after path.grow updated snode-dic
        for node in self.nodes:
            if new_nov:
                node[new_nov] = self.path.chvdict[new_nov]
            else:
                for nv in self.path.snode_dic: # sonde-nov
                    if nv not in node:
                        node[nv] = self.path.chvdict[nv]

    def _contains_single(self, single_node):
        for nd in self.nodes:
            if node1_C_node2(nd, single_node, self.steps): return True
        return False    


    def _fill(self, node):
        if self.path.classname != 'Path': return node
        nd = copy.deepcopy(node)
        for nv, cvs in self.path.chvdict:
            if nv not in node:
                nd[nv] = cvs
        return nd

    def add_node(self, node, srcdic=None):
        added = False
        if type(node) == list:
            for nd in node:
                added = added or self.add_node(nd, srcdic)
            return added
        elif is_single(node):
            expand_steps = None
            if self.path.classname=='Path': self.path.steps
            return node_to_lst(self._fill(node), self.nodes, expand_steps)
        else:
            doit = node_seq(node)
            while not doit.done:
                nd = doit.get_next()
                added = added or self.add_node(nd, srcdic)
        # if added; input srcdic
        while len(srcdic) > 0:
            key, msg = srcdic.popitem()
            if added:
                self.srcdic[key] = msg
            else:
                self.srcdic[key] = False

    def _subtract_single(self, ind, sngl):
        # self.nodes[ind] - sngl
        node = self.nodes[ind]
        res = _split_single(node, sngl)
        # False means: sngl doesn't intersect with self.nodes[ind]
        if res == False: return # not modified: self.nodes not changed
        if res == True:         # self.nodes[ind] is single, and == sngl
            del self.nodes[ind] # delete it from self.nodes
        else: # sngl is subset of self.nodes[ind]
            # res is list of dicts that are rest of node after subtract sngl
            for e in res: # adding these dicts in place of ind
                self.nodes.insert(ind, e)

    def intersect(self, other, only_intersects=False):
        lst = []
        for index, mynode in enumerate(self.nodes):
            for oind, other_node in enumerate(other.nodes):
                intscts = _node_intersect(mynode, other_node)
                if len(intscts) > 0:
                    # @self.nodes[index] ^ other.nodes[oind] -> [nd, nd, ..]
                    # each nd is a single intersect-dict node
                    lst.append((index, oind, intscts))
        if len(lst) > 0:
            if only_intersects:
                res = []
                for three in res:
                    for e in three[-1]:
                        res.append(e)
                return res
            # only_intersects == False
            return lst
        return None

    def subtract(self, other):
        inter_res = self.intersect(other)
        if not inter_res: return None
        while len(inter_res) > 0:
            ele = inter_res.pop()   # from behind, so that ind remains valid
            ind, _, intersects = ele
            for sngl in intersects:
                self._subtract_single(ind, sngl)
            

def test_node_intersect():
    nd1 = {60:{1,2,3}, 57:{5,6,7}, 54:{0,1}}
    nd2 = {60:{1,3}, 57:{5,6}, 54:{0}}
    lst = _node_intersect(nd1, nd2)
    x = 0

def test_seq():
    nd2 = {60:{1,3}, 57:{5,6}, 54:{0}}
    seq = Sequencer(nd2)
    while not seq.done:
        s = seq.get_next()
        print(s)
    x = 0
    seq.reset()
    while not seq.done:
        s = seq.get_next()
        print(s)
    x = 0


def test():
    # test_node_intersect()
    test_seq()

if __name__ == '__main__':
    test()