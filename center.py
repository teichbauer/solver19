from basics import verify_sat, add_vk1
known_sats = [
    # sat 0
  { 59: 1, 58: 1, 57: 1, 56: 0, 55: 0, 54: 1, 53: 0, 52: 1, 51: 1, 50: 0, # all
    49: 1, 48: 1, 47: 1, 46: 1, 45: 0, 44: 0, 43: 0, 42: 1, 41: 1, 40: 1, # all
    39: 0, 38: 0, 37: 1, 36: 1, 35: 0, 34: 0, 33: 0, 32: 0, 31: 1, 30: 1, # all
    29: 0, 28: 1, 27: 1, 26: 0, 25: 0, 24: 0, 23: 1, 22: 0, 21: 1, 20: 1, # 29:0, 26:0
    19: 0, 18: 1, 17: 1, 16: 0, 15: 0, 14: 1, 13: 1, 12: 0, 11: 0, 10: 0, # all
     9: 0,  8: 0,  7: 1,  6: 1,  5: 1,  4: 0,  3: 1,  2: 1,  1: 0,  0: 1, # all
   },
    # sat 1
  { 59: 1, 58: 1, 57: 1, 56: 0, 55: 0, 54: 1, 53: 0, 52: 1, 51: 1, 50: 0,
    49: 1, 48: 1, 47: 1, 46: 1, 45: 0, 44: 0, 43: 0, 42: 1, 41: 1, 40: 1,
    39: 0, 38: 0, 37: 1, 36: 1, 35: 0, 34: 0, 33: 0, 32: 0, 31: 1, 30: 1,
    29: 0, 28: 1, 27: 1, 26: 0, 25: 0, 24: 0, 23: 1, 22: 0, 21: 1, 20: 1, # 29:0, 26:1
    19: 0, 18: 1, 17: 1, 16: 0, 15: 0, 14: 1, 13: 1, 12: 0, 11: 0, 10: 0,
     9: 0,  8: 0,  7: 1,  6: 1,  5: 1,  4: 0,  3: 1,  2: 1,  1: 0,  0: 1,
  },
    # sat 2
  { 59: 1, 58: 1, 57: 1, 56: 0, 55: 0, 54: 1, 53: 0, 52: 1, 51: 1, 50: 0,
    49: 1, 48: 1, 47: 1, 46: 1, 45: 0, 44: 0, 43: 0, 42: 1, 41: 1, 40: 1,
    39: 0, 38: 0, 37: 1, 36: 1, 35: 0, 34: 0, 33: 0, 32: 0, 31: 1, 30: 1,
    29: 1, 28: 1, 27: 1, 26: 0, 25: 0, 24: 0, 23: 1, 22: 0, 21: 1, 20: 1, # 29:1, 26:0
    19: 0, 18: 1, 17: 1, 16: 0, 15: 0, 14: 1, 13: 1, 12: 0, 11: 0, 10: 0,
     9: 0,  8: 0,  7: 1,  6: 1,  5: 1,  4: 0,  3: 1,  2: 1,  1: 0,  0: 1,
   },
    # sat 3
  { 59: 1, 58: 1, 57: 1, 56: 0, 55: 0, 54: 1, 53: 0, 52: 1, 51: 1, 50: 0,
    49: 1, 48: 1, 47: 1, 46: 1, 45: 0, 44: 0, 43: 0, 42: 1, 41: 1, 40: 1,
    39: 0, 38: 0, 37: 1, 36: 1, 35: 0, 34: 0, 33: 0, 32: 0, 31: 1, 30: 1,
    29: 1, 28: 1, 27: 1, 26: 0, 25: 0, 24: 0, 23: 1, 22: 0, 21: 1, 20: 1, # 29:1, 26:1
    19: 0, 18: 1, 17: 1, 16: 0, 15: 0, 14: 1, 13: 1, 12: 0, 11: 0, 10: 0,
     9: 0,  8: 0,  7: 1,  6: 1,  5: 1,  4: 0,  3: 1,  2: 1,  1: 0,  0: 1,
   },
    # sat 4
  { 59: 1, 58: 1, 57: 1, 56: 0, 55: 0, 54: 1, 53: 1, 52: 1, 51: 1, 50: 0,
    49: 1, 48: 1, 47: 1, 46: 1, 45: 0, 44: 0, 43: 0, 42: 1, 41: 1, 40: 1,
    39: 0, 38: 0, 37: 1, 36: 1, 35: 0, 34: 0, 33: 0, 32: 0, 31: 1, 30: 1,
    29: 0, 28: 1, 27: 1, 26: 0, 25: 0, 24: 0, 23: 1, 22: 0, 21: 1, 20: 1, # 29:0, 26:0
    19: 0, 18: 1, 17: 1, 16: 0, 15: 0, 14: 1, 13: 1, 12: 0, 11: 0, 10: 0,
     9: 0,  8: 0,  7: 1,  6: 1,  5: 1,  4: 0,  3: 1,  2: 1,  1: 0,  0: 1,
   },
    # sat 5
  { 59: 1, 58: 1, 57: 1, 56: 0, 55: 0, 54: 1, 53: 1, 52: 1, 51: 1, 50: 0,
    49: 1, 48: 1, 47: 1, 46: 1, 45: 0, 44: 0, 43: 0, 42: 1, 41: 1, 40: 1,
    39: 0, 38: 0, 37: 1, 36: 1, 35: 0, 34: 0, 33: 0, 32: 0, 31: 1, 30: 1,
    29: 0, 28: 1, 27: 1, 26: 0, 25: 0, 24: 0, 23: 1, 22: 0, 21: 1, 20: 1, # 29:0, 26:1
    19: 0, 18: 1, 17: 1, 16: 0, 15: 0, 14: 1, 13: 1, 12: 0, 11: 0, 10: 0,
     9: 0,  8: 0,  7: 1,  6: 1,  5: 1,  4: 0,  3: 1,  2: 1,  1: 0,  0: 1,
   },
    # sat 6
  { 59: 1, 58: 1, 57: 1, 56: 0, 55: 0, 54: 1, 53: 1, 52: 1, 51: 1, 50: 0,
    49: 1, 48: 1, 47: 1, 46: 1, 45: 0, 44: 0, 43: 0, 42: 1, 41: 1, 40: 1,
    39: 0, 38: 0, 37: 1, 36: 1, 35: 0, 34: 0, 33: 0, 32: 0, 31: 1, 30: 1,
    29: 1, 28: 1, 27: 1, 26: 0, 25: 0, 24: 0, 23: 1, 22: 0, 21: 1, 20: 1, # 29:1, 26:0
    19: 0, 18: 1, 17: 1, 16: 0, 15: 0, 14: 1, 13: 1, 12: 0, 11: 0, 10: 0,
     9: 0,  8: 0,  7: 1,  6: 1,  5: 1,  4: 0,  3: 1,  2: 1,  1: 0,  0: 1,
   },
    # sat 7
  { 59: 1, 58: 1, 57: 1, 56: 0, 55: 0, 54: 1, 53: 1, 52: 1, 51: 1, 50: 0,
    49: 1, 48: 1, 47: 1, 46: 1, 45: 0, 44: 0, 43: 0, 42: 1, 41: 1, 40: 1,
    39: 0, 38: 0, 37: 1, 36: 1, 35: 0, 34: 0, 33: 0, 32: 0, 31: 1, 30: 1,
    29: 1, 28: 1, 27: 1, 26: 0, 25: 0, 24: 0, 23: 1, 22: 0, 21: 1, 20: 1, # 29:1, 26:1
    19: 0, 18: 1, 17: 1, 16: 0, 15: 0, 14: 1, 13: 1, 12: 0, 11: 0, 10: 0,
     9: 0,  8: 0,  7: 1,  6: 1,  5: 1,  4: 0,  3: 1,  2: 1,  1: 0,  0: 1,
   }
]

