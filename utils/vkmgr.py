from utils.vk3picker import Vk3Picker
from center import Center

class VKManager:
    # A wrapper class around vkdic, with some facilitating/helper tools
    def __init__(self, vkdic, initial=False):
        self.vkdic = vkdic
        if initial:
            # bdic:{<bit>: <set of all knames that has this bit>}
            self.bdic = self.make_bdic()
            self.picker = Vk3Picker(self, Center.rootvks)
    
    def make_choice(self, nov): # nov: layer-label of choice made
        # --- what is a layer-label:
        # if the starting number of vars: 60, after picked the first 
        # root-vks, the 3 bits these root-vks sit on will get cut. 
        # So when making next choice of MPKs, there are then 57
        # and next: 54, 51, 48,.. till vkdic is exhausted (length=0)
        # ---------------------------------------------------------
        vals = [0,1,2,3,4,5,6,7] # all 8 possible children-vals
        # --- results from picker.pick() call: 
        # chvals: the remaining ch-vals that are not sit upon by vk3s
        # vk3s: list of vk3 picked as root vks
        # t2s: list of knames of vks touching 2 bits of root-vks
        # t21: list of knames of vks touching 1 bits of root-vks
        # ------------------------------
        chvals, vk3s, t2s, t1s = self.picker.pick(vals, nov)
        return chvals, vk3s, t2s, t1s
    
    def clone(self):
        vkdic = {kn: vk.clone() for kn, vk in self.vkdic.items()}
        vkm = VKManager(vkdic)
        vkm.bdic = {b: s.copy() for b, s in self.bdic.items()}
        return vkm

    def pop_vk(self, vk): # vk can be kname(str), or VKlause-inst
        kname = vk.kname
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
    