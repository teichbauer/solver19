from datetime import datetime


def print_cvs(cvs):
    def print_set(s):
        msg = "("
        lst = sorted(s)
        for v in lst:
            msg += str(v)
        msg += ")"
        return msg
    
    if type(cvs) == set:
        return print_set(cvs)
    
    nvs = sorted(cvs, reverse=True) # novs-listed in reverse-order
    msg = ""
    for nv in nvs:
        cvsstr = print_set(cvs[nv])
        msg += f"{nv}:{cvsstr} "
    msg = msg.strip()
    return "{ " + msg + " }"

def pd(dic, more_space=False):
    ks = sorted(dic, reverse=True)
    dstr = "{ "
    for k in ks:
        if more_space:
            dstr += f"{k}:" + print_cvs(dic[k]).ljust(11,' ')
        else:
            dstr += f"{k}:" + print_cvs(dic[k]) + ' '
    dstr += "}"
    return dstr

def print_dic(dic):
    dstr = ""
    for b in sorted(dic, reverse=True):
        bstr = str(b).rjust(2,' ')
        dstr += f"{bstr}-{dic[b]} "
    dstr = dstr.strip()
    return "[" + dstr + "]"

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

def add_vk1(vk1,   # single-bit vk, with nov  and cvs on snode of nov
            vkdic, # {<kn>: <vk1>,...}
            bdic,  # {<bit>: [kn, kn,..]}
            kns):  # [kn, ..]
    name = vk1.kname
    lst = bdic.setdefault(vk1.bits[0], [])
    if name not in lst:
        lst.append(name)
    if name not in kns:
        kns.append(name)
    if vkdic != None and name not in vkdic:
        vkdic[name] = vk1


def remove_vk1(vk1, vkdic, bdic, kns):
    if type(vk1) == str:
        name = vk1
        vk1 = vkdic[vk1]
    else:
        name = vk1.kname
        bit = vk1.bits[0]
        if name in bdic[bit]:
            del bdic[bit][name]
            if len(bdic[bit]) == 0:
                del bdic[bit]
        if name in kns:
            kns.remove(name)
        return vkdic.pop(name)
    
def remove_vk2(vk2, vkdic, bdic, kns):
    if type(vk2) == str:
        name = vk2
        vk = vkdic[vk2]
    else:
        name = vk2.kname
    if kns != None and name in kns:
        kns.remove(name)
    for bit in vk2.bits:
        if name not in bdic[bit]:
            bdic[bit].remove(name)
            if len(bdic[bit]) == 0:
                del bdic[bit]
    if vkdic != None and name in vkdic:
        vkdic.pop(name)




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
        # x = 10
        # msg = "even" if x % 2 == 0 else "odd"  -> output: even
        kstr = str(k) if k > 9 else f" {str(k)}"
        m += f"{kstr}: {str(d[k])}, "
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

def merge_cvs(cvs0, cvs1): 
    xcvs = cvs0.copy()
    nvs0 = set(cvs0.keys())
    nvs1 = set(cvs1.keys())
    if nvs0 != nvs1: return None
    nvs = list(nvs0)
    if cvs0[nvs[0]] == cvs1[nvs[0]]:
        xcvs[nvs[1]] = xcvs[nvs[1]].union(cvs1[nvs[1]])
        return xcvs
    elif cvs0[nvs[1]] == cvs1[nvs[1]]:
        xcvs[nvs[0]] = xcvs[nvs[0]].union(cvs1[nvs[0]])
        return xcvs
    return None

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
    from utils.vklause import VKlause
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
