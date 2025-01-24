from utils.vk3picker import Vk3Picker
from center import Center

class VKManager:
    def __init__(self, vkdic, initial=False):
        self.vkdic = vkdic
        if initial:
            # bdic:{<bit>: <set of all knames that has this bit>}
            self.bdic = self.make_bdic()
            self.picker = Vk3Picker(self, Center.rootvks)
    
    def make_choice(self, nov):
        vals = [0,1,2,3,4,5,6,7]
        chvals, vk3s, t2s, t1s = self.picker.pick(vals, nov)
        t2s.sort()
        t1s.sort()
        return chvals, vk3s, t2s, t1s
    
    def clone_vkdic(self):
        return {kn: vk.clone() for kn, vk in self.vkdic.items()}

    def clone(self):
        vkdic = {kn: vk.clone() for kn, vk in self.vkdic.items()}
        vkm = VKManager(vkdic)
        vkm.bdic = {b: s.copy() for b, s in self.bdic.items()}
        return vkm

    def pop_vk(self, vk): # vk can be kname(str), or VKlause-inst
        kname = [vk.kname, vk][type(vk) == str]
        if kname not in self.vkdic: return None
        vkx = self.vkdic.pop(kname)
        # also drop from choice inside picker.chdic
        self.picker.drop_choice(vkx)
        for bit in vkx.bits:
            if kname in self.bdic[bit]:
                self.bdic[bit].remove(kname)
                if len(self.bdic[bit]) == 0:
                    self.bdic.pop(bit)
            else:
                raise Exception(f"pop {kname} failed")
        return vkx

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
    