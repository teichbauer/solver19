from utils.cvsnodetools import *
from pathnode import PathNode

class BitBlocker:
    # on a bit in repo.bdic1: {bit: {0: BitBlocker(), 1:BitBlocker()}}
    def __init__(self, bit, val, repo):
        self.bit = bit
        self.val = val
        # self.nodes = [] # list of nodes
        self.noder = PathNode(repo)
        self.repo = repo    # can be VKRepository or Path
        self.repo.bbpool[(bit, val)] = self
        self.srcdic = {}

    def clone(self, repo):
        ninst = BitBlocker(self.bit, self.val, repo)
        # ninst.nodes = [copy.deepcopy(n) for n in self.nodes]
        ninst.noder = self.noder.clone()
        ninst.srcdic = self.srcdic.copy()
        bbpool_key = (ninst.bit, ninst.val)
        if bbpool_key not in repo.bbpool:
            repo.bbpool[bbpool_key] = ninst
        return ninst

    @property
    def steps(self):
        if self.repo.classname == 'Path':
            return self.repo.steps
        return None

    @property
    def chvdict(self):
        if self.repo.classname == 'Path':
            return self.repo.chvdict
        return None

    def merge(self, other_bb):
        nds = []
        other_bb.expand()
        for node in other_bb.noder.nodes:
            node_iter = Sequencer(node)
            while not node_iter.done:
                bb_node = node_iter.get_next() # bb_node: a single-cvs-dict
                if self.contains_single(bb_node): 
                    continue
                nds.append(bb_node)
        for nd in nds:
            self.noder.nodes.append(nd)

    def spousal_conflict(self, spouse):
        spouse.expand_nodes()
        sindex = 0
        while sindex < len(spouse.nodes):
            deleted = self.filter_conflict(spouse.nodes[sindex])
            if deleted: 
                del spouse.nodes[sindex]
            else:
                sindex += 1
        x = 0

    def subtr_node(self, delta_node, srcnodes=None):
        if srcnodes == None:
            srcnodes = self.nodes
        expand_star(delta_node, self.chvdict)
        expand_star(srcnodes, self.chvdict)
        if type(srcnodes) == list:
            res_nodes = []
            for node in srcnodes:
                node = subtract_delta_node(node, delta_node)
                if type(node) == dict and len(node) > 0: 
                    res_nodes.append(node)
                elif type(node) == list:
                    for nd in node:
                        res_nodes.append(nd)
            return res_nodes
        return subtract_delta_node(srcnodes, delta_node)
    
    def add_node(self, node, srcdic):
        init_node_sig = signature(self.noder.nodes)
        self.noder.add_node(node, srcdic)
        new_node_sig = signature(self.noder.nodes)
        return init_node_sig != new_node_sig

    def filter_conflict(self, node):
        node_delta = []
        for nd in self.nodes:
            cmm = node_intersect(nd, node, self.steps)
            if cmm != None and len(cmm) > 0:
                self.repo.blckmgr.add_block(cmm)
                node_delta.append(cmm)
        for delta in node_delta:
            node = self.subtr_node(delta, node)
            self.nodes = self.subtr_node(delta)
        return len(node) == 0
            
    def filter_vk2(self, vk2, # the vk2 touching self.bit
                   new_vk1,   # vk2 can generate vk1 or not: (T/F)
                   is_local): # witin a snode(T) or across snodes(F)
        node = {vk2.nov: set()}
        if new_vk1:
            vk1 = vk2.clone('NewVk', [self.bit], node)
        for nd in self.noder.nodes:
            assert(vk2.nov in nd), f"node has no nov: {vk2.nov}"
            if is_local: # number of entries in nd is 1
                # this happens when snode-local S-bb causing a T-bb
                cmm = nd[vk2.nov].intersection(vk2.cvs)
                if len(cmm) == 0: continue
                vk2.cvs -= cmm  # vk2.cvs be reduced
                node[vk2.nov].update(cmm)
            else: 
                # nd has >1 entry(multiple nvs): This happens across snodes
                cmm = nd[vk2.nov].intersection(vk2.cvs)
                if len(cmm) == 0: continue
                for nv in nd:
                    if nv == vk2.nov: node[nv].update(cmm)
                    else:             node.setdefault(nv,set()).update(nd[nv])
        # any nv in node empty-> invalid
        if not node_valid(node): return None
        if not is_local: self.repo.exclmgr.add(vk2.kname, copy.deepcopy(node))
        if new_vk1:
            bb_dic = self.repo.bdic1.setdefault(vk1.bit, {})
            bb = bb_dic.setdefault(vk1.val, 
                                   BitBlocker(vk1.bit, vk1.val, self.repo))
            bb_updated = bb.add_node(vk1.cvs, {vk2.kname: f'U{vk2.nov}'})
            check_spouse(bb_dic)
            return (vk1.bit, vk1.val), bb_updated
        return None
    
    def contains_single(self, node):
        for nd in self.nodes:
            if node1_C_node2(nd, node, self.steps): return True
        return False

    def intersect(self, node, res=None):
        self.expand_nodes()
        if res==None: res = []
        if type(node) == BitBlocker:
            for nd in node.nodes:
                self.intersect(nd, res)
        for nd in self.nodes:
            cmm = node_intersect(nd, node)
            if cmm: res.append(cmm)
        return res

    def expand(self, new_nov=None):
        if self.repo.classname == 'Path':
            self.noder.expand(new_nov)
        return self



    # def iter_node(self):
    #     return (for y in self.expand_nodes().nodes)