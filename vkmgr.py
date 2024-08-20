from vk3picker import Vk3Picker
from stail import STail
from tools import sort_length_list
from collections import OrderedDict

class VKManager:
    def __init__(self, vkdic, initial=False):
        self.vkdic = vkdic
        if initial:
            self.bdic = self.make_bdic()
            self.picker = Vk3Picker(self)
    
    def make_choice(self):
        vals = [0,1,2,3,4,5,6,7]
        chvals, vk3s, t2s, t1s = self.picker.pick(vals)
        t2s.sort()
        t1s.sort()
        return chvals, vk3s, t2s, t1s

    def clone(self):
        vkdic = {kn: vk.clone() for kn, vk in self.vkdic.items()}
        vkm = VKManager(vkdic)
        vkm.bdic = {b: s.copy() for b, s in self.bdic.items()}
        return vkm

    def pop_vk(self, vk): # vk can be kname(str), or VKlause-inst
        if type(vk) == str: # vk is kname
            if vk in self.vkdic:
                vkx = self.vkdic.pop(vk)
            else:
                return None
        else:  # vk is VKlause instance
            if vk.kname in self.vkdic:
                vkx = self.vkdic.pop(vk.kname)
            else:
                return None
        # also drop from choice inside picker.chdic
        self.picker.drop_choice(vkx)
        for bit in vkx.bits:
            if vkx.kname in self.bdic[bit]:
                self.bdic[bit].remove(vkx.kname)
                if len(self.bdic[bit]) == 0:
                    self.bdic.pop(bit)
            else:
                raise Exception(f"pop {vkx.kname} failed")
        return vkx

    def drop_bits(self, bits, kns, vks):
        for bit in bits:
            self.bdic.pop(bit)
        for vk in vks:
            self.vkdic.pop(vk.kname)
        for kn in kns:
            if kn in self.vkdic:
                vk = self.vkdic.pop(kn)
                # vk.clone(bits) will return a clone with dropped bits
                # the original vk will not be modified
                self.vkdic[kn] = vk.clone(bits)
            else:
                x = 1

    def make_bdic(self):
        # make a bit-dict:
        # build a set of kns(klause-names) for each bit
        bdic = {}
        for kn, vk in self.vkdic.items():
            for b in vk.dic:
                if b not in bdic:  # hope this is faster than
                    bdic[b] = set([])  # bdic.setdefault(b,set([]))
                bdic[b].add(kn)
        return bdic

    def make_taildic(self, snode):
        taildic = {v: STail(snode, v) for v in snode.choice[0] }
        for kn in snode.choice[2]: # touch-2 vk3s
            if kn in snode.vkm.vkdic:
                vk = snode.vkm.pop_vk(kn)
                vk1 = snode.bgrid.reduce_vk(vk)
                b, v = vk1.dic.popitem()
                for cv in vk1.cvs:
                    satval = int(not v)
                    taildic[cv].satdic[b] = satval
                    snode.add_sat(b, satval, cv)

        for kn in snode.choice[3]:
            # will result into vk2s
            if kn in self.vkdic:
                vk = self.pop_vk(kn)
                vk2 = snode.bgrid.reduce_vk(vk)
                snode.vk2dic[vk2.kname] = vk2
                for b in vk2.bits:
                    snode.bdic.setdefault(b, []).append(vk2.kname)
                for cv in vk2.cvs:
                    taildic[cv].add_vk2(vk2)
        # satdic may have bit(s) overlapping with vk2, resulting into
        # more satdic entries. Handle that here
        for tail in taildic.values():
            if len(tail.satdic) > 0:
                tail.grow_sat(tail.satdic.copy())
        # make snode.bkys-dic
        dic = {}
        bkys = []
        for chv, tail in taildic.items():
            lst = list(tail.bdic.keys())
            lst += snode.bgrid.bits
            for b in tail.satdic:
                lst.append(b)
            lst.sort()
            tpl = tuple(lst)
            dic.setdefault(tpl, []).append(chv)
            if tpl not in bkys:
                bkys.append(tpl)
        bks = sort_length_list(bkys)
        bkdic = OrderedDict()
        for bk in bks:
            bkdic[bk] = dic[bk]
        snode.bkdic = bkdic
        snode.taildic = taildic
    
    # internal usage for unit test
    def _invkdic(self, kns):
        for kn in kns:
            if kn not in self.vkdic:
                print(f'{kn} not in vkdic')
        print('done')