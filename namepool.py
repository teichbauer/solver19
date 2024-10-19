class NamePool:
    SNAMES = ['C', 'S', 'T','Q']    # Q is end-test, causing alarm
    # DNAMES = ['C','D','E','Q']
    RNAMES = ['R']              #?
    UNAMES = ['C', 'U', 'V', 'X','Q'] # 0 1 2 3 max:3
    SPOOL = []
    UPOOL = []

    def __init__(self, kname): # kname without prefix letter
        self.head = kname[0]
        self.nindex = self.UNAMES.index(self.head)
        self.tail = kname[1:]

    def next_sname(self, given=None):  # given: a gien(fixed) single letter 
        if given: 
            res = given + self.tail
        else:
            self.nindex += 1
            self.head = self.SNAMES[self.nindex]
            assert self.head != 'Q'
            res = self.head + self.tail
        self.SPOOL.append(res)
        return res

    def next_uname(self, given=None):  # given: a gien(fixed) single letter 
        if given: 
            res = given + self.tail
        else:
            self.nindex += 1
            self.head = self.UNAMES[self.nindex]
            assert self.head != 'Q'
            res = self.head + self.tail
        self.UPOOL.append(res)
        return res
    

