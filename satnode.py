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
        self.taildic = vkm.make_taildic(self)  # 
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
            # self.grow_sats()
            self.grow_path()

            # dic33 = Center.snodes[33].local_sats()
            # dic36 = Center.snodes[36].local_sats()
            x = 1
    def grow_path(self, final_path=[], base_path=None):
        if not base_path:
            base_path = self.local_sats()
        while len(base_path) > 0:
            base_kys, bsat_pairs = base_path.popitem()
            for satpair in bsat_pairs:
                sats, sname = satpair
                hpath = self.parent.local_sats(sats, sname)
                if not hpath:
                    continue
                # fkys, fsat_pairs = hpath.popitem()
                if self.parent.nov == 60:
                    xx = 9
                    # for fsat in fsat_pairs:
                    #     final_path.append(fsat)
                else:
                    self.parent.grow_path(final_path, hpath)
                    xx = 9

    def grow_sats(self, lpath_base=None):
        if not lpath_base:
            lpath_base = self.local_sats()
        hpath_base = self.parent.local_sats()
        # newpath = []
        pathdic = {}
        cflct_cnt = 0
        sat_cnt = 0
        while len(lpath_base) > 0:
            lbky, lst = lpath_base.popitem()
            hbase = hpath_base.copy()
            while len(hbase) > 0:
                hbky, hst = hbase.popitem()
                for lsat, lntp in lst:
                    for hsat, hntp in hst:
                        if sat_conflict(lsat, hsat):
                            cflct_cnt += 1
                            # print(f"{lntp} and {hntp} have conflict")
                        else:
                            pn = f"{lntp}+{hntp}"
                            sat_cnt += 1
                            nsat = lsat.copy()
                            nsat.update(hsat)
                            Center.all_conflict((nsat, pn), self.parent.nov + 3)
                            bits = list(nsat.keys())
                            bits.sort()
                            pathdic\
                                .setdefault(tuple(bits),[])\
                                .append((nsat, pn))
                    xx = 7
                xx = 6
            xx = 5
        print(f"conflict-cont: {cflct_cnt}, nof-sat: {sat_cnt}")
        tkys = list(pathdic.keys())
        kys = sort_length_list(tkys)
        path_base = OrderedDict()
        for k in kys:
            path_base[k] = pathdic[k]
        if self.parent.nov < 60:
            self.parent.grow_sats(path_base)
        return 


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

    def filter_conflict(self, sat_name_pair):
        lsat, sname = sat_name_pair
        # lsatbits = set(lsat)
        # overlbits = lsatbits.intersection(self.tail_bits())
        print(f"search {sname} on {self.nov}")
        # valid_sats = []
        local_sats = self.local_sats(lsat,sname)
        # local_sats = self.local_sats()
        # while len(local_sats) > 0:
        #     lbks, sats = local_sats.popitem()
        #     # bs = sat_bits.intersection(lbks)
        #     for s in sats:
        #         if not sat_conflict(s[0], lsat):
        #             pn = f"{sname}+{s[1]}"
        #             ss = s[0].copy()
        #             ss.update(sat_name_pair[0])
        #             valid_sats.append((ss, pn))
        #         else:
        #             print(f"{sname}+{s[1]} in conflict")
        #     x = 9
        # return valid_sats
        return local_sats

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

