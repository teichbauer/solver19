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
        if not lst: return False
        self.noder.subtract_singles(lst)
        spouse.noder.subtract_singles(lst)
        self.repo.blckmgr.add_block(lst)

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
                
    def filter_vk2(self, vk2,   # the vk2 touching self.bit
                   new_vk1,     # vk2 can generate vk1 or not: (T/F)
                   is_local):   # witin a snode(T) or across snodes(F)
        node = {vk2.nov: set()} # vk2.cvs's intersection with this bb
        if new_vk1:
            vk1 = vk2.clone('NewVk', [self.bit], node)
        for nd in self.noder.nodes:
            assert(vk2.nov in nd), f"node has no nov: {vk2.nov}"
            if is_local: # vk2 & bb has the same nov(repo is VKRepository)
                # if vk2.cvs intersects with bb
                cmm = nd[vk2.nov].intersection(vk2.cvs) # vk2.cvs vs. bb.nodes
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
        if not node_valid(node): return None # vk2. not touching any node in bb
        if not is_local: self.repo.exclmgr.add(vk2.kname, copy.deepcopy(node))
        if new_vk1:
            bb_dic = self.repo.bdic1.setdefault(vk1.bit, {})
            if vk1.val not in bb_dic:
                bb_dic[vk1.val] = BitBlocker(vk1.bit, vk1.val, self.repo)
            # in case bb was there already, and add_node has not modified
            # it, then bb_updated will be False: if this bb has been processed
            # then it should not be added back for processing.
            # see repo.filter_vk2s
            bb_updated = bb_dic[vk1.val].noder.add_node(
                vk1.cvs, {vk2.kname: f'U{vk2.nov}'})
            check_spouse(bb_dic)
            return (vk1.bit, vk1.val), bb_updated
        return None
    
    def intersect(self, node, res=None):
        self.noder.expand(self.repo.chvdict)
        if res==None: res = []
        if type(node) == BitBlocker:
            return self.noder.intersect(node, True)
        return self.noder.node_intersect(node, True)
