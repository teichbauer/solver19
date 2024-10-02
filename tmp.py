# from vechost.py/ VectorHost
import copy

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

