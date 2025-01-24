import sys, copy
import time
from utils.basics import ordered_dic_string, verify_sat, display_vkdic
from center import Center
from utils.satholder import SatHolder
from satnode import SatNode
from utils.vkmgr import VKManager
from utils.vklause import VKlause

def get_vkdic_from_cfg(cfgfile):
    # file_path: a json file:
    #  { 'kdic': { 'C0001':{7: 1, 14: 0, 30: 0},.. },  ## 266 3-sat clauses
    #    'nov': 60,                                    ## 60 variables
    #  }
    file_path = "./configs/" + cfgfile
    sdic = eval(open(file_path).read()) # {'kdic:.., 'nov':60}}
    Center.set_maxnov(sdic["nov"]) # Center.maxnov=60, .bits: {0,1,..59}
    vkdic = {}
    for kn, klause in sdic['kdic'].items():
        vkdic[kn] = VKlause(kn, klause)
    return vkdic

def process(cnfname):
    vkdic = get_vkdic_from_cfg(cnfname)
    Center.set_init(vkdic)  # make copy into Center.origin_vkdic
    # VKMgr is a wrapper of vkdic, with some tools
    vkm = VKManager(vkdic, True) # initial: True
    satslots = list(range(Center.maxnov)) # [0,1,2,..59]
    sat_holder = SatHolder(satslots)
    sn = SatNode(None, sat_holder, vkm)  # parent: None
    return sn.spawn()

def work(configfilename, verify=True):
    start_time = time.time()
    # generating sats - the major task
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
