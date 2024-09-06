from bitgrid import BitGrid
from center import Center
from tools import *
from collections import OrderedDict
from sat_path import SatPath

class SatNode:
    def __init__(self, parent, sh, vkm):
        self.parent = parent
        self.sh = sh
        self.vkm = vkm  # all 3vks in here
        self.repo = Center
        if parent == None:
            self.nov = Center.maxnov
            Center.root_snode = self
        else:
            self.nov = parent.nov - 3
        self.choice = vkm.make_choice() # (vals, bits, t2s, t1s)
        self.vk2dic = {}    # vk2s in all tails
        self.bdic = {}      # bit-dic for all vk2s in vk2dic
        self.satdic = {} # {<bit>:[<val>,[cv1,cv2,..]]}
        self.bgrid = BitGrid(self)
        vkm.make_taildic(self)  # make self.taildic, self.bkdic
        Center.snodes[self.nov] = self
        self.next = None
        self.next_sh = self.sh.reduce(self.bgrid.bits)

    def spawn(self):
        if len(self.vkm.vkdic) > 0:  # there exist vk3 in vkm.vkdic, make next
            self.next = SatNode(self, self.next_sh.clone(), self.vkm)
            return self.next.spawn()
        else:  # when there is no more vk3
            Center.last_nov = self.nov
            Center.sat_pool = [] # list of sat-path(dics)
            print(f"NOV:{self.nov}")
            self.grow_path(27)

    def grow_path(self, base_nov, final_path=[], base_path=None):
        if self.parent.nov == 60:
            xx = 9
        if not base_path:
            base_path = self.local_sats()
        base_kys, bsat_pairs = base_path
        while len(bsat_pairs) > 0:
            satpair = bsat_pairs.pop() # get the last, which is the longest
            sats, sname = satpair
            hpath = self.parent.local_sats(sats, sname)
            leng1 = len(hpath[1]) # number of sats
            if leng1 == 0:
                print(f"no path up here")
                continue
            else:
                if self.parent.nov >= base_nov:
                    bky, pairs = hpath
                    while len(pairs) > 0:
                        ppair = pairs.pop()
                        psat, psname = ppair
                        sat_path = SatPath(psname, psat, base_nov+3)
                        if sat_path.grow(final_path):
                            y = 9
                        else:
                            print(f"jumping over {psname}")
                            continue
                else:
                    print(f"NOV:{self.parent.nov}")
                    self.parent.grow_path(base_nov, final_path, hpath)

    def local_sats(self, csatdic={}, pname=""):
        '''
        # returns a path_base, that is an OrderedDict:
        #  {<bkey>:[ele1,ele2,..], <bkey>:[e1,e2]}, where
        # ele: ({sat},(nov,chv)).
        # in this ordered-dict, bkeys are ordered: longer one behind,
        # so that, path_base.popitem() will pop out the longest (bkey,ele)
        # ------------------------------------------------------
        # a b-key is a bit-tuple; sat-bits sorted into a tuple
        # ------------------------------------------------------
        '''
        bkeys = [] # dic-keys: all tuples
        dic = {}   # un-sorted dict
        path_base = OrderedDict()
        # [{k0, k1), [(),(),(<pair>),..]}], where 
        # <pair>: ({<sat>}, "<name")
        result = [] 
        nosats = 0
        for chv, tail in self.taildic.items():
            tail_sats = tail.start_sats(csatdic)
            # nosats += len(tail_sats)
            if not tail_sats:
                # print(f"{pname} has not path up")
                continue
            tslng = len(tail_sats)
            for sind, tail_sat in enumerate(tail_sats):
                nosats += 1
                bits = list(tail_sat.keys())
                bits.sort()
                bitstp = tuple(bits)
                bkeys.append(bitstp)
                kindx = self.bk_index(chv)
                pnx = f"{self.nov}.{chv}.k{kindx}-{tslng}:{sind+1}"
                if not pname:
                    pn = pnx
                else:
                    pn = f"{pname}+{pnx}"
                dic.setdefault(bitstp,[]).append((tail_sat, pn))
        bks = sort_length_list(bkeys) # sort -> [(.),(..),(...),...]
        for bk in bks:
            path_base[bk] = dic[bk]
        print(f"{pn}-{self.nov} has {nosats} sats")
        result.append(tuple(path_base.keys()))
        sats = []
        for spairs in path_base.values():
            for pair in spairs:
                sats.append(pair)
        result.append(sats)
        # result.append(tuple(path_base.values()))
        # return path_base
        return result
    # end of def local_sats(self):

    def bk_index(self, chval):
        for bk_ind, bkval in enumerate(self.bkdic.values()):
            if chval in bkval:
                return bk_ind
        return -1

    def tail_bits(self, incl_root=False):
        print(f'my nov: {self.nov}')
        bits = set(self.bdic)
        bits.update(self.satdic)
        if incl_root:
            bits.update(self.bgrid.bits)
        return bits

    def add_sat(self, bit, val, cv, satdic=None):
        if not satdic:
            satdic = self.satdic
        sat_info = satdic.setdefault(bit, {})
        cvs = sat_info.setdefault(val, [])
        if cv not in cvs:
            cvs.append(cv)

