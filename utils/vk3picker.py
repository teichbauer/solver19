class Vk3Picker:
    # What is MPK most popular v3-klause:
    # the vk3(s) touching the most other vk3s
    # vk3 with 3 touching bits (with other vk3) ranked highst
    # vk3 with 2 touching bits (with other vk3) ranked 2nd, 1-touch the thirs
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
                        if vk not in lst:
                            lst.append(vk)
            x = 0
        self.tdic = tdic
        self.chdic = chdic
    
    def biggest_choice(self, nobits):
        td = self.tdic
        max_vk = None
        for vk in self.chdic[nobits]:
            if not max_vk:
                max_vk = vk
            else:
                if len(td[vk.kname][nobits]) > len(td[max_vk.kname][nobits]):
                    max_vk = vk
        self.chdic[nobits].remove(max_vk)
        if len(self.chdic[nobits]) == 0:
            self.chdic.pop(nobits)
        return max_vk

    def pickt3(self, vals, nov):
        # self.chdic has touch-3 choice. Take one
        # original chck_vals: [0..7], after choice, at least one removed
        lst = self.chdic[3]
        vk3 = lst.pop(0)
        vk3.nov = nov
        vk3s = [vk3]
        v = vk3.cmprssd_value()
        if v in vals:
            vals.remove(v)
        self.vkm.pop_vk(vk3)
        ind3 = 0
        while ind3 < len(lst):
            if lst[ind3].bits == vk3.bits:
                vk3x = lst.pop(ind3)
                vk3x.nov = nov
                vk3s.append(vk3x)
                v = vk3x.cmprssd_value()
                if v in vals:
                    vals.remove(v)
                self.vkm.pop_vk(vk3x)
            else:
                ind3 += 1
        if len(lst) == 0:
            self.chdic.pop(3)
        self.rootvks[nov] = vk3s
        return (vals, 
                vk3s, 
                list(self.tdic[vk3.kname].get(2,[])),
                list(self.tdic[vk3.kname].get(1,[])))

    def pickt2(self, vals, nov):
        # self.chdic has no touch-3, but touch-2 choice. Take one
        vk3 = self.biggest_choice(2)
        self.rootvks[nov] = [vk3]
        vk3.nov = nov
        v = vk3.cmprssd_value()
        if v in vals:
            vals.remove(v)
        self.vkm.pop_vk(vk3)
        return (vals, 
                [vk3], 
                list(self.tdic[vk3.kname].get(2,[])),
                list(self.tdic[vk3.kname].get(1,[])))

    def pickt1(self, vals, nov):
        # self.chdic has no touch-3/-2 choice. Take one touch-1
        vk3 = self.biggest_choice(1)
        vk3.nov = nov
        self.rootvks[nov] = [vk3]
        v = vk3.cmprssd_value()
        if v in vals:
            vals.remove(v)
        self.vkm.pop_vk(vk3)
        return (vals, 
                [vk3], 
                list(self.tdic[vk3.kname].get(2,[])),
                list(self.tdic[vk3.kname].get(1,[])))

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
        vks = self.chdic.get(2,[])
        if vk in vks:
            # print(f'dropping {vk.kname} from choice[2]')
            self.chdic[2].remove(vk)
            if len(self.chdic[2]) == 0:
                self.choice.pop(2)
            
        vks = self.chdic.get(1,[])
        # if vk in self.chdic[1]:
        if vk in vks:
            # print(f'dropping {vk.kname} from choice[1]')
            self.chdic[1].remove(vk)
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

