from center import Center
from utils.basics import pd
from utils.tools import *
from utils.namedrive import NameDrive
from blockmgr import BlockMgr
from bblocker import BitBlocker
import copy

class VKRepoitory:
    def __init__(self, snode):
        self.bdic1 = {}     # {bit: bblocker, bit:bblocker, ..}
        self.bdic2 = {}     # {bit: [k2n, k2n,..], bit:[], ..}
        self.k1ns = []      # [k1n, k1n,..]
        self.vk2dic = {}    # {k2n:vk2, k2n: vk2,...}
        self.blckmgr = BlockMgr(self)
        self.excls = {}     # {kn:[node, node,..],..} vk not 2b used in nodes
        self.snode = snode  # related snode
        self.driver = None
        self.inflog = {}    # {key:[info,info,..], key:[], ...}

    def clone(self, driver):
        xrepo = VKRepoitory(self.snode)
        xrepo.driver = driver   # pathfinder
        xrepo.bdic1 = {b: lst[:] for b, lst in self.bdic1.items()}
        xrepo.bdic2 = {b: lst[:] for b, lst in self.bdic2.items()}
        xrepo.k1ns = self.k1ns[:]
        xrepo.vk2dic = {kn:vk2 for kn, vk2 in self.vk2dic.items()}
        xrepo.blckmgr  = self.blckmgr.clone(xrepo)
        xrepo.bbmgr = self.bbmgr.clone(xrepo)
        for kn, lst in self.excls.items():
            xrepo.excls[kn] = [copy.deepcopy(node) for node in lst]
        return xrepo
    
    def filter_vk2s(self, bb_bits):
        # in local-mode (inside snode, no merge across snodes)
        # check vk2s against bit-blockers: if vk2.cvs get cut, or
        # new bit-blocker generated from b-t-blocker<->vk2
        bit12 = bb_bits.intersection(self.bdic2)
        new_bb_bits = set()
        for b in bit12:
            k2ns = self.bdic2[b]
            for kn in k2ns:
                vk2 = self.vk2dic[kn]
                val = vk2.dic[b]
                for v in self.bdic1[b]:
                    # v != val-> gen new vk1, v == val -> only reduce vk2.cvs
                    # in case of new-vk1, collect vk1.bit into new_bb_bits
                    new_vk1 = self.bdic1[b][v].filter_vk2(vk2, v != val)
                    if new_vk1: new_bb_bits.add(new_vk1.bit)
        if len(new_bb_bits) > 0:
            # these bits are new, recursion on them
            self.filter_vk2s(new_bb_bits)


    def add_snode_root(self, bgrid):
        bdic1_rbits = sorted(set(self.bdic1).intersection(bgrid.bits))
        for rb1 in bdic1_rbits:
            for k1n in self.bdic1[rb1]:
                vk1 = Center.vk1dic[k1n]
                cvs = bgrid.cvs_subset(vk1.bit, vk1.val)
                # these cvs are hits with vk1.cvs node
                if type(vk1.cvs) == set:
                    block_added = self.blckmgr.add_block(
                        fill_dict(self.driver.chvdic,
                                  {vk1.nov: cvs.intersection(vk1.cvs)})
                    )
                else:
                    nd = copy.deepcopy(vk1.cvs)
                    nd[bgrid.nov] = cvs
                    block_added = self.blckmgr.add_block(nd)
        # handle vk2s bouncing with bgrid.bits
        cmm_rbits = sorted(set(self.bdic2).intersection(bgrid.bits))
        for rb in cmm_rbits:
            for k2n in self.bdic2[rb]:
                vk2 = self.vk2dic[k2n]
                if set(vk2.bits).issubset(bgrid.bits):
                    hit_cvs = bgrid.vk2_hits(vk2)
                    print(f"{k2n} inside {bgrid.nov}-root, blocking {hit_cvs}")
                    block = fill_dict(self.driver.chvdic,
                                {vk2.nov:vk2.cvs.copy(), bgrid.nov: hit_cvs})
                    block_added = self.blckmgr.add_block(block)
                else:# vk1.cvs is compound  caused by overlapping 
                    # with xsn.root-bits, will be named with R-prefix
                    x_cvs_subset = bgrid.cvs_subset(rb, vk2.dic[rb])
                    node = fill_dict(self.driver.chvdic,
                            {vk2.nov: vk2.cvs.copy(), bgrid.nov: x_cvs_subset})
                    self.add_excl(vk2, copy.deepcopy(node))
                    name = NameDrive.rname()
                    new_vk1 = vk2.clone(name, [rb], node) # R prefix, drop rb
                    new_vk1.source = vk2.kname
                    self.add_vk1(new_vk1)
    # end of def add_snode_root(self, bgrid):
    
    def insert_vk2(self, vk2):
        name = vk2.kname
        b1, b2 = vk2.bits
        if (b1 not in self.bdic2) or name not in self.bdic2[b1]:
            self.bdic2.setdefault(b1,[]).append(name)
        if (b2 not in self.bdic2) or name not in self.bdic2[b2]:
            self.bdic2.setdefault(b2,[]).append(name)
        self.vk2dic[name] = vk2


    def add_bblocker(self, bit, val, node, info=None):
        # BitBlocker(bit, self)
        bb_dic = self.bdic1.setdefault(bit, {})
        bb_dic[val] = BitBlocker(bit, val, self)
        bb_dic[val].add(node, info)

    def add_vk2(self, vk2):
        bits = set(self.bdic1).intersection(vk2.bits)
        for bit in bits:
            self.bdic1[bit].check_vk2(vk2)
        self.insert_vk2(vk2)
        # handle case of 2 overlapping bits with existing vk2
        self.proc_vk2pair(vk2) # if vk2 has a twin in vk2dic

    def proc_vk2pair(self, vk2):
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
                if self.driver: expand_vk1s(self, vk1)
                self.add_vk1(vk1)

    def add_excl(self, vk2, node):
        if len(node) == 1: # in case node has only 1 entry like {60:{3,7}
            nov, cvs = tuple(node.items())[0] # like {60:{3,7}}->60, {3,7}
            if nov == vk2.nov:  # vk2,cvs:{2,3,6,7}
                vk2.cvs -= cvs  # vk2.cvs -> {2,6}
                return True
        lst = self.excls.setdefault(vk2.kname, [])
        if node in lst: return False
        for ind, old_dic in enumerate(lst):
            cont = test_containment(node, old_dic)  # param-names: (d1, d2)
            if not cont: continue
            if cont['cat'].startswith('contain'):
                # {cat: "contain: d1 in d2"}: 
                # user the container, dump the other
                container = cont['cat'].split(':')[1].split()[-1] # d2
                if container == 'd2': # old_dic is the container
                    return False
                elif container == 'd1':
                    lst[ind] = node           # node replace that one
                    return True               # node has been "added"
            if cont['cat'] == "mergable": # merge on mergable nov into old_dic
                nv = cont['merge-nov']
                old_dic[nv].update(node[nv])
                return True  # don't put into lst, since already to old-dic
        lst.append(node)
        return True
