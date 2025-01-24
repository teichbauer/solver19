
import copy
from utils.sequencer import Sequencer
from utils.cvsnodetools import *

def _node_intersect(n1, n2): # both n1 and n2 can be compound or single
    # n1 and n2 must have the same novs
    # returning a list of single-nodes, that are intersections of n1/n2
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

class NodeManager:
    def __init__(self, path, nodes=None):
        self.path = path
        if nodes: 
            self.nodes = [copy.deepcopy(n) for n in nodes]
        else:
            self.nodes = [] #
        self.srcdic = {}

    def clone(self):
        ninst = NodeManager(self.path, self.nodes)
        ninst.srcdic = copy.deepcopy(self.srcdic)
        return ninst

    def expand(self, chvdict): # after path.grow updated snode-dic
        for node in self.nodes:
            for nv, chv in chvdict.items(): # sonde-nov
                if nv not in node:
                    node[nv] = chv

    def containing_single(self, single_node):
        for nd in self.nodes:
            if node1_C_node2(nd, single_node, self.path.steps): return True
        return False   


    def _fill(self, node):
        if self.path.classname != 'Path': return node
        nd = copy.deepcopy(node)
        for nv, cvs in self.path.chvdict.items():
            if nv not in node:
                nd[nv] = cvs
        return nd

    def add_node(self, node, srcdic=None):
        added = False
        if type(node) == list:
            for nd in node:
                added = self.add_node(nd, srcdic) or added
            return added
        elif is_single(node):
            expand_steps = None
            if self.path.blckmgr.blocked(node): return False
            if self.path.classname=='Path':
                expand_steps = self.path.steps
            return node_to_lst(self._fill(node), self.nodes, expand_steps)
        else:
            doit = Sequencer(node)
            while not doit.done:
                nd = doit.get_next()
                # the order is important: make sure func-call happens
                added = self.add_node(nd, srcdic) or added
        # if added; input srcdic
        while srcdic and len(srcdic) > 0:
            key, msg = srcdic.popitem()
            if added:
                # should srcdic be single k/v or a list?
                if key in self.srcdic:
                    print(f'srcdic{key}/{msg} was in already!')
                self.srcdic[key] = msg
            else:
                self.srcdic[key] = False
        return added

    def node_intersect(self, node, only_intersects=False):
        # intersect between self(NodeManager) and a node (single or not). return:
        # self(node,True): [<single-node>,..]
        # self(node): [(my-index, single-node), ...]
        lst = []
        for ind, nd in enumerate(self.nodes):
            tlst = _node_intersect(nd, node)
            for e in tlst:
                if e not in lst:
                    if only_intersects:
                        lst.append(e)
                    else:
                        lst.append((ind, e))
        return lst

    def intersect(self, other, only_intersects=False):
        # intersect between 2 NodeManagers. return:
        # self(node,True): [<single-node>,..]
        # self(node): [(my-index, other-index, single-node), ...]
        lst = []
        for oind, ond in enumerate(other.nodes):
            tlst = self.node_intersect(ond, only_intersects) 
            for e in tlst:
                if only_intersects:
                    lst.append(e)
                else:
                    lst.append((e[0], oind, e[1]))
        if len(lst) > 0:
            return lst
        return None
    
    def subtract_singles(self, singles): # singles: [<single-node>,...]
        # first serialize all into alist of singles
        lst = []
        for node in self.nodes:
            sq = Sequencer(node)
            lst += sq.serialize_2_singles()
        res = []
        for broken in lst:
            if broken in singles: continue
            res.append(broken)
        self.nodes = res

    def subtract(self, other):
        inter_res = self.intersect(other, only_intersects=True)
        if not inter_res: return None
        self.subtract_singles(inter_res)
        return True
            

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