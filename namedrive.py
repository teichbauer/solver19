class NameDrive:
    Rcount = 0
    Rrecycles = []
    Scount = 0
    Srecycles = []
    Tcount = 0
    Trecycles = []
    Dcount = 0
    Drecycles = []
    Ucount = 0
    Urecycles = []

    @classmethod
    def rname(cls):
        if len(cls.Rrecycles) > 0:
            return 'R' + str(cls.Rrecycles.pop()).rjust(4,'0')
        cls.Rcount += 1
        return "R" + str(cls.Rcount).rjust(4,'0')
    
    @classmethod
    def sname(cls):
        if len(cls.Srecycles) > 0:
            return 'S' + str(cls.Srecycles.pop()).rjust(4,'0')
        cls.Scount += 1
        return "S" + str(cls.Scount).rjust(4,'0')

    @classmethod
    def tname(cls):
        if len(cls.Trecycles) > 0:
            return 'T' + str(cls.Trecycles.pop()).rjust(4,'0')
        cls.Tcount += 1
        return "T" + str(cls.Tcount).rjust(4,'0')
    
    @classmethod
    def dname(cls):
        if len(cls.Drecycles) > 0:
            return 'D' + str(cls.Drecycles.pop()).rjust(4,'0')
        cls.Dcount += 1
        return "D" + str(cls.Dcount).rjust(4,'0')
    
    @classmethod
    def uname(cls):
        if len(cls.Urecycles) > 0:
            return 'U' + str(cls.Urecycles.pop()).rjust(4,'0')
        cls.Ucount += 1
        return "U" + str(cls.Ucount).rjust(4,'0')
    
    @classmethod
    def recycle_name(cls, name):
        prefix = name[0]
        count = int(name[1:])
        if prefix == 'U':
            if count == cls.Ucount:
                cls.Ucount -= 1
            else:
                cls.Urecycles.append(count)
        elif prefix == 'T':
            if count == cls.Tcount:
                cls.Tcount -= 1
            else:
                cls.Trecycles.append(count)
        elif prefix == 'S':
            if count == cls.Scount:
                cls.Scount -= 1
            else:
                cls.Srecycles.append(count)
        elif prefix == 'R':
            if count == cls.Rcount:
                cls.Rcount -= 1
            else:
                cls.Rrecycles.append(count)
        elif prefix == 'D':
            if count == cls.Dcount:
                cls.Dcount -= 1
            else:
                cls.Drecycles.append(count)
        else:
            raise Exception("What to do?")