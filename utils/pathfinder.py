from pathblocker import PathBlocker
from bblocker import BitBlocker
class SatPath:
    def __init__(self, path):
        self.path = path.clone()
        self.bbbits = set(path.bdic1)

    def explore(self, layer):
        sats = []
        self.path.grow(layer)
        return sats


class PathFinder:
    def __init__(self, path, layers):
        self.path = path
        novs = [18,21,24,27,30,33,36,39,42,45,48,51]
        self.layers = [layers[nv] for nv in novs]

    def find_satpath(self):
        BitBlocker.let_pb_filter_bb = False
        # grow with root-bits/bitblockers of all layers
        for layer in self.layers:
            self.path.grow0(layer) # pb_filter_bb = False
        # --------------------------
        # grow with vk2s
        pindex = 0
        layer = self.layers[pindex]
        satpath = SatPath(self.path)

        sats = satpath.explore(layer)
        x = 9


    def find_rblockers(self, pth=None):
        if not pth: 
            pth = self.path
        bbbits = set(pth.bdic1)
        # self.path.output_all_bb() -> 2025-02-13-bitblockers.txt
        rblcks = []
        for layer in self.layers:
            lgrid = layer.bgrid
            bs = bbbits.intersection(lgrid.bits)
            for b in bs:
                cvss = layer.bgrid.cvs_subset(b, 0) # (cvs0s, cvs1s)
                for bv in (0,1):
                    bb = pth.bdic1[b].get(bv, None)
                    if not bb: continue
                    for nd in bb.noder.nodes:
                        rblcks.append(nd.copy())
                        rblcks[-1][lgrid.nov] = cvss[bv]
        return rblcks


            
            