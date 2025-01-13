### 2024-11-28
```
when vk2 hit 1 bit of root bits of a sn, this vk2 should be totally
removed from vk2dic of path(Now that I have path, but not vkrepo)
the reason: for hit_cvs: vk2->vk1->bb, for mis_cvs, it is obsolete anyway
```

### 2024-11-27
```
path.grow(S60 + S57) <-S54: path has a bit-blocker(19-0) and S54 has 
root[20-1 19-0 7-0]. [19-0] will have hit-cvs:(015), no-hit-cvs:(2367)
bb.node ^ 54:(015) will generate block, where bb(19-0) will be covered,
and on [19-1](2367) bb(19-0) will not be hit. This means, bb(19-0)
can be removed. If there is bb(19-1), this would generated a block
(added to blckmgr) and bb(19-1) will then be removed.
```
### 2024-11-23a
```
when merging S57 into S60, 60:C0120[53-0 28-0](467) touches 
57root[49-1 36-0 28-1], B(28-0):57(0246)/B(28-1):57:(137). 
Here C0120 will be excluded anywhere, because for 28-0, 
it will form a bit-block [53-0] where C0120 will not 
be used; and for 28-1, C0120 is unhit(to be excluded). and
that is the reason self.exclmgr.add(C0120, None)
```
  
### 2024-10-22
---
#### in tools.py/vk1s_mergable(vk1a, vk1b) when merging S54 to s60+57
```
vk1a:  57:U0053[21-0]{60:(4) 57:(0) 54:(1357)}
vk1b:  57:U0053[21-0]{60:(234) 57:(0)}
```
- should they be mergable? In this case vk1b covers all child-vals of S54
  That means, it would have 54:(*). Here, 60:(234) is a superset of 60:(4)
  so that vk1a can be omitted - vk1b totally covers it. Here two cases are possible:

    1. mergable:
       if vkb.cvs/vka.cvs has the same # of novs(let's say 3 nvs), and, 
       on all but one nov, vk1b and vk1a have one cvs(sets), that are different cvs can be merged: the cvs from vka and vkb on this nov, can be merged.

    2. containment:
       if vk1b has 1 ot more nov less than vk1a has, logically, vk1b has full coverage for those missing nov. And, for each novs vk1b and vk1a share, vk1b[nv] is a superset of vk1a[nov], then, vk1a is contained by vk1b, and can be omitted.

### 2024-10-31
#### question: how can vk1s be merged?
- **vk1s on bit-12**
```
57:U0389 [12-0]{ 60:(123467) 57:(3)    54:(0123)    51:(157)     }
57:U0209 [12-0]{ 60:(123)    57:(23)   54:(2367)    51:(0124567) }
57:U0372 [12-0]{ 60:(123)    57:(23)   54:(0123567) 51:(157)     }
57:U0123 [12-0]{ 60:(13)     57:(0)    54:(57)      51:(0124567) }
57:U0355 [12-0]{ 60:(14)     57:(3)    54:(026)     51:(157)     }
57:U0223 [12-0]{ 60:(2367)   57:(0123) 54:(37)      51:(0124567) }
57:U0219 [12-0]{ 60:(23)     57:(0)    54:(2367)    51:(0124567) }
57:U0320 [12-0]{ 60:(23)     57:(13)   54:(0)       51:(0124567) }
57:U0086 [12-0]{ 60:(4)      57:(0123) 54:(57)      51:(0124567) }
57:U0221 [12-0]{ 60:(4)      57:(01)   54:(37)      51:(0124567) }
57:U0144 [12-0]{ 60:(7)      57:(01)   54:(57)      51:(0124567) }
57:U0278 [12-0]{ 60:(467)    57:(013)  54:(26)      51:(0124567) }
57:U0334 [12-0]{ 60:(4)      57:(13)   54:(13)      51:(0124567) }

60:U0401 [12-1]{ 60:(2367)   57:(0123) 54:(1357)    51:(157)     }
60:U0021 [12-1]{ 60:(23)     57:(0)    54:(0123567) 51:(0124567) }
60:U0054 [12-1]{ 60:(23)     57:(0123) 54:(015)     51:(0124567) }
60:U0257 [12-1]{ 60:(7)      57:(1)    54:(5)       51:(0124567) }
```

#### question: how can blocks be merged?
```
blocks:
----------------------------------------------------
{ 60:(467)      57:(4)        54:(0123567)  }
{ 60:(23)       57:(0)        54:(0123567)  }
{ 60:(23)       57:(01)       54:(015)      }
{ 60:(46)       57:(0246)     54:(0123)     }
{ 60:(4)        57:(0123467)  54:(37)       }
{ 60:(123467)   57:(23)       54:(01)       }
{ 60:(4)        57:(4)        54:(1)        }
{ 60:(3)        57:(0)        54:(57)       }
{ 60:(3)        57:(0)        54:(5)        }
{ 60:(7)        57:(1)        54:(57)       }
{ 60:(46)       57:(04)       54:(1357)     }
{ 60:(4)        57:(04)       54:(1357)     }
{ 60:(12346)    57:(04)       54:(57)       }
{ 60:(4)        57:(014)      54:(1357)     }
{ 60:(4)        57:(014)      54:(57)       }
{ 60:(46)       57:(04)       54:(57)       }
{ 60:(467)      57:(014)      54:(57)       }
{ 60:(123)      57:(04)       54:(57)       }
{ 60:(23)       57:(0)        54:(2367)     }
{ 60:(23)       57:(0)        54:(37)       }
{ 60:(7)        57:(1)        54:(5)        }
{ 60:(67)       57:(0246)     54:(26)       }
{ 60:(467)      57:(2)        54:(26)       }
{ 60:(67)       57:(0)        54:(26)       }
{ 60:(23)       57:(13)       54:(0)        }
```