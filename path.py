from utils.cvsnodetools import *
from utils.tools import outputlog
from vkrepo import VKRepository

class Path(VKRepository):
    def __init__(self, lyr):
        VKRepository.__init__(self, lyr, 'Path')
        self.lyr_dic  = {lyr.nov: lyr} # starting-snode as the first

    def add_lr_root(self, bgrid):
        bdic1_rbits = sorted(set(self.bdic1).intersection(bgrid.bits))
        for rb1 in bdic1_rbits:
            bb_dic = self.bdic1[rb1]
            for bv, bb in bb_dic:
                hit_cvs, mis_cvs = bgrid.cvs_subset(bb.bit, bv)
                for node in bb.nodes:
                    bl = copy.deepcopy(node)    # making a new block
                    bl.update({bgrid.nov: hit_cvs}) # and add it to blckmgr
                    self.blckmgr.add_block(bl)
                del bb_dic[bv]      # IL2024-11-27 on the reason
            if len(bb_dic) == 0:    # why it is to be removed. 
                del self.bdic1[rb1]
        # handle vk2s from path.bdic2 in touch with sn.bgrid.bits
        cmm_rbits = sorted(set(self.bdic2).intersection(bgrid.bits))
        for rb in cmm_rbits:
            kns = self.bdic2[rb]
            while len(kns) > 0:
                vk2 = self.vk2dic[kns.pop(0)]
                if set(vk2.bits).issubset(bgrid.bits):
                    hit_cvs = bgrid.vk2_hits(vk2)
                    m =f"{vk2.kname} in {bgrid.nov}-root, blocking {hit_cvs}"
                    print(m)
                    block = self.expand_node({vk2.nov:vk2.cvs.copy(), 
                                              bgrid.nov: hit_cvs})
                    block_added = self.blckmgr.add_block(block)
                else:# vk1.cvs is compound  caused by overlapping 
                    hit_cvs, mis_cvs = bgrid.cvs_subset(rb, vk2.dic[rb])
                    node = self.expand_node(
                        {vk2.nov: vk2.cvs.copy(), bgrid.nov: hit_cvs})
                    new_vk1 = vk2.clone("NewVk", [rb], node) # R prefix, drop rb
                    self.add_bblocker( new_vk1.bit, new_vk1.val, node,
                        {vk2.kname: f"R{vk2.nov}-{bgrid.nov}/{rb}"} )
                # for {<mis_cvs>}, vk2 -> bit-blocker, 
                # for mis_cvs vk2 cannot hit. So vk2 will be out
                self.remove_vk2(vk2)  # IL2024-11-23a + IL2024-11-28
    # end of add_sn_root

    def grow(self, lyr): # grow on next layer-node
        self.lyr_dic[lyr.nov] = lyr
        for bb in self.bbpool.values():
            bb.noder.expand(self.chvdict)
        self.add_lr_root(lyr.bgrid)
        for bit, bbdic in lyr.repo.bdic1.items():
            dic = self.bdic1.setdefault(bit, {}) # sn.repo-bbdic add to here
            for v, bb in bbdic.items():
                bb.noder.expand(self.chvdict)
                if v in dic:
                    dic[v].merge(bb)
                else:
                    dic[v] = bb.clone(self)  # cloning also put into bbpool
            dic[v].check_spouse()
        new_bits = set()
        for vk2 in lyr.repo.vk2dic.values():
            self.add_vk2(vk2, new_bits)
        self.filter_vk2s()

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
