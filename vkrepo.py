from center import Center
from utils.basics import pd
from utils.tools import *
from blockmgr import BlockMgr
from bblocker import *
from exclmgr import ExclMgr
import copy

class VKRepoitory:
    def __init__(self, snode_dic):
        self.bdic1 = {}     # {bit: bblocker, bit:bblocker, ..}
        self.bdic2 = {}     # {bit: [k2n, k2n,..], bit:[], ..}
        self.vk2dic = {}    # {k2n:vk2, k2n: vk2,...}
        self.blckmgr = BlockMgr(self)
        self.exclmgr = ExclMgr(self)
        self.snode_dic = snode_dic  # related snode
        self.pathmgr = None
        self.inflog = {}    # {key:[info,info,..], key:[], ...}

    def clone(self, pathmgr):
        xrepo = VKRepoitory(self.snode_dic.copy())
        xrepo.pathmgr = pathmgr   # pathfinder
        xrepo.bdic1 = {b:{v: bb.clone(self) for v, bb in bbdic.items()} 
                       for b, bbdic in self.bdic1.items()}
        xrepo.bdic2 = {b: lst[:] for b, lst in self.bdic2.items()}
        xrepo.vk2dic = {kn:vk2 for kn, vk2 in self.vk2dic.items()}
        xrepo.blckmgr  = self.blckmgr.clone(xrepo)
        xrepo.exclmgr = self.exclmgr.clone(xrepo)
        xrepo.inflog = self.inflog.copy()
        return xrepo
    
    @property
    def steps(self):
        return sorted(self.snode_dic)
    
    @property
    def chvdict(self):
        return {nv: set(sn.bgrid.chvals) for nv, sn in self.snode_dic.items()}

    def add_snode_root(self, bgrid):
        bdic1_rbits = sorted(set(self.bdic1).intersection(bgrid.bits))
        for rb1 in bdic1_rbits:
            for bb in self.bdic1[rb1].values():
                cvs = bgrid.cvs_subset(bb.bit, bb.val)
                nd = fill_nvs({bgrid.nov: cvs})
                if bb.add(nd, [f"from {bgrid.nov}-root:{cvs}"]):
                    block_added = self.blckmgr.add_block(nd)
        # handle vk2s bouncing with bgrid.bits
        cmm_rbits = sorted(set(self.bdic2).intersection(bgrid.bits))
        for rb in cmm_rbits:
            for k2n in self.bdic2[rb]:
                vk2 = self.vk2dic[k2n]
                if set(vk2.bits).issubset(bgrid.bits):
                    hit_cvs = bgrid.vk2_hits(vk2)
                    print(f"{k2n} inside {bgrid.nov}-root, blocking {hit_cvs}")
                    block = fill_dict(self.chvdict,
                                {vk2.nov:vk2.cvs.copy(), bgrid.nov: hit_cvs})
                    block_added = self.blckmgr.add_block(block)
                else:# vk1.cvs is compound  caused by overlapping 
                    # with xsn.root-bits, will be named with R-prefix
                    x_cvs_subset = bgrid.cvs_subset(rb, vk2.dic[rb])
                    node = fill_dict(self.chvdict,
                            {vk2.nov: vk2.cvs.copy(), bgrid.nov: x_cvs_subset})
                    self.exclmgr.add(vk2.kname, copy.deepcopy(node))
                    # self.add_excl(vk2, copy.deepcopy(node))
                    new_vk1 = vk2.clone("NewVk", [rb], node) # R prefix, drop rb
                    self.add_bblocker(new_vk1.bit, new_vk1.val, node,
                                      {vk2.kname: f"R{vk2.nov}-{rb}"})
    # end of def add_snode_root(self, bgrid):
    
    def insert_vk2(self, vk2):
        name = vk2.kname
        b1, b2 = vk2.bits
        if (b1 not in self.bdic2) or name not in self.bdic2[b1]:
            self.bdic2.setdefault(b1,[]).append(name)
        if (b2 not in self.bdic2) or name not in self.bdic2[b2]:
            self.bdic2.setdefault(b2,[]).append(name)
        self.vk2dic[name] = vk2

    def add_bblocker(self, bit, val, node, srcdic):
        # BitBlocker(bit, self)
        bb_dic = self.bdic1.setdefault(bit, {})
        bb = bb_dic.setdefault(val, BitBlocker(bit, val, self))
        bb.add(node, srcdic)
        check_spouse(bb_dic)

    def filter_vk2s(self, bb_pairs, local=False):
        # in local-mode (inside snode, no merge across snodes)
        # check vk2s against bit-blockers: if vk2.cvs get cut, or
        # new bit-blocker generated from b-t-blocker<->vk2
        bbp_index = 0
        # bb_pairs can grow here: not for-loop
        while bbp_index < len(bb_pairs): 
            bb_bit, bb_val = bb_pairs[bbp_index]
            bb = self.bdic1[bb_bit][bb_val]
            # bb_dic = self.bdic1[b]
            k2ns = self.bdic2[bb_bit]
            for kn in k2ns:
                vk2 = self.vk2dic[kn]
                val = vk2.dic[bb_bit]
                if vk2.kname in bb.srcdic: continue
                new_bbp = bb.filter_vk2(vk2, bb_val != val, local)
                if new_bbp and (new_bbp not in bb_pairs):
                    bb_pairs.append(new_bbp)
            bbp_index += 1
        x = 9
                # for v in bb_dic:
                #     if vk2.kname in bb_dic[v].srcdic: continue
                #     # v != val-> gen new vk1, v == val -> only reduce vk2.cvs
                #     # in case of new-vk1, collect vk1.bit into new_bb_bits
                #     new_bit = bb_dic[v].filter_vk2(vk2, v != val, local)
                #     if new_bit and (new_bit in self.bdic2) and \
                #        (new_bit not in bit12):
                #         bit12.append(new_bit)

    def add_vk2(self, vk2, new_bits):
        bits = set(self.bdic1).intersection(vk2.bits)
        if len(bits) > 0:
            for bit in bits:
                bb_dic = self.bdic1[bit]
                vk2_node = fill_nvs({vk2.nov: vk2.cvs}, self.steps)
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

    def proc_vk2pair(self, vk2, new_bits=None):
        # check if vk2 share its 2 bits with an existing vk2, if yes
        # and if both vals on the same bit are the same, and the vals on
        # the bit are diff, then a new vk1 is generated. 
        # This is based on the fact: (a + b)( a + not_b) == a
        b1, b2 = vk2.bits
        kns1 = self.bdic2[b1]
        kns2 = self.bdic2[b2]
        xkns = set(kns1).intersection(kns2)
        xkns.remove(vk2.kname)
        while len(xkns) > 0:
            _vk2 = self.vk2dic[xkns.pop()]
            vk1 = handle_vk2pair(vk2, _vk2)
            if vk1: 
                if new_bits: new_bits.add(vk1.bit)
                self.add_bblocker(
                    vk1.bit, vk1.val,vk1.cvs,
                    {vk2.kname:f'D{vk2.nov}',_vk2.kname:f'D{_vk2.nov}'})
        x = 0
