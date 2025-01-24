from utils.basics import pd, verify_sat
from utils.cvsnodetools import *
from utils.sequencer import Sequencer
from utils.knowns import GRIDSATS
from nodemanager import NodeManager
import copy


class BlockMgr:
    def __init__(self, repo):
        self.repo = repo
        self.blockers = {1:[], 2:[], 3:[]}
    
    def clone(self, newrepo):
        inst = BlockMgr(newrepo)
        for n, lst in self.blockers.items():
            inst.blockers[n] = self.blockers[n][:]
        return inst
    
    def add_block(self, newblock):
        if type(newblock) == list:
            for blck in newblock:
                self.add_block(blck)
        elif type(newblock) == dict:
            leng = len(newblock)
            if newblock not in self.blockers[leng]:
                self.blockers[leng].append(newblock)
    
    def blocked(self, single): # test if a single-thrd-dict-node is blockers
        return single in self.blockers[len(single)]

    def test_block(self, block=None): # block==None: test all
        if block==None:
            for bl in self.block:
                res = self.test_block(bl)
        else:
            doit = Sequencer(block)
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

    # def showall(self, more_space=False):
    #     m = "blocs:\n" + "-"*80 + "\n"
    #     for i, b in enumerate(self.blocks):
    #         m += f"{i}: {pd(b, more_space)}\n"
    #     return m
