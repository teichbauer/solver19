class CVS:
    def __init__(self, cvs, nv = None): # cvs is a set of integers, or '*'
        self.nov = nv
        self.cvs = cvs
    def __lt__(self, other): # other contains self: True or False
        return other == {'*'} or self.cvs.issubset(other.cvs)
    def __gt__(self, other): # self contains other: True or False
        return self.cvs == {'*'} or\
               self.cvs.issuperset(other.cvs)
    def __eq__(self, other): # self == other: True or False
        return self.cvs == other.cvs

class Node:
    def __init__(self, dic): # dic: {<nov>: <set-of-cvs>,...}
        self.dic = dic
        
    def fill_missing(self, other):
        mynvs = sorted(self.dic, reverse=True) # bigger nov front
        otnvs = sorted(other.dic, reverse=True)
        if len(mynvs) > len(otnvs):
            for nv in (set(self.dic) - set(other.dic)):
                other.dic[nv] = CVS({'*'}, nv)
        elif len(otnvs) > len(mynvs):
            for nv in (set(other.dic) - set(self.dic)):
                self.dic[nv] = CVS({'*'}, nv)
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