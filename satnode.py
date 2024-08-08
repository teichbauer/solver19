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
            self.grow_sats()
            # dic18, nos18 = Center.snodes[18].local_sats()
            # dic21, nos21 = Center.snodes[21].local_sats()
            # dic24, nos24 = Center.snodes[24].local_sats()
            # dic, nos = Center.snodes[27].local_sats()
            x = 1

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


    def local_sats(self):
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
            tail_sats = tail.start_sats()
            nosats += len(tail_sats)
            for tail_sat in tail_sats:
                bits = list(tail_sat.keys())
                bits.sort()
                bitstp = tuple(bits)
                bkeys.append(bitstp)
                # put into un-sorted dic
                dic.setdefault(bitstp,[])\
                   .append((tail_sat, f"{self.nov}.{chv}"))
        bks = sort_length_list(bkeys) # sort -> [(.),(..),(...),...]
        for bk in bks:
            path_base[bk] = dic[bk]
        print(f"{self.nov} has {nosats} sats")
        return path_base


    def find_pathbase(self, sat2add):
        pathbase = {} # {chv: [new_sats],...}
        bitsdic = {} # {(bit-tuple):[tail-sat,...]}
        for chv, tail in self.taildic.items():
            satlst = tail.start_sats()
            for sindex, sat in enumerate(satlst):
                if not sat_conflict(sat2add, sat):
                    ss = sat2add.copy()
                    ss.update(sat)
                    bits = list(ss.keys())
                    bits.sort()
                    bitsdic.setdefault(tuple(bits),[]).append((chv, sindex))
                    pathbase.setdefault(chv,[]).append(ss)
        # msg = self.show_path_sats(new_paths)        # print(msg)
        bkeys = []
        for k in bitsdic.keys():
            index = -1
            for ind, x in enumerate(bkeys):
                if len(k) > len(x):
                    index = ind
                    break
            if index > -1:
                bkeys.insert(index, k)
            else:
                bkeys.append(k)
        self.parent.grow_path(bkeys, bitsdic, pathbase,)

    def grow_path(self, bitkeys, bitsdic, pathbase):
        new_path = {}
        # bkeys = bitkeys.copy()
        # bkey = bkeys.pop(0)
        lchv, lsats = pathbase.popitem()
        for chv, tail in self.taildic.items():
            chvsats = new_path.setdefault(chv, [])
            satlst = tail.start_sats()
            for mysat in satlst:
                for lsat in lsats:
                    if not sat_conflict(lsat, mysat):
                        xsat = mysat.copy()
                        xsat.update(lsat)
                        chvsats.append(xsat)
        if self.parent:
            total = sum(len(lst) for lst in new_path.values())
            if  total > 0:
                self.parent.grow_path(None, None, new_path)
            else:
                return False
        else:
            xx = 9
            return True

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

