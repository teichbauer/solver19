from datetime import datetime


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


def verify_sat(vkdic, sat, collect=False):
    lst = set([])
    for vk in vkdic.values():
        if vk.hit(sat):
            if collect:
                lst.add(vk.kname)
            else:
                return False
    if collect and len(lst) > 0:
        return lst
    return True


def nov_val(msg):  # '12.4' -> 12, 4
    lst = []
    for m in msg.split("."):
        lst.append(int(m))
    return lst


def get_bit(val, bit):
    return (val >> bit) & 1


def set_bit(val, bit_index, new_bit_value):
    """Set the bit_index (0-based) bit of val to x (1 or 0)
    and return the new val.
    the input param val remains unmodified, for val is passed-in by-value !
    """
    mask = 1 << bit_index  # mask - integer with just the chosen bit set.
    val &= ~mask  # Clear the bit indicated by the mask (if x == 0)
    if new_bit_value:
        val |= mask  # If x was True, set the bit indicated by the mask.
    return val  # Return the result, we're done.


def set_bits(val, d):
    for b, v in d.items():
        val = set_bit(val, b, v)
    return val


def oppo_binary(binary_value):
    return (binary_value + 1) % 2


def get_sdic(filename):
    path = "./configs/" + filename
    sdic = eval(open(path).read())
    return sdic


def ordered_dic_string(d):
    m = "{ "
    ks = sorted(d.keys(), reverse=True)
    for k in ks:
        m += str(k) + ": " + str(d[k]) + ", "
    m = m.strip(", ")
    m += " }"
    return m


def print_json(nov, vkdic, fname):
    sdic = {"nov": nov, "kdic": {}}
    for kn, vk in vkdic.items():
        sdic["kdic"][kn] = vk.dic
    ks = sorted(list(sdic["kdic"].keys()))

    with open(fname, "w") as f:
        f.write("{\n")
        f.write('    "nov": ' + str(sdic["nov"]) + ",\n")
        f.write('    "kdic": {\n')
        # for k, d in sdic['kdic'].items():
        for k in ks:
            msg = ordered_dic_string(sdic["kdic"][k])[0]
            line = f'        "{k}": {msg},'
            f.write(f"{line}\n")
        f.write("    }\n}")


def topvalue(vk):
    # shift all bit to top positions and return that n-bits value
    # E.G. {7:1, 5:0, 0:1} -> 101/5
    bits = vk.bits[:]
    v = 0
    while bits:
        v = (v << 1) | vk.dic[bits.pop(0)]
    return v


def topbits(nov, nob):
    lst = list(range(nov)[-nob:])
    lst.reverse()
    return lst


def vkdic_remove(vkdic, kns):
    """remove vk from vkdic, if vk.kname is in kns(a list)"""
    kd = {}
    for kn, vk in vkdic.items():
        if kn not in kns:
            kd[kn] = vk
    return kd


def display_vkdic(vkd, title=None, outfile=None):
    kns = list(vkd.keys())
    kns.sort()
    if outfile:
        now = datetime.now()
        with open(outfile, 'w') as ofile:
            ofile.write(f"{now.isoformat()}\n----------------------\n")
            if title:
                ofile.write(f"{title}\n---------\n")
            for kn in kns:
                vk = vkd[kn]
                msg, dummy = ordered_dic_string(vk.dic)
                ofile.write(f"{kn}: {msg}\n")
    else:
        if title:
            print(title)
        for kn in kns:
            vk = vkd[kn]
            print(f"{kn}: " + ordered_dic_string(vk.dic)[0])
        print("-------------")


def testing(bgrid):
    from vklause import VKlause
    """ 
    cvd:[0,5]/000, 101
    bits: 16,6,1
    """
    vk1 = VKlause('vk1', {16: 0, 6: 0})
    vk2 = VKlause('vk2', {16: 0, 6: 1})
    vk3 = VKlause('vk3', {16: 1, 6: 0})
    vk4 = VKlause('vk4', {16: 1, 6: 1})
    vk5 = VKlause('vk5', {16: 0, 1: 0})
    vk6 = VKlause('vk6', {16: 0, 1: 1})
    vk7 = VKlause('vk7', {16: 1, 1: 0})
    vk8 = VKlause('vk8', {16: 1, 1: 1})
    vk9 = VKlause('vk9', {6: 0, 1: 0})
    vkA = VKlause('vkA', {6: 0, 1: 1})
    vkB = VKlause('vkB', {6: 1, 1: 0})
    vkC = VKlause('vkC', {6: 1, 1: 1})
    vkD = VKlause('vkD', {16: 0, 10: 1})
    vkE = VKlause('vkE', {16: 1, 10: 1})
    vkF = VKlause('vkF', {6: 0, 10: 1})
    vkG = VKlause('vkG', {6: 1, 10: 1})
    vkH = VKlause('vkH', {1: 0, 10: 1})
    vkI = VKlause('vkI', {1: 1, 10: 1})

    x = 1
