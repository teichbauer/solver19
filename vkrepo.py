from center import Center
from utils.basics import pd
from utils.cvsnodetools import *
from utils.tools import *
from blockmgr import BlockMgr
from bblocker import BitBlocker
from exclmgr import ExclMgr
import copy

class VKRepository:
    def __init__(self, snode):
        self.bdic1 = {}     # {bit: bblocker, bit:bblocker, ..}
        self.bdic2 = {}     # {bit: [k2n, k2n,..], bit:[], ..}
        self.vk2dic = {}    # {k2n:vk2, k2n: vk2,...}
        cn = 'VKRepository'
        self.classname = cn
        self.blckmgr = [None, BlockMgr(self)][cn == 'VKRepository']
        self.exclmgr = [None, ExclMgr(self) ][cn == 'VKRepository']
        self.snode = snode  # related snode
        self.inflog = {}    # {key:[info,info,..], key:[], ...}

    def clone(self):
        xrepo = VKRepository(self.snode)
        xrepo.bdic1 = {b:{v: bb.clone(self) for v, bb in bbdic.items()} 
                       for b, bbdic in self.bdic1.items()}
        xrepo.bdic2 = {b: lst[:] for b, lst in self.bdic2.items()}
        xrepo.vk2dic = {kn:vk2 for kn, vk2 in self.vk2dic.items()}
        xrepo.blckmgr  = self.blckmgr.clone(xrepo)
        xrepo.exclmgr = self.exclmgr.clone(xrepo)
        xrepo.inflog = self.inflog.copy()
        return xrepo
    
    def insert_vk2(self, vk2):
        name = vk2.kname
        b1, b2 = vk2.bits
        if (b1 not in self.bdic2) or name not in self.bdic2[b1]:
            self.bdic2.setdefault(b1,[]).append(name)
        if (b2 not in self.bdic2) or name not in self.bdic2[b2]:
            self.bdic2.setdefault(b2,[]).append(name)
        self.vk2dic[name] = vk2

    def add_bblocker(self, bit, val, node, srcdic):
        bb_dic = self.bdic1.setdefault(bit, {})
        flip_val = flip(val)
        if flip_val in bb_dic:
            bb_dic[flip_val].filter_conflict(node)
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
                result =  bb.filter_vk2(vk2, bb_val != val, local)
                if result:
                    new_bbp, bb_updated = result
                    if new_bbp not in bb_pairs:
                        bb_pairs.append(new_bbp)
                    elif bb_pairs.index(new_bbp) < bbp_index and bb_updated:
                        # bb_pairs.index(new_bbp) cannot == bb_index, and
                        # if it is behind bb_index: no need to be added.
                        # only when new_bbp has been processed and now it is
                        # updated, then it needs to be added/proc-again.
                        bb_pairs.append(new_bbp)
            bbp_index += 1
        x = 9

    def add_vk2(self, vk2, new_bits):
        bits = set(self.bdic1).intersection(vk2.bits)
        if len(bits) > 0:
            vk2_node = expand_star({vk2.nov: vk2.cvs}, self.chvdict)
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

    def remove_vk2(self, vk2):
        for bit in vk2.bits:
            if vk2.kname in self.bdic2[bit]:
                self.bdic2[bit].remove(vk2.kname)
                if len(self.bdic2[bit]) == 0:
                    del self.bdic2[bit]
        del self.vk2dic[vk2.kname]