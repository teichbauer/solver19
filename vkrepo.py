from center import Center
from utils.basics import pd
from utils.tools import *
from pathblocker import PathBlocker
from bblocker import BitBlocker
from exclmgr import ExclMgr

class VKRepository:
    def __init__(self, layer):
        self.bbpool = {} # {{<bit>,<bval): <bit-blocker>}}
        self.layer   = layer  # related layer
        self.inflog  = {}   # {key:[info,info,..], key:[], ...}
        self.bdic1   = {}   # {bit: bblocker, bit:bblocker, ..}
        self.bdic2   = {}   # {bit: [k2n, k2n,..], bit:[], ..}
        self.vk2dic  = {}   # {k2n:vk2, k2n: vk2,...}
        self.pblocker = PathBlocker(self)
        self.exclmgr = ExclMgr(self)
    
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
        if val not in bb_dic:
            bb_dic[val] = BitBlocker(bit, val, self)
        if bb_dic[val].add_bb_node(node, srcdic):
            bb_dic[val].check_spouse()

    def filter_vk2s(self, local):
        bbkeys = sorted(self.bbpool)
        bbkindex = 0
        while bbkindex < len(bbkeys):
            bb = self.bbpool[bbkeys[bbkindex]]
            k2ns = self.bdic2.get(bb.bit, [])
            for kn in k2ns:
                if kn in bb.noder.srcdic: 
                    continue
                vk2 = self.vk2dic[kn]
                bb_bit = bb_val = None  # possible bit-blocker (bit, val) pair
                if vk2.dic[bb.bit] != bb.val: 
                    bb_bit, bb_val = vk2.other_bv(bb.bit)
                if local:
                    proc_vk2 = bb.proc_local_vk2 
                else:
                    proc_vk2 = bb.proc_path_vk2
                result =  proc_vk2(vk2, bb_bit, bb_val)
                if result:
                    new_bbp, bb_updated = result
                    if new_bbp not in bbkeys:
                        bbkeys.append(new_bbp)
                    elif bbkeys.index(new_bbp) < bbkindex and bb_updated:
                        # bbkeys.index(new_bbp) cannot == bbkeys, and
                        # if it is behind bb_index: no need to add to bbkeys.
                        # only when new_bbp has been processed(new_bbp)
                        # and now it is now updated, then it needs at the end, 
                        # to be added/proc-again.
                        bbkeys.append(new_bbp)
            bbkindex += 1

    def proc_vk2pair(self, vk2): # if vk2 has a(or >1) twin in bdic2
        # check condition: if vk2 share its 2 bits with another vk2, if yes
        # and if both vals on hte bit-1 are the same, and the vals on
        # the bit-2 are diff, then a new vk1 is generated. 
        # This is based on the fact: (a + b)( a + not_b) == a
        b1, b2 = vk2.bits
        kns1 = self.bdic2[b1] # list of knames on bit-1
        kns2 = self.bdic2[b2] # list of knames on bit-2
        xkns = set(kns1).intersection(kns2) # kname(s) appearing in both lists
        xkns.remove(vk2.kname) # vk2.kname is for sure in there: pop it out
        while len(xkns) > 0:   # kname(s) remaining?
            _vk2 = self.vk2dic[xkns.pop()]  # _vk2 that shares 2 bits with vk2
            vk1 = handle_vk2pair(vk2, _vk2) # check condition described above
            if vk1: # a new vk1 resulted?
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