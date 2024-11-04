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
            if self.auto_reset:
                self.reset('reset')
            else:
                self.done = "done"
        return result

class Sequencer:
    def __init__(self, base): # base is list of lst
        self.base = base
        self.base_leng = len(base)
        self.itrs = []
        self.done = False
        for ind, lst in enumerate(base):
            if ind == 0:
                self.itrs.append(ItorHost(lst, ind, False))
            else:
                self.itrs.append(ItorHost(lst, ind))

    def get_next(self):
        res = []
        for ind in range(self.base_leng):
            res.append(self.itrs[ind].curr_val)
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
            
def test(data):
    sq = Sequencer(data)
    count = 0
    while not sq.done:
        count += 1
        # {count:>2} right-align occupy 2 spaces. < would be left-align
        print(f"{count:>2}: {sq.get_next()}") 
    print(f'DONE. {count=}')

if __name__ == '__main__':
    test(((1,2,3),(11,22,33),(111,222,333)))
    x = 1



