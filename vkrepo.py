from center import Center
from tools import handle_vk2pair, cvs_intersect

sngl_cvs = (  # cvs is a set like {0,1,2,3}, or {5}
    'S', # 2 touch-bits resulted vk1: C0212->S0212, C0212 disappeared
    'T', # Snnnn vk1 splits a vk2
    'D'  # 2 vk2a in the same snode, (a + not-b)(a + b) -> a (vk1): Dnnnn
)
cmpd_cvs = (  # compound-cvs: lie {60:{3,5}, 57:{0,1}}
    'U',
    'V',
    'X'
)

class VKRepoitory:
    def __init__(self, snode):
        self.bdic1 = {}     # {bit: [k1n, k1n,..], bit:[], ..}
        self.bdic2 = {}     # {bit: [k2n, k2n,..], bit:[], ..}
        self.k1ns = []      # [k1n, k1n,..]
        self.vk2dic = {}    # {k2n:vk2, k2n: vk2,...}
        self.blocks = []    # [node, ..] node:{nov:cvs, nv:..} where snode fails
        self.excls = {}     # {kn:[node, node,..],..} vk not 2b used in nodes
        self.snode = snode  # related snode
        self.inflog = {}    # {key:[info,info,..], key:[], ...}

    def add_vk1(self, vk1, add2center=True):
        name = vk1.kname
        if name in self.k1ns:
            vk = Center.vk1dic[name]
            if vk.equal(vk1):
                self.inflog.setdefault(name,[])\
                    .append(f"add_vk1:{name} already in. Not added")
                return
            elif name[0] == 'U':
                name = f"V{name[1:]}"
            else:
                raise Exception("vk1 name conflict-1")
        # handle with existing vk1s
        self.k1ns.append(name)
        if vk1.bit in self.bdic1:
            for kn in self.bdic1[vk1.bit]:
                vk = Center.vk1dic[kn]
                cmm = vk1.cvs.intersection(vk.cvs)
                if vk1.nov == vk.nov and \
                    name[0] in sngl_cvs and vk.kname[0] in sngl_cvs: 
                    # both vk and vk1 sngl-cvs
                    if cmm == vk1.cvs:
                        if vk.val == vk1.val:
                            self.inflog.setdefault(name,[])\
                            .append(f"add_vk1:{name} b/v existed. Not added")
                        else: # vk.val != vk1.val
                            self.inflog.setdefault(name,[])\
                            .append(f"add_vk1:{name}:total added as bock.")
                        return
                    elif vk.val != vk1.val and len(cmm) > 0:
                        node = {vk.nov: cmm}
                        self.blocks.append(node)
                        self.inflog.setdefault(name,[])\
                            .append(f"{name} causes block: {node}")
                else:
                    print("what to do?")

        self.bdic1.setdefault(vk1.bit,[]).append(name)
        if add2center:
            Center.add_vk1(vk1)
        # handle with vk2s
        if vk1.bit in self.bdic2:
            for kn in self.bdic2[vk1.bit]:
                vk = self.vk2dic[kn]
                cmm = cvs_intersect((vk1.nov, vk1.cvs),(vk.nov, vk.cvs))
                if not cmm: continue
                self.add_excl(vk, cmm)
                if vk.dic[vk1.bit] != vk1.val:
                    vkx = vk.clone('U', [vk1.bit], cmm)
                    self.add_vk1(vkx)

    def add_vk2(self, vk2):
        name = vk2.kname
        for b in vk2.bits:
            if b in self.bdic1:
                kns = self.bdic1[b]  # for loop variable must be immutable
                for kn in kns:
                    vk1 = Center.vk1dic[kn]
                    cmm = cvs_intersect((vk1.nov, vk1.cvs),(vk2.nov, vk2.cvs))
                    if not cmm: continue
                    self.add_excl(vk2, cmm)
                    if vk2.dic[b] != vk1.val:
                        if len(cmm) == 1:
                            vkx = vk2.clone('T', [b], cmm[vk2.nov])
                        else:
                            vkx = vk2.clone('U', [b], cmm)
                        self.add_vk1(vkx)
        # if vk2 with the same bits exits?
        b1, b2 = vk2.bits
        if (b1 not in self.bdic2) or name not in self.bdic2[b1]:
            self.bdic2.setdefault(b1,[]).append(name)
        if (b2 not in self.bdic2) or name not in self.bdic2[b2]:
            self.bdic2.setdefault(b2,[]).append(name)
        self.vk2dic[name] = vk2

        # handle case of 2 overlapping bits with existing vk2
        kns1 = self.bdic2[b1]
        kns2 = self.bdic2[b2]
        xkns = set(kns1).intersection(kns2)
        xkns.remove(name)
        while len(xkns) > 0:
            vk1 = handle_vk2pair(vk2, self.vk2dic[xkns.pop()])
            if vk1:
                self.add_vk1(vk1)

    def add_excl(self, vk2, node):
        if len(node) == 1: # in case node has only 1 entry like {60:{3,7}
            nov, cvs = tuple(node.items())[0] # like {60:{3,7}}->60, {3,7}
            if nov == vk2.nov:  # vk2,cvs:{2,3,6,7}
                vk2.cvs -= cvs  # vk2.cvs -> {2,6}
                return True
        lst = self.excls.setdefault(vk2.kname, [])
        if node in lst: return False
        for d in lst:
            for nv, cvs in node.items():
                contained = nv in d and cvs.issubset(d[nv])
                if not contained: break
            if contained: return False
        lst.append(node)
        return True
