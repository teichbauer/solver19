from utils.basics import pd, verify_sat
from utils.knowns import GRIDSATS
from utils.noder import *


class PathBlocker:
    def __init__(self, path):
        self.path = path
        if path.classname == 'VKRepository':
            self.novs = [path.layer.nov]
        else:
            self.novs = sorted(path.lyr_dic, reverse=True)
        self.pbtree = {} # path-blocker-tree
        self.blockers = {1:[], 2:[], 3:[]}
    
    def clone(self, newrepo): # to be removed?
        inst = PathBlocker(newrepo)
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

    def trump_blocked(self, single):
        # if any existing block shorter than single,
        # is contained in single, and is hit: return T
        # ------------------------ E.G.
        # single: {54:(0) 57(1) 60(7)} and there is a shorter blocker:
        #   {57(1) 60(7)} -> return T
        leng = len(single) - 1
        while leng > 0:
            for bl in self.blockers[leng]:
                hit = True
                for nv, cv in bl.items():
                    _hit = (nv in single) and single[nv].issuperset(cv)
                    if not _hit: 
                        hit = False
                        break
                if hit: return True
            leng -= 1
        return False

    
    def blocked(self, single): # test if a single-thrd-dict-node is blockers
        return single in self.blockers[len(single)]

    def output(self):
        for lng in (1,2,3):
            if len(self.blockers[lng]) > 0:
                print(f'length: {lng}:\n')
                for abl in self.blockers[lng]:
                    print(abl)
                print('-'*80)

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
        for kn, vk2 in self.path.vk2dic.items():
            if vk2.cvs.issuperset(pthrd[vk2.nov]):
                dic[kn] = vk2
        return dic

    def verify_pth(self, pth): # pth: (7,1,4) or (2,1,5,2)
        # pth = (2,1,5,2) means, {60:2,57:1,54:5,51:2}
        plst = list(pth)    # make pth a list that is mutable
        lst1 = self.blocks[:]
        lst2 = []
        nvs = self.path.driver.steps[:]
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

def test_trump():
    abb = PathBlocker(None) # path : None
    abb.add_block(
        [{60:{7} }, 
         {60:{5}, 57:{0}}, 
         {60:{1}, 57:{0}, 54:{1}},
         {60:{1}, 57:{0}, 54:{2}},
         {60:{1}, 57:{0}, 54:{3}},
        ])
    res = abb.trump_blocked({60:{5}, 57:{0}, 54:{5,6,7}})
    print(f"res: {res}")

if __name__ == '__main__':
    test_trump()