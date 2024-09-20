class Vk3Picker:
    def __init__(self, vkm, Center):
        # vkm mus have its bdic mfinished
        self.vkm = vkm
        self.Center = Center
        self.tdic, self.chdic = self.make_tdic_chdic(vkm)
        # self.chdic = self.make_chdic(self.tdic)
        xx = 0


    def make_tdic_chdic(self, vkm):
        tdic = {}   # touch-dic: 3 touch-lst, 2-touch-lst, 1-touch-lst
        chdic = {}
        for kn, vk in vkm.vkdic.items():
            tdic[kn] = {'all': set([])} 
            for b in vk.bits:
                for knx in vkm.bdic[b]:
                    if knx != kn and (not knx in tdic[kn]['all']):
                        tdic[kn]['all'].add(knx)
                        vkx = vkm.vkdic[knx]
                        noshared_bits = len(vk.dic.keys() & vkx.dic.keys())
                        tdic[kn].setdefault(noshared_bits,set([])).add(knx)
                        lst = chdic.setdefault(noshared_bits, []) # .append(kn)
                        if vk not in lst:
                            lst.append(vk)

        return tdic, chdic
    
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
        self.Center.rootvks[nov] = vk3s
        return (vals, 
                vk3s, 
                list(self.tdic[vk3.kname].get(2,[])),
                list(self.tdic[vk3.kname].get(1,[])))

    def pickt2(self, vals, nov):
        # self.chdic has no touch-3, but touch-2 choice. Take one
        vk3 = self.biggest_choice(2)
        self.Center.rootvks[nov] = [vk3]
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
        self.Center.rootvks[nov] = [vk3]
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
            print(f'dropping {vk.kname} from choice[2]')
            self.chdic[2].remove(vk)
            if len(self.chdic[2]) == 0:
                self.choice.pop(2)
            
        vks = self.chdic.get(1,[])
        # if vk in self.chdic[1]:
        if vk in vks:
            print(f'dropping {vk.kname} from choice[1]')
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
        # any nk in tdic[vk.kname][2] or [1], will still be in vkm.vkdic
        candkns = self.tdic[vk.kname].get(2,set([]))
        for knx in candkns:
            # every knx in vk's t2s kn-list, vkx should also
            # have vk.kname in its t2s-list, remove vk.kname from that
            if knx in self.tdic and vk.kname in self.tdic[knx][2]:
                self.tdic[knx][2].remove(vk.kname)
                if len(self.tdic[knx][2]) == 0:
                    if knx in self.vkm.vkdic:
                        vkx = self.vkm.vkdic[knx]
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
                    if knx in self.vkm.vkdic:
                        vkx = self.vkm.vkdic[knx]
                        if vkx in self.chdic[1]:
                            self.chdic[1].remove(vkx)
                            if len(self.chdic[1]) == 0:
                                self.chdic.pop(1)

