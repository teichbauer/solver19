from center import Center

class NodeGroup:
    # node: {60:2, 57:1, 54:0,..}
    # node-group(ng): {60:(2,3), 54:(0 3,5,7)}
    def __init__(self, nov):
        self.nov = nov
        self.node_blockers = []  # [ng1 ng2,, ..]
        self.vk2_blockers = {}   # {kn: ng,..}
        # -----------------------
        self.k1ns = []
        self.bdic1 = {}
        self.vk2dic = {}
        self.vk2dic = {}
        # --------------------
        self.nodegrps = []

    def add_nb(self, nb):   # add node-blocker
        pass

    def add_vkblocker(self, vb):    # add vk2-blocker
        pass


