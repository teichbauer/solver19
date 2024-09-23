from vklause import VKlause

class VectorHost:
    def __init__(self, 
                 snode,     # root-bitgrid of the snode
                 tailkeys): # {<chval>: <ch-bkey>, ...}
        self.snode = snode
        self.Center = snode.Center
        self.tailkeys = tailkeys

    def total_key(self, chv):
        return self.tailkeys[chv].union(self.snode.bgrid.bits)

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
            xsn = self.Center.snodes[nov - 3]
            cmm_rbits = set(self.snode.bdic).intersection(xsn.bgrid.bits)
            for rb in cmm_rbits:
                for kn in self.snode.bdic[rb]:
                    vk2 = self.snode.vk2dic[kn]
                    if set(vk2.bits).issubset(xsn.bgrid.bits):
                        pass
                    else:
                        x_cvs_subset = xsn.bgrid.cvs_subset(rb, vk2.dic[rb])
                        vk1 = vk2.clone(
                            'U',    # prefix is U
                            [rb],   # dropped bits
                            {self.snode.nov: vk2.cvs, xsn.nov: x_cvs_subset}
                        )
                        self.Center.add_vk1(vk1)
            nov -= 3
