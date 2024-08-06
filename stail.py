from center import Center

def sat_conflict(sat1, sat2):
    intersection_bits1 = set(sat1).intersection(sat2)
    for b in intersection_bits1:
        if sat1[b] != sat2[b]:
            return True
    return False

def get_vk2sats(vk2):
    d = vk2.dic
    sats = []
    k1, k2 = list(vk2.dic.keys())
    sats.append({k1: d[k1], k2: int(not d[k2])})
    sats.append({k1: int(not(d[k1])), k2: d[k2]})
    sats.append({k1: int(not(d[k1])), k2: int(not d[k2])})
    return sats

def multi_vk2_sats(vk2s):
    all_sats = []
    sats = get_vk2sats(vk2s.pop(0))
    while len(vk2s) > 0:
        satxs = get_vk2sats(vk2s.pop(0))
        for sat in sats:
            for satx in satxs:
                if not sat_conflict(sat, satx):
                    ss = sat.copy()
                    ss.update(satx)
                    if ss not in all_sats:
                        all_sats.append(ss)
    return all_sats

class STail:
    def __init__(self, snode, chval): #vkm, anc_bits, check_val):
        self.snode = snode
        self.cval = chval      # check_vals
        self.bdic = {}
        self.vk2s = {}
        self.root_sats = snode.bgrid.grid_sat(chval)
        self.satdic = {}  # {<bit>: <val>}

    def sat_filter(self):

        sat = self.root_sats.copy()
        vk2s = self.vk2s.copy()
        if len(vk2s):
            vk2_sats = get_vk2sats(vk2s.popitem()[1])
            for s in vk2_sats:
                ss = sat.copy()
                ss.update(s)
                self.snode.parent.find_paths(ss)
        else:
            pass
            # self.snode.find_path(sat)

    def tail_bits(self):
        bits = set(self.bdic)
        bits.update(self.satdic)
        return bits

    def find_path(self, sat, path):
        bits = self.tail_bits()

    def add_vk2(self, vk2):
        self.vk2s[vk2.kname] = vk2
        for b in vk2.bits:
            self.bdic.setdefault(b, []).append(vk2.kname)

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