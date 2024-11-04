
class PathSequence:
    def __init__(self, path_dict):
        # path_dict: {60:{2,3,4}, 57:{0,1}, 54:(1,2,3)}
        self.nvs = sorted(path_dict, reverse=True) # get list of nov in descending order
        self.base = [sorted(path_dict[nv])  for nv in self.nvs]
        self.base_leng = len(self.base)
        self.seq_lengs = [len(cvs) for cvs in self.base]
        self.reset()
        
    def reset(self):
        self.sinds = [0 for x in range(len(self.base))] # index for each
        self.lsnd = self.base_leng - 1 # last-index
        # self.base_index = 
        self.done = False
        
    def increase_seq_index(self):
        self.sinds[self.lsnd] += 1
        reset_last = False
        while self.sinds[self.lsnd] == self.seq_lengs[self.lsnd]: # overflow
            self.lsnd -= 1
            self.sinds[self.lsnd] += 1
            reset_last = True

        if self.lsnd < 0: 
            self.done = True
            return

        li = self.lsnd + 1
        while li < self.base_leng:
            # reset index to 0 for all si in [si..base_leng)
            self.sinds[li] = 0
            li += 1
        if reset_last:
            self.lsnd = self.base_leng - 1 # last-index
        
    def get_next(self):
        res = [self.base[i][self.sinds[i]] for i in range(self.base_leng)]
        self.increase_seq_index()
        res_dic = { self.nvs[ind]:cvs for ind, cvs in enumerate(res)}
        return res_dic


def test_PSequence(data): 
    # data = {64:set([2,3]), 57:set([0,1,5]), 54:set([2,3]) }
    pseq = PathSequence(data)
    index = 0
    while not pseq.done:
        val = pseq.get_next()
        index += 1
        print(f"{index}: {val}")
    print(f"Done with {index} output")

if __name__ == '__main__':
    data = {64:set([2,3]), 57:set([0,1,5]), 54:set([2,3]) }
    print(f"{data=}")
    test_PSequence(data)
    x = 0
