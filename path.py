from utils.tools import outputlog
from vkrepo import VKRepository
from utils.noder import *
from center import Center
from utils.pathfinder import PathFinder

class Path(VKRepository):
    def __init__(self, lyr):
        VKRepository.__init__(self, lyr, 'Path')
        self.finder = PathFinder(self, Center.layers)

    # ------------------------------------------------------------------
    # growing path on a new layer, handle layer-root-bits touching path
    # ------------------------------------------------------------------
    def add_lyr_root(self, bgrid): # bgrid from new layer
        # handle root-bits touching path bit-blocker-bits (bdic1-bits)
        bdic1_rbits = sorted(set(self.bdic1).intersection(bgrid.bits))
        for rb1 in bdic1_rbits:
            # The logic here, see IL2025-02-27 (docs/idealog.md:2025-01-27)
            bb_dic = self.bdic1.pop(rb1) # bbs on this bit popped out/removed
            for bb in bb_dic.values():
                hit_cvs, _ = bgrid.cvs_subset(bb.bit, bb.val) # _ : mis_cvs
                for nd in bb.noder.nodes:
                    nd[bgrid.nov] = hit_cvs
                    self.pblocker.add_block(nd, len(nd))
        # handle root-bits touching vk2s from path.bdic2 
        cmm_rbits = sorted(set(self.bdic2).intersection(bgrid.bits))
        for rb in cmm_rbits:
            kns = self.bdic2[rb][:]
            while len(kns) > 0:
                vk2 = self.vk2dic[kns.pop(0)]
                if set(vk2.bits).issubset(bgrid.bits):
                    hit_cvs = bgrid.vk2_hits(vk2)
                    m =f"{vk2.kname} in {bgrid.nov}-root, blocking {hit_cvs}"
                    print(m)
                    block = {vk2.nov:vk2.cvs.copy(), bgrid.nov: hit_cvs}
                    pblock_added = self.pblocker.add_block(block)
                else: 
                    hit_cvs, _ = bgrid.cvs_subset(rb, vk2.dic[rb]) # _: mis_cvs
                    node = self.expand_node(
                        {vk2.nov: vk2.cvs.copy(), bgrid.nov: hit_cvs})
                    bit, val = vk2.other_bv(rb)
                    self.add_bblocker( bit, val, node,
                        {vk2.kname: f"R{vk2.nov}-{bgrid.nov}/{rb}"} )
                # for hit_cvs, vk2 -> bit-blocker with <node> 
                # for mis_cvs vk2 cannot hit. So vk2 will be removed
                self.remove_vk2(vk2)  # IL2024-11-23a + IL2024-11-28
    # end of add_lyr_root

    def grow(self, lyr): # grow on next layer-node
        self.lyr_dic[lyr.nov] = lyr
        # for path_bb in self.bbpool.values():
        #     path_bb.noder.expand(self.chvdict)
        self.add_lyr_root(lyr.bgrid)
        for bit, lyr_dic in lyr.repo.bdic1.items():
            path_dic = self.bdic1.setdefault(bit, {})
            for v, bb in lyr_dic.items():
                # bb.noder.expand(self.chvdict)
                if v in path_dic:
                    path_dic[v].merge(bb)
                else:
                    # cloning also put into bbpool
                    path_dic[v] = bb.clone(self)  
            conflicts_existed = path_dic[v].check_spouse()
        for vk2 in lyr.repo.vk2dic.values():
            self.add_vk2(vk2)
        self.filter_vk2s(local=False)
        x = 0

    def _show_blocks(self):
        self.pblocker.output()
        bbits = sorted(self.bdic1)
        for b in bbits:
            for v, bb in self.bdic1[b].items():
                print(bb.output())
            print('-'*20)
    
    def bottomup(self, lyr):
        # self._show_blocks()
        x = 0

    def write_log(self, outfile_name):
        ofile = open(outfile_name, 'w')
        msg = outputlog(self)
        ofile.write(msg)
        ofile.close()

    def expand_node(self, node):
        if type(node) == list:
            for nd in node:
                self.expand_node(nd)
        elif type(node) == dict:
            for nv in self.chvdict:
                if (nv not in node) or (node[nv] == {'*'}):
                    node[nv] = self.chvdict[nv]
        return node

    def add_vk2(self, vk2):
        bits = set(self.bdic1).intersection(vk2.bits)
        if len(bits) > 0:
            vk2_node = self.expand_node({vk2.nov: vk2.cvs})
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
