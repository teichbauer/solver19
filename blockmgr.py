from basics import pd
from tools import fill_dict
import copy

class BlockMgr:
    def __init__(self, repo):
        self.repo = repo
        self.blocks = []

    def clone(self):
        newinst = BlockMgr()
        newinst.blocks = [copy.deepcopy(node) for node in self.blocks]
        return newinst
    
    def expand(self):
        for ind in range(len(self.blocks)):
            fill_dict(self.repo.driver.chvdic, self.blocks[ind])

    def verify_pth(self, pth): # pth: (7,1,4) or (2,1,5,2)
        # pth = (2,1,5,2) means, {60:2,57:1,54:5,51:2}
        plst = list(pth)    # make pth a list that is mutable
        lst1 = self.blocks[:]
        lst2 = []
        nvs = self.repo.driver.steps[:]
        assert(len(pth) == len(nvs)), f"path {pth} not complete."
        while len(nvs) > 0:
            nv = nvs.pop(0)  # get highst nov out
            # collect b in blocks with pth[0] in b[60]
            pv = plst.pop(0)
            for b in lst1:
                if pv in b[nv]:
                    lst2.append(b)
            # if no block with b[60] contain pth[0], 
            # no hit possible: pth is verified
            if len(lst2) == 0: return True
            lst1 = lst2
            lst2 = []
        return False # there is (at least) one block that contains pth: blocked
    
    def add_block(self, newblock):
        for ind, b in enumerate(self.blocks):
            res = self.block_conain(b, newblock)
            if res == 1:        # block is contained in b
                return False
            if res == -1:
                self.blocks[ind] = newblock
                return None
        self.blocks.append(newblock)
        return True

    def block_conain(self, super, sub):
        # contain means, for every nv in super, 
        # super[nv] is superset of sub[nov], if true: return 1
        # if for any nov, this is not true:
        #   test if for super <-> sub, this be true: return -1
        # if neither of the two is a superset of the other, return 0
        for nv in super:
            if not super.issuperset(sub[nv]): 
                if self.block_conain(sub, super):
                    return -1
                return 0
        return 1
    
    def showall(self, more_space=False):
        m = "blocs:\n" + "-"*80 + "\n"
        for i, b in enumerate(self.blocks):
            m += f"{i}: {pd(b, more_space)}\n"
        return m
