from basics import *
from stail import STail
from collections import OrderedDict

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

    for kn in snode.choice[3]: # all vk(kn) touching 1 bit o f snode's root
        # will result into vk2s
        if kn in snode.vkm.vkdic:
            vk = snode.vkm.pop_vk(kn)
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
