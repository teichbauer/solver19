from basics import *
from vklause import VKlause
from stail import STail

def sort_length_list(lst):
    # [(...),(.......),(.)] => [(.),(...),(.......)]
    xlst = []
    while len(lst) > 0:
        e = lst.pop(0)
        indx = -1
        for ind, ex in enumerate(xlst):
            if len(e) < len(ex):
                indx = ind
                break
        if indx > -1:
            xlst.insert(indx, e)
        else:
            xlst.append(e)
    return xlst

def orderedDictIndex(od, key):
    lst = [k for k in od]
    if key not in lst:
        return -1
    return lst.index(key)

def multi_vk2_sats(vk2s):
    all_sats = []
    sats = get_vk2sats(vk2s.pop(0))
    while len(vk2s) > 0:
        satxs = get_vk2sats(vk2s.pop(0))
        for sat in sats:
            for satx in satxs:
                if not sat_conflict(sat, satx):
                    ss = sat.copy()
                    ss.update(satx)
                    if ss not in all_sats:
                        all_sats.append(ss)
    return all_sats

def filter_conflict(snode, satdic):
    excl_chvs = set([])
    for bit, vdic in snode.satdic.items():
        if bit in satdic:
            for v, cvs in vdic.items():
                if v != satdic[bit]:
                    excl_chvs.update(cvs)
    for vk in snode.vk2dic.values():
        if vk.hit(satdic):
            # print(f"vk {vk.kname} hit with {vk.cvs}")
            excl_chvs.update(vk.cvs)
    return excl_chvs

def make_taildic(snode):
    # choice[0]: chvals, [1]: vk3s, [2]: touchd 2 bits, [3]: touched 1 bit
    snode.taildic = {v: STail(snode, v) for v in snode.choice[0] }
    # all vk(kn) touching 1, or 2 bit o f snode's root
    for kn in snode.choice[2] + snode.choice[3]: 
        # will result into vk2s
        if kn in snode.vkm.vkdic:
            vk = snode.vkm.pop_vk(kn)
            vk.nov = snode.nov
            vk12 = snode.bgrid.reduce_vk(vk)
            if vk12.nob == 1:  # touched 2 bits, vk12 is vk1: C0212->S0212
                vk12.kname = vk.kname.replace('C','S')
            snode.add_vk(vk12)  # vk1.kname into snode.k1ns set
            for cv in vk12.cvs:
                snode.taildic[cv].add_vk(vk12)
    # vk1(s) may have bit(s) overlapping with vk2, resulting into
    # more vk1(s). Handle that here
    if len(snode.k1ns) > 0:
        grow_vk1(snode, snode.k1ns.copy())
    # make snode.bkys-dic
    keydic = {}
    for chv, tail in snode.taildic.items():
        keydic[chv] = set(tail.bdic.keys())
    x = 0

def grow_vk1(snode, kns):
    new_kns = set([])
    while len(kns) > 0: #
        vk1 = snode.Center.vk1dic[kns.pop()]
        b, v = tuple(vk1.dic.items())[0] # vk1.dic.(key, val)
        ckns = [xkn for xkn in snode.bdic2.get(b,[]) if xkn.startswith('C')]
        for ckn in ckns:
            vk = snode.vk2dic[ckn]
            s_cvs = vk.cvs.intersection(vk1.cvs)
            if len(s_cvs) == 0:
                continue
            # if vk1 is hit by v: snode is hit, this snode is over for vk1.cvs
            if vk.dic[b] == v: # if vk1[b] is not hit, vk can be voided
                for cv in s_cvs:
                    snode.taildic[cv].remove_vk(vk.kname)
                    vk.cvs.remove(cv) 
                    # if vk.cvs becomes empty, remove from snode
                    if len(vk.cvs) == 0 and vk.kname in snode.bdic2[b]:
                        snode.remove_vk(vk)
            else: # vk.dic[b] != v,
                # when vk1 not hit: {b: not v}, vk.dic[b] is hit, vk -> xvk1
                dic = vk.dic.copy()
                dic.pop(b)
                # vk1 with kname:Snnnn is a vk1 resulted from 2-touches
                # vk1.kname = Tnnnn is derived vk1 that is splitted from 
                # Cnnnn, the cvs is a subset of Cnnnn
                xvk1 = VKlause( vk.kname.replace('C','T'), 
                                dic, vk.nov, s_cvs)
                new_kns.add(xvk1.kname)
                for cv in s_cvs:
                    snode.taildic[cv].remove_vk(vk.kname)
                    snode.taildic[cv].add_vk(xvk1)
                snode.add_vk(xvk1)
                # snode.Center.add_vk1(xvk1)
                vk.cvs = vk.cvs - s_cvs
                if len(vk.cvs) == 0:
                    snode.remove_vk(vk)
    if len(new_kns) > 0:
        grow_vk1(snode, new_kns)
    # end of grow-vk1


def test_water(sname, satdic, snodes, start_nov):
    # example: start_nov=33
    # snds = [s33, s36, s39, s42, s45, s48, s51, s54, s57, s60]
    # ------------------------------------------------------------
    m = ordered_dic_string(satdic)
    print(f"{sname}: {m}")
    snds = [snodes[n] for n in range(start_nov, 61, 3)]  # inclusive of 60
    for snode in snds:
        res = filter_conflict(snode, satdic)
        rvs = set(snode.bgrid.chvals).difference(res)
        # print(f"{snode.nov} excluds: {res}")
        if len(rvs) == 0:
            print(f"{snode.nov} blocked")
            return False
    return True

def handle_vk2pair(vkx, vky):
    assert type(vkx.cvs) == set, "vk2-pair with no-set cvs"
    assert type(vky.cvs) == set, "vk2-pair with no-set cvs"
    b1, b2 = vkx.bits
    if vkx.nov == vky.nov:
        cmm = vkx.intersection(vky.cvs)
        if len(cmm) > 0:
            if vkx.dic[b1] == vky.dic[b1]:
                if vkx.dic[b2] != vky.dic[b2]:
                    return vkx.clone('S', [b2], cmm)
            elif vkx.dic[b2] == vky.dic[b2]:
                if vkx.dic[b1] != vky.dic[b1]:
                    return vkx.clone('S', [b1], cmm)
    else: # vkx.nov != vky.nov
        node = {vkx.nov: vkx.cvs, vky.nov: vky.cvs}
        if vkx.dic[b1] == vky.dic[b1]:
            if vkx.dic[b2] != vky.dic[b2]:
                return vkx.clone('X', [b2], node)
        elif vkx.dic[b2] == vky.dic[b2]:
            if vkx.dic[b1] != vky.dic[b1]:
                return vkx.clone('X', [b1], node)
    return None

