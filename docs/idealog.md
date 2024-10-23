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


