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
