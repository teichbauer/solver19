from utils.basics import *
import copy

def outputlog(path):
    from datetime import datetime
    now = datetime.now()
    ts = now.isoformat().split('.')[0] # cutoff more precision than sec.
    msg = f"{ts}: vkrepo log\n" + "="*80 + "\n"
    msg += f"bdic1:\n----------------------------------------------------\n"
    bitlst = sorted(set(path.bdic1))  # all bits in sorted order
    for bit in bitlst:
        msg += f"{bit}: ["
        for kn in path.bdic1[bit]:
            msg += f"{kn}  "
        msg += "]\n"
    msg += f"----------------------------------------------------\n\n"
    msg += f"bdic2:\n----------------------------------------------------\n"
    bitlst = sorted(set(path.bdic2))  # all bits in sorted order
    for bit in bitlst:
        msg += f"{bit}: ["
        for kn in path.bdic2[bit]:
            msg += f"{kn}  "
        msg += "]\n"
    msg += f"----------------------------------------------------\n\n"
    msg += f"vk1s:\n----------------------------------------------------\n"
    k1ns = sorted(path.k1ns)
    for kn in k1ns:
        msg += vk1dic[kn].po() +'\n'
    msg += f"----------------------------------------------------\n\n"
    msg += f"vk2s:\n----------------------------------------------------\n"
    k2ns = sorted(path.vk2dic)
    for kn in k2ns:
        vk2 = path.vk2dic[kn]
        msg += vk2.po() +'\n'
    msg += f"----------------------------------------------------\n\n"
    msg += path.blckmgr.showall(True)
    msg += f"----------------------------------------------------\n\n"
    msg += f"excls:\n----------------------------------------------------\n"
    kns = sorted(path.excls)
    for kn in kns:
        msg += f"{kn}:\n"
        lst = path.excls[kn]
        for excl in lst:
            msg += f"    {pd(excl)}\n"
        msg += "\n"
    return msg

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

def handle_vk2pair(vkx, vky):
    assert type(vkx.cvs) == set, "vk2 shouldn't have dict cvs"
    assert type(vky.cvs) == set, "vk2 shouldn't have dict cvs"
    b1, b2 = vkx.bits # vkx and vky sit on the same 2 bits
    new_vk1 = None
    if vkx.nov == vky.nov:
        cmm = vkx.cvs.intersection(vky.cvs)
        if len(cmm) > 0:
            vkx.cvs -= cmm
            vky.cvs -= cmm
            if vkx.dic[b1] == vky.dic[b1]:
                if vkx.dic[b2] != vky.dic[b2]:
                    new_vk1 = vkx.clone("NewVk", [b2], {vkx.nov:cmm})
            elif vkx.dic[b2] == vky.dic[b2]:
                if vkx.dic[b1] != vky.dic[b1]:
                    new_vk1 = vkx.clone("NewVk", [b1], {vkx.nov:cmm})
    else: # vkx.nov != vky.nov
        node = {vkx.nov: vkx.cvs.copy(), vky.nov: vky.cvs.copy()}
        if vkx.dic[b1] == vky.dic[b1]:
            if vkx.dic[b2] != vky.dic[b2]:
                new_vk1 = vkx.clone("NewVk", [b2], node)
        elif vkx.dic[b2] == vky.dic[b2]:
            if vkx.dic[b1] != vky.dic[b1]:
                new_vk1 = vkx.clone("NewVk", [b1], node)
    return new_vk1

flip = lambda val: (val + 1) % 2

def print_vk2dic(vk2dic):
    for vk in vk2dic.values():
        print(vk.po())
