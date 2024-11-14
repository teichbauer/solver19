from utils.bitgrid import BitGrid
from center import Center
from utils.tools import sort_length_list
from collections import OrderedDict
from sat_path import SatPath
from vkrepo import VKRepoitory
from utils.stail import STail
from utils.namedrive import NameDrive
from pathfinder import PathFinder

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
        self.repo = VKRepoitory({self.nov:self})
        self.fill_repo()
        Center.slice(self)
        self.next = None
        self.next_sh = self.sh.reduce(self.bgrid.bits)
        if Center.logging:
            self.logfile = open("logfile.txt",'a')
        else:
            self.logfile = None

    def fill_repo(self):
        repo = self.repo
        for kn in self.choice[2] + self.choice[3]: 
            if kn in self.vkm.vkdic:
                vk = self.vkm.pop_vk(kn)
                vk.nov = self.nov
                vk12 = self.bgrid.reduce_vk(vk)
                if vk12.nob == 1:
                    repo.add_bblocker(vk12.bit, vk12.val, 
                                     {self.nov: vk12.cvs},
                                     [f"from {vk12.kname}"])
                else:
                    repo.insert_vk2(vk12)
                    repo.proc_vk2pair(vk12)
        bit12 = sorted(set(repo.bdic1).intersection(repo.bdic2))
        repo.filter_vk2s(bit12) # process vk2s touching bit-blockers

    def spawn(self):
        if len(self.vkm.vkdic) > 0:  # there exist vk3 in vkm.vkdic, make next
            self.next = SatNode(self, self.next_sh.clone(), self.vkm)
            return self.next.spawn()
        else:  # when there is no more vk3
            Center.last_nov = self.nov
            Center.sat_pool = [] # list of sat-path(dics)
            print(f"NOV:{self.nov}")
            pathfinder = PathFinder(Center.snodes[60])
            # pathrepo = Center.snodes[60].repo.clone()
            pathfinder.grow(Center.snodes[57])
            # pathrepo.write_logmsg('./logs/loginfo.txt')
            pathfinder.grow(Center.snodes[54])
            pathfinder.grow(Center.snodes[51])
            pathfinder.block_filter()
            pathfinder.write_log('./logs/loginfo.txt')
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
