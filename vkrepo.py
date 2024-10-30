from center import Center
from tools import *
from namedrive import NameDrive
import copy

class VKRepoitory:
    def __init__(self, snode):
        self.bdic1 = {}     # {bit: [k1n, k1n,..], bit:[], ..}
        self.bdic2 = {}     # {bit: [k2n, k2n,..], bit:[], ..}
        self.k1ns = []      # [k1n, k1n,..]
        self.vk2dic = {}    # {k2n:vk2, k2n: vk2,...}
        self.blocks = []    # [node, ..] node:{nov:cvs, nv:..} where snode fails
        self.excls = {}     # {kn:[node, node,..],..} vk not 2b used in nodes
        self.snode = snode  # related snode
        self.pathsteps = [snode.nov]
        self.inflog = {}    # {key:[info,info,..], key:[], ...}

    def write_logmsg(self, outfile_name):
        ofile = open(outfile_name, 'w')
        msg = outputlog(self, Center.vk1dic)
        ofile.write(msg)
        ofile.close()

    def fill_dict(self, dic):
        for nv in self.pathsteps:
            if nv not in dic:
                dic[nv] = set(Center.snodes[nv].bgrid.chvals)
        return dic

    def expand_vk1s(self, vk1=None):
        if vk1:
            if type(vk1.cvs) == set:
                vk1.cvs = {vk1.nov: vk1.cvs}
            self.fill_dict(vk1.cvs)
        else:
            for kn in self.k1ns:
                vk1 = Center.vk1dic[kn]
                self.expand_vk1s(vk1)

    def expand_excls(self):
        for kn, lst in self.excls.items():
            for dic in lst:
                self.fill_dict(dic)

    def expand_blocks(self):
        for dic in self.blocks:
            self.fill_dict(dic)

    def clone(self):
        xrepo = VKRepoitory(self.snode)
        xrepo.bdic1 = {b: lst[:] for b, lst in self.bdic1.items()}
        xrepo.bdic2 = {b: lst[:] for b, lst in self.bdic2.items()}
        xrepo.k1ns = self.k1ns[:]
        xrepo.vk2dic = {kn:vk2 for kn, vk2 in self.vk2dic.items()}
        xrepo.blocks = [copy.deepcopy(node) for node in self.blocks]
        for kn, lst in self.excls.items():
            xrepo.excls[kn] = [copy.deepcopy(node) for node in lst]
        return xrepo
    
    def add_snode_root(self, bgrid):
        bdic1_rbits = sorted(set(self.bdic1).intersection(bgrid.bits))
        for rb1 in bdic1_rbits:
            for k1n in self.bdic1[rb1]:
                vk1 = Center.vk1dic[k1n]
                cvs = bgrid.cvs_subset(vk1.bit, vk1.val)
                # these cvs are hits with vk1.cvs node
                if type(vk1.cvs) == set:
                    self.blocks.append(
                        self.fill_dict({vk1.nov: cvs.intersection(vk1.cvs)}))
                else:
                    nd = copy.deepcopy(vk1.cvs)
                    nd[bgrid.nov] = cvs
                    if nd not in self.blocks:
                        self.blocks.append(self.fill_dict(nd))
        # handle vk2s bouncing with bgrid.bits
        cmm_rbits = sorted(set(self.bdic2).intersection(bgrid.bits))
        for rb in cmm_rbits:
            for k2n in self.bdic2[rb]:
                vk2 = self.vk2dic[k2n]
                if set(vk2.bits).issubset(bgrid.bits):
                    hit_cvs = bgrid.vk2_hits(vk2)
                    print(f"{k2n} inside {bgrid.nov}-root, blocking {hit_cvs}")
                    block = self.fill_dict({vk2.nov:vk2.cvs.copy(), 
                                            bgrid.nov: hit_cvs})
                    if block not in self.blocks:
                        self.blocks.append()
                else:# vk1.cvs is compound  caused by overlapping 
                    # with xsn.root-bits, will be named with R-prefix
                    x_cvs_subset = bgrid.cvs_subset(rb, vk2.dic[rb])
                    node = self.fill_dict({vk2.nov: vk2.cvs.copy(), 
                                           bgrid.nov: x_cvs_subset})
                    self.add_excl(vk2, copy.deepcopy(node))
                    name = NameDrive.rname()
                    new_vk1 = vk2.clone(name, [rb], node) # R prefix, drop rb
                    new_vk1.source = vk2.kname
                    self.add_vk1(new_vk1)
    
    def merge_snode(self, sn):
        self.pathsteps.append(sn.nov)
        self.expand_vk1s()
        self.expand_excls()
        self.expand_blocks()
        self.add_snode_root(sn.bgrid)
        for k1n in sn.vkrepo.k1ns:
            self.add_vk1(Center.vk1dic[k1n])
        for vk2 in sn.vkrepo.vk2dic.values():
            self.add_vk2(vk2)
        # self.write_logmsg('./docs/loginfo.txt')
        x = 9

    def newvk1_to_vk1(self, nvk, ovk, add_nvk=False): 
        # new-vk1 and old-vk1 are sitting on the same bit
        if nvk.val != ovk.val:
            cmm = cvs_intersect(nvk, ovk)
            if cmm: 
                infokey = tuple(sorted([nvk.kname, ovk.kname]))
                self.inflog.setdefault(infokey,[])\
                    .append("resulted in block:"+str(cmm))
                if cmm not in self.blocks:
                    self.blocks.append(cmm)
            if add_nvk:
                self.insert_vk1(nvk)
            return True # no duplicated old-vk1 existing
        else: # b/v == b/v
            return vk1s_unify_test(nvk, ovk) # vnk/d1, ovk/d2



    def insert_vk1(self, vk1, add2center): # simply add vk1 to the repo
        self.k1ns.append(vk1.kname)
        self.bdic1.setdefault(vk1.bit,[]).append(vk1.kname)
        if add2center:
            Center.add_vk1(vk1)
    
    def insert_vk2(self, vk2):
        name = vk2.kname
        b1, b2 = vk2.bits
        if (b1 not in self.bdic2) or name not in self.bdic2[b1]:
            self.bdic2.setdefault(b1,[]).append(name)
        if (b2 not in self.bdic2) or name not in self.bdic2[b2]:
            self.bdic2.setdefault(b2,[]).append(name)
        self.vk2dic[name] = vk2

    def newvk1_to_vk2(self, nvk, vk2):
        '''# when a vk1 shares 1 bit with an existing vk2, and vk1 and vk2 
        # have no intersect in cvs, return - nothing happens. But if they
        # do have cvs-intersection(cmm) on their common nov, then 2 cases:
        # 1. vk1.val == vk2.dic[bit] -> vk2's cvs(on the same nov) 
        #    reduces by cmm
        # 2. vk1.val != vk2.dic[bit] -> 
        #    2.1: vk2's cvs(on the same nov) 
        #    2.2: new vk1 is generated for the other bit, with cmm'''
        cmm = cvs_intersect(nvk, vk2)
        if not cmm: return
        self.add_excl(vk2, copy.deepcopy(cmm))
        if vk2.dic[nvk.bit] != nvk.val:
            name = NameDrive.uname()
            new_vk1 = vk2.clone(name, [nvk.bit], cmm)
            new_vk1.source = vk2.kname
            self.add_vk1(new_vk1)

    def add_vk1(self, vk1, add2center=True):
        self.expand_vk1s(vk1)
        print(vk1.print_out())
        add_newvk1 = True
        # handle with existing vk1s
        if vk1.bit in self.bdic1:
            for kn in self.bdic1[vk1.bit]:
                if not self.newvk1_to_vk1(vk1, Center.vk1dic[kn]):
                    NameDrive.recycle_name(vk1.kname)
                    add_newvk1 = False
                    break
        # handle with vk2s
        if vk1.bit in self.bdic2:
            for kn in self.bdic2[vk1.bit]: # all vk2 are named 'Cnnnn'
                if vk1.source == kn: continue
                vk = self.vk2dic[kn]
                self.newvk1_to_vk2(vk1, vk)
        if add_newvk1:
            self.insert_vk1(vk1, add2center)

    def handle_vk1_block(self, vk1):
        # for a newly found vk1, see if an opposite vk(1) exists in this
        # repo, and if yes do the two generat a block? if yes, put it in
        if vk1.kname in self.k1ns or vk1.bit not in self.bdic1: 
            return
        for kn in self.bdic1[vk1.bit]:
            vk = Center.vk1dic[kn]
            if vk.val != vk1.val:
                cmm = cvs_intersect(vk, vk1)
                if cmm and cmm not in self.blocks:
                    self.blocks.append(cmm)

    def add_vk2(self, vk2):
        print(vk2.print_out())
        for b in vk2.bits:
            if b in self.bdic1:
                kns = self.bdic1[b]  # for loop variable must be immutable
                for kn in kns:
                    vk1 = Center.vk1dic[kn]
                    cmm = cvs_intersect(vk1, vk2)
                    if not cmm: continue
                    self.add_excl(vk2, copy.deepcopy(cmm))
                    if vk2.dic[b] != vk1.val:
                        if len(cmm) == 1:
                            name = NameDrive.tname()
                            new_vk1 = vk2.clone(name,[b], cmm[vk2.nov])
                        else:
                            name = NameDrive.uname()
                            new_vk1 = vk2.clone(name,[b], cmm)
                        new_vk1.source = vk2.kname
                        self.add_vk1(new_vk1)
        self.insert_vk2(vk2)
        # handle case of 2 overlapping bits with existing vk2
        self.proc_vk2pair(vk2) # if vk2 has a twin in vk2dic

    def proc_vk2pair(self, vk2):
        # check if vk2 share its 2 bits with an existing vk2, if yes
        # and if both vals on the same bit are the same, and the vals on
        # the bit are diff, then a new vk1 is generated. 
        # This is based on the fact: (a + b)( a + not_b) == a
        b1, b2 = vk2.bits
        kns1 = self.bdic2[b1]
        kns2 = self.bdic2[b2]
        xkns = set(kns1).intersection(kns2)
        xkns.remove(vk2.kname)
        while len(xkns) > 0:
            _vk2 = self.vk2dic[xkns.pop()]
            vk1 = handle_vk2pair(vk2, _vk2)
            if vk1: 
                self.expand_vk1s(vk1)
                self.add_vk1(vk1)


    def add_excl(self, vk2, node):
        if len(node) == 1: # in case node has only 1 entry like {60:{3,7}
            nov, cvs = tuple(node.items())[0] # like {60:{3,7}}->60, {3,7}
            if nov == vk2.nov:  # vk2,cvs:{2,3,6,7}
                vk2.cvs -= cvs  # vk2.cvs -> {2,6}
                return True
        lst = self.excls.setdefault(vk2.kname, [])
        if node in lst: return False
        for ind, old_dic in enumerate(lst):
            cont = test_containment(node, old_dic)  # param-names: (d1, d2)
            if not cont: continue
            if cont['cat'].startswith('contain'):
                # {cat: "contain: d1 in d2"}: 
                # user the container, dump the other
                container = cont['cat'].split(':')[1].split()[-1] # d2
                if container == 'd2': # old_dic is the container
                    return False
                elif container == 'd1':
                    lst[ind] = node           # node replace that one
                    return True               # node has been "added"
            if cont['cat'] == "mergable": # merge on mergable nov into old_dic
                nv = cont['merge-nov']
                old_dic[nv].update(node[nv])
                return True  # don't put into lst, since already to old-dic
        lst.append(node)
        return True
