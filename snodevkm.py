from center import Center


class SnodeVkm:
    def __init__(self, sat2):
        self.nov = sat2.snode.nov
        self.sat2 = sat2
        self.chvkdic = sat2.chvkdic
        self.kn1s = set([])
        self.kn2s = set([])
        self._kn1s = set([])
        self._kn2s = set([])
        self._bdic = sat2.bdict
        self.x = 0
        self.vk12dic = sat2.vk12dic
        for kn, vk in self.vk12dic.items():
            if vk.nob == 1:
                self._kn1s.add(kn)
            else:
                self._kn2s.add(kn)
            for b in vk.bits:
                self._bdic.setdefault(b, set([])).add(kn)

    def sort_chvkdic(self):
        self.bitdic = {}
        kns = list(self.vk12dic.keys())
        for kn in kns:
            vk = self.vk12dic[kn]
            if vk.nob == 1:
                self.add_vk1(vk)
            else:
                self.add_vk2(vk)
        x = 1

    def add_vk1(self, vk):
        self.added = False
        bit = vk.bits[0]
        kns = self.bitdic.get(bit, []).copy()
        for kn in kns:
            if kn in self.kn1s:
                vk1 = self.vk12dic[kn]
                if vk1.dic[bit] != vk.dic[bit]:
                    added = self.add_kicker_vk1(vk, vk1)
                    self.added = self.added or added
                else:  # self.vk12dic[kn].dic[bit] == vk.dic[bit]
                    added = self.add_duplicated_vk1(vk, vk1)
                    self.added = self.added or added
            elif kn in self.kn2s:
                vk2 = self.vk12dic[kn]
                if bit in vk2.bits:
                    if vk2.dic[bit] == vk.dic[bit]:
                        # a vk2 has the same v on this bit:
                        # remove vk2 from vs vk is on
                        added = self.add_shadowing(vk, self.vk12dic[kn])
                        self.added = self.added or added
                    else:  # vk2 has diff val on this bit
                        # drop a bit:it becomes vk1, add it back as vk1
                        added = self.add_cutting(vk, self.vk12dic[kn])
                        self.added = self.added or added
                else:
                    self.added = self.add2chvkdic(vk)
        if not self.added:
            self.add2chvkdic(vk)
    # ---- end of def add_vk1(self, vk) -----------------------------

    def add_vk2(self, vk):
        for kn in self.kn1s:  # any existing vk1 covers vk?
            b = self.vk12dic[kn].bits[0]
            if b in vk.bits:
                self.add_shadowed(vk, self.vk12dic[kn], b)
        # find vk2s with same bits
        pair_kns = []
        for kn in self.kn2s:
            if kn == vk.kname:
                continue
            if self.vk12dic[kn].bits == vk.bits:
                pair_kns.append(kn)
        bs = vk.bits
        if len(pair_kns) == 0:  # there is no pair
            self.add2chvkdic(vk)
        else:
            for pk in pair_kns:
                pvk = self.vk12dic[pk]
                if vk.dic[bs[0]] == pvk.dic[bs[0]]:
                    if vk.dic[bs[1]] == pvk.dic[bs[1]]:
                        self.add_duplicate(vk, pvk)
                    else:  # b0: same value, b1 diff value
                        self.add_dupbits_compliment(vk, pvk, bs[1])
                elif vk.dic[bs[1]] == pvk.dic[bs[1]]:
                    self.add_dupbits_compliment(vk, pvk, bs[0])
    # ---- end of def add_vk2(self, vk): --------------------------

    ##########################################################################
    def add2bitdic(self, vk):
        if vk.nob == 1:
            self.kn1s.add(vk.kname)
        else:
            self.kn2s.add(vk.kname)
        for b in vk.bits:
            self.bitdic.setdefault(b, set([])).add(vk.kname)
            if vk.kname not in self._bdic[b]:
                self._bdic[b].add(vk.kname)

    def add2chvkdic(self, vk):
        self.add2bitdic(vk)
        for v in vk.cvs:
            if v in self.chvkdic and vk not in self.chvkdic[v]:
                self.chvkdic[v].add(vk)
        return True

    def register(self, new_vk, done=None):
        self.add2bitdic(new_vk)
        name = new_vk.kname
        self.vk12dic[name] = new_vk
        for b in new_vk.bits:
            self._bdic[b].add(name)
        if new_vk.nob == 1:
            self._kn1s.add(name)
            if done:
                self.kn1s.add(name)
        else:
            self._kn2s.add(name)
            if done:
                self.kn2s.add(name)

    def add_duplicate(self, vk, old_vk):
        self.add2bitdic(vk)
        for v in vk.cvs:
            if v not in old_vk.cvs:
                self.chvkdic[v].add(vk)
        return True

    def add_dupbits_compliment(
            self,
            vk,           # nob==2, vk.bits == old_vk.bits: svbit and dvbit
            old_vk,       # nob==2, on sbit vk[svbit]==old_vk[svbit]
            diff_v_bit):  # vk.dic[diff_v_bit] != old_vk.dic[diff_v_bit]
        self.add2bitdic(vk)
        # new vk1 on svbit, vk1.kname: "M***"
        vk1 = vk.clone([diff_v_bit])
        vk1.cvs = set([])
        self.register(vk1, True)

        avs = vk.cvs.union(old_vk.cvs)
        vs = vk.cvs.intersection(old_vk.cvs)
        vs1 = vk.cvs - old_vk.cvs  # left-over in vk after removing old-vk.cvs
        for v in avs:
            if v in vs:
                if old_vk in self.chvkdic[v]:
                    self.chvkdic[v].discard(old_vk)
                self.chvkdic[v].add(vk1)
                vk1.cvs.add(v)
            elif v in vs1:
                if vk not in self.chvkdic[v]:
                    self.chvkdic[v].add(vk)
                    self.kn2s.add(vk.kname)
        return True

    def add_shadowed(self,
                     vk,             # shadowed vk(nob==2), to be added
                     shadowing_vk,   # existing vklause(vk1) shadowing vk
                     vk1_bit):       # the shadowing-bit
        # vk is shadowed by existing vk1(E.G. {9:0, 11:1} by {9:0})
        # vs from vk1.cvs should be excluded from vk.cvs
        self.add2bitdic(vk)
        shadowed_cvs = shadowing_vk.cvs
        if vk.dic[vk1_bit] == shadowing_vk.dic[vk1_bit]:
            for v in vk.cvs:
                # if v not shadowed, add vk to v, shadowed: vk notadd to v
                if v in self.chvkdic and (v not in shadowed_cvs):
                    if vk not in self.chvkdic[v]:
                        self.chvkdic[v].add(vk)
        else:  # vk[vk1_bit] != shadowing_vk[vk1_bit]: vk->vk1 for shadowed vs
            cut_vk = vk.clone([vk1_bit])
            cut_vk.cvs = set([])
            # register cut_vk
            self.register(cut_vk, True)

            if vk.cvs == shadowed_cvs and vk.kname in self._bdic[vk1_bit]:
                self._bdic[vk1_bit].discard(vk.kname)

            for v in vk.cvs:
                if v in shadowed_cvs:
                    self.chvkdic[v].add(cut_vk)
                    cut_vk.cvs.add(v)
                else:
                    self.chvkdic[v].add(vk)
        return True  # vk has been added to chvkdic

    def add_shadowing(self,
                      vk,         # vk being added(nob==1), shadowing old_vk
                      old_vk):    # shadowed old-vk (nob==2)
        self.add2bitdic(vk)
        for v in vk.cvs:
            if old_vk in self.chvkdic[v]:
                self.chvkdic[v].discard(old_vk)  # remove old_vk from this v
            self.chvkdic[v].add(vk)              # add vk to v
        return True  # vk has been added to chvkdic

    def add_cutting(self,
                    vk,         # vk1 to be added (on bit b ->inside vk2.bits)
                    old_vk2):   # vk2[b] == !vk.dic[b]
        # vk2 get bit b dropped, becoming vk1 (on vk.cvs)
        # vk.cvs removed old-vk.cvs
        self.add2bitdic(vk)
        # vk2 gets cut, resulting vk1
        vk1 = old_vk2.clone(vk.bits)    # vk1.kname: 'C<nnn>' -> 'M<nnn>'
        # register vk1
        self.register(vk1, True)

        # add vk1, set its cvs
        vk1.cvs = set([])
        for v in vk.cvs:
            self.chvkdic[v].add(vk)
            if old_vk2 in self.chvkdic[v]:
                self.chvkdic[v].discard(old_vk2)
                vk1.cvs.add(v)
                self.chvkdic[v].add(vk1)
        return True  # vk has been added to chvkdic

    def add_kicker_vk1(self,
                       vk,         # vk1 being added
                       hit_vk):    # old vk1 conflict: old_vk[bit] != vk[bit]
        self.add2bitdic(vk)
        for v in vk.cvs:
            if v in hit_vk.cvs:
                self.chvkdic.pop(v, None)
            else:
                self.chvkdic[v].add(vk)
        return True  # vk has been added to chvkdic

    def add_duplicated_vk1(self,
                           vk,      # vk(nob==1) and old_vk(nob==1)
                           old_vk):  # vk[bit] == old_vk[bit]
        self.add2bitdic(vk)
        for v in vk.cvs:
            if v not in old_vk.cvs:
                self.chvkdic[v].add(vk)
                if vk.kname not in self._bdic[vk.bits[0]]:
                    self._bdic[vk.bits[0]].add(vk.kname)

    def add_duplicated_vk1(self,     # vk(nob==1) and old_vk(nob==1)
                           vk,       # vk.bits[0] == old_vk.bits[0]
                           old_vk):  # vk[bit] == old_vk[bit]
        if vk.cvs == old_vk.cvs or old_vk.cvs.issuperset(vk.cvs):
            return False
        if vk.cvs.issuperset(old_vk.cvs):
            self.bitdic[vk.bits[0]].discard(old_vk.kname)
            self._bdic[vk.bits[0]].discard(old_vk.kname)
        self.add2bitdic(vk)
        for v in vk.cvs:
            self.chvkdic[v].discard(old_vk)
            self.chvkdic[v].add(vk)
        return True
