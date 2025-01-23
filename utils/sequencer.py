def pthrd_in_node(pt, node):
    for nv, cv in pt.items():
        if not cv.issubset(node[nv]):
            return False
    return True
    
def pt_in_nodes(pt, nodes, not_contained_pts):
    nds = nodes[:]
    notin = True
    while len(nds) > 0 and notin:
        nd = nds.pop()
        notin = not pthrd_in_node(pt, nd)
    if notin: not_contained_pts.append(pt)

def itor(lst):
    for ind, e in enumerate(lst): yield e

class ItorHost:
    def __init__(self, lst, index, auto_reset=True):
        self.lst = lst
        self.index = index
        self.auto_reset = auto_reset
        self.reset()
    
    def reset(self, done=None):
        self.done = done
        self.itr = itor(self.lst)
        self.curr_val = next(self.itr)

    def get_next(self):
        result = self.curr_val
        try:
            self.curr_val = next(self.itr)
        except StopIteration:
            if self.auto_reset:  self.reset('reset')
            else:                self.done = "done"
        return result

class Sequencer:
    ''' 
    node : {60: {1, 2, 3}, 57: {0, 1}, 54: {1, 5, 7}}, output 18 path-threads:
    -------------------------------
     1: {60: {1}, 57: {0}, 54: {1}}
     2: {60: {1}, 57: {0}, 54: {5}}
     3: {60: {1}, 57: {0}, 54: {7}}
     4: {60: {1}, 57: {1}, 54: {1}}
     5: {60: {1}, 57: {1}, 54: {5}}
     6: {60: {1}, 57: {1}, 54: {7}}
     7: {60: {2}, 57: {0}, 54: {1}}
     8: {60: {2}, 57: {0}, 54: {5}}
     9: {60: {2}, 57: {0}, 54: {7}}
    10: {60: {2}, 57: {1}, 54: {1}}
    11: {60: {2}, 57: {1}, 54: {5}}
    12: {60: {2}, 57: {1}, 54: {7}}
    13: {60: {3}, 57: {0}, 54: {1}}
    14: {60: {3}, 57: {0}, 54: {5}}
    15: {60: {3}, 57: {0}, 54: {7}}
    16: {60: {3}, 57: {1}, 54: {1}}
    17: {60: {3}, 57: {1}, 54: {5}}
    18: {60: {3}, 57: {1}, 54: {7}}
    '''
    def __init__(self, node): # node: {60:{1,2,3,4}, 57:(0,1), 54:{2,3},51:{0}}
        self.node = node
        self.nvs = sorted(node, reverse=True) # [60,57,54,51]
        # self.base: [[1,2,3,4],[0,1],[2,3],[0]]
        self.base = tuple([tuple(sorted(node[nv])) for nv in self.nvs])
        self.leng = len(self.nvs)
        self.reset()

    def reset(self): # after reset, iterator will start from the first pthrd
        self.done = False
        self.itrs = []
        for ind, lst in enumerate(self.base):
            if ind == 0:
                self.itrs.append(ItorHost(lst, ind, False))
            else:
                self.itrs.append(ItorHost(lst, ind))

    def get_next(self): # yield/iterate all pthrds possible
        res = {}        # a single pthrd, like: {60:{2}, 57:{1}, 54:{5}}
        for ind, nv in enumerate(self.nvs):
            res.setdefault(nv, set()).add(self.itrs[ind].curr_val)
            # res.append(self.itrs[ind].curr_val)
        it = self.itrs[ind]
        while True:
            it.get_next()
            if it.done == 'reset':
                it.done = None
                it = self.itrs[it.index - 1]
            elif it.done == 'done':
                self.done = True
                break
            else: break
        return res

    def serialize_2_singles(self):
        outputs = []
        while not self.done:
            outputs.append(self.get_next())
        return outputs

def test_serialize_2_singles(data):
    sq = Sequencer(data)
    result = sq.serialize_2_singles()
    for ind, e in enumerate(result):
        print(f"{ind}: {e}")

def test(data):
    print(f"{data = }\n" + '-'*80)
    sq = Sequencer(data)
    count = 0
    while not sq.done:
        count += 1
        # f"{count:>2}" - right-align occupy 2 spaces. < would be left-align
        print(f"{count:>4}: {sq.get_next()}")
    print('-'*80)
    sq.reset()
    print(f"{data = }\n" + '-'*80)
    # ---- testing reset
    sq = Sequencer(data)
    count = 0
    while not sq.done:
        count += 1
        # f"{count:>2}" - right-align occupy 2 spaces. < would be left-align
        print(f"{count:>4}: {sq.get_next()}")
    print('-'*80)

if __name__ == '__main__':
    data = { 60:{1,2,3}, 57:{0,21}, 54:{1,5,7} }
    test_serialize_2_singles(data)


    # test(data)
    ### output:
    #
    # data = {60: {1, 2, 3}, 57: {0}, 54: {1, 5, 7}}
    # ---------------------------------------------------------------------------
    # 1: {60: {1}, 57: {0}, 54: {1}}
    # 2: {60: {1}, 57: {0}, 54: {5}}
    # 3: {60: {1}, 57: {0}, 54: {7}}
    # 4: {60: {2}, 57: {0}, 54: {1}}
    # 5: {60: {2}, 57: {0}, 54: {5}}
    # 6: {60: {2}, 57: {0}, 54: {7}}
    # 7: {60: {3}, 57: {0}, 54: {1}}
    # 8: {60: {3}, 57: {0}, 54: {5}}
    # 9: {60: {3}, 57: {0}, 54: {7}}
    # --------------------------------------------------------------------------
    #
    ###  testing reset:
    #
    # data = {60: {1, 2, 3}, 57: {0}, 54: {1, 5, 7}}
    # --------------------------------------------------------------------------
    # 1: {60: {1}, 57: {0}, 54: {1}}
    # 2: {60: {1}, 57: {0}, 54: {5}}
    # 3: {60: {1}, 57: {0}, 54: {7}}
    # 4: {60: {2}, 57: {0}, 54: {1}}
    # 5: {60: {2}, 57: {0}, 54: {5}}
    # 6: {60: {2}, 57: {0}, 54: {7}}
    # 7: {60: {3}, 57: {0}, 54: {1}}
    # 8: {60: {3}, 57: {0}, 54: {5}}
    # 9: {60: {3}, 57: {0}, 54: {7}}
    # --------------------------------------------------------------------------


