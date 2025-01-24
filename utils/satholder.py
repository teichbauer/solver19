from utils.basics import get_bit, set_bits
from datetime import datetime


class SatHolder:
    """ Manages variable-/bit-names. """

    def __init__(self, varray):
        self.varray = varray
        self.ln = len(varray)

    def reduce(self, topbits):
        """ topbits: a list of bits, E.G.:[16,6,1]
        taking topbits(3 pieces) from varray
        return a new satholder with new new varray
        After this.self.varray has reverse (high..low) bit-order."""
        varray = [b for b in self.varray if b not in topbits]
        self.varray = list(reversed(topbits[:]))  # [1,6,16]
        self.ln = len(topbits)
        return SatHolder(varray)

    def drop_vars(self, vars):  # drop 1 var or list/set of vars from varray
        if type(vars) == type(0):
            if vars in self.varray:
                self.varray.remove(vars)
                self.ln -= 1
        else:  # list or set
            for v in vars:
                self.drop_vars(v)
        return self

    def clone(self):
        return SatHolder(self.varray[:])

    def full_sats(self):
        sats = {v: 2 for v in self.varray}
        return sats
