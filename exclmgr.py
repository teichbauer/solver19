from utils.cvsnodetools import *

class Excl:
    def __init__(self, node=None):
        self.nodes = []
        if node:
            self.add(node)

    def clone(self):
        nexcl = Excl()
        nexcl.nodes = copy.deepcopy(self.nodes)
        return nexcl

    def add(self, node):
        if type(node) == list:
            for nd in node:
                self.add(nd)
        else:
            seq = node_seq(node)
            while not seq.done:
                nt = seq.get_next()
                if nt not in self.nodes:
                    self.nodes.append(nt)

class ExclMgr:
    def __init__(self, repo):
        self.repo = repo
        self.dic = {} # {kn: Excl}

    def clone(self, repo):
        nexclmgr = ExclMgr(repo)
        nexclmgr.dic = {kn: excl.clone() for kn, excl in self.dic.items()}
        return nexclmgr
    
    def add(self, vkname, node):
        self.dic.setdefault(vkname, Excl()).add(node)