from utils.noder import Noder, copy

class ExclMgr:
    def __init__(self, repo):
        self.repo = repo
        # dic: {kn: Noder} - for a vk/kn, these nodes are locations
        # where this vk shouldn't be used(to be excluded)
        self.dic = {} 
        self.excluded_vkns = []

    def clone(self, repo):
        nexclmgr = ExclMgr(repo)
        nexclmgr.dic = {kn: excl.clone() for kn, excl in self.dic.items()}
        nexclmgr.excluded_vkns = self.excluded_vkns[:]
        return nexclmgr
    
    def add(self, vkname, node):
        if node == None: 
            self.dic.pop(vkname, None)
            if vkname not in self.excluded_vkns:
                self.excluded_vkns.append(vkname)
            return
        # if vkname in self.excls: return #??
        if vkname not in self.dic:
            if type(node) == Noder:
                self.dic[vkname] = node
            else:
                self.dic[vkname] = Noder(self.repo, node)
        # self.dic[vkname].add_node(copy.deepcopy(node))