from utils.cvsnodetools import *

class BitBlocker:
    # on a bit in repo.bdic1: {bit: {0: BitBlocker(), 1:BitBlocker()}}
    def __init__(self, bit, val, repo):
        self.bit = bit
        self.val = val
        self.nodes = [] # list of nodes
        self.repo = repo
        self.srcdic = {}

    def clone(self, repo):
        ninst = BitBlocker(self.bit, self.val, repo)
        ninst.nodes = [copy.deepcopy(n) for n in self.nodes]
        ninst.srcdic = self.srcdic.copy()
        return ninst

    def merge(self, bb, nvs):
        nds = []
        bb = fill_nvs(bb, nvs)
        for nd in self.nodes:
            if bb.contains(nd): continue
            nds.append(nd)
        self.nodes = nds

    def spousal_conflict(self, spouse):
        blocks = []
        for other_node in spouse.nodes:
            for node in self.nodes:
                res = node_intersect(node, other_node, self.repo.steps)
                if res != None:
                    blocks.append(res)
        for bl in blocks:
            self.subtr_node(bl)
            spouse.subtr_node(bl)
            self.repo.blckmgr.add_block(bl)

    def subtr_node(self, delta_node):
        res_nodes = []
        for node in self.nodes:
            node = subtract_delta_node(node, delta_node, self.repo.chvdict)
            if type(node) == dict: 
                res_nodes.append(node)
            elif type(node) == list:
                for nd in node:
                    res_nodes.append(nd)
        self.nodes = res_nodes
        x = 0

    def add(self, node, srcdic):
        if type(node) == list:
            for nd in node:
                self.add(nd, srcdic)
        elif is_single(node):
            added = node_to_lst(node, self.nodes, self.repo.steps)
        else:
            doit = node_seq(node)
            while not doit.done:
                nd = doit.get_next()
                self.add(nd, srcdic)
        while len(srcdic) > 0: 
            kname, msg = srcdic.popitem()
            if added:
                self.srcdic[kname] = msg
            else:
                self.srcdic[kname] = False
        return self

    def filter_nodes(self, nodes, nd):
        pnds = []
        for nx in nodes:
            cmm = node_intersect(nx, nd, self.repo.steps)
            if cmm:
                pnds.append(cmm)
        return pnds


    def filter_vk2(self, vk2, # the vk2 touching self.bit
                   new_vk1,   # vk2 can generate vk1 or not: (T/F)
                   is_local): # witin a snode(T) or across snodes(F)
        node = {vk2.nov: set()}
        if new_vk1:
            vk1 = vk2.clone('NewVk', [self.bit], node)
        for nd in self.nodes:
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
                    if nv == vk2.nov:   node[nv].update(cmm)
                    else:               node[nv] = nd[nv]
        if not node_valid(node): return None # any nv in node empty-> invalid
        if not is_local: self.repo.exclmgr.add(copy.deepcopy(node))
        if new_vk1:
            bb_dic = self.repo.bdic1.setdefault(vk1.bit, {})
            bb = bb_dic.setdefault(vk1.val, 
                                   BitBlocker(vk1.bit, vk1.val, self.repo))
            bb.add(vk1.cvs, {vk2.kname: f'U{vk2.nov}'})
            check_spouse(bb_dic)
            return vk1
        return None
    
    def contains(self, node):
        for nd in self.nodes:
            if node1_C_node2(nd, node, self.repo.steps): return True
        return False

    def intersect(self, node):
        res = []
        for nd in self.nodes:
            cmm = node_intersect(nd, node, self.repo.steps)
            if cmm: res.append(cmm)
        return res

