base = ((1,2,3,4,6,7),(0,1,2,3,4,6,7),(0,1,2,3,5,6,7))
def gen(b):
    res = []
    for s60 in base[0]:
        res.append(s60)
        for s57 in base[1]:
            res.append(s57)
            for s54 in base[2]:
                res.append(s54)
                yield tuple(res)
                res.pop()
            res.pop()
        res.pop()
def main():
    g = gen(base)
    try:
        ind = 1
        while True:
            v = next(g)
            p = str(ind).rjust(3,' ')
            print(f"{p}: {v}")
            ind += 1
    except:
        print('done')

if __name__ == "__main__":
    main()
#--------- output: (6*7*7 = ) 294 x possible tuples -------------
'''
  1: (1, 0, 0)
  2: (1, 0, 1)
  3: (1, 0, 2)
  4: (1, 0, 3)
  5: (1, 0, 5)
  6: (1, 0, 6)
  7: (1, 0, 7)
  8: (1, 1, 0)
  9: (1, 1, 1)
 10: (1, 1, 2)
 11: (1, 1, 3)
 12: (1, 1, 5)
 13: (1, 1, 6)
 14: (1, 1, 7)
 15: (1, 2, 0)
 16: (1, 2, 1)
 17: (1, 2, 2)
 18: (1, 2, 3)
 19: (1, 2, 5)
 20: (1, 2, 6)
 21: (1, 2, 7)
 22: (1, 3, 0)
 23: (1, 3, 1)
 24: (1, 3, 2)
 25: (1, 3, 3)
 26: (1, 3, 5)
 27: (1, 3, 6)
 28: (1, 3, 7)
 29: (1, 4, 0)
 30: (1, 4, 1)
 31: (1, 4, 2)
 32: (1, 4, 3)
 33: (1, 4, 5)
 34: (1, 4, 6)
 35: (1, 4, 7)
 36: (1, 6, 0)
 37: (1, 6, 1)
 38: (1, 6, 2)
 39: (1, 6, 3)
 40: (1, 6, 5)
 41: (1, 6, 6)
 42: (1, 6, 7)
 43: (1, 7, 0)
 44: (1, 7, 1)
 45: (1, 7, 2)
 46: (1, 7, 3)
 47: (1, 7, 5)
 48: (1, 7, 6)
 49: (1, 7, 7)
 50: (2, 0, 0)
 51: (2, 0, 1)
 52: (2, 0, 2)
 53: (2, 0, 3)
 54: (2, 0, 5)
 55: (2, 0, 6)
 56: (2, 0, 7)
 57: (2, 1, 0)
 58: (2, 1, 1)
 59: (2, 1, 2)
 60: (2, 1, 3)
 61: (2, 1, 5)
 62: (2, 1, 6)
 63: (2, 1, 7)
 64: (2, 2, 0)
 65: (2, 2, 1)
 66: (2, 2, 2)
 67: (2, 2, 3)
 68: (2, 2, 5)
 69: (2, 2, 6)
 70: (2, 2, 7)
 71: (2, 3, 0)
 72: (2, 3, 1)
 73: (2, 3, 2)
 74: (2, 3, 3)
 75: (2, 3, 5)
 76: (2, 3, 6)
 77: (2, 3, 7)
 78: (2, 4, 0)
 79: (2, 4, 1)
 80: (2, 4, 2)
 81: (2, 4, 3)
 82: (2, 4, 5)
 83: (2, 4, 6)
 84: (2, 4, 7)
 85: (2, 6, 0)
 86: (2, 6, 1)
 87: (2, 6, 2)
 88: (2, 6, 3)
 89: (2, 6, 5)
 90: (2, 6, 6)
 91: (2, 6, 7)
 92: (2, 7, 0)
 93: (2, 7, 1)
 94: (2, 7, 2)
 95: (2, 7, 3)
 96: (2, 7, 5)
 97: (2, 7, 6)
 98: (2, 7, 7)
 99: (3, 0, 0)
100: (3, 0, 1)
101: (3, 0, 2)
102: (3, 0, 3)
103: (3, 0, 5)
104: (3, 0, 6)
105: (3, 0, 7)
106: (3, 1, 0)
107: (3, 1, 1)
108: (3, 1, 2)
109: (3, 1, 3)
110: (3, 1, 5)
111: (3, 1, 6)
112: (3, 1, 7)
113: (3, 2, 0)
114: (3, 2, 1)
115: (3, 2, 2)
116: (3, 2, 3)
117: (3, 2, 5)
118: (3, 2, 6)
119: (3, 2, 7)
120: (3, 3, 0)
121: (3, 3, 1)
122: (3, 3, 2)
123: (3, 3, 3)
124: (3, 3, 5)
125: (3, 3, 6)
126: (3, 3, 7)
127: (3, 4, 0)
128: (3, 4, 1)
129: (3, 4, 2)
130: (3, 4, 3)
...
278: (7, 4, 5)
279: (7, 4, 6)
280: (7, 4, 7)
281: (7, 6, 0)
282: (7, 6, 1)
283: (7, 6, 2)
284: (7, 6, 3)
285: (7, 6, 5)
286: (7, 6, 6)
287: (7, 6, 7)
288: (7, 7, 0)
289: (7, 7, 1)
290: (7, 7, 2)
291: (7, 7, 3)
292: (7, 7, 5)
293: (7, 7, 6)
294: (7, 7, 7)
done
'''