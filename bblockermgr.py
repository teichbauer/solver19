from center import Center
from utils.sequencer import Sequencer
from utils.tools import break_node, fill_dict
import copy

class BitBlockerMgr:
    # managing vk1s on a bit
    def __init__(self, repo):
        self.bbdic = {} # {bit: {0:[node-list], 1:[node-list]}, bit: {}, ..}
        self.repo = repo
        self.log = []

    def clone(self, xrepo):
        xbbmgr = BitBlockerMgr(xrepo)
        xbbmgr.bbdic = copy.deepcopy(self.bbdic)
        xbbmgr.log = self.log.copy()
        return xbbmgr
    
    def expand(self):
        pass

    def sat(self):
        return {self.bit: tuple(self.nodes)[0]}
    
    def collect_sat(self, pthrd, bits): # bits come from vk2dic for a pthrd
        bs = set(self.bbdic).intersection(bits)
        sat = {}
        for b in bs:
            for v in (0, 1):
                if pthrd in self.bbdic[v]:
                    sat[b] = (v + 1) % 2  # reverse 0/1
        return sat

    def add(self, vk1, node=None):
        if not node: node = vk1.cvs
        doit = break_node(node, Sequencer)
        if doit == True:
            dic = self.bbdic.setdefault(vk1.bit,{})
            if node not in dic.setdefault(vk1.val,[]):
                dic[vk1.val].append(node)
        else:
            while not doit.done:
                nd = doit.get_next()
                self.add(vk1, nd)
        

