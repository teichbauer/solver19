import sys
import time
from utils.basics import get_sdic, ordered_dic_string, verify_sat, display_vkdic
from center import Center
from utils.satholder import SatHolder
from satnode import SatNode
from utils.vkmgr import VKManager
from utils.vklause import VKlause


def make_vkdic(kdic):
    vkdic = {}
    for kn, klause in kdic.items():
        vkdic[kn] = VKlause(kn, klause)
    return vkdic


def make_vkm(cnf_fname):
    vkdic = get_vkdic_from_cfg(cnf_fname)
    vkm = VKManager(vkdic, True) # initial: True
    Center.set_init(vkm)
    return vkm


def process(cnfname):
    vkm = make_vkm(cnfname)
    satslots = list(range(Center.maxnov))
    sh = SatHolder(satslots)
    sn = SatNode(None, sh, vkm)  # parent: None
    return sn.spawn()


def get_vkdic_from_cfg(cfgfile):
    sdic = get_sdic(cfgfile)
    Center.set_maxnov(sdic["nov"])
    vkdic = make_vkdic(sdic["kdic"])
    return vkdic


def work(configfilename, verify=True):
    start_time = time.time()
    sats = process(configfilename)
    now_time = time.time()
    time_used = now_time - start_time
    ln = len(sats)
    print(f"there are {ln} sats:")

    for ind, sat in enumerate(sats):
        msg, cnt2 = ordered_dic_string(sat)
        if cnt2 > 0:
            m = f"{ind+1}({2**cnt2}):"
        else:
            m = f"{ind+1}:"
        m += msg
        if verify:
            verified = verify_sat(Center.orig_vkm.vkdic, sat)
            m += f", verified: {verified}"
        print(m)
    print(f"Time used: {time_used}")


if __name__ == "__main__":
    # configfilename = 'cfg100-450.json'
    configfilename = "cfg60-266.json"
    # configfilename = 'cfg60-280.json'
    # configfilename = 'cfg60-262.json'
    # configfilename = 'config1.json'
    # configfilename = 'cfg12-45.json'
    # configfilename = 'cfg12-55.json'

    if len(sys.argv) > 1:
        configfilename = sys.argv[1].strip()

    work(configfilename)

    x = 1
