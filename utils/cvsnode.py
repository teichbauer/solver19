import copy
# from basics import print_dic
class CVS:
    def __init__(self, cvs): # cvs is a set of integers, or '*'
        self.cvs = cvs
    
    def clone(self):
        return CVS(self.cvs.copy())
    
    def __lt__(self, other): # other contains self: True or False
        return other == {'*'} or self.cvs.issubset(other.cvs)
    
    def __gt__(self, other): # self contains other: True or False
        return self.cvs == {'*'} or\
               self.cvs.issuperset(other.cvs)
    
    def __eq__(self, other): # self == other: True or False
        return self.cvs == other.cvs
    
    def intersect(self, other):
        if other.cvs == {'*'}:  return self.clone()
        if self.cvs == {'*'}:   return other.clone()
        cmm = self.cvs.intersection(other.cvs)
        if len(cmm) > 0: return CVS(cmm)
        return None

    def po(self):
        m = '('
        for v in sorted(self.cvs):
            m += str(v)
        m += ')'
        return m

class Node:
    def __init__(self, dic): # dic: {<nov>: <set-of-cvs>,...}
        self.dic = dic
        self.nvs = sorted(dic, reverse=True)

    def new_entry(self, nov, cvs): # add a newk/v into self.dic
        self.dic[nov] = cvs  # insert a new k/v
        # insert nov into self.nvs, keep descending order in tact
        ind = 0
        while ind < len(self.nvs):
            if self.nvs[ind] < nov:
                self.nvs.insert(ind, nov)
                return
            ind += 1
        self.nvs.append(nov)

    def clone(self):
        dic = {nv: cvs.clone() for nv, cvs in self.dic.items()}
        return Node(dic)
    
    def is_thrd(self):  # all cvs are single. {'*'} counts as single
        for cvs in self.dic.values():
            if len(cvs.cvs) > 1: return False
        return True

    def gen_thread(self, Seq):
        if self.is_thrd(): return True
        se1 = Seq(self.dic)

    
    def fill_missing(self, other):
        if self.nvs == other.nvs: return
        if len(self.nvs) > len(other.nvs):
            for nv in (set(self.dic) - set(other.dic)):
                other.new_entry(nv, CVS({'*'}))
        else:
            for nv in (set(other.dic) - set(self.dic)):
                self.new_entry(nv, CVS({'*'}))

    def po(self):
        dstr = '{ '
        for nv in self.nvs:
            dstr += f"{nv}:{self.dic[nv].po()} "
        return dstr + '}'
    
    def __lt__(self, other):
        self.fill_missing(other)
        for nv, cvs in self.dic.items():
            if self.dic[nv] > other.dic[nv]:
                return False
        return True
    
    def __gt__(self, other):
        self.fill_missing(other)
        for nv, cvs in self.dic.items():
            if self.dic[nv] < other.dic[nv]:
                return False
        return True
    
    def __eq__(self, other):
        self.fill_missing(other)
        for nv, cvs in self.dic.items():
            if self.dic[nv] != other.dic[nv]:
                return False
        return True
    
    def contains(self, other): # other is containes in self?
        return self > other
    
    def intersect(self, other): # other can also be (nov, cvs-set), for vk2
        if type(other) == tuple: # vk2.cvs is of type set, 
            nv, cvs_set = other
            _node = self.clone()
            if nv not in _node.dic:
                _node.new_entry(nv, CVS(cvs_set))
            else:
                cmm = _node.dic[nv].intersection(cvs_set)
                if len(cmm) == 0: return None
                _node.dic[nv] = CVS(cmm)
            return _node
        # other is a Node too
        dic = {}
        self.fill_missing(self,other)
        for nv in self.dic:
            intrsct = self.dic[nv].intersection(other.dic[nv])
            if len(intrsct) == 0: return None
            dic[nv] = intrsct
        return Node(dic)

node1 = Node({60:CVS({0,1,2},60), 57:CVS({0,5},57)})
node2 = Node({60:CVS({0,1,2},60), 57:CVS({0}, 57)})
node3 = Node({60:CVS({0,1,2},60), 57:CVS({5},57), 54:CVS({2,3},54)})
node4 = Node({60:CVS({0,1,2},60), 57:CVS({0,5},57)})

def test():
    f1 = node1 > node2
    f2 = node1 > node3
    node1.dic[54] > node3.dic[54]
    x = 0

def main():
    test()

if __name__ == '__main__':
    main()