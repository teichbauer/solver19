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
                    block = expand_star({vk2.nov:vk2.cvs.copy(), 
                                       sn_bgrid.nov: hit_cvs}, self.chvdict)
                    block_added = self.blckmgr.add_block(block)
                else:# vk1.cvs is compound  caused by overlapping 
                    hit_cvs, mis_cvs = sn_bgrid.cvs_subset(rb, vk2.dic[rb])
                    node = expand_star({vk2.nov: vk2.cvs.copy(), 
                                      sn_bgrid.nov: hit_cvs}, self.chvdict)
                    new_vk1 = vk2.clone("NewVk", [rb], node) # R prefix, drop rb
                    self.add_bblocker( new_vk1.bit, new_vk1.val, node,
                        {vk2.kname: f"R{vk2.nov}-{sn_bgrid.nov}/{rb}"} )
                # for {<mis_cvs>}, vk2 should be out: so in path vk2 is out
                self.remove_vk2(vk2)  # IL2024-11-23a + IL2024-11-28
    # end of add_sn_root

    def grow(self, sn):
        self.snode_dic[sn.nov] = sn
        # self.repo.blckmgr.expand()
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

    @property
    def steps(self):
        return sorted(self.snode_dic, reverse=True) # [60, 57, 54, ...]

    @property
    def chvdict(self):
        return {nv: set(sn.bgrid.chvals) for nv, sn in self.snode_dic.items()}
