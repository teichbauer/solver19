from center import Center
from tools import filter_conflict

class SatPath:
    def __init__(self, name, sat, nov):
        self.snds = [Center.snodes[n] for n in range(nov, 61, 3)]
        self.name = name
        self.sat = sat
        self.nov = nov
        self.schvs = {}

    def check(self):
        for snode in self.snds:
            res = filter_conflict(snode, self.sat)
            rvs = set(snode.bgrid.chvals).difference(res)
            # print(f"{snode.nov} excluds: {res}")
            if len(rvs) == 0:
                print(f"{snode.nov} blocked")
                return False
            else:
                self.schvs[snode.nov] = rvs
        return True
    
    def grow(self, sats):
        if self.check():
            snode = Center.snodes[self.nov]
            new_path = snode.local_sats(self.sat, self.name)
            return True
        # new_path = SatPath("name", self.sat, self.nov+3)
        else:
            return False

