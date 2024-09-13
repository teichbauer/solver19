from basics import sat_conflict, get_vk2sats

class STail:
    def __init__(self, snode, chval): #vkm, anc_bits, check_val):
        self.snode = snode
        self.cval = chval      # check_vals
        self.bdic = {}  # {<bit>: [<kname>,..]}
        self.vk2s = {}
        self.root_sats = snode.bgrid.grid_sat(chval)
        self.k1ns = set([])

    def start_sats(self,csatdic={}):
        # csatdic cannot have conflict with root_sats
        sats = []
        sat = self.root_sats.copy()
        # if sat_conflict(self.satdic, csatdic):
        #     return None
        # sat.update(self.satdic)
        sat.update(csatdic)
        sats.append(sat)
        vk2s = self.vk2s.copy()
        if len(vk2s) == 0:
            return sats
        while len(vk2s):
            res_sats = []
            _, vk2 = vk2s.popitem()
            vk2_sats = get_vk2sats(vk2, csatdic)
            for rs in sats:
                for s in vk2_sats:
                    ss = rs.copy()
                    ss.update(s)
                    res_sats.append(ss)
            sats = res_sats
        return res_sats

    def add_vk(self, vk):
        self.vk2s[vk.kname] = vk
        if vk.nob == 1:
            self.k1ns.add(vk.kname)
        for b in vk.bits:
            self.bdic.setdefault(b, []).append(vk.kname)

    def remove_vk(self, kn):
        vk = self.vk2s.pop(kn)
        if vk.kname.startswith('S') and vk.kname in self.k1ns:
            self.k1ns.remove(vk.kname)
        for b in vk.bits:
            self.bdic[b].remove(kn)
            if len(self.bdic[b]) == 0:
                del self.bdic[b]


    def grow_sat(self, sdic):
        new_sdic = {}
        while len(sdic) > 0:
            b, v = sdic.popitem()
            # self.bdic[b] will change. use clone before it mutate
            kns = self.bdic.get(b,[])[:] 
            for kn in kns:
                vk2x = self.vk2s[kn]
                # vk2x has bit b. vkx should be removed from 
                # self.vk2s, regardless 
                # vk2x.dic[b] == v or not
                self.vk2s.pop(kn)   # vk2s is a dict
                # remove vkx.kname from self.bdic
                for bx in vk2x.bits:
                    self.bdic[bx].remove(vk2x.kname)
                    if len(self.bdic[bx]) == 0:
                        self.bdic.pop(bx)
                # remove the cv(self.cval) from vkx.cvs
                vk2x.cvs.remove(self.cval)
                if len(vk2x.cvs) == 0: # when vkx has no cv: 
                    # remove it from snode.vk2dic
                    self.snode.vk2dic.pop(vk2x.kname)
                    # also remove it from snode.bdic
                    for bx in vk2x.bits:
                        if vk2x.kname in self.snode.bdic[bx]:
                            self.snode.bdic[bx].remove(vk2x.kname)
                            if len(self.snode.bdic[bx]) == 0:
                                self.snode.bdic.pop(bx)
                if vk2x.dic[b] == v: # vkx is hit: resulting in a new sat
                    dd = vk2x.dic.copy()
                    dd.pop(b)
                    bx, vx = dd.popitem()
                    sat_val = int(not vx)
                    new_sdic[bx] = sat_val
                    self.snode.add_sat(bx, sat_val, self.cval)
        if len(new_sdic) > 0:
            self.satdic.update(new_sdic)
            self.grow_sat(new_sdic)

