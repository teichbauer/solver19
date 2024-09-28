from center import Center
import copy

def merge(hsnode, lsnode):
    bdic2 = copy.deepcopy(hsnode.bdic)
    for bit, kns in lsnode.bdic.items():
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
                    vk2 = Center.vk2dic[k2n]
                    if k1n[0] != 'U' and \
                      (k2n[1:]==k1n[1:] or (k2n[0]=='C' and vk2.nov==vk1.nov)):
                        continue # when k1n[0] is NOT 'U', this may happen
                    if vk2.dic[b] != vk1.dic[b]:
                        nk1n = vk2.kname.replace('C', 'U')
                        nvk1 = vk2.clone(nk1n, [b])
                        if k1n[0] == 'U':
                            nvk1.cvs = vk1.cvs.copy()
                            if vk1.nov == vk2.nov:
                                ncvs = nvk1.cvs.pop(vk1.nov)
                                nvk1.cvs[vk1.nov] = vk2.cvs.intersection(ncvs)
                                if len(nvk1.cvs[vk2.nov]) > 0:
                                    # adding nvk1
                                    in_bdic1[b].append(nk1n)
                                    in_k1ns.append(nk1n)
                                    Center.vk1dic[nk1n] = nvk1
                                    Center.vk1info[vk2.nov].append(nk1n)
                                    new_bdic1.setdefault(b, []).append(nk1n)
                        else:
                            x = 0
                    else: # vk2.dic[b] == vk1.dic[b]
                        x = 0
        xbits = set(new_bdic1).intersection(in_bdic2)
        new_bdic1 = {}
        if len(xbits) == 0:
            return

class VectorHost:
    def __init__(self, 
                 snode,     # root-bitgrid of the snode
                 tailkeys): # {<chval>: <ch-bkey>, ...}
        self.snode = snode
        self.tailkeys = tailkeys

    def total_key(self, chv):
        return self.tailkeys[chv].union(self.snode.bgrid.bits)

    def find_tvk1s(self):
        nov = self.snode.nov
        while nov > 18:
            xsn = Center.snodes[nov - 3]
            cmm_rbits = set(self.snode.bdic).intersection(xsn.bgrid.bits)
            for rb in cmm_rbits:
                for kn in self.snode.bdic[rb]:
                    vk2 = self.snode.vk2dic[kn]
                    if set(vk2.bits).issubset(xsn.bgrid.bits):
                        print("special case happening")
                    else:
                        x_cvs_subset = xsn.bgrid.cvs_subset(rb, vk2.dic[rb])
                        vk1 = vk2.clone(
                            'U',    # prefix is U
                            [rb],   # dropped bits
                            {self.snode.nov: vk2.cvs, xsn.nov: x_cvs_subset}
                        )
                        self.snode.add_vk(vk1)
            # bits_h2l = set(self.snode.bdic1).intersection(xsn.bdic)
            # bits_l2h = set(xsn.bdic1).intersection(self.snode.bdic)
            mbdic2, mbdic1, mvk2dic, mk1ns = merge(self.snode, xsn)
            grow_vk1(mbdic2, mbdic1, mk1ns)
            nov -= 3

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

