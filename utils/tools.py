from utils.basics import *
from center import Center
from utils.namedrive import NameDrive
import copy

def outputlog(repo, vk1dic):
    from datetime import datetime
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
        msg += vk1dic[kn].po() +'\n'
    msg += f"----------------------------------------------------\n\n"
    msg += f"vk2s:\n----------------------------------------------------\n"
    k2ns = sorted(repo.vk2dic)
    for kn in k2ns:
        vk2 = repo.vk2dic[kn]
        msg += vk2.po() +'\n'
    msg += f"----------------------------------------------------\n\n"
    msg += repo.blckmgr.showall(True)
    msg += f"----------------------------------------------------\n\n"
    msg += f"excls:\n----------------------------------------------------\n"
    kns = sorted(repo.excls)
    for kn in kns:
        msg += f"{kn}:\n"
        lst = repo.excls[kn]
        for excl in lst:
            msg += f"    {pd(excl)}\n"
        msg += "\n"
    return msg

def path_iterator(base): # base:[(10,20),(3,4),(a,b)]
    # -> (10,3,a),(10,3,b), (10,4,a),(10,4,b), (20,3,a),(20,3,b), ...
    res = []
    for i in range(len(base)):
        for s60 in base[0]:
            res.append(s60)
            for s57 in base[1]:
                res.append(s57)
                for s54 in base[2]:
                    res.append(s54)
                    yield tuple(res)
                    res.pop()
                res.pop()
            res.pop()
# -------------------------------

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


def cvs_intersect(vkx, vky): # vkx is vk1, vky: vk1 or vk2
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
    # assert nov in td    # don't know yet what to do ???
    # (57, {2,3}) + (60,{60:(1,2,3}, 57:{3,4,6}}) => 
    # ts:(57, {2,3})  td: (60,{60:(1,2,3}, 57:{3,4,6}})
    # return {60:(1,2,3), 57:{3}}
    if nov in td:
        cmm = ts.intersection(td[nov])
        if len(cmm) == 0: return None
        tx = td.copy()
        tx[nov] = cmm
        return tx
    td[nov] = vky.cvs
    return td

def handle_vk2pair(vkx, vky):
    assert type(vkx.cvs) == set, "vk2 shouldn't have dict cvs"
    assert type(vky.cvs) == set, "vk2 shouldn't have dict cvs"
    b1, b2 = vkx.bits # vkx and vky sit on the same 2 bits
    new_vk1 = None
    if vkx.nov == vky.nov:
        cmm = vkx.cvs.intersection(vky.cvs)
        if len(cmm) > 0:
            name = NameDrive.dname()
            vkx.cvs -= cmm
            vky.cvs -= cmm
            if vkx.dic[b1] == vky.dic[b1]:
                if vkx.dic[b2] != vky.dic[b2]:
                    new_vk1 = vkx.clone(name, [b2], cmm)
            elif vkx.dic[b2] == vky.dic[b2]:
                if vkx.dic[b1] != vky.dic[b1]:
                    new_vk1 = vkx.clone(name, [b1], cmm)
    else: # vkx.nov != vky.nov
        node = {vkx.nov: vkx.cvs.copy(), vky.nov: vky.cvs.copy()}
        name = NameDrive.dname()
        if vkx.dic[b1] == vky.dic[b1]:
            if vkx.dic[b2] != vky.dic[b2]:
                new_vk1 = vkx.clone(name, [b2], node)
        elif vkx.dic[b2] == vky.dic[b2]:
            if vkx.dic[b1] != vky.dic[b1]:
                new_vk1 = vkx.clone(name, [b1], node)
    if new_vk1:
        new_vk1.source = vkx.kname
        if type(new_vk1.cvs) == set:
            new_vk1.cvs = {new_vk1.nov: new_vk1.cvs}
        return new_vk1
    return None

def test_containment(d1, d2): # d1: new, d2: old. both are dict
    diffs = []
    d1_in_d2 = [] # novs where short[nov] is subset of long[nov]
    d2_in_d1 = [] # novs where long[nov] is subset of short[nov]
    sames = []
    # in case d1/d2 have same nof nov, but they are diff: not mergable
    leng = len(d1)
    for nv, vs in d1.items():
        if vs.issubset(d2[nv]):       # d1 in d2
            d1_in_d2.append(nv)        # add to lng_in_short
            if vs.issuperset(d2[nv]): # short also in long
                sames.append(nv)           # they are same
        elif vs.issuperset(d2[nv]):   # short in long
            d2_in_d1.append(nv)        # add to short_in_long
        else:
            diffs.append(nv)           # they are different
    if len(diffs) > 1: return None     # more than 1 diff nov: not mergable
    if len(sames) == leng:  return {'cat': 'same'}
    if len(d2_in_d1) == leng:
        return { 'cat': 'contain: d2 in d1'}
    if len(d1_in_d2) == leng:
        return { 'cat': 'contain: d1 in d2'}
    if len(diffs) == 1 and len(sames) == leng - 1:
        return {'cat': 'mergable', 'merge-nov': diffs[0]}
    return None # log-in-short:1 and short-in-long:1 ->None

def vk1s_unify_test(new_vk, old_vk):
    if new_vk.bit != old_vk.bit or new_vk.val != old_vk.val:
        return True # to be added (no duplication)
    if type(new_vk.cvs) != dict or type(old_vk.cvs) != dict: return None
    res = test_containment(new_vk.cvs, old_vk.cvs)
    if not res: return True # to be added (no duplication)
    if res['cat'].startswith('contain'):
        lst = res['cat'].split(':')[1].split() # [d1, in, d2]
        # returning the containing vk.kname
        if lst[2] == 'd2':  # new-vk is contained in old-vk
            return False    # new_vk should not be added to repo
        if lst[2] == 'd1':  # new-vk contains the old-vk
            old_vk.cvs = copy.deepcopy(new_vk.cvs)
            return False
    if res['cat'] == 'same': return False
    if res['cat'] == 'mergable':
        old_vk.cvs[res['merge-nov']].update(new_vk.cvs[res['merge-nov']])
        # return res['merge-nov']
        return False
    raise Exception(f"test_containment returns: {res}")

def fill_dict(chvdic, dic):
    for nv in chvdic:
        if nv not in dic:
            dic[nv] = set(chvdic[nv])
    return dic

def expand_vk1s(repo, vk1=None):
    if vk1:
        if type(vk1.cvs) == set:
            vk1.cvs = {vk1.nov: vk1.cvs}
        fill_dict(repo.driver.chvdic, vk1.cvs)
    else:
        for kn in repo.k1ns:
            vk1 = Center.vk1dic[kn]
            expand_vk1s(repo, vk1)

def expand_excls(repo):
    for kn, lst in repo.excls.items():
        for dic in lst:
            fill_dict(repo.driver.chvdic, dic)

def is_single(node):
    for cvs in node.values():
        if len(cvs) > 1: return False
    return True

def break_node(node, Seq):
    # all values in node is a single valued set - node is single, no break
    if is_single(node): return True 
    return Seq(node) # returna generator

def print_vk2dic(vk2dic):
    for vk in vk2dic.values():
        print(vk.po())
