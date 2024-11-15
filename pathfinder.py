from utils.tools import *
from utils.cvsnodetools import check_spouse

class PathFinder:
    def __init__(self, start_snode):
        self.snode = start_snode
        self.repo = start_snode.repo.clone(self)
        self.repo.pathmgr = self

    def write_log(self, outfile_name):
        ofile = open(outfile_name, 'w')
        msg = outputlog(self.repo, Center.vk1dic)
        ofile.write(msg)
        ofile.close()


    def grow(self, sn):
        repo = self.repo
        repo.snode_dic[sn.nov] = sn
        # self.repo.blckmgr.expand()
        repo.add_snode_root(sn.bgrid)
        for bit, bbdic in sn.repo.bdic1.items():
            dic = repo.bdic1.setdefault(bit, {})
            for v, bb in bbdic.items():
                if v in dic:
                    dic[v].merge(bb, repo.steps)
                else:
                    dic[v] = bb.clone(repo)
            check_spouse(dic)
        new_bits = set()
        for vk2 in sn.repo.vk2dic.values():
            repo.add_vk2(vk2, new_bits)
        if len(new_bits) > 0:
            bit12 = sorted(new_bits.intersection(repo.bdic2))
            self.repo.filter_vk2s(bit12)


    def fishout_path(self):
        all_paths = self.pgenerator()
        valids = []
        for p in all_paths:
            if self.repo.blckmgr.verify_pth(p):
                valids.append(p)
        return valids

    def pgenerator(self):
        base = [self.chvdic[nv] for nv in self.steps]
        paths = []
        g = path_iterator(base)
        try:
            while True:
                t = next(g)
                paths.append(t)
        except:
            print(f"there are {len(paths)} paths")
            return paths

