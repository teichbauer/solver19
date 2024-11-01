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
        self.repo.blckmgr.expand()
        self.repo.add_snode_root(sn.bgrid)
        for k1n in sn.vkrepo.k1ns:
            self.repo.add_vk1(Center.vk1dic[k1n])
        for vk2 in sn.vkrepo.vk2dic.values():
            self.repo.add_vk2(vk2)
        x = 9


    def fishout_path(self):
        all_paths = self.pgenerator()
        valids = []
        for p in all_paths:
            if self.repo.blckmgr.verify_pth(p)
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
        base = self.chvdic.values()
        paths = []
        g = gen(base)
        try:
            while True:
                t = next(g)
                paths.append(t)
        except:
            print(f"there are {len(paths)} paths")
            return paths

