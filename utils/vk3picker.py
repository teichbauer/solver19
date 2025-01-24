class Vk3Picker:
    # What is MPK most popular v3-klause:
    # the vk3(s) touching the most other vk3s
    # vk3 with 3 touching bits (with other vk3)/MPK-3 ranked highst
    # vk3 with 2 touching bits (with other vk3)/MPK-2 ranked 2nd, 
    # MPK-1 ranks the thirs
    # --------------------------------------
    # pick MPK will reduce the whole nov - 3. So , case of 60 variables:
    # rootvks: {60: [vk3,..], 57:[], 54:[], ..} 
    # this goes until there is no vk3 left. As for cfg60-266.json, it goes 
    # until 18:[]
    # ------------------------------
    # task of this Vk3Picker is: to choose the next MPK, put into rootvks
    # -------------------------------------------------------------------------
    def __init__(self, vkm, rootvks): # rootvks <- Center.rootvks, global var
        self.vkm = vkm
        self.vkdic = vkm.vkdic
        # rootvks: {60:}
        self.rootvks = rootvks  # global var in Center. Here is a ref to it.
        self.make_tdic_chdic(self.vkdic)


    def make_tdic_chdic(self, vkdic):
        # -- tdic --
        # is a super dict, {[<each-kn>]:<share-dic>,...}, where
        # <share-dic> :
        #   {'all':{set of all kns sharing at least 1 bit with vk},
        #     1: {set of all kns sharing 1 bit},
        #     2: {set of all kns sharing 2 bits},
        #     3: {set of all kns sharing 3 bits},
        #   }
        #############
        # -- chdic --
        # is a dict, keyed by integer 1, 2 or 3:
        # { 
        #    1: {set of kname of vk, where vk has 1-bit touch},
        #    2: {set of kname of vk, where vk has 2-bit touch},
        #    3: {set of kname of vk, where vk has 3-bit touch},
        # }
        ###########################################################
        tdic = {} 
        chdic = {}
        for kn, vk in vkdic.items():
            tdic[kn] = {'all': set([])} # all kns(not self-kn) in touch
            for b in vk.bits:           # loop thru 3 bits of this vk
                for knx in self.vkm.bdic[b]: # all kns sitting on this bit
                    if knx != kn and (not knx in tdic[kn]['all']):
                        tdic[kn]['all'].add(knx) # collect into 'all'-set
                        vkx = vkdic[knx]
                        # how many bits are share across vk and vkx
                        noshared_bits = len(vk.dic.keys() & vkx.dic.keys())
                        tdic[kn].setdefault(noshared_bits,set([])).add(knx)
                        lst = chdic.setdefault(noshared_bits, []) # .append(kn)
                        if kn not in lst:
                            lst.append(kn)
            x = 0
        self.tdic = tdic
        self.chdic = chdic
    
    def biggest_choice(self, nobits):
        td = self.tdic
        max_kn = None
        kns = self.chdic[nobits]
        for kn in kns:
            if not max_kn: max_kn = kn
            else:
               if len(td[kn][nobits]) > len(td[max_kn][nobits]): 
                   max_kn = kn

        self.chdic[nobits].remove(max_kn)
        if len(self.chdic[nobits]) == 0:
            self.chdic.pop(nobits)
        return self.vkdic[max_kn]

    def pickt3(self, vals, nov):
        # self.chdic has touch-3 choice. Take one
        # original chck_vals: [0..7], after choice, at least one removed
        kn_lst = self.chdic[3]
        kname = kn_lst.pop(0)
        vk3 = self.vkdic[kname]
        vk3.nov = nov
        vk3s = [vk3]
        v = vk3.cmprssd_value()
        if v in vals:
            vals.remove(v)
        self.vkm.pop_vk(vk3)
        if kname in self.chdic[2]: self.chdic[2].remove(kname)
        if kname in self.chdic[1]: self.chdic[1].remove(kname)
        t2s = sorted(self.tdic[kname].get(2,set()))
        t1s = sorted(self.tdic[kname].get(1,set()))
        ind3 = 0
        while ind3 < len(self.chdic[3]):
            knx = kn_lst.pop(ind3)
            vk3x = self.vkdic[knx]
            if vk3x.bits == vk3.bits:
                vk3x.nov = nov
                vk3s.append(vk3x)
                v = vk3x.cmprssd_value()
                if v in vals:
                    vals.remove(v)
                self.vkm.pop_vk(vk3x)
                if knx in self.chdic[2]: self.chdic[2].remove(knx)
                if knx in self.chdic[1]: self.chdic[1].remove(knx)
            else:
                ind3 += 1
        if len(kn_lst) == 0:
            self.chdic.pop(3)
        self.rootvks[nov] = vk3s
        return (vals, vk3s, t2s, t1s)

    def pickt2(self, vals, nov):
        # take the kn in chdic[2] with the most touch-count
        vk3 = self.biggest_choice(2)
        self.rootvks[nov] = [vk3]
        vk3.nov = nov
        v = vk3.cmprssd_value()
        if v in vals:
            vals.remove(v)
        self.vkm.pop_vk(vk3)
        return (vals, [vk3], 
                sorted(self.tdic[vk3.kname].get(2,set())),
                sorted(self.tdic[vk3.kname].get(1,set())))

    def pickt1(self, vals, nov):
        # take the kn in chdic[1] with the most touch-count
        vk3 = self.biggest_choice(1)
        vk3.nov = nov
        self.rootvks[nov] = [vk3]
        v = vk3.cmprssd_value()
        if v in vals:
            vals.remove(v)
        self.vkm.pop_vk(vk3)
        return (vals, [vk3], 
                sorted(self.tdic[vk3.kname].get(2,set())),
                sorted(self.tdic[vk3.kname].get(1,set())))

    def pick(self, check_values, nov):
        # if chdic has 3-list, pick from that, else
        # if chdic has 2-list, pick from that, else, 
        # pick from 1-list
        if 3 in self.chdic:
            return self.pickt3(check_values, nov)
        if 2 in self.chdic:
            return self.pickt2(check_values, nov)
        if 1 in self.chdic:
            return self.pickt1(check_values, nov)

    def drop_choice(self, vk):
        kns = self.chdic.get(2,[])
        if vk.kname in kns:
            # print(f'dropping {vk.kname} from choice[2]')
            self.chdic[2].remove(vk.kname)
            if len(self.chdic[2]) == 0:
                self.choice.pop(2)
            
        kns = self.chdic.get(1,[])
        # if vk in self.chdic[1]:
        if vk.kname in kns:
            # print(f'dropping {vk.kname} from choice[1]')
            self.chdic[1].remove(vk.kname)
            if len(self.chdic[1]) == 0:
                self.choice.pop(1)
        self.clean_choice(vk)

    def clean_choice(self, vk):
        if type(vk) == type([]):
            for vkx in vk:
                self.clean_choice(vkx)
            return
        # vk has been removed from choice[1|2]
        # here, remove it also from all other vkxs's t2s or t1s
        # remove vk from all these
        # -------------------------------------------
        # any nk in tdic[vk.kname][2] or [1], will still be in vkdic
        candkns = self.tdic[vk.kname].get(2,set([]))
        for knx in candkns:
            # every knx in vk's t2s kn-list, vkx should also
            # have vk.kname in its t2s-list, remove vk.kname from that
            if knx in self.tdic and vk.kname in self.tdic[knx][2]:
                self.tdic[knx][2].remove(vk.kname)
                if len(self.tdic[knx][2]) == 0:
                    if knx in self.vkdic:
                        vkx = self.vkdic[knx]
                        if vkx in self.chdic[2]:
                            self.chdic[2].remove(vkx)
                            if len(self.chdic[2]) == 0:
                                self.chdic.pop(2)

        candkns = self.tdic[vk.kname].get(1,set([]))
        for knx in candkns:
            # every knx in vk's t1s kn-list, vkx should also
            # have vk.kname in its t1s-list, remove vk.kname from that
            if knx in self.tdic and vk.kname in self.tdic[knx][1]:
                self.tdic[knx][1].remove(vk.kname)
                if len(self.tdic[knx][1]) == 0:
                    if knx in self.vkdic:
                        vkx = self.vkdic[knx]
                        if vkx in self.chdic[1]:
                            self.chdic[1].remove(vkx)
                            if len(self.chdic[1]) == 0:
                                self.chdic.pop(1)