class Center:
    maxnov = 0
    satbitdic = {}  # every snode has 3x <sat-bit>:<snode> in here
    bits = set([])
    bdic = {}
    sats = []
    limit = 10
    snodes = {}
    rootvks = {}
    vk1dic = {}
    vk1info = {}  # {<nov>: [k1n, k1n, ..], <nov>:[...]}
    vk2dic = {}   # {<kb>:<vk2>, ..}
    vk1bdic = {}  # all vk1-touched bits
    vknames = {}
    orig_vkdic = None
    logging = False

    @classmethod
    def set_maxnov(cls, nov):
        cls.maxnov = nov
        cls.bits = set(range(nov))

    @classmethod
    def set_init(cls, vkm):
        cls.orig_vkdic = vkm.clone_vkdic() # vkm.clone()
        for kn, vk in cls.orig_vkdic.items():
            for b in vk.bits:
                cls.bdic.setdefault(b, set([])).add(kn)
        cls.bdic
        cls.rest_kns = list(Center.orig_vkdic.keys())

    @classmethod
    def slice(cls, snode):
        cls.vknames[snode.nov] = []
        for vk in snode.choice[1]: # vk3s
            myvk = cls.orig_vkdic[vk.kname]
            cls.remove_kn(snode.nov, vk.kname, 'root')
        for kn in snode.choice[2]: # vk1(2bits touch)-knames
            cls.remove_kn(snode.nov, kn, '2bit')
        for kn in snode.choice[3]: # vk2(1bit-touch)-knames)
            cls.remove_kn(snode.nov, kn, '1bit')
        x = 0
    
    @classmethod
    def add_vk1(cls, vk1):
        kns = cls.vk1info.setdefault(vk1.nov, [])
        add_vk1(vk1, cls.vk1dic, cls.vk1bdic, kns)

    @classmethod
    def remove_kn(cls, nov, kn, typename):
        if kn in cls.rest_kns:
            cls.rest_kns.remove(kn)
            cls.orig_vkdic[kn].type = typename
            cls.orig_vkdic[kn].nov = nov
            cls.vknames[nov].append(f"{kn}-{typename}")
        else:
            print('weord-0')

    @classmethod
    def sat_failed(cls, sat, nov=-1):
        if nov == -1:
            for vk in cls.orig_vkdic.values():
                if vk.hit(sat):
                    print(f"hit-vk: {vk.kname} on {vk.nov}")
                    return True
        else:
            kns = cls.vknames[nov]
            sn = cls.snodes[nov]
            sats = []
            vals = list(sn.bgrid.chvals)
            for chv in vals:
                ss = sat.copy()
                ss.update(sn.bgrid.grid_sat(chv))
                sats.append((chv, ss))
            for chv, s in sats:
                for kn in kns:
                    vk = cls.orig_vkdic[kn.split('-')[0]]
                    if vk.hit(s):
                        print(f"hit-vk: {vk.kname} on {vk.nov}")
                        vals.remove(chv)
                        break
            return len(vals) == 0
        return False

    @classmethod
    def set_xkeys(cls): # build bit-crossing dic
        for nov, snode in cls.snodes.items():
            snode.vecmgr.down_intersec_vecdic(nov)
            snode.vecmgr.up_intersec_vecdic(nov)
        x = 0

        
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

