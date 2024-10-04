from center import Center
import copy
from basics import add_vk1, add_vk2


class VectorHost:
    # class variables:
    # node: {60:{2,3,4}, 57:{0,1}, 54: {2},..}
    excl_dic = {} # {<kn>: [<node1>,..] k2n should be excluded from nodes
    blocks = []  # [<node>,<node>,...] these nodes are hit(dead)

    def __init__(self, snode):     # root-bitgrid of the snode
        self.nov = snode.nov
        self.bdic2 = copy.deepcopy(snode.bdic2)
        self.vk2dic = snode.vk2dic.copy()
        self.bdic1 = copy.deepcopy(snode.bdic1)
        self.k1ns = snode.k1ns.copy()

    def merge_down(self, lsnode):
        for bit, kns in lsnode.bdic2.items():
            lst = self.bdic2.setdefault(bit, [])
            for kn in kns:
                if kn in lst:
                    print("weird")
                else:
                    lst.append(kn)
        for kn, vk2 in lsnode.vk2dic.items():
            self.vk2dic[kn] = vk2
        for bit, kns in lsnode.bdic1.items():
            lst = self.bdic1.setdefault(bit, [])
            for kn in kns:
                if kn in lst:
                    print("weird-2")
                else:
                    lst.append(kn)
        self.k1ns += lsnode.k1ns
        self.find_Rvk1(lsnode)
        self.grow()

    def grow(self):
        xbits = set(self.bdic1).intersection(self.bdic2)
        while len(xbits) > 0:
            nbdic1 = {}
            for b in xbits:
                k1ns = self.bdic1[b]
                for k1n in k1ns:
                    vk1 = Center.vk1dic[k1n]
                    k2ns = self.bdic2[b]
                    for k2n in k2ns:
                        nvk1 = None
                        if k2n[1:] == k1n[1:]: continue
                        vk2 = Center.vk2dic[k2n]
                        if k1n[0] in ('U','V','R'): #vk1.cvs dict{nov1:,nov2:}
                            node = vk1.cvs.copy()
                            cmm_cvs = vk2.cvs.intersection(node[vk2.nov])
                            if len(cmm_cvs) == 0: continue
                            node.update({vk2.nov:cmm_cvs})
                            self.excl_k2n(k2n, node) # ??
                            if vk2.dic[b] != vk1.dic[b]:
                                nvk1 = vk2.clone('U', [b], node)
                        else: # vk1 is a S/T, not a compound:
                            if vk2.nov == vk1.nov:
                                if k2n[0] == 'C': continue 
                                else: x = 0 # can this happen?
                            elif k2n[0] == 'C': 
                                node = {vk1.nov:vk1.cvs, vk2.nov:vk2.cvs}
                                if vk2.dic[b] != vk1.dic[b]:
                                    nvk1 = vk2.clone('U', [b], node)
                                self.excl_k2n(k2n, node) # ??
                            else: x = 0 # can this happen?
                        if nvk1:
                            self.add_vk1(nvk1)
                            self.block_test(nvk1)
                            nbdic1.setdefault(nvk1.bits[0],[]).append(nvk1.kname)
            xbits = set(nbdic1).intersection(self.bdic2)

    def find_Rvk1(self, xsn):
        cmm_rbits = set(self.bdic2).intersection(xsn.bgrid.bits)
        for rb in cmm_rbits:
            for k2n in self.bdic2[rb]:
                vk2 = self.vk2dic[k2n]
                if set(vk2.bits).issubset(xsn.bgrid.bits):
                    hit_cvs = xsn.bgrid.vk2_hits(vk2)
                    print(f"{k2n} inside {xsn.nov}-root, blocking {hit_cvs}")
                    self.blocks.append({vk2.nov:vk2.cvs, xsn.nov: hit_cvs})
                else:
                    # compound Vk1s that are caused by overlapping 
                    # with xsn.root-bits, will be named with R-prefix
                    x_cvs_subset = xsn.bgrid.cvs_subset(rb, vk2.dic[rb])
                    node = {vk2.nov: vk2.cvs, xsn.nov: x_cvs_subset}
                    if k2n in self.excl_dic and node in self.excl_dic[k2n]:
                        continue
                    vk1 = vk2.clone\
                        ('R',        # prefix for root-bit of xsn
                        [rb], node)  # dropping xsn-root-bit, on node
                    self.add_vk1(vk1)
                    self.excl_k2n(k2n, node)
                    self.block_test(vk1)

    def add_vk1(self, vk1):
        name = vk1.kname
        # a vk2 may have both of its bits turned to vk1. So the prefix
        # 'U' may have been used. In that case, use 'V' as vk1 name prefix
        if name[0] == 'U' and name in self.k1ns:
            vk1.kname = f'V{name[1:]}'
        add_vk1(vk1, None,  # vk1dic is only held in Center.vk1dic
                self.bdic1, 
                self.k1ns)
        Center.add_vk1(vk1)

    def block_test(self, vk1):
        def set2node(s, set_nov, node):
            if set_nov in node:
                xset = s.intersection(node[set_nov])
                if len(xset) > 0:
                    xnode = node.copy()
                    xnode.update({set_nov: xset})
                    return xnode
                else: return None
            else:
                print("weird-01")
                return None

        def node2node(n1, n2):
            xnode = n1.copy()
            for nv, st in n2.items():
                if nv in xnode:
                    xs = st.intersection(xnode[nv])
                    if len(xs) == 0:
                        return None
                    xnode.update({nv: xs})
            return xnode

        # see if vk1 is causing block-node(s)
        bit = vk1.bits[0]
        k1ns = self.bdic1[bit]
        for k1n in k1ns:
            if vk1.kname == k1n: continue
            xvk1 = Center.vk1dic[k1n]
            res = None
            if xvk1.dic[bit] != vk1.dic[bit]:
                if type(vk1.cvs) == dict:
                    if type(xvk1.cvs) == dict:
                        res = node2node(vk1.cvs, xvk1.cvs)
                    else:   # xvk1.cvs is a set
                        res = set2node(xvk1.cvs, xvk1.nov, vk1.cvs)
                else:  # vk1.cvs is a set
                    if type(xvk1.cvs) == dict:
                        res = set2node(vk1.cvs, vk1.nov, xvk1.cvs)
                    else: # both are sets
                        print("what to do?")
            if res and (res not in self.blocks):
                self.blocks.append(res)

    def excl_k2n(self, k2n, node):
        self.excl_dic.setdefault(k2n, []).append(node)

