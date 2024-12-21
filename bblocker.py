from utils.cvsnodetools import *

class BBUT: # bit-blocker-update-tester
    def __init__(self, initial_bb):
        self.bb_bit = initial_bb.bit
        self.bb_val = initial_bb.val
        self.init_node_count = len(initial_bb.nodes)
        self.init_node_sig = signature(initial_bb.nodes)

    def test_update(self, bb):
        assert(bb.bit == self.bb_bit), "BBUT usage wrong"
        assert(bb.val == self.bb_val), "BBUT usage wrong"
        if self.init_node_count == 0: return False
        new_sig = signature(bb.nodes)
        return new_sig != self.init_node_sig

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

    def merge(self, bb):
        nds = []
        bb.expand_nodes()
        for node in bb.nodes:
            node_it = Sequencer(node)
            while not node_it.done:
                bb_node = node_it.get_next()
                if self.contains(bb_node): 
                    continue
                nds.append(bb_node)
        for nd in nds:
            self.nodes.append(nd)

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

    def add(self, node, srcdic):
        if type(node) == list:
            for nd in node:
                self.add(nd, srcdic)
        elif is_single(node):
            added = node_to_lst(node, self.nodes, self.steps)
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
                    if nv == vk2.nov: node[nv].update(cmm)
                    else:             node.setdefault(nv,set()).update(nd[nv])
        # any nv in node empty-> invalid
        if not node_valid(node): return None
        if not is_local: self.repo.exclmgr.add(vk2.kname, copy.deepcopy(node))
        if new_vk1:
            bb_dic = self.repo.bdic1.setdefault(vk1.bit, {})
            bb = bb_dic.setdefault(vk1.val, 
                                   BitBlocker(vk1.bit, vk1.val, self.repo))
            bbut = BBUT(bb)
            bb.add(vk1.cvs, {vk2.kname: f'U{vk2.nov}'})
            bb_updated = bbut.test_update(bb)
            check_spouse(bb_dic)
            return (vk1.bit, vk1.val), bb_updated
        return None
    
    def contains(self, node):
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

    def expand_nodes(self):
        if self.repo.classname == 'Path':
            expand_star(self.nodes, self.chvdict)
        return self



    # def iter_node(self):
    #     return (for y in self.expand_nodes().nodes)