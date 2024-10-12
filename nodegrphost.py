from center import Center
import copy
from tools import handle_vk2pair
from basics import add_vk1, add_vk2, merge_cvs

def cvs_intersect(tp1, tp2): # tuple1: (nv1,cvs1), tuple2: (nv2,cvs2)
    '''#--- in case of set-typed cvs, nv1 or nv2 plays a role
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
    #======================================================================='''
    t1 = type(tp1[1])
    t2 = type(tp2[1])
    if t1 == t2:
        if t1 == set:
            if tp1[0] != tp2[0]: 
                return {tp1[0]: tp1[1], tp2[0]: tp2[1]}
            cmm = tp1[1].intersection(tp2[1])
            if len(cmm)==0: return None
            return {tp1[0]: cmm}
        else: # both t1 and t2 are dicts
            l1 = len(t1)
            l2 = len(t2)
            if l1 == l2:
                tx = t1.copy()
                for nv, cvs in t1.items():
                    cmm = cvs.intersection(t2[nv])
                    if len(cmm) == 0: return None
                    tx[nv] = cmm
                return tx
            # t1 and t2 are of diff length
            elif l1 > l2: # make sure t2 is the longer one
                t1, t2 = t2, t1 # swap 
            tx = t1.copy()      # tx copy from the shorter one
            for nv, cvs in t2.items():  # look thru the longer one
                if nv in t1:
                    cmm = t1[nv].intersection(t2[nv])
                    if len(cmm): return None
                    tx[nv] = cmm
                else:
                    tx[nv] = 99  # nv in tx is a wild-card
            return tx
    elif t1 == set: # t2 is dict
        ts = tp1[1]
        td = tp2[1]
        nov = tp1[0]
    else: # t2 == set
        ts = tp2[1]
        td = tp1[1]
        nov = tp2[0]
    assert nov in td    # don't know yet what to do ???
    # (57, {2,3}) + (60,{60:(1,2,3}, 57:{3,4,6}}) => 
    # ts:(57, {2,3})  td: (60,{60:(1,2,3}, 57:{3,4,6}})
    # return {60:(1,2,3), 57:{3}}
    cmm = ts.intersection(td[nov])
    if len(cmm) == 0: return None
    tx = td.copy()
    tx[nov] = cmm
    return tx


