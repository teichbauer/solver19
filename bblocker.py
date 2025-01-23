from utils.cvsnodetools import *
from nodemanager import NodeManager

class BitBlocker:
    # on a bit in repo.bdic1: {bit: {0: BitBlocker(), 1:BitBlocker()}}
    def __init__(self, bit, val, repo):
        self.bit = bit
        self.val = val
        # self.nodes = [] # list of nodes
        self.noder = NodeManager(repo)
        self.repo = repo    # can be VKRepository or Path
        self.repo.bbpool[(bit, val)] = self

    def clone(self, repo):
        ninst = BitBlocker(self.bit, self.val, repo)
        # ninst.nodes = [copy.deepcopy(n) for n in self.nodes]
        ninst.noder = self.noder.clone()
        bbpool_key = (ninst.bit, ninst.val)
        if bbpool_key not in repo.bbpool:
            repo.bbpool[bbpool_key] = ninst
        return ninst

    def merge(self, other_bb):
        nds = []
        for node in other_bb.noder.nodes:
            node_iter = Sequencer(node)
            while not node_iter.done:
                bb_node = node_iter.get_next() # bb_node: a single-cvs-dict
                if self.noder.containing_single(bb_node): 
                    continue
                nds.append(bb_node)
        self.noder.add_node(nds)

    def spousal_conflict(self, spouse):
        lst = self.noder.intersect(spouse.noder, only_intersects=True)
        if not lst: return False # no spouse-modified
        self.noder.subtract_singles(lst)
        spouse.noder.subtract_singles(lst)
        self.repo.blckmgr.add_block(lst)
        return True # spouse-existed, and has been modified

    def subtr_node(self, delta_node, srcnodes=None):
        if srcnodes == None:
            srcnodes = self.nodes
        expand_star(delta_node, self.repo.chvdict)
        expand_star(srcnodes, self.repo.chvdict)
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

    def proc_local_vk2(self, vk2, 
                       bb_bit, bb_val): # bb_bit/bb_val None/None or both not
        node = {vk2.nov: set()}
        for nd in self.noder.nodes:
            cmm = nd[vk2.nov].intersection(vk2.cvs) # vk2.cvs vs. bb.nodes
            if len(cmm) == 0: continue
            vk2.cvs -= cmm  # vk2.cvs be reduced
            node[vk2.nov].update(cmm)
        if not node_valid(node): return None # vk2. not touching any node in bb
        if bb_bit: # both bb_bit/bb_val not None
            bb_dic = self.repo.bdic1.setdefault(bb_bit, {})
            if bb_val not in bb_dic:
                bb_dic[bb_val] = BitBlocker(bb_bit, bb_val, self.repo)
            bb_updated = bb_dic[bb_val].noder.add_node(
                node, {vk2.kname: f'U{vk2.nov}'})
            spouse_modified = bb_dic[bb_val].check_spouse()
            return (bb_bit, bb_val), bb_updated
        return None

    def proc_path_vk2(self, vk2,  
                      bb_bit, bb_val): # bb_bit/bb_val None/None or both not
        nodes = []
        for nd in self.noder.nodes:
            assert(vk2.nov in nd), f"node has no nov: {vk2.nov}"
            cmm = nd[vk2.nov].intersection(vk2.cvs)
            if len(cmm) == 0: continue
            node = {}
            for nv in nd:
                if nv == vk2.nov: node.setdefault(nv,set()).update(cmm)
                else:             node.setdefault(nv,set()).update(nd[nv])
            nodes.append(node)
        if len(nodes) == 0: return None # vk2. not touching any node in bb
        self.repo.exclmgr.add(vk2.kname, copy.deepcopy(nodes))
        if bb_bit: # both bb_bit/bb_val not None
            bb_dic = self.repo.bdic1.setdefault(bb_bit, {})
            if bb_val not in bb_dic:
                bb_dic[bb_val] = BitBlocker(bb_bit, bb_val, self.repo)
            bb_updated = bb_dic[bb_val].noder.add_node(
                nodes, {vk2.kname: f'U{vk2.nov}'})
            spouse_modified = bb_dic[bb_val].check_spouse()
            return (bb_bit, bb_val), bb_updated
        return None
    
    def intersect(self, node, res=None):
        self.noder.expand(self.repo.chvdict)
        if res==None: res = []
        if type(node) == BitBlocker:
            return self.noder.intersect(node, True)
        return self.noder.node_intersect(node, True)

    def check_spouse(self, spouse=None):
        spouse = self.spouse
        if spouse: 
            return self.spousal_conflict(spouse)
        return None
    
    @property
    def key(self):
        return (self.bit, self.val)

    @property
    def spouse(self):
        return self.repo.bdic1[self.bit].get(flip(self.val), None)