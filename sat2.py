# from center import Center
from snodevkm import SnodeVkm


class Sat2:
    def __init__(self, parent, v, vk12dic):
        self.parent = parent
        if type(parent).__name__ == 'Sat2':
            self.snode = parent.snode
            self.sats = parent.sats.copy()
            self.sats[parent.maxb] = v
            self.name = f"{parent.maxb}.{v}"
        else:   # parent is a snode
            self.name = 'root'
            self.snode = parent
            self.sats = {}
        self.alive = True
        self.vk12dic = vk12dic
        self.chvkdic = {v: set([]) for v in self.snode.bgrid.chvset}
        self.bdict = {}
        self.svkm = SnodeVkm(self)
        self.find_maxb()

    def filter_sats(self, sats, vkdic):
        x = 0
        pass

    def find_maxb(self):
        self.maxb = 8
        # self.maxb = -1
        # maxcnt = 0
        # for b in self.bdict:
        #     if len(self.bdict[b]) > maxcnt:
        #         maxcnt = len(self.bdict[b])
        #         self.maxb = b

    def verify(self, nov, stop_nov):
        while nov > stop_nov:
            self.svkm.sort_chvkdic()
            break
        x = 2

    def split2(self):
        self.children = {}
        # a vk with the same kname in children[0] and in children[1], are
        # refering to the same vk, .copy only shallow copy kname/vk entries
        self.children[0] = self.vk12dic.copy()  # vkdic0 for sat[maxb]:0
        self.children[1] = self.vk12dic.copy()  # vkdic1 for sat[maxb]:1
        kns = self.bdict[self.maxb]
        for kn in kns:
            # example: C0032:{8:0, 56:1}, C0189:{8:1, 2:0}
            vk = self.vk12dic[kn]
            if vk.nob == 2:
                # C0032 & C0189 cannot exist as vk2 in neither C[0] or C[1]
                if self.children[0]:    # self.children[0] is not None
                    self.children[0].pop(kn)
                if self.children[1]:    # self.children[1] is not None
                    self.children[1].pop(kn)
                # C0032->M0032:{56:1}, C0189->M0189:{2:0}
                vk1 = vk.clone([self.maxb]) # drop maxb,
                if vk.dic[self.maxb] == 0:   # for children[0], vk->vk1
                    if self.children[0]:     # C0032.dic[8]==0
                        self.children[0][vk1.kname] = vk1  # M0032:{56:1}
                    # if sat[maxb]==1, C0032 is a NO-HIT: don't add in C[1]
                else:  # vk.dic[maxb] == 1   # C0189[8]==1> M0189:{2:0}
                    # C0189 is a NO-HIT in children[0]
                    # for children[1] (bit-sat-value: 1) vk -> vk1
                    if self.children[1]:
                        self.children[1][vk1.kname] = vk1  # M0189:{2:0}
            else:   # vk.nob == 1 : a vk1 already
                if self.vk12dic[kn].bits[0] == 0:
                    self.children[0] = None  # children[0] is impossible
                else:  # vk12dic[kn].bits[0] == 1
                    self.children[1] = None  # children[1] is impossible
        if self.children[0]:
            self.children[0] = Sat2(self, 0, self.children[0])
        if self.children[1]:
            self.children[1] = Sat2(self, 1, self.children[1])
        if self.children[0] == None and self.children[0] == None:
            self.alive = False