class NodeGroupHost:
    # class variables:
    # node: {60:{2,3,4}, 57:{0,1}, 54: {2},..}
    excl_dic = {} # {<kn>: [<node1>,..] k2n should be excluded from nodes
    blocks = []  # [<node>,<node>,...] these nodes are hit(dead)

    def __init__(self, snode):     # root-bitgrid of the snode
        self.nov = snode.nov
        self.bdic2 = copy.deepcopy(snode.bdic2)
        self.vk2dic = snode.vk2dic.copy()
        self.bdic1 = copy.deepcopy(snode.bdic1)
        self.k1ns = snode.k1ns.copy()

    def merge_down(self, lsnode):
        for kn in lsnode.k1ns:  
            # add vk1s from lsnode to self. Center already has them
            add_vk1(Center.vk1dic[kn],
                    None,   # no vk1dic, since Center.vk1dic already has it
                    self.bdic1, self.k1ns)  # add to self.k1ns
        for vk2 in lsnode.vk2dic.values():
            add_vk2(vk2, self.vk2dic, self.bdic2, None) # no self.k2ns
        self.find_root_vk1(lsnode)
        self.grow()

    def merge_snode(self, lsnode):
        self.find_root_vk1(lsnode)
        for kn in lsnode.k1ns:
            self.putin_vk1(Center.vk1dic[kn])
        for kn, vk in lsnode.vk2dic.items():
            self.putin_vk2(vk)
        x = 9
    
    def putin_block(self, blck):
        if blck:
            self.blocks.append(blck)

    def _vk1andvk2(self, vk1bit, vk1, vk2):
        cmm_cvs = cvs_intersect((vk1.nov,vk1.cvs),(vk2.nov,vk2.cvs))
        if not cmm_cvs: return
        self.add_excl(vk2.kname, cmm_cvs)
        if vk2.dic[vk1bit] != vk1.dic[vk1bit]:
            xvk1 = vk2.clone('U', [vk1bit], cmm_cvs)
            self.putin_vk1(xvk1)
        else:
            x = 0

    def putin_vk1(self, vk1):
        if not self.add_vk1(vk1): return
        b = vk1.bits[0]
        kns = self.bdic1.setdefault(b,[])
        for kn in kns:
            if kn == vk1.kname: continue
            vk = Center.vk1dic[kn]
            if vk.dic[b] != vk1.dic[b]:
                block = cvs_intersect((vk1.nov, vk1.cvs), (vk.nov, vk.cvs))
                self.putin_block(block)
        if b in self.bdic2:
            for kn in self.bdic2[b]:
                if kn[1:] == vk1.kname[1:]: continue
                self._vk1andvk2(b, vk1, self.vk2dic[kn])
        else:
            x = 0

    def putin_vk2(self, vk2):
        xbits2 = set(self.bdic1).intersection(vk2.bits)
        for b in xbits2:
            for k1n in self.bdic1[b]:
                self._vk1andvk2(b, Center.vk1dic[k1n], vk2)
        k2ns = list(self.vk2dic)
        for kn in k2ns:
            xvk = self.vk2dic[kn]
            if xvk.bits == vk2.bits:
                vk1x = handle_vk2pair(xvk, vk2)
                if vk1x:
                    self.putin_vk1(vk1x)
            add_vk2(vk2, self.vk2dic, self.bdic2, None)


    def grow(self):
        xbits = list(set(self.bdic1).intersection(self.bdic2))
        while len(xbits) > 0:
            nbdic1 = {}
            xbits.sort()
            for b in xbits:
                k1ns = self.bdic1[b]
                for k1n in k1ns:
                    vk1 = Center.vk1dic[k1n]
                    k2ns = self.bdic2[b]
                    for k2n in k2ns:
                        nvk1 = None
                        if k2n[1:] == k1n[1:]: continue
                        vk2 = Center.vk2dic[k2n]
                        if k1n[0] in ('U','V','R'): #vk1.cvs dict{nov1:,nov2:}
                            node = vk1.cvs.copy()
                            cmm_cvs = vk2.cvs.intersection(node[vk2.nov])
                            if len(cmm_cvs) == 0: continue
                            node.update({vk2.nov:cmm_cvs})
                            self.add_excl(k2n, node) # ??
                            if vk2.dic[b] != vk1.dic[b]:
                                nvk1 = vk2.clone('U', [b], node)
                        else: # vk1 is a S/T, not a compound:
                            if vk2.nov == vk1.nov:
                                if k2n[0] == 'C': continue 
                                else: x = 0 # can this happen?
                            elif k2n[0] == 'C': 
                                node = {vk1.nov:vk1.cvs, vk2.nov:vk2.cvs}
                                if vk2.dic[b] != vk1.dic[b]:
                                    nvk1 = vk2.clone('U', [b], node)
                                self.add_excl(k2n, node) # ??
                            else: x = 0 # can this happen?
                        if nvk1:
                            if not self.add_vk1(nvk1): continue # not added
                            self.add_block(nvk1)
                            nbdic1.setdefault(nvk1.bits[0],[]).append(nvk1.kname)
            xbits = list(set(nbdic1).intersection(self.bdic2))

    def find_root_vk1(self, xsn):
        bdic1_rbits = set(self.bdic1).intersection(xsn.bgrid.bits)
        for rb1 in bdic1_rbits:
            for k1n in self.bdic1[rb1]:
                vk1 = Center.vk1dic[k1n]
                cvs = xsn.bgrid.cvs_subset(vk1.bits[0], vk1.dic[vk1.bits[0]])
                # these cvs are hits with vk1.cvs node
                cmm_cvs = cvs_intersect((vk1.nov, vk1.cvs),(xsn.nov, cvs))
                self.blocks.append(cmm_cvs)
        cmm_rbits = set(self.bdic2).intersection(xsn.bgrid.bits)
        for rb in cmm_rbits:
            for k2n in self.bdic2[rb]:
                vk2 = self.vk2dic[k2n]
                if set(vk2.bits).issubset(xsn.bgrid.bits):
                    hit_cvs = xsn.bgrid.vk2_hits(vk2)
                    print(f"{k2n} inside {xsn.nov}-root, blocking {hit_cvs}")
                    self.blocks.append({vk2.nov:vk2.cvs, xsn.nov: hit_cvs})
                else:# vk1.cvs is compound  caused by overlapping 
                    # with xsn.root-bits, will be named with R-prefix
                    x_cvs_subset = xsn.bgrid.cvs_subset(rb, vk2.dic[rb])
                    node = {vk2.nov: vk2.cvs, xsn.nov: x_cvs_subset}
                    if self.add_excl(k2n, node):
                        vk1 = vk2.clone('R',[rb], node) # R prefix, drop rb
                        if self.add_vk1(vk1):
                            self.add_block(vk1)

    def add_vk1(self, vk1):
        def mergeable(vkx, vky):
            bitx = vkx.bits[0]
            bity = vky.bits[0]
            if bitx != bity or vkx.dic[bitx] != vky.dic[bitx]:
                return None
            if type(vkx.cvs) == dict and type(vky.cvs) == dict:
                merged_cvs = merge_cvs(vkx.cvs, vky.cvs)
                if merged_cvs:
                    vkx.cvs = merged_cvs
                    return vkx
            return None
                   
        name = vk1.kname
        # a vk2 may have both of its bits turned to vk1. So the prefix
        # 'U' may have been used. In that case, use 'V' as vk1 name prefix
        if name in self.k1ns:
            xvk1 = Center.vk1dic[name]
            if xvk1.equal(vk1): return False
            if mergeable(xvk1, vk1): # merge into xvk1
                return False  
            else:
                name = f"V{name[1:]}"
                if name in self.k1ns:
                    xvk1 = Center.vk1dic[name]
                    if xvk1.equal(vk1): return False
                    if mergeable(xvk1, vk1): # merge into xvk1
                        return False
                    print("special case occurs here")
                else:
                    vk1.kname = name
        add_vk1(vk1, None,  # vk1dic is only held in Center.vk1dic
                self.bdic1, 
                self.k1ns)
        Center.add_vk1(vk1)
        return True

    def add_block(self, vk1):
        # see if this vk1 causes a block, if yes, add the block to self.blocks
        def set2node(s, set_nov, node):
            if set_nov in node:
                xset = s.intersection(node[set_nov])
                if len(xset) > 0:
                    xnode = node.copy()
                    xnode.update({set_nov: xset})
                    return xnode
                else: return None
            else:
                print("weird-01")
                return None

        def node2node(n1, n2):
            xnode = n1.copy()
            for nv, st in n2.items():
                if nv in xnode:
                    xs = st.intersection(xnode[nv])
                    if len(xs) == 0:
                        return None
                    xnode.update({nv: xs})
            return xnode

        # see if vk1 is causing block-node(s)
        bit = vk1.bits[0]
        k1ns = self.bdic1[bit]
        for k1n in k1ns:
            if vk1.kname == k1n: continue
            xvk1 = Center.vk1dic[k1n]
            res = None
            if xvk1.dic[bit] != vk1.dic[bit]:
                if type(vk1.cvs) == dict:
                    if type(xvk1.cvs) == dict:
                        res = node2node(vk1.cvs, xvk1.cvs)
                    else:   # xvk1.cvs is a set
                        res = set2node(xvk1.cvs, xvk1.nov, vk1.cvs)
                else:  # vk1.cvs is a set
                    if type(xvk1.cvs) == dict:
                        res = set2node(vk1.cvs, vk1.nov, xvk1.cvs)
                    else: # both are sets
                        print("what to do?")
            if res and (res not in self.blocks):
                self.blocks.append(res)

    def add_excl(self, k2n, node):
        lst = self.excl_dic.setdefault(k2n, [])
        if node in lst: return False
        for d in lst:
            for nv, cvs in node.items():
                contained = nv in d and cvs.issubset(d[nv])
                if not contained: break
            if contained: return False
        lst.append(node)
        return True

