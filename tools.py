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

def sat_conflict(sat1, sat2):
    intersection_bits1 = set(sat1).intersection(sat2)
    for b in intersection_bits1:
        if sat1[b] != sat2[b]:
            return True
    return False

def get_vk2sats(vk2, csatdic={}):
    d = vk2.dic
    sats = []
    b1, b2 = list(d.keys())
    v1, v2 = d.values()
    s1 = {b1: v1, b2: int(not v2)}
    if not sat_conflict(s1, csatdic):
        sats.append(s1)
    s2 = {b1: int(not(v1)), b2: v2}
    if not sat_conflict(s2, csatdic):
        sats.append(s2)
    s3 = {b1: int(not(v1)), b2: int(not v2)}
    if not sat_conflict(s3, csatdic):
        sats.append(s3)
    return sats

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

