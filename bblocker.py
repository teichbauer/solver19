from utils.noder import *

class BitBlocker:
    # on a bit in repo.bdic1: {bit: {0: BitBlocker(), 1:BitBlocker()}}
    def __init__(self, bit, val, repo):
        self.bit = bit
        self.val = val
        # self.nodes = [] # list of nodes
        self.noder = Noder(repo)
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
        self.repo.pblocker.add_block(lst)
        return True # spouse-existed, and has been modified

    def proc_local_vk2(self, vk2, 
                       bb_bit, bb_val): # bb_bit/bb_val None/None or both not
        node = {vk2.nov: set()}
        for nd in self.noder.nodes:
            cmm = nd[vk2.nov].intersection(vk2.cvs) # vk2.cvs vs. bb.nodes
            if len(cmm) == 0: continue
            vk2.cvs -= cmm  # vk2.cvs be reduced
            node[vk2.nov].update(cmm)
        # vk2. not touching any node in bb
        if Noder.invalid_node(node): return None 
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
    
    def output(self, cmp_nodes=None): # cmp_nodes: [{},{},..]
        def calc_power(d):
            n = 1
            for cv in d.values():
                n = n* len(cv)
            return n
        
        msg = str(self.key) + ':\n'
        if not cmp_nodes:
            lst = self.noder.compact()
            return self.output(lst)
        elif type(cmp_nodes) == list:
            for d in cmp_nodes:
                cnt = calc_power(d)
                msg += str(d) + '\t#' + f'\t{cnt}\n'
            return msg

    @property
    def key(self):
        return (self.bit, self.val)

    @property
    def spouse(self):
        return self.repo.bdic1[self.bit].get(flip(self.val), None)