class PathFinder:
    def __init__(self, path, layers):
        self.path = path
        novs = [18,21,24,27,30,33,36,39,42,45,48,51]
        self.layers = [layers[nv] for nv in novs]
        self.rbits = set()
        for lyr in self.layers:
            self.rbits.update(lyr.bgrid.bits)

    def find_rblockers(self, pth=None):
        if not pth: 
            pth = self.path
        bbbits = set(pth.bdic1)
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


            
            