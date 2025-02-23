from utils.tools import outputlog
from vkrepo import VKRepository
from utils.noder import *
from center import Center
from utils.pathfinder import PathFinder

class Path(VKRepository):
    # constructor can be used as a cloner
    def __init__(self, seed_repo): # seed_repo: inst of VKrepository/Path
        self.bbpool = {}
        self.bdic1 = {}
        for b, bbdic in seed_repo.bdic1.items():
            self.bdic1[b] = {}
            for v, bb in bbdic.items():
                self.bdic1[b][v] = bb.clone(self)
                self.bbpool[(b,v)] = self.bdic1[b][v]
        self.bdic2    = {b: lst[:] for b, lst in seed_repo.bdic2.items()}
        self.vk2dic   = {kn:vk2 for kn, vk2 in seed_repo.vk2dic.items()}
        self.inflog   = seed_repo.inflog.copy()
        if type(seed_repo) == VKRepository:
            self.lyr_dic = {seed_repo.layer.nov: seed_repo.layer}
        else:
            self.lyr_dic  = seed_repo.lyr_dic.copy()
        self.pblocker = seed_repo.pblocker.clone(self)
        self.exclmgr  = seed_repo.exclmgr.clone(self)
        self.finder   = PathFinder(self, Center.layers)

    def clone(self):
        return Path(self)

    # ------------------------------------------------------------------
    # growing path on a new layer, handle layer-root-bits touching path
    # ------------------------------------------------------------------
    def grow_lyr_root(self, layer): # bgrid from new layer
        # handle root-bits touching path bit-blocker-bits bdic1_rbits
        bdic1_rbits = sorted(set(self.bdic1).intersection(layer.bgrid.bits))
        for rbit in bdic1_rbits: # new-layer's bgrid, on this root-bit rbit: 
            # get [<hit-0-cvs>,<hit-1-cvs]
            hit01cvs = layer.bgrid.cvs_subset(rbit, 0) # [hit-0-cvs, hit-1-cvs]
            # ----------------------------------------------------------------
            # Now from path-side: since every bb (on bv=0, bv=1) in bb_dic
            # it will be removed (become path-block). So bb_dic on this rbit
            # be pooped out from path.bdic1
            bb_dic = self.bdic1.pop(rbit) # bb_dic is from path: popped-out
            for bv in (0, 1):
                bb = bb_dic.pop(bv, None)
                if not bb: continue # not every bit in bdic1 has both (0,1)
                # when lyr has chval in hit_cva, and there exists a bit-blocker
                # node on this bb(bit/bitval): making the clause hit False, 
                # this becomes a path-block - node.update{lyr.nov: hit_cvs}
                # should be excluded from sat-path
                for nd in bb.noder.nodes:
                    node = copy.deepcopy(nd)
                    node[layer.bgrid.nov] = hit01cvs[bv] # cvs-set for bv
                    self.pblocker.add_block(node, len(node))
            # now every bb in bb_dic is popped out. so it is now empty
        # -----------------------------------------------------------------
        # handle root-bits touching vk2s from path.bdic2 
        cmm_rbits = sorted(set(self.bdic2).intersection(layer.bgrid.bits))
        for rbit in cmm_rbits:
            kns = self.bdic2[rbit][:]
            while len(kns) > 0:
                vk2 = self.vk2dic[kns.pop(0)] # loop from front to end
                if set(vk2.bits).issubset(layer.bgrid.bits):
                    # vk2's 2 bit both are on layer's root-bits
                    hit_cvs = layer.bgrid.vk2_hits(vk2)
                    m =f"{vk2.kname} in {layer.nov}-root, blocking {hit_cvs}"
                    print(m)
                    block = {vk2.nov:vk2.cvs.copy(), layer.nov: hit_cvs}
                    pblock_added = self.pblocker.add_block(block)
                else: 
                    # vk2 has 1 bit on layer's root-bit
                    # with vk2[rbit] on layer's root bit: rbit, get hit-cvs
                    hit_cvs, _ = layer.bgrid.cvs_subset(rbit, vk2.dic[rbit]) 
                    node = {vk2.nov: vk2.cvs.copy(), layer.nov: hit_cvs}
                    bit, val = vk2.other_bv(rbit) # bit/bv for new bit-block
                    self.add_bblocker( bit, val, node,
                        {vk2.kname: f"R{vk2.nov}-{layer.nov}/{rbit}"} )
                # for hit_cvs, vk2 -> bit-blocker with <node> 
                # for mis_cvs(here: _) vk2 cannot hit. So vk2 will be removed
                self.remove_vk2(vk2)  # IL2024-11-23a + IL2024-11-28
    # end of grow_lyr_root

    def grow0(self, layer):
        self.lyr_dic[layer.nov] = layer
        # ---------------------------------
        # handle lyr-root-bits touching path.bdic1 or bdic2(vk2s)
        self.grow_lyr_root(layer)
        # --------------------------------
        # obsorb all lyr.bdic1's bit-blockers
        self.grow_layer_bb(layer)

    def grow(self, lyr): # grow on next layer-node
        self.grow0(lyr)
        # --------------------------------
        # add lyr's vk2s
        self.grow_vk2s(lyr)

        #region purpose of calling self.filter_vk2s(local=False)
        # all vk2s may have sit on 1/2 bits of bdic1 where bit-blockers are
        # This may it may generate new bit-blocker - and this bit-blocker may 
        # even have collide with other vk2/or with other bdic1-bits.
        # handle all that in filter_vk2s here.
        #endregion
        self.filter_vk2s(local=False) # vk2s from multi-layer: local=False
        x = 0

    def grow_layer_bb(self, lyr):
        #region obsorbing lyr.bdic1/bit-blockers -----------
        # lyr.bdic1[bit] where bit-value can be 0/1 (one of 0/1 or both)
        # lyr/bdic1[3][0]: bit-blocker for (3,0)
        # lyr/bdic1[3][1]: bit-blocker for (3,1)
        # endregion ----------------------------------------
        for bit, lyr_dic in lyr.repo.bdic1.items():
            # path may have this bit. if it does, 0 or 1 may in it
            path_dic = self.bdic1.setdefault(bit, {}) # path.bdic1[bit]: {..}
            for v, bb in lyr_dic.items(): # v: bit-value, bb: bit-blocker
                if v in path_dic:   # in case this bit-value is in: merge
                    path_dic[v].merge(bb)
                else:       # not in clone it from lyr into path.bdic1[bit][v]
                    # cloning also put into bbpool
                    path_dic[v] = bb.clone(self)  
            conflicts_existed = path_dic[v].check_spouse()

    def grow_vk2s(self, layer):
        for vk2 in layer.repo.vk2dic.values():
            bits = set(self.bdic1).intersection(vk2.bits)
            if len(bits) > 0:
                vk2_node = {vk2.nov: vk2.cvs}
                for bit in bits:
                    bb_dic = self.bdic1[bit]
                    for v in bb_dic:
                        # msg = bb_dic[v].output()
                        # print(f'vk2/kname: {vk2.kname} - ',)
                        # print(msg)
                        cmm = bb_dic[v].intersect(vk2_node)
                        if len(cmm) == 0: continue
                        # print('cmm: ',)
                        # msg = Noder.pout(cmm)
                        # print(msg)
                        self.exclmgr.add(vk2.kname, cmm)
                        if v != vk2.dic[bit]:
                            new_bit, new_val = vk2.other_bv(bit)
                            self.add_bblocker(new_bit,  new_val, cmm,
                                            {vk2.kname: f'U{vk2.nov}'})
            self.insert_vk2(vk2)
            # handle case of 2 overlapping bits with existing vk2
            self.proc_vk2pair(vk2) # if vk2 has a twin in vk2dic

    def _show_blocks(self):
        self.pblocker.output()
        bbits = sorted(self.bdic1)
        for b in bbits:
            for v, bb in self.bdic1[b].items():
                print(bb.output())
            print('-'*20)
    
    def bottomup(self):
        self.finder.find_satpath()
        # self._show_blocks()
        x = 0

    def write_log(self, outfile_name):
        ofile = open(outfile_name, 'w')
        msg = outputlog(self)
        ofile.write(msg)
        ofile.close()

    def add_vk2(self, vk2):
        bits = set(self.bdic1).intersection(vk2.bits)
        if len(bits) > 0:
            vk2_node = {vk2.nov: vk2.cvs}
            for bit in bits:
                bb_dic = self.bdic1[bit]
                for v in bb_dic:
                    # msg = bb_dic[v].output()
                    # print(f'vk2/kname: {vk2.kname} - ',)
                    # print(msg)
                    cmm = bb_dic[v].intersect(vk2_node)
                    if len(cmm) == 0: continue
                    # print('cmm: ',)
                    # msg = Noder.pout(cmm)
                    # print(msg)
                    self.exclmgr.add(vk2.kname, cmm)
                    if v != vk2.dic[bit]:
                        new_bit, new_val = vk2.other_bv(bit)
                        self.add_bblocker(new_bit,  new_val, cmm,
                                        {vk2.kname: f'U{vk2.nov}'})
        self.insert_vk2(vk2)
        # handle case of 2 overlapping bits with existing vk2
        self.proc_vk2pair(vk2) # if vk2 has a twin in vk2dic
    
    def output_all_bb(self):
        bdic1_bits = sorted(self.bdic1)
        print(f'There are {len(bdic1_bits)} bb-bits:')
        print(bdic1_bits)
        print('-'*40)
        for bit in bdic1_bits:
            for bv in (0,1):
                bb = self.bdic1[bit].get(bv, None)
                if bb:
                    print(bb.output())

    @property
    def steps(self):
        return sorted(self.lyr_dic, reverse=True) # [60, 57, 54, ...]

    @property
    def chvdict(self):
        return {nv: set(sn.bgrid.chvals) for nv, sn in self.lyr_dic.items()}
