from utils.basics import pd, verify_sat
from utils.noder import Noder
from utils.sequencer import Sequencer

class PathBlocker:
    def __init__(self, path):
        self.path = path
        self.blockers = {}
    
    def clone(self, newrepo): # to be removed?
        inst = PathBlocker(newrepo)
        for n, lst in self.blockers.items():
            inst.blockers[n] = self.blockers[n][:]
        return inst
    
    def add_single(self, single_block, leng):
        lind = 1
        while lind <= leng:
            if lind in self.blockers:
                if lind < leng:
                    if self.blockers[lind].containing_single(single_block):
                        return False
                else: # lind == leng, and self.blockers has leng in it
                    if self.blockers[lind].add_node(single_block):
                        updated = self.filter_bb(single_block)
                        return True
            elif lind == leng: # leng was not in - here is first
                # create new Noder inst, add it in
                self.blockers[leng] = Noder(self.path, [single_block])
                updated = self.filter_bb(single_block)
                return True
            lind += 1

    def filter_bb(self, single_pb):
        modified = False
        # loop thru every bblock-noder in self.path.bbpool
        # kick out nodes covered by this single=pblock
        for bb in self.path.bbpool.values():
            if bb.noder.containing_single(single_pb):
                modified = bb.subtract_singles([single_pb]) or modified
            else:
                x = 9
        return modified

    def add_block(self, newblock, leng=None): # leng only if newblock is dict
        added = False
        if type(newblock) == list:
            for blck in newblock:
                added = self.add_block(blck, len(blck)) or added
        elif type(newblock) == dict:
            if Noder.is_single(newblock):
                added = self.add_single(newblock, leng) or added
            else:
                sq = Sequencer(newblock)
                while not sq.done:
                    added = self.add_block(sq.get_next(), leng) or added
            return added
    
    def single_blocked(self, single): 
        # test if a single-thrd-dict-node is blocked
        ind = 1
        while ind <= len(single):
            if ind in self.blockers and \
                self.blockers[ind].containing_single(single):
                return True
            else: 
                ind += 1
        return False

    def output(self):
        print(f"All path-blockers:")
        for lng in self.blockers:
            print(f"Length: {lng}:")
            self.blockers[lng].output()

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

if __name__ == '__main__':
    test_trump()