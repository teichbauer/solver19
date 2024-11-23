from utils.basics import pd, verify_sat
from utils.cvsnodetools import *
from utils.sequencer import Sequencer
from utils.knowns import GRIDSATS
import copy


class BlockMgr:
    def __init__(self, repo):
        self.repo = repo
        self.blocks = []

    def clone(self, new_repo):
        newinst = BlockMgr(new_repo)
        newinst.blocks = [copy.deepcopy(node) for node in self.blocks]
        return newinst
    
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
        if len(self.blocks) == 0:
            # self.test_block(newblock)
            self.blocks.append(newblock)
            return True
        index = 0
        while index < len(self.blocks):
            b = self.blocks[index]
            res = self.block_contain(b, newblock)
            if res != 0:
                if res == 1: return False # block is contained in b
                if res == -1:  # newblock over-writes/replace
                    del self.blocks[index]
                    continue # no need to increase ind
            index += 1
        # self.blocks.append(newblock)
        self.putin(newblock)
        return True


    def block_contain(self, super, sub):
        if node1_C_node2(super, sub, self.repo.steps): 
            return 1    # super contains sub
        if node1_C_node2(sub, super, self.repo.steps): 
            return -1   # sub contains super
        return 0

    def putin(self, newblck):
        seq = Sequencer(newblck)
        # all pthrds not contained in self.blocks
        rests = seq.reduce_from_iter(self.blocks, [])
        for pt in rests:
            self.blocks.append(pt)
        x = 9

    def test_pthrd(self, pthrd):
        pass
        # bbsat = self.bbmgr.collect_sat(pthrd)
        # sat = copy.deecopy(bbsat)
        # vk2dic = self.collect_vk2dic(pthrd)
        # for nv, cv in pthrd.items():
        #     sat.update(GRIDSATS[nv][tuple(cv)[0]])
        # return verify_sat(vk2dic, sat)
    
    def test_block(self, block=None): # block==None: test all
        if block==None:
            for bl in self.block:
                res = self.test_block(bl)
        else:
            doit = node_seq(block)
            if doit == True: # block is a single
                if self.test_pthrd(block):
                    print(f"{block} passed.")
                else:
                    print(f"{block} failed.")
            else:
                print(f"breaking {block} and test them:")
                while not doit.done:
                    self.test_block(doit.get_next())

    def collect_vk2dic(self, pthrd):
        dic = {}
        for kn, vk2 in self.repo.vk2dic.items():
            if vk2.cvs.issuperset(pthrd[vk2.nov]):
                dic[kn] = vk2
        return dic

    def showall(self, more_space=False):
        m = "blocs:\n" + "-"*80 + "\n"
        for i, b in enumerate(self.blocks):
            m += f"{i}: {pd(b, more_space)}\n"
        return m
