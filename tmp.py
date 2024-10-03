# from vechost.py/ VectorHost
import copy
from center import Center

def merge(hsnode, lsnode):
    bdic2 = copy.deepcopy(hsnode.bdic2)
    for bit, kns in lsnode.bdic2.items():
        lst = bdic2.setdefault(bit, [])
        for kn in kns:
            if kn in lst:
                print("weird")
            else:
                lst.append(kn)
    vk2dic = hsnode.vk2dic.copy()  # vk2s are not cloned. Here they are refs
    for kn, vk2 in lsnode.vk2dic.items():
        vk2dic[kn] = vk2
    bdic1 = copy.deepcopy(hsnode.bdic1)
    for bit, kns in lsnode.bdic1.items():
        lst = bdic1.setdefault(bit, [])
        for kn in kns:
            if kn in lst:
                print("weird-2")
            else:
                lst.append(kn)
    k1ns = hsnode.k1ns + lsnode.k1ns
    return bdic2, bdic1, vk2dic, k1ns

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


class VectoreHost:
    '''...'''

    def down_intersec_vecdic(self, nov):
        if nov < 21: return
        div_dic = {}    # {<nv>:{<cv>:{lcv:iv,..},..},<nv>:{}}
        while nov > 18:
            nov -= 3
            xsn = self.snode.Center.snodes[nov]
            nvdic = div_dic.setdefault(xsn.nov,{})
            for mycv, mykey in self.tailkeys.items():
                cdic = nvdic.setdefault(mycv,{})
                for cv in xsn.vecmgr.tailkeys:
                    xset = mykey.intersection(xsn.vecmgr.total_key(cv))
                    if len(xset) > 0:
                        cdic[cv] = xset
        self.div_dic = div_dic

    def up_intersec_vecdic(self, nov):
        if nov >= 60: return
        uiv_dic = {}
        while nov < 60:
            nov += 3
            xsn = self.snode.Center.snodes[nov]
            nvdic = uiv_dic.setdefault(xsn.nov,{})
            for mycv in self.tailkeys:
                total_key = self.total_key(mycv)
                cdic = nvdic.setdefault(mycv,{})
                for cv, ky in xsn.vecmgr.tailkeys.items():
                    xset = total_key.intersection(ky)
                    if len(xset) > 0:
                        cdic[cv] = xset
        self.uiv_dic = uiv_dic

    def find_tvk1s(self):
        nov = self.snode.nov
        while nov > 18:
            xsn = Center.snodes[nov - 3]
            cmm_rbits = set(self.snode.bdic2).intersection(xsn.bgrid.bits)
            for rb in cmm_rbits:
                for kn in self.snode.bdic2[rb]:
                    vk2 = self.snode.vk2dic[kn]
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
                        self.snode.add_vk(vk1)
                        self.excl_k2n(kn, node)
                        self.block_test(vk1)
            mbdic2, mbdic1, mvk2dic, mk1ns = merge(self.snode, xsn)
            grow_vk1(mbdic2, mbdic1, mk1ns)
            nov -= 3

