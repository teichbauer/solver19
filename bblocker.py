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

    def filter_vk2(self, vk2, new_vk1): # vk2 can generate vk1 or not: (T/F)
        if new_vk1:
            vk1 = vk2.clone('NewVk', [self.bit], {vk2.nov: set()})
        else: vk1 = None
        for nd in self.nodes:
            nv, cvs = tuple(nd.items())[0] # nd can only have 1 nv/cvs entry
            if nv == vk2.nov:
                cmm = cvs.intersection(vk2.cvs)
                if len(cmm) == 0: continue
                vk2.cvs -= cmm
                if vk1: vk1.add_cvs(cmm, vk2.nov)
        if vk1 and len(vk1.cvs[vk2.nov]) > 0:
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

