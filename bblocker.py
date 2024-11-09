from center import Center
from utils.sequencer import Sequencer
from utils.cvsnodetools import *
import copy

class BitBlocker:
    # on a bit in repo.bdic1: {bit: {0: BitBlocker(), 1:BitBlocker()}}
    def __init__(self, bit, val, repo):
        self.bit = bit
        self.val = val
        self.nodes = [] # list of nodes
        self.repo = repo
        self.log = []

    def add(self, node, infos=None):
        if is_single(node):
            node_to_lst(node, self.nodes)
        else:
            doit = node_seq(node)
            while not doit.done:
                nd = doit.get_next()
                self.add(nd, infos)
        if len(infos) > 0: self.log.append(infos.pop())
        return self

    def filter_nodes(self, nodes, nd):
        pnds = []
        for nx in nodes:
            cmm = node_intersect(nx, nd)
            if cmm:
                pnds.append(cmm)
        return pnds

    def filter_vk2(self, vk2, new_vk1): # vk2 can generate vk1 or not: (T/F)
        if new_vk1:
            vk1 = vk2.clone('_', [self.bit], {vk2.nov: set()})
        else: vk1 = None
        for nd in self.nodes:
            nv, cvs = tuple(nd.items())[0] # nd can only have 1 nv/cvs entry
            assert(vk2.nov == nv),"nov wrong in bb"
            cmm = cvs.intersection(vk2.cvs)
            if len(cmm) == 0: continue
            vk2.cvs -= cmm
            if vk1: vk1.add_cvs(cmm, vk2.nov)
        if vk1 and len(vk1.cvs[vk2.nov]) > 0:
            bb_dic = self.repo.bdic1.setdefault(vk1.bit, {})
            bb = bb_dic[vk1.val] = BitBlocker(vk1.bit, vk1.val, self.repo)
            bb.add(vk1.cvs, [f"from {vk2.kname}: {vk1.bit}/{vk1.val}"]) 
            if vk1.bit in self.repo.bdic2:
                kns = self.bdic2[vk1.bit]
                for kn in kns:
                    xvk2 = self.repo.vk2dic[kn]
                    xval = xvk2.dic[vk1.bit]
                    bb.filter_vk2(xvk2, vk1.val != xval)

    def merge_add(self, val, node, info=None, nlst=None):
        pass

    def merge_check_vk2(self, vk2):
        if self.bit not in vk2.bits: return # vk2 shares no bit
        node = {vk2.nov: vk2.cvs}
        val = vk2.dic[self.bit]
        excl_nodes = self.ndic[val]
        blck_nodes = self.ndic[flip(val)]

        for nd in excl_nodes:
            x = 0

        for nd in blck_nodes:
            x = 0

