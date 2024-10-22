from basics import *
import copy
from namepool import NamePool
from datetime import datetime

def outputlog(repo, vk1dic):
    now = datetime.now()
    ts = now.isoformat().split('.')[0] # cutoff more precision than sec.
    msg = f"{ts}: vkrepo log\n" + "="*80 + "\n"
    msg += f"bdic1:\n----------------------------------------------------\n"
    bitlst = sorted(set(repo.bdic1))  # all bits in sorted order
    for bit in bitlst:
        msg += f"{bit}: ["
        for kn in repo.bdic1[bit]:
            msg += f"{kn}  "
        msg += "]\n"
    msg += f"----------------------------------------------------\n\n"
    msg += f"bdic2:\n----------------------------------------------------\n"
    bitlst = sorted(set(repo.bdic2))  # all bits in sorted order
    for bit in bitlst:
        msg += f"{bit}: ["
        for kn in repo.bdic2[bit]:
            msg += f"{kn}  "
        msg += "]\n"
    msg += f"----------------------------------------------------\n\n"
    msg += f"vk1s:\n----------------------------------------------------\n"
    k1ns = sorted(repo.k1ns)
    for kn in k1ns:
        msg += vk1dic[kn].print_out() +'\n'
    msg += f"----------------------------------------------------\n\n"
    msg += f"vk2s:\n----------------------------------------------------\n"
    k2ns = sorted(repo.vk2dic)
    for kn in k2ns:
        vk2 = repo.vk2dic[kn]
        msg += vk2.print_out() +'\n'
    msg += f"----------------------------------------------------\n\n"
    msg += f"blocks:\n----------------------------------------------------\n"
    for bl in repo.blocks:
        msg += str(bl) + '\n'
    msg += f"----------------------------------------------------\n\n"
    msg += f"excls:\n----------------------------------------------------\n"
    kns = sorted(repo.excls)
    for kn in kns:
        msg += f"{kn}:\n"
        lst = repo.excls[kn]
        for excl in lst:
            msg += f"    {str(excl)}\n"
        msg += "\n"
    return msg

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

def cvs_subset(big_cvs, small_cvs):
    # check if small-cvs is a subset of big-cvs
    if type(big_cvs) == set and type(small_cvs) == set:
        cmm = small_cvs.intersection(big_cvs)
        if len(cmm) == 0: return None
        return cmm
    if type(big_cvs) == dict and type(small_cvs) == dict:
        res = big_cvs.copy()
        for nv, cvs in small_cvs.items():
            if nv not in big_cvs or not cvs.issubset(big_cvs[nv]):
                return None
            res[nv] = big_cvs - cvs
        return res


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

def cvs_intersect(vkx, vky): # tuple1: (nv1,cvs1), tuple2: (nv2,cvs2)
    '''
    #--- in case of set-typed vk.cvs, vk.nov plays a role
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
    #=======================================================================
    '''
    cvs1 = copy.deepcopy(vkx.cvs)
    cvs2 = copy.deepcopy(vky.cvs)
    if type(vkx.cvs) ==type(vky.cvs):
        if type(vkx.cvs) == set: # both are sets
            if vkx.nov != vky.nov: 
                return {vkx.nov: vkx.cvs.copy(), vky.nov: vky.cvs.copy()}
            cmm = vkx.cvs.intersection(vky.cvs)
            if len(cmm)==0: return None
            return {vkx.nov: cmm}
        else: # both vkx.cvs and vky.cvs are dicts
            if len(cvs1) == len(cvs2):
                tx = copy.deepcopy(cvs1)
                for nv, cvs in cvs1.items():
                    cmm = cvs.intersection(cvs2[nv])
                    if len(cmm) == 0: return None
                    tx[nv] = cmm
                return tx
            # vkx.cvs and vky.cvs are of diff length
            elif len(cvs1) > len(cvs2): # make sure t2 is the longer one
                cvs1, cvs2 = cvs2, cvs1 # swap 
            tx = copy.deepcopy(cvs1)      # tx copy from the shorter one
            for nv, cvs in cvs2.items():  # look thru the longer one
                if nv in cvs1:
                    cmm = cvs1[nv].intersection(cvs2[nv])
                    if len(cmm): return None
                    tx[nv] = cmm
                else:
                    tx[nv] = 99  # nv in tx is a wild-card
            return tx
    # vkx.cvs and vky.cvs are of different type: set/dict or dict/set
    elif type(cvs1) == set: # cvs2 is dict
        ts, td = cvs1, cvs2
        nov = vkx.nov
    else: # cvs2 is a set
        ts, td = cvs2, cvs1
        nov = vky.nov
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
            name = NamePool(vkx.kname).next_sname('D')
            vkx.cvs -= cmm
            vky.cvs -= cmm
            if vkx.dic[b1] == vky.dic[b1]:
                if vkx.dic[b2] != vky.dic[b2]:
                    return vkx.clone(name, [b2], cmm)
            elif vkx.dic[b2] == vky.dic[b2]:
                if vkx.dic[b1] != vky.dic[b1]:
                    return vkx.clone(name, [b1], cmm)
    else: # vkx.nov != vky.nov
        node = {vkx.nov: vkx.cvs.copy(), vky.nov: vky.cvs.copy()}
        name = NamePool(vkx.kname).next_uname('Y')
        if vkx.dic[b1] == vky.dic[b1]:
            if vkx.dic[b2] != vky.dic[b2]:
                return vkx.clone(name, [b2], node)
        elif vkx.dic[b2] == vky.dic[b2]:
            if vkx.dic[b1] != vky.dic[b1]:
                return vkx.clone(name, [b1], node)
    return None

def test_containment(d1, d2): # if d1 is contained in d2
    # contain means: for each entry(k/v) in d1, d2 has the same key, and
    # d1[k] is a subset of d2[k]
    for k, v in d1.items():
        if not d2[k].issuperset(v): return False
    return True


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
