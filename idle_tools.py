from tools import *

def reduce_cvs(vk, cmm):
    '''
    # reduce vk.cvs by cmm, where it has been certain, cmm is subset
    # of vk.cvs. 2 cases:
    # 1. vk.cvs and cmm are sets like vk.cvs:{0,1,2,3} and cmm: {2,3}
    #    vk.cvs is reduces by cmm becomes: vk.cvs == {0,1}
    # 2. vk.cvs:{60:(0,1,2,3}, 57: {1,3,5}}, cmm: {60:{1}, 57:{3}}
    #    vk.cvs is then reduced by cmm and becomes
    #    {60:(0,2,3}, 57: {1,5}}
    '''
    if type(vk.cvs) == set:
        if type(cmm) == set:
            vk.cvs -= cmm
        else: # cmm: {57:{2,3}}
            vk.cvs -= cmm[vk.nov]
    else: # vk.cvs is a dict
        if type(cmm) == set:
            vk.cvs[vk.nov] -= cmm
        else: # cmm is a dict
            for nv, s in cmm.items():
                vk.cvs[nv] -= s
    return vk


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

def vk1s_mergable(vk1a, vk1b):
    if vk1a.nov != vk1b.nov or vk1a.bit != vk1b.bit: return False
    if vk1a.kname[0] not in ('U','V') or vk1b.kname[0] not in ('U','V'): 
        return False
    return vk1a.cvs[vk1a.nov] == vk1b.cvs[vk1a.nov]

def merge_vk1_to_ovk1(vk1, ovk1):
    nvs = list(vk1.cvs)  # get the novs as a list
    nvs.remove(vk1.nov)
    for nv in nvs:
        for cv in vk1.cvs[nv]:
            ovk1.cvs[nv].add(cv)
    return ovk1

def condense(vepro):
    # compact blocks
    res = []
    for bl in vepro.blocks:
        if bl not in res:
            res.append(bl)
    vepro.blocks = res
    # compact excls
    for kn, lst in vepro.excls.items():
        res = []
        for excl in lst:
            pass

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
