from vklause import VKlause
from bitgrid import BitGrid
from center import Center
# from sat2 import Sat2
from basics import display_vkdic, ordered_dic_string, verify_sat
from stail import sat_conflict, sort_length_list
from collections import OrderedDict


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
        if len(self.vkm.vkdic) > 0:
            # as long as there exist vk3 in vkm.vkdic, make next
            self.next = SatNode(self, self.next_sh.clone(), self.vkm)
            return self.next.spawn()
        else:
            # when there is no more vk3
            Center.last_nov = self.nov
            Center.sat_pool = [] # list of sat-path(dics)
            print(f"NOV:{self.nov}")
            self.grow_path()

    def grow_path(self, final_path=[], base_path=None):
        if not base_path:
            base_path = self.local_sats()
        while len(base_path) > 0:
            base_kys, bsat_pairs = base_path.popitem()
            leng = len(bsat_pairs)
            print(f"{self.nov}-bkey: {base_kys} with {leng} pairs")
            n = 0
            for satpair in bsat_pairs:
                n += 1
                sats, sname = satpair
                print(f"{self.parent.nov} trial on {sname}-{n}/{leng}")
                hpath = self.parent.local_sats(sats, sname)
                leng1 = len(hpath)
                if leng1 == 0:
                    print(f"no path up here")
                    continue
                print(f"{sname}-{n}/{leng}-{self.parent.nov} has {leng1} bkys")
                if self.parent.nov == 60:
                    xx = 9
                elif len(hpath) > 0:
                    if self.parent.nov == 33:
                        res = self.parent.filter_conflict(sats)
                        yy = 0
                    print(f"NOV:{self.parent.nov}")
                    self.parent.grow_path(final_path, hpath)
                else:
                    print(f"{sname} stops here")

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
        nosats = 0
        for chv, tail in self.taildic.items():
            tail_sats = tail.start_sats(csatdic)
            # nosats += len(tail_sats)
            if not tail_sats:
                # print(f"{pname} has not path up")
                continue
            for tail_sat in tail_sats:
                nosats += 1
                bits = list(tail_sat.keys())
                bits.sort()
                bitstp = tuple(bits)
                bkeys.append(bitstp)
                if not pname:
                    pn = f"{self.nov}.{chv}"
                else:
                    pn = pname + f"+{self.nov}.{chv}"
                dic.setdefault(bitstp,[]).append((tail_sat, pn))
        bks = sort_length_list(bkeys) # sort -> [(.),(..),(...),...]
        for bk in bks:
            path_base[bk] = dic[bk]
        print(f"{self.nov} has {nosats} sats")
        return path_base
    # end of def local_sats(self):

    def filter_conflict(self, satdic):
        excl_chvs = set([])
        for bit, vdic in self.satdic.items():
            if bit in satdic:
                for v, cvs in vdic.items():
                    if v != satdic[bit]:
                        excl_chvs.update(cvs)
        for vk in self.vk2dic.values():
            if vk.hit(satdic):
                print(f"vk {vk.kname} hit with {vk.cvs}")
                excl_chvs.update(vk.cvs)
        return excl_chvs


    def tail_bits(self, incl_root=False):
        print(f'my nov: {self.nov}')
        bits = set(self.bdic)
        bits.update(self.satdic)
        if incl_root:
            bits.update(self.bgrid.bits)
        return bits

    def show_path_sats(self, psats):
        m = ''
        for chv, sats in psats.items():
            m += str(chv) + ': \n'
            for sat in sats:
                lst = list(sat.keys())
                lst.sort(reverse=True)
                m += '    ' + ordered_dic_string(sat)[0] + '\t' + str(lst) + '\n'
            m += '\n'
        return m

    def add_sat(self, bit, val, cv, satdic=None):
        if not satdic:
            satdic = self.satdic
        sat_info = satdic.setdefault(bit, {})
        cvs = sat_info.setdefault(val, [])
        if cv not in cvs:
            cvs.append(cv)

