from basics import set_bit
from vklause import VKlause


class BitGrid:
    BDICS = {
        0: {2: 0, 1: 0, 0: 0},
        1: {2: 0, 1: 0, 0: 1},
        2: {2: 0, 1: 1, 0: 0},
        3: {2: 0, 1: 1, 0: 1},
        4: {2: 1, 1: 0, 0: 0},
        5: {2: 1, 1: 0, 0: 1},
        6: {2: 1, 1: 1, 0: 0},
        7: {2: 1, 1: 1, 0: 1},
    }

    def __init__(self, snode): #bits, chvals, nov):  #
        # in example of two anchor-vks: 
        # C0141{16:0,6:0,1:0} and C0234{16:1,6:0,1:1}  (000,101)/(0,5)
        # 6 children-vals: [1,2,3,4,6,7]
        # grid-bits: high -> low, descending order
        self.ancvk3s = snode.choice[1]
        self.bits = self.ancvk3s[0].bits[:]  # bits [16, 6, 1]
        self.bits.reverse()             # [1, 6, 16]
        self.bitset = set(self.bits)
        self.nov = snode.nov
        self.chvals = snode.choice[0] # [1,2,3,4,6,7]

    def grid_sat(self, val):
        return {self.bits[b]: v for b, v in self.BDICS[val].items()}
    
    def reduce_vk(self, vk):
        # vk is vk3 with 1 or 2 bit(s) in self.bits,
        # but not 3 - vk is not a avk (totally contained in self.bits)
        scvs, outdic = self.cvs_and_outdic(vk)
        cvs = scvs.intersection(self.chvals)
        return VKlause(vk.kname, outdic, self.nov, cvs)

    def vary_bits(self, val, bits, cvs):
        # set val[b] = 0 and 1 for each b in bits, 
        # collecting each val after each setting into cvs
        if len(bits) == 0:
            cvs.add(val)
        else:
            bit = bits.pop()
            for v in (0, 1):
                nval = set_bit(val, bit, v)
                if len(bits) == 0:
                    cvs.add(nval)
                else:
                    self.vary_bits(nval, bits[:], cvs)
        return cvs

    def cvs_and_outdic(self, vk):  # vk is vk3 with 1 or 2 bit(s) in self.bits
        g = [2, 1, 0]  #
        # cvs may contain 2 or 4 values in it
        cvs = set([])
        # vk's dic values within self.grid-bits, forming a value in (0..7)
        # example: grids: (16,6,1), vk.dic:{29:0, 16:1, 1:0} has
        # {16:1,1:0} iwithin grid-bits, forming a value of 4/1*0 where
        # * is the variable value taking 0/1 - that will be set by
        # self.vary_bits call, but for to begin, set v to be 4/100
        v = 0
        out_dic = {}  # dic with 1 or 2 k/v pairs, for making vk12
        for b in vk.dic:
            if b in self.bits:
                ind = self.bits.index(b)  # self.bits: descending order
                g.remove(ind)
                v = set_bit(v, ind, vk.dic[b])
            else:
                out_dic[b] = vk.dic[b]
        # get values of all possible settings of untouched bits in g
        cvs = self.vary_bits(v, g, cvs)
        return cvs, out_dic