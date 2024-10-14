from bitgrid import BitGrid
from basics import remove_vk1, remove_vk2, add_vk1, add_vk2
from center import Center
from tools import *
from collections import OrderedDict
from sat_path import SatPath
from nodegrphost import NodeGroupHost
from vkrepo import VKRepoitory

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
        self.choice = vkm.make_choice(self.nov) # (vals, bits, t2s, t1s)
        self.vk2dic = {}    # vk1s + vk2s in all tails
        self.k1ns = []      # knames of all vk1s in all taildic
        self.bdic2 = {}      # bit-dic for all vk2s in vk2dic
        self.bdic1 = {}
        self.bgrid = BitGrid(self)
        self.vkrepo = VKRepoitory(self)
        make_taildic(self)  # make self.taildic, self.bkdic
        Center.snodes[self.nov] = self
        Center.slice(self)
        self.next = None
        self.next_sh = self.sh.reduce(self.bgrid.bits)
        if Center.logging:
            self.logfile = open("logfile.txt",'a')
        else:
            self.logfile = None

    def spawn(self):
        if len(self.vkm.vkdic) > 0:  # there exist vk3 in vkm.vkdic, make next
            self.next = SatNode(self, self.next_sh.clone(), self.vkm)
            return self.next.spawn()
        else:  # when there is no more vk3
            Center.last_nov = self.nov
            Center.sat_pool = [] # list of sat-path(dics)
            print(f"NOV:{self.nov}")
            nodehost = NodeGroupHost(Center.snodes[60])
            nodehost.merge_snode(Center.snodes[57])
            # nodehost.merge_down(Center.snodes[57]
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
        bits = set(self.bdic2)
        if incl_root:
            bits.update(self.bgrid.bits)
        return bits

    def add_vk(self, vk):
        if vk.nob == 1:
            # snode local
            add_vk1(vk, 
                    None,       # there is no snode.vk1dic
                    self.bdic1,
                    self.k1ns)
            # Center
            self.Center.add_vk1(vk)
        else:
            # snode local
            add_vk2(vk, 
                    self.vk2dic, 
                    self.bdic2, 
                    None)       # there is no snode.kn2s
            add_vk2(vk,
                    self.Center.vk2dic,
                    self.Center.vk2bdic,
                    None)       # there is no Center.kn1s
            # if vk2 with the same bits exits?
            b1, b2 = vk.bits
            kns1 = self.bdic2[b1]
            kns2 = self.bdic2[b2]
            xkns = set(kns1).intersection(kns2)
            xkns.remove(vk.kname)
            # while len(xkns) > 0:
            #     x = 9
                # vk1 = handle_vk2pair(vk, self.vk2dic[xkns.pop()])
                # if vk1:
                #     self.add_vk(vk1)

    def remove_vk(self, vk):
        if vk.nob == 1:
            # delete snode local
            remove_vk1(vk, 
                       None,        # there is no snode.vk1dic
                       self.bdic1,  # snode.bdic1
                       self.k1ns)
            # delete from Center
            remove_vk1(vk,
                       self.Center.vk1dic,
                       self.Center.bdic1,
                       self.Center.vk1info[self.nov])
        else:
            # delete snode local
            remove_vk2(vk, self.vk2dic, self.bdic2, 
                       None)  # there is no self.vk2kns
            remove_vk2(vk, self.Center.vkdic, self.Center.vk2bdic,
                       None)  # there is no Center.vk2ns

    def print_vk2dic(self):
        for vk in self.vk2dic.values():
            print(vk.print_msg())
