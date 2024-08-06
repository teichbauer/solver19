from vklause import VKlause
from bitgrid import BitGrid
from center import Center
from sat2 import Sat2
from basics import display_vkdic, ordered_dic_string, verify_sat


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
            Center.sat_paths = [] # list of sat-path(dics)
            for tail in self.taildic.values():
                tail.sat_filter()
            # while snode:
            #     snode.all_hitbits()
            #     snode = snode.parent
            x = 1
    def find_paths(self, sat, path):
        for tail in self.taildic.values():
            tail.find_path(sat,path)

    def add_sat(self, bit, val, cv,satdic=None):
        if not satdic:
            satdic = self.satdic
        sat_info = satdic.setdefault(bit, {})
        cvs = sat_info.setdefault(val, [])
        if cv not in cvs:
            cvs.append(cv)

    def find_hits(self, snode):
        # based on the bits in root-sats and satdic
        # looking upwards for hits
        bits = self.bgrid.bitset.copy()  # root-bits
        bits.update(self.satdic.keys())
        tail_and_sat_bits = set(snode.satdic).union(snode.bdic)
        hit_bits = bits.intersection(tail_and_sat_bits)
        # ------------------------
        my_tailbits = set(self.bdic)
        parent_tailbits = set(snode.bdic)
        tail_overlap_its = my_tailbits.intersection(parent_tailbits)
        return hit_bits, tail_overlap_its

    def all_hitbits(self):
        print(f'my nov: {self.nov}')
        snode = self.parent
        while snode:
            hbits, obits = self.find_hits(snode)
            print(f'hit-bits with {snode.nov}: {hbits}')
            print(f'oberlap-bits with {snode.nov}: {obits}')
            snode = snode.parent



