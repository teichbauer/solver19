from center import Center
from tools import handle_vk2pair, cvs_intersect, reduce_cvs, cvs_subset
from namepool import NamePool

class VKRepoitory:
    def __init__(self, snode):
        self.bdic1 = {}     # {bit: [k1n, k1n,..], bit:[], ..}
        self.bdic2 = {}     # {bit: [k2n, k2n,..], bit:[], ..}
        self.k1ns = []      # [k1n, k1n,..]
        self.vk2dic = {}    # {k2n:vk2, k2n: vk2,...}
        self.blocks = []    # [node, ..] node:{nov:cvs, nv:..} where snode fails
        self.excls = {}     # {kn:[node, node,..],..} vk not 2b used in nodes
        self.snode = snode  # related snode
        self.inflog = {}    # {key:[info,info,..], key:[], ...}

    def clone(self):
        xrepo = VKRepoitory(self.snode)
        xrepo.bdic1 = {b: lst[:] for b, lst in self.bdic1.items()}
        xrepo.bdic2 = {b: lst[:] for b, lst in self.bdic2.items()}
        xrepo.k1ns = self.k1ns[:]
        xrepo.vk2dic = {kn:vk2 for kn, vk2 in self.vk2dic.items()}
        xrepo.blocks = [node.copy() for node in self.blocks]
        for kn, lst in self.excls.items():
            xrepo.excls[kn] = [node.copy() for node in lst]
        return xrepo
    
    def add_snode_root(self, bgrid):
        bdic1_rbits = set(self.bdic1).intersection(bgrid.bits)
        for rb1 in bdic1_rbits:
            for k1n in self.bdic1[rb1]:
                vk1 = Center.vk1dic[k1n]
                cvs = bgrid.cvs_subset(vk1.bits[0], vk1.dic[vk1.bits[0]])
                if not cvs: continue
                # these cvs are hits with vk1.cvs node
                if type(vk1.cvs) == set:
                    self.blocks.append({vk1.nov: cvs.intersection(vk1.cvs)})
                else:
                    nd = vk1.cvs.copy()
                    nd[bgrid.nov] = cvs
                    self.blocks.append(nd)
        # handle vk2s bouncing with bgrid.bits
        cmm_rbits = set(self.bdic2).intersection(bgrid.bits)
        for rb in cmm_rbits:
            for k2n in self.bdic2[rb]:
                vk2 = self.vk2dic[k2n]
                if set(vk2.bits).issubset(bgrid.bits):
                    hit_cvs = bgrid.vk2_hits(vk2)
                    print(f"{k2n} inside {bgrid.nov}-root, blocking {hit_cvs}")
                    self.blocks.append({vk2.nov:vk2.cvs, bgrid.nov: hit_cvs})
                else:# vk1.cvs is compound  caused by overlapping 
                    # with xsn.root-bits, will be named with R-prefix
                    x_cvs_subset = bgrid.cvs_subset(rb, vk2.dic[rb])
                    node = {vk2.nov: vk2.cvs, bgrid.nov: x_cvs_subset}
                    if self.add_excl(vk2, node):
                        vk1 = vk2.clone(NamePool(vk2.kname).next_uname('R'),
                                        [rb], node) # R prefix, drop rb
                        self.add_vk1(vk1)
    
    def merge_snode(self, sn):
        self.add_snode_root(sn.bgrid)
        for k1n in sn.vkrepo.k1ns:
            self.add_vk1(Center.vk1dic[k1n])
        for vk2 in sn.vkrepo.vk2dic.values():
            self.add_vk2(vk2)
        x = 9

    def newvk1_to_vk1(self, nvk, ovk, add_nvk=False): 
        # new-vk1 and old-vk1 are sitting on the same bit
        if nvk.val != ovk.val:
            cmm = cvs_intersect(nvk, ovk)
            if cmm: 
                infokey = tuple(sorted([nvk.kname, ovk.kname]))
                self.inflog.setdefault(infokey,[])\
                    .append("resulted in block:"+str(cmm))
                self.blocks.append(cmm)
        if add_nvk:
            self.insert_vk1(nvk)

    def insert_vk1(self, vk1, add2center): # simply add vk1 to the repo
        name = vk1.kname
        if name in self.k1ns:
            if vk1.equal(Center.vk1dic[name]): return
            vk1.kname = NamePool(name).next_uname()
        self.k1ns.append(vk1.kname)
        self.bdic1.setdefault(vk1.bit,[]).append(vk1.kname)
        if add2center:
            Center.add_vk1(vk1)
    
    def insert_vk2(self, vk2):
        name = vk2.kname
        b1, b2 = vk2.bits
        if (b1 not in self.bdic2) or name not in self.bdic2[b1]:
            self.bdic2.setdefault(b1,[]).append(name)
        if (b2 not in self.bdic2) or name not in self.bdic2[b2]:
            self.bdic2.setdefault(b2,[]).append(name)
        self.vk2dic[name] = vk2

    def newvk1_to_vk2(self, nvk, vk2):
        # when a vk1 shares 1 bit with an existing vk2, and vk1 and vk2 
        # have no intersect in cvs, return - nothing happens. But if they
        # do have cvs-intersection(cmm) on their common nov, then 2 cases:
        # 1. vk1.val == vk2.dic[bit] -> vk2's cvs(on the same nov) 
        #    reduces by cmm
        # 2. vk1.val != vk2.dic[bit] -> 
        #    2.1: vk2's cvs(on the same nov) 
        #    2.2: new vk1 is generated for the other bit, with cmm
        cmm = cvs_intersect(nvk, vk2)
        if not cmm: return
        self.add_excl(vk2, cmm)
        if vk2.dic[nvk.bit] != nvk.val:
            vkx = vk2.clone(NamePool(vk2.kname).next_uname(), 
                            [nvk.bit], cmm)
            # vkx = vk2.clone('U', [nvk.bit], cmm)
            self.add_vk1(vkx)

    def add_vk1(self, vk1, add2center=True):
        print(vk1.print_msg())
        # handle with existing vk1s
        if vk1.bit in self.bdic1:
            for kn in self.bdic1[vk1.bit]:
                self.newvk1_to_vk1(vk1, Center.vk1dic[kn])
        # handle with vk2s
        if vk1.bit in self.bdic2:
            for kn in self.bdic2[vk1.bit]: # all vk2 are named 'Cnnnn'
                if vk1.kname[1:] == kn[1:]: continue
                vk = self.vk2dic[kn]
                self.newvk1_to_vk2(vk1, vk)
        self.insert_vk1(vk1, add2center)

    def handle_vk1_block(self, vk1):
        # for a newly found vk1, see if an opposite vk(1) exists in this
        # repo, and if yes do the two generat a block? if yes, put it in
        if vk1.kname in self.k1ns or vk1.bit not in self.bdic1: 
            return
        for kn in self.bdic1[vk1.bit]:
            vk = Center.vk1dic[kn]
            if vk.val != vk1.val:
                cmm = cvs_intersect(vk, vk1)
                if cmm:
                    self.blocks.append(cmm)

    def add_vk2(self, vk2):
        print(vk2.print_msg())
        for b in vk2.bits:
            if b in self.bdic1:
                kns = self.bdic1[b]  # for loop variable must be immutable
                for kn in kns:
                    vk1 = Center.vk1dic[kn]
                    cmm = cvs_intersect(vk1, vk2)
                    if not cmm: continue
                    self.add_excl(vk2, cmm)
                    if vk2.dic[b] != vk1.val:
                        if len(cmm) == 1:
                            vkx = vk2.clone(NamePool(vk2.kname).next_sname('T'),
                                            [b], cmm[vk2.nov])
                        else:
                            vkx = vk2.clone(NamePool(vk2.kname).next_uname(),
                                            [b], cmm)
                        self.add_vk1(vkx)
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
            vk1 = handle_vk2pair(vk2, self.vk2dic[xkns.pop()])
            if vk1: self.add_vk1(vk1)


    def add_excl(self, vk2, node):
        if len(node) == 1: # in case node has only 1 entry like {60:{3,7}
            nov, cvs = tuple(node.items())[0] # like {60:{3,7}}->60, {3,7}
            if nov == vk2.nov:  # vk2,cvs:{2,3,6,7}
                vk2.cvs -= cvs  # vk2.cvs -> {2,6}
                return True
        lst = self.excls.setdefault(vk2.kname, [])
        if node in lst: return False
        for d in lst:
            for nv, cvs in node.items():
                contained = nv in d and cvs.issubset(d[nv])
                if not contained: break
            if contained: return False
        lst.append(node)
        return True
