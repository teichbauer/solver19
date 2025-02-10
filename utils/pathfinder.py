class PathFinder:
    def __init__(self, path, layers):
        self.path = path
        novs = [18,21,24,27,30,33,36,39,42,45,48,51,54]
        self.layers = [layers[nv] for nv in novs]

    def find_rblockers(self, pth=None):
        if not pth: 
            pth = self.path
        rblcks = []
        for layer in self.layers:
            lgrid = layer.bgrid
            bs = set(pth.bdic1).intersection(lgrid.bits)
            for b in bs:
                cvs0s, cvs1s = layer.bgrid.cvs_subset(b, 0)
                if 0 in pth.bdic1[b]:
                    for nd in pth.bdic1[b][0].noder.nodes:
                        rblcks.append(nd.copy())
                        rblcks[-1][lgrid.nov] = cvs0s
                if 1 in pth.bdic1[b]:
                    for nd in pth.bdic1[b][1].noder.nodes:
                        rblcks.append(nd.copy())
                        rblcks[-1][lgrid.nov] = cvs1s
        return rblcks


            
            