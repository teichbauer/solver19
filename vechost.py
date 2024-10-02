from center import Center
import copy
from basics import add_vk1, add_vk2

def grow_vk1(in_bdic2, in_bdic1, in_k1ns):
    new_bdic1 = {}
    xbits = set(in_bdic1).intersection(in_bdic2)
    while True:
        while len(xbits) > 0:
            b = xbits.pop()
            k1ns = in_bdic1[b]
            for k1n in k1ns:
                vk1 = Center.vk1dic[k1n]
                k2ns = in_bdic2[b]
                for k2n in k2ns:
                    new_vk1 = None
                    if k2n[1:] == k1n[1:]: continue
                    vk2 = Center.vk2dic[k2n]
                    if k1n[0] in ('U','R'): # in case of Rnnn / Unnn
                        # vk1.cvs is a compound: dict{nov1:, nov2:}
                        new_cvs = vk1.cvs.copy()
                        cmm_cvs = vk2.cvs.intersection(new_cvs[vk2.nov])
                        if len(cmm_cvs) == 0:
                            continue
                        if vk2.dic[b] != vk1.dic[b]:
                            new_cvs.update({vk2.nov:cmm_cvs})
                            new_vk1 = vk2.clone('U', [b], new_cvs)
                        else: # vk2.dic[b] == vk1.dic[b]
                            x = 0 # vk2 exclusion?
                    else: # vk1 is not a compound: no cmm cvs btwn vk1 & vk2
                        if vk2.nov == vk1.nov:
                            if k2n[0] == 'C':
                                continue 
                            else:
                                x = 0 # can this happen?
                        else:
                            if k2n[0] == 'C': 
                                new_cvs = {vk1.nov:vk1.cvs, vk2.nov:vk2.cvs}
                                new_vk1 = vk2.clone('U', [b], new_cvs)
                            else:
                                x = 0 # can this happen?
                    if new_vk1:
                        add_vk1(new_vk1, None, in_bdic1, in_k1ns)
                        Center.add_vk1(new_vk1)
                        new_bdic1.setdefault(new_vk1.bits[0], [])\
                                 .append(new_vk1.kname)
        xbits = set(new_bdic1).intersection(in_bdic2)
        if len(xbits) == 0: return
        else: new_bdic1 = {}

class VectorHost:
    # class variables:
    # node: {60:{2,3,4}, 57:{0,1}, 54: {2},..}
    excl_dic = {} # {<kn>: [<node1>,..] k2n should be excluded from nodes
    blocks = []  # [<node>,<node>,...] these nodes are hit(dead)

    def __init__(self, snode):     # root-bitgrid of the snode
        self.snode = snode
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
        grow_vk1(self.bdic2, self.bdic1, self.k1ns)

    def find_Rvk1(self, xsn):
        cmm_rbits = set(self.bdic2).intersection(xsn.bgrid.bits)
        for rb in cmm_rbits:
            for k2n in self.bdic2[rb]:
                vk2 = self.vk2dic[k2n]
                if set(vk2.bits).issubset(xsn.bgrid.bits):
                    print("special case happening")
                else:
                    # compound Vk1s that are caused by overlapping 
                    # with xsn.root-bits, will be named with R-prefix
                    x_cvs_subset = xsn.bgrid.cvs_subset(rb, vk2.dic[rb])
                    node = {self.snode.nov: vk2.cvs, xsn.nov: x_cvs_subset}
                    vk1 = vk2.clone\
                        ('R',        # prefix for root-bit of xsn
                        [rb], node)  # dropping xsn-root-bit, on node
                    self.add_vk(vk1)
                    self.excl_k2n(k2n, node)
                    self.block_test(vk1)

    def add_vk1(self, vk1):
        add_vk1(vk1, None,  # vk1dic is only held in Center.vk1dic
                self.bdic1, 
                self.k1ns)
        Center.add_vk1(vk1)

    def block_test(self, vk1):
        # see if vk1 is causing block-node(s)
        bit = vk1.bits[0]
        k1ns = Center.vk1bdic[bit]
        for k1n in k1ns:
            xvk1 = Center.vk1dic[k1n]
            if xvk1.dic[bit] != vk1.dic[bit]:
                x = 0
            

    def excl_k2n(self, k2n, node):
        self.excl_dic.setdefault(k2n, []).append(node)

