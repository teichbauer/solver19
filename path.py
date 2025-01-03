from utils.cvsnodetools import *
from utils.tools import outputlog
from vkrepo import VKRepository

class Path(VKRepository):
    def __init__(self, snode):
        VKRepository.__init__(self, snode, 'Path')
        self.snode_dic  = {snode.nov: snode} # starting-snode as the first

    def add_sn_root(self, sn_bgrid):
        bdic1_rbits = sorted(set(self.bdic1).intersection(sn_bgrid.bits))
        for rb1 in bdic1_rbits:
            bb_dic = self.bdic1[rb1]
            for bv, bb in bb_dic:
                hit_cvs, mis_cvs = sn_bgrid.cvs_subset(bb.bit, bv)
                for node in bb.nodes:
                    bl = copy.deepcopy(node)    # making a new block
                    bl.update({sn_bgrid.nov: hit_cvs}) # and add it to blckmgr
                    self.blckmgr.add_block(bl)
                del bb_dic[bv]      # IL2024-11-27 on the reason
            if len(bb_dic) == 0:    # why it is to be removed. 
                del self.bdic1[rb1]
        # handle vk2s bouncing with bgrid.bits
        cmm_rbits = sorted(set(self.bdic2).intersection(sn_bgrid.bits))
        for rb in cmm_rbits:
            kns = self.bdic2[rb]
            while len(kns) > 0:
                vk2 = self.vk2dic[kns.pop(0)]
                if set(vk2.bits).issubset(sn_bgrid.bits):
                    hit_cvs = sn_bgrid.vk2_hits(vk2)
                    m =f"{vk2.kname} in {sn_bgrid.nov}-root, blocking {hit_cvs}"
                    print(m)
                    block = self.expand_node({vk2.nov:vk2.cvs.copy(), 
                                              sn_bgrid.nov: hit_cvs})
                    block_added = self.blckmgr.add_block(block)
                else:# vk1.cvs is compound  caused by overlapping 
                    hit_cvs, mis_cvs = sn_bgrid.cvs_subset(rb, vk2.dic[rb])
                    node = self.expand_node(
                        {vk2.nov: vk2.cvs.copy(), sn_bgrid.nov: hit_cvs})
                    new_vk1 = vk2.clone("NewVk", [rb], node) # R prefix, drop rb
                    self.add_bblocker( new_vk1.bit, new_vk1.val, node,
                        {vk2.kname: f"R{vk2.nov}-{sn_bgrid.nov}/{rb}"} )
                # for {<mis_cvs>}, vk2 should be out: so in path vk2 is out
                self.remove_vk2(vk2)  # IL2024-11-23a + IL2024-11-28
    # end of add_sn_root

    def grow(self, sn):
        self.snode_dic[sn.nov] = sn
        for bb in self.bbpool.values():
            bb.expand(sn.nov)
        self.add_sn_root(sn.bgrid)
        for bit, bbdic in sn.repo.bdic1.items():
            dic = self.bdic1.setdefault(bit, {}) # sn.repo-bbdic add to here
            for v, bb in bbdic.items():
                if v in dic:
                    dic[v].merge(bb)
                else:
                    dic[v] = bb.clone(self)
            check_spouse(dic)
        new_bits = set()
        for vk2 in sn.repo.vk2dic.values():
            self.add_vk2(vk2, new_bits)
        bb_pairs = [] # [(<bb-bit>,<bb-val>),..]
        for b in sorted(new_bits):
            for v in self.bdic1[b]:
                bb_pairs.append((b,v))
        self.filter_vk2s(bb_pairs)

    def write_log(self, outfile_name):
        ofile = open(outfile_name, 'w')
        msg = outputlog(self)
        ofile.write(msg)
        ofile.close()

    def expand_node(self, node):
        if type(node) == list:
            for nd in node:
                self.expand_node(nd)
        elif type(node) == dict:
            for nv in self.chvdict:
                if (nv not in node) or (node[nv] == {'*'}):
                    node[nv] = self.chvdict[nv]
        return node

    def add_vk2(self, vk2, new_bits):
        bits = set(self.bdic1).intersection(vk2.bits)
        if len(bits) > 0:
            vk2_node = self.expand_node({vk2.nov: vk2.cvs})
            for bit in bits:
                bb_dic = self.bdic1[bit]
                for v in bb_dic:
                    cmm = bb_dic[v].intersect(vk2_node)
                    if len(cmm) == 0: continue
                    self.exclmgr.add(vk2.kname, cmm)
                    if v != vk2.dic[bit]:
                        vk1 = vk2.clone("NewVk", [bit], cmm)
                        self.add_bblocker(vk1.bit, vk1.val, cmm,
                                        {vk2.kname: f'U{vk2.nov}'})
                        new_bits.add(vk1.bit)
        self.insert_vk2(vk2)
        # handle case of 2 overlapping bits with existing vk2
        self.proc_vk2pair(vk2, new_bits) # if vk2 has a twin in vk2dic
        return new_bits
    
    @property
    def steps(self):
        return sorted(self.snode_dic, reverse=True) # [60, 57, 54, ...]

    @property
    def chvdict(self):
        return {nv: set(sn.bgrid.chvals) for nv, sn in self.snode_dic.items()}
