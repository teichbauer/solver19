from tools import *

class PathFinder:
    def __init__(self, start_snode):
        self.snode = start_snode
        self.repo = start_snode.vkrepo.clone(self)
        self.steps = [self.snode.nov]
        self.chvdic = {start_snode.nov: start_snode.bgrid.chvals[:]}

    def write_log(self, outfile_name):
        ofile = open(outfile_name, 'w')
        msg = outputlog(self.repo, Center.vk1dic)
        ofile.write(msg)
        ofile.close()


    def grow(self, sn):
        self.steps.append(sn.nov)
        self.chvdic[sn.nov] = sn.bgrid.chvals[:]
        expand_vk1s(self.repo)
        expand_excls(self.repo)
        expand_blocks(self.repo)
        self.repo.add_snode_root(sn.bgrid)
        for k1n in sn.vkrepo.k1ns:
            self.repo.add_vk1(Center.vk1dic[k1n])
        for vk2 in sn.vkrepo.vk2dic.values():
            self.repo.add_vk2(vk2)
        x = 9
    def block_filter(self):
        blocks = self.repo.blocks
        paths = self.fishout_path()
        for p in paths:
            print(p)


    def verify_pth(self, lst, pth): # pth: (7,1,4)
        nvs = (60, 57, 54)
        cand60 = []
        for b in lst:
            if pth[0] in b[60]:
                cand60.append(b)
        if len(cand60) == 0: return True
        cand57 = []
        for b in cand60:
            if pth[1] in b[57]:
                cand57.append(b)
        if len(cand57) == 0: return True
        cand54 = []
        for b in cand57:
            if pth[2] in b[54]:
                cand54.append(b)
        return len(cand54) == 0

    def fishout_path(self):
        all_paths = self.pgenerator()
        valids = []
        for p in all_paths:
            if self.verify_pth(self.repo.blocks, p):
                valids.append(p)
        return valids

    def pgenerator(self):
        def gen(b):
            res = []
            for s60 in base[0]:
                res.append(s60)
                for s57 in base[1]:
                    res.append(s57)
                    for s54 in base[2]:
                        res.append(s54)
                        yield tuple(res)
                        res.pop()
                    res.pop()
                res.pop()
        # -------------------------------
        base = ((1,2,3,4,6,7),(0,1,2,3,4,6,7),(0,1,2,3,5,6,7))
        paths = []
        g = gen(base)
        try:
            while True:
                t = next(g)
                paths.append(t)
        except:
            print(f"there are {len(paths)} paths")
            return paths

