class VectorHost:
    def __init__(self, 
                 snode,     # root-bitgrid of the snode
                 tailkeys): # {<chval>: <ch-bkey>, ...}
        self.snode = snode
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