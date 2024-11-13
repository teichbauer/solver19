from utils.tools import *

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
        self.repo.snode_dic[sn.nov] = sn
        # self.repo.blckmgr.expand()
        self.repo.add_snode_root(sn.bgrid)
        for bit, bbdic in sn.repo.bdic1.items():
            dic = self.repo.bdic1.setdefault(bit, {})
            for v, bb in bbdic.items():
                if v in dic:
                    dic[v].merge(bb, self.repo.steps())
                else:
                    dic[v] = bb.clone(self.repo)
            if len(dic) == 2:
                dic[0].spouse = dic[1]
                dic[1].spouse = dic[0]
                dic[0].spousal_conflict()
        for vk2 in sn.repo.vk2dic.values():
            self.repo.add_vk2(vk2)
        x = 9


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

