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


def cvs_intersect(tp1, tp2): # tuple1: (nv1,cvs1), tuple2: (nv2,cvs2)
    '''#--- in case of set-typed cvs, nv1 or nv2 plays a role
    # 1：(60, {1,2,3}) + (60,{2,4,6})          =>  {60:{2}}
    # 2: (60, {1,2,3}) + (60,{0,4,6})          =>  None: no common cv
    # 3: (60, {1,2,3}) + (57, {0, 1, 2, 3}) =>{60:{1,2,3}, 57:{0,1,2,3}}
    #--- in case a cvs is a dict, its nv can be ignored
    ## if both are dict, one entry with no intersection leads to None-return
    # 4: (60, {1,2,3}) + (60, {60:(2,3}, 57:{0,4} })   => {60:{2}, 57:{0,4}}
    # 5: (60, {1,2,3}) + (60, {60:(0,4}, 57:{0,4} })   => None
    # 6: (60,{60:(1,2,3), 57:(0,4} }) + (57,{60:{0}, 57:{0,4} }) => None
    # 7: (60,{60:(1,2,3), 57:(0,4} }) + (57,{60:{2}, 57:{0,4} }) 
    #     => {60:{2}, 57:{0,4}}
    #======================================================================='''
    t1 = type(tp1[1])
    t2 = type(tp2[1])
    if t1 == t2:
        if t1 == set:
            if tp1[0] != tp2[0]: 
                return {tp1[0]: tp1[1], tp2[0]: tp2[1]}
            cmm = tp1[1].intersection(tp2[1])
            if len(cmm)==0: return None
            return {tp1[0]: cmm}
        else: # both t1 and t2 are dicts
            l1 = len(t1)
            l2 = len(t2)
            if l1 == l2:
                tx = t1.copy()
                for nv, cvs in t1.items():
                    cmm = cvs.intersection(t2[nv])
                    if len(cmm) == 0: return None
                    tx[nv] = cmm
                return tx
            # t1 and t2 are of diff length
            elif l1 > l2: # make sure t2 is the longer one
                t1, t2 = t2, t1 # swap 
            tx = t1.copy()      # tx copy from the shorter one
            for nv, cvs in t2.items():  # look thru the longer one
                if nv in t1:
                    cmm = t1[nv].intersection(t2[nv])
                    if len(cmm): return None
                    tx[nv] = cmm
                else:
                    tx[nv] = 99  # nv in tx is a wild-card
            return tx
    elif t1 == set: # t2 is dict
        ts = tp1[1]
        td = tp2[1]
        nov = tp1[0]
    else: # t2 == set
        ts = tp2[1]
        td = tp1[1]
        nov = tp2[0]
    assert nov in td    # don't know yet what to do ???
    # (57, {2,3}) + (60,{60:(1,2,3}, 57:{3,4,6}}) => 
    # ts:(57, {2,3})  td: (60,{60:(1,2,3}, 57:{3,4,6}})
    # return {60:(1,2,3), 57:{3}}
    cmm = ts.intersection(td[nov])
    if len(cmm) == 0: return None
    tx = td.copy()
    tx[nov] = cmm
    return tx

def handle_vk2pair(vkx, vky):
    assert type(vkx.cvs) == set, "vk2-pair with no-set cvs"
    assert type(vky.cvs) == set, "vk2-pair with no-set cvs"
    b1, b2 = vkx.bits
    if vkx.nov == vky.nov:
        cmm = vkx.cvs.intersection(vky.cvs)
        if len(cmm) > 0:
            if vkx.dic[b1] == vky.dic[b1]:
                if vkx.dic[b2] != vky.dic[b2]:
                    vkx.cvs -= cmm
                    vky.cvs -= cmm
                    return vkx.clone('D', [b2], cmm)
            elif vkx.dic[b2] == vky.dic[b2]:
                if vkx.dic[b1] != vky.dic[b1]:
                    vkx.cvs -= cmm
                    vky.cvs -= cmm
                    return vkx.clone('D', [b1], cmm)
    else: # vkx.nov != vky.nov
        node = {vkx.nov: vkx.cvs, vky.nov: vky.cvs}
        if vkx.dic[b1] == vky.dic[b1]:
            if vkx.dic[b2] != vky.dic[b2]:
                return vkx.clone('X', [b2], node)
        elif vkx.dic[b2] == vky.dic[b2]:
            if vkx.dic[b1] != vky.dic[b1]:
                return vkx.clone('X', [b1], node)
    return None


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
