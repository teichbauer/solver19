from basics import verify_sat
# from sat2 import Sat2


class Center:
    maxnov = 0
    satbitdic = {}  # every snode has 3x <sat-bit>:<snode> in here
    bits = set([])
    sats = []
    limit = 10
    snodes = {}
    vk12kndic = {}  # {nov: [kns]}
    sumbdic = {}
    sumvk12dic = {}
    orig_vkm = None

    @classmethod
    def set_maxnov(cls, nov):
        cls.maxnov = nov
        cls.bits = set(range(nov))

    @classmethod
    def set_blinks(cls):
        nov = cls.maxnov
        x = 1
        # sn = cls.snodes[nov]

    @classmethod
    def solve(cls):
        # sat2 = Sat2(None, None, cls.sumvk12dic)
        # sat2.split2()
        # if sat2.children[1]:
        #     # sat2.children[1].verify(cls.vk12kndic, cls.maxnov, cls.last_nov)
        #     sat2.children[1].verify(cls.maxnov, cls.last_nov)
        # if sat2.children[0]:
        #     sat2.children[0].verify(cls.maxnov, cls.last_nov)
        x = 1

    @classmethod
    def set_satbits(cls):
        """ called only after snode(last_nov) is done.
            1: unify bits from every snode's 3 sat-bits into cls.satbits
            2: group front-kns in every snode's child-vk12m
            """
        cls.satbits = set(cls.satbitdic)
        cls.tailbits = cls.bits - cls.satbits
        nov = cls.maxnov
        while nov > cls.last_nov:
            snode = cls.snodes[cls.maxnov]
            for ch, vkm in snode.vk12mdic.items():
                all_kns = set(vkm.vkdic)
                kns = set([])
                vkm.tail_kns = set([])  # vk with both bits in tail
                bs = cls.tailbits.intersection(vkm.bdic)
                for b in bs:
                    for kn in vkm.bdic[b]:
                        kns.add(kn)
                        if cls.tailbits.issuperset(vkm.vkdic[kn].bits):
                            vkm.tail_kns.add(kn)
                vkm.tailpart_kns = kns  # kn with at least 1 bit in tail
                # front_kns are vks with both bits in satbits
                vkm.front_kns = all_kns - kns
                x = 0
            nov -= 3

    @classmethod
    def bit_overlaps(cls, nov):
        print(f"Showing overlappings for {nov}")
        print("="*80)
        bdic0 = cls.sumbdic[nov]
        bdic = bdic0
        gcount = {}
        for b in bdic0:
            bcount = gcount.setdefault(f"nov-{nov}.{b}", {})
            bcount[nov] = (len(bdic0[b][0]), len(bdic0[b][1]))
            print("-"*20 + f" {nov}:{b} - {bdic0[b][0]},{bdic0[b][1]}")
            nv = nov - 3
            while True:
                bdic = cls.sumbdic[nv]
                cnt = gcount.setdefault(nv, {})
                print(f"{nv}:")
                for bit in bdic:
                    if bit == b:
                        c0 = len(bdic[b][0])
                        c1 = len(bdic[b][1])
                        m = f"  -> {nv}:{bit} - [{bdic[bit][0]},{bdic[bit][1]}]"
                        cnt[bit] = (c0, c1)
                        print(m)
                        print('---')
                print(f"-"*80)
                nv -= 3
                if nv == cls.last_nov:
                    break
        print(str(gcount))

    @classmethod
    def show_sumvk12m(cls, nov):
        dic = cls.sumvk12m[nov]
        ks = sorted(dic.keys())
        print(f"{nov} has {len(ks)} vks:")
        for k in ks:
            m = f"{k}:{str(dic[k][0].dic)}, {str(dic[k][1])}"
            print(m)
