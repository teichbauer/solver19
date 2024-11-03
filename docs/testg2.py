class Seq:
    def __init__(self, lst):
        self.lst = lst
        self.ind = -1
        
    def next(self):
        self.ind += 1
        if self.ind == len(self.lst):
            self.ind = -1   # reset
            return None
        return self.lst[self.ind]
    
def test_seq(data):
    seq = Seq(data) # data : (11,22,33)
    while True:
        res = seq.next()
        if res:
            print(res)
            e = input('hit any key')
        else:
            print('Done')
            break

class SeqIter:
    def __init__(self, base):  # lst/tuple of sequences, like ((0,1,2),(5,7))
        self.base_leng = len(base)
        self.base = base
        self.seq_lengs = [len(s) for s in base]
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
        return res
        
                
def test_iter(data): # 
    siter = SeqIter(data)
    index = 1
    while not siter.done:
        val = siter.get_next()
        print(f"{index}: {val=}")
        index += 1
    print(f'DONE with {index-1} outputs.')
    
if __name__ == '__main__':
    #test_seq((11,12,13,14))
    data = (('a','b'),(22,33),(1,2,3))
    test_iter(data)
    x = 0