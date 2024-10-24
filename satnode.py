from bitgrid import BitGrid
from center import Center
from tools import sort_length_list
from collections import OrderedDict
from sat_path import SatPath
from vkrepo import VKRepoitory
from stail import STail
from namepool import NamePool

class SatNode:
    def __init__(self, parent, sh, vkm):
        self.parent = parent
        self.sh = sh
        self.vkm = vkm  # all 3vks in here
        self.Center = Center
        if parent == None:
            self.nov = Center.maxnov
            Center.root_snode = self
        else:
            self.nov = parent.nov - 3
        Center.snodes[self.nov] = self
        # choice[0]: chvals, [1]: vk3s, [2]: touchd 2 bits, [3]: touched 1 bit
        self.choice = vkm.make_choice(self.nov) # (vals, bits, t2s, t1s)
        self.bgrid = BitGrid(self)
        self.vkrepo = VKRepoitory(self)
        self.taildic = {v: STail(self, v) for v in self.choice[0] }
        self.make_taildic()  # make taildic
        Center.slice(self)
        self.next = None
        self.next_sh = self.sh.reduce(self.bgrid.bits)
        if Center.logging:
            self.logfile = open("logfile.txt",'a')
        else:
            self.logfile = None

    def make_taildic(self):
        # all vk(kn) touching 1, or 2 bit o f snode's root
        for kn in self.choice[2] + self.choice[3]: 
            if kn in self.vkm.vkdic:
                vk = self.vkm.pop_vk(kn)
                vk.nov = self.nov
                vk12 = self.bgrid.reduce_vk(vk)
                if vk12.nob == 1:  # touched 2 bits, vk12 is vk1: C0212->S0212
                    vk12.kname = NamePool(vk.kname).next_sname()
                    self.vkrepo.add_vk1(vk12)
                else:
                    self.vkrepo.add_vk2(vk12)
        for vk2 in self.vkrepo.vk2dic.values():
            for cv in vk2.cvs:
                self.taildic[cv].add_vk(vk2)
        for k1n in self.vkrepo.k1ns:
            vk1 = self.Center.vk1dic[k1n]
            for cv in vk1.cvs:
                self.taildic[cv].add_vk(vk1)
        x = 0

    def spawn(self):
        if len(self.vkm.vkdic) > 0:  # there exist vk3 in vkm.vkdic, make next
            self.next = SatNode(self, self.next_sh.clone(), self.vkm)
            return self.next.spawn()
        else:  # when there is no more vk3
            Center.last_nov = self.nov
            Center.sat_pool = [] # list of sat-path(dics)
            print(f"NOV:{self.nov}")
            pathrepo = Center.snodes[60].vkrepo.clone()
            pathrepo.merge_snode(Center.snodes[57])
            # pathrepo.write_logmsg('./logs/loginfo.txt')
            pathrepo.merge_snode(Center.snodes[54])
            pathrepo.write_logmsg('./logs/loginfo.txt')
            x = 9

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
                        sat_path = SatPath(psname, psat, base_nov+3, self.logfile)
                        if sat_path.grow(final_path):
                            self.logfile.close()
                            y = 9
                        else:
                            # print(f"jumping over {psname}")
                            if Center.logging:
                                msg = f"jumping over {psname}\n"
                                self.logfile.write(msg)
                            continue
                else:
                    # print(f"NOV:{self.parent.nov}")
                    self.parent.grow_path(base_nov, final_path, hpath)

    def local_sats(self, csatdic={}, pname="",chv_filter=None):
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
            if chv_filter and chv not in chv_filter:
                continue
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
        # print(f"{pn} has {nosats} sats")
        result.append(tuple(path_base.keys()))
        sats = []
        for spairs in path_base.values():
            for pair in spairs:
                pn = f"{nosats}-"+str(len(sats)+1)
                name = f"{pair[1]}[{pn}]"
                sats.append((pair[0],name))
        result.append(sats)
        return result
    # end of def local_sats(self):

    def bk_index(self, chval):
        for bk_ind, bkval in enumerate(self.bkdic.values()):
            if chval in bkval:
                return bk_ind
        return -1

    def tail_bits(self, incl_root=False):
        print(f'my nov: {self.nov}')
        bits = set(self.vkrepo.bdic2)
        if incl_root:
            bits.update(self.bgrid.bits)
        return bits

    def print_vk2dic(self):
        for vk in self.vkrepo.vk2dic.values():
            print(vk.print_msg())
