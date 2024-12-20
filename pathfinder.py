from utils.tools import *
from utils.cvsnodetools import check_spouse

class PathFinder:
    def __init__(self, start_snode):
        self.snode = start_snode
        self.repo = start_snode.repo.clone(self)
        self.repo.pathmgr = self

    def write_log(self, outfile_name):
        ofile = open(outfile_name, 'w')
        msg = outputlog(self)
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
                    dic[v].merge(bb)
                else:
                    dic[v] = bb.clone(repo)
            check_spouse(dic)
        new_bits = set()
        for vk2 in sn.repo.vk2dic.values():
            repo.add_vk2(vk2, new_bits)
        bb_pairs = [] # [(<bb-bit>,<bb-val>),..]
        for b in sorted(new_bits):
            for v in repo.bdic1[b]:
                bb_pairs.append((b,v))
        self.repo.filter_vk2s(bb_pairs)
