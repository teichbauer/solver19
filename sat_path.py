from center import Center
from utils.tools import filter_conflict

class SatPath:
    def __init__(self, name, sat, nov,logfile=None):
        self.snds = [Center.snodes[n] for n in range(nov, 61, 3)]
        self.name = name
        self.sat = sat
        self.nov = nov
        self.schvs = {}
        self.logfile = logfile

    def check(self):
        for snode in self.snds:
            if snode.nov == 39:
                x = 0
            res = filter_conflict(snode, self.sat)
            rvs = set(snode.bgrid.chvals).difference(res)
            # print(f"{snode.nov} excluds: {res}")
            if len(rvs) == 0:
                # print(f"{snode.nov} blocked")
                if Center.logging:
                    msg = f"{snode.nov} blocked\n"
                    self.logfile.write(msg)
                # ver = Center.sat_failed(self.sat, snode.nov)
                return False
            else:
                self.schvs[snode.nov] = rvs
        return True
    
    def grow(self, final_sats):
        if self.check():
            snode = Center.snodes[self.nov]
            new_path = snode.local_sats(
                self.sat, 
                self.name, 
                self.schvs[snode.nov])
            if len(new_path[1]) == 0:
                return False
            elif self.nov == 60:
                _, pairs = new_path
                leng = len(pairs)
                print(f"found {leng} sats!")
                for ind, pair in enumerate(pairs):
                    final_sats.append(pair)
                    print(f"{ind}-th sat: {pair}")
                return True
            else:
                _, pairs = new_path
                while len(pairs) > 0:
                    sat, sname = pairs.pop()
                    n_path = SatPath(sname, sat, self.nov + 3, self.logfile)
                    if n_path.grow(final_sats):
                        y = 8
                    else:
                        continue
                else:
                    return False
        # new_path = SatPath("name", self.sat, self.nov+3)
        else:
            return False

