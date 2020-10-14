from Node import Node, Entry, MBR
from itertools import combinations
from itertools import product
import queue
import time
import sys
import copy 
import math

class RTree(object):
    def __init__(self):
        self.mMax = 5
        self.mMin = 2
        self.nNodes = 0
        self.root = None
        self.nPoints = 0

    def insert(self, e):
        if self.root is None:
            #n = Node(p.x, p.y, p.x, p.y, self.nNodes + 1)
            n = Node(e.x, e.y, e.xx, e.yy, self.nNodes + 1, e.feat, e.name)
            self.root = n
            self.nNodes += 1
        else:
            n = self.root

        #e = Entry(p.x, p.y, self.nPoints + 1)
        #self.nPoints += 1


        l = self.chooseLeaf(n, e)
        l.addEntry(e)

        if len(l.entries) > self.mMax:
            n = self.split(l)
            self.adjustTree(n)
        else:
            self.adjustTree(l)
        self.nPoints += 1

    def chooseLeaf(self, n, e):
        if n.isLeaf: return n

        mininc = sys.float_info.max
        nnext = None
        for c in n.entries:
            inc = self.getRequiredExpansion(c, e)
            if inc < mininc:
                mininc = inc
                nnext = c

        return self.chooseLeaf(nnext, e)


    def getRequiredExpansion(self, n, e):
        area = self.getArea(n)
        delta_w = abs(e.xx - n.xx) + abs(e.x - n.x)
        delta_h = abs(e.yy - n.yy) + abs(e.y - n.y)
        expended = (n.xx - n.x + delta_w) * (n.yy - n.y + delta_h)
        return expended - area


    def getArea(self, e):
        w = e.xx - e.x
        h = e.yy - e.y
        return w * h


    def split(self, n):
        s1, s2 = self.pickSeeds(n)
        n1 = Node(s1.x, s1.y, s1.xx, s1.yy, self.nNodes + 1, s1.feat, s1.name)
        n2 = Node(s2.x, s2.y, s2.xx, s2.yy, self.nNodes + 2, s2.feat, s2.name)
        self.nNodes += 2
        n1.addEntry(s1)
        n2.addEntry(s2)

        n.entries.remove(s1)
        n.entries.remove(s2)
        self.distribute(n, n1, n2)

        self.tighten(n1)
        self.tighten(n2)

        if not n.isLeaf: 
            n1.isLeaf = False
            n2.isLeaf = False
        else:
            n.isLeaf = False

        if n.parent is not None:
            n.parent.entries.remove(n)
            n.parent.addEntry(n1)
            n.parent.addEntry(n2)
            np = n.parent
            n = None
            self.tighten(np)

            return np

        else:
            n.addEntry(n1)
            n.addEntry(n2)        
            return n

        
    def pickSeeds(self, n):
        maxArea = -1 * sys.float_info.max

        s = None
        t = None
        for e1 in n.entries:
            for e2 in n.entries:
                if e1 != e2:
                    r = MBR(e1, e2)
                    a = self.getArea(r) - self.getArea(e1) - self.getArea(e2)
                    if a > maxArea:
                        maxArea = a
                        s = e1
                        t = e2
        return s, t


    def distribute(self, n, n1, n2):
        th = self.mMax - self.mMin + 1

        while len(n.entries) > 0 and len(n1.entries) < th  and len(n2.entries) < th: 
            e = self.pickNext(n, n1, n2)
            a1 = self.getArea(MBR(n, n1)) - self.getArea(n)
            a2 = self.getArea(MBR(n, n2)) - self.getArea(n)

            n.entries.remove(e)
            if a1 < a2:                                 n1.addEntry(e)
            elif a2 < a1:                               n2.addEntry(e)
            elif self.getArea(n1) < self.getArea(n2):   n1.addEntry(e)
            elif self.getArea(n1) > self.getArea(n2):   n2.addEntry(e)
            elif len(n1.entries) < len(n2.entries):     n1.addEntry(e)
            else:                                       n2.addEntry(e)

        if len(n.entries) > 0:
            if len(n1.entries) >= th:
                while len(n.entries) > 0:
                    e = n.entries[0]
                    n2.addEntry(e)
                    n.entries.remove(e)
            else:
                while len(n.entries) > 0:
                    e = n.entries[0]
                    n1.addEntry(e)
                    n.entries.remove(e)


    def pickNext(self, n, n1, n2):
        maxArea = -1
        s = None
        for e in n.entries:
            a1 = self.getArea(MBR(e, n1)) - self.getArea(n1)
            a2 = self.getArea(MBR(e, n2)) - self.getArea(n2)
            a = abs(a1 - a2)
            if maxArea < a:
                maxArea = a
                s = e

        return s



    def adjustTree(self, n):
        self.tighten(n)
        if len(n.entries) > self.mMax:
            np = self.split(n)            
            self.adjustTree(np)
        elif n.parent is not None:
            self.adjustTree(n.parent)


    def tighten(self, n):
        x = sys.float_info.max 
        y = sys.float_info.max 
        xx = sys.float_info.min 
        yy = sys.float_info.min 

        n.sig = 0

        for e in n.entries:
            if e.x < x:         x = e.x
            if e.xx > xx:       xx = e.xx
            if e.y < y:         y = e.y
            if e.yy > yy:       yy = e.yy

            n.sig = n.sig | e.sig

        n.x = x
        n.y = y
        n.xx = xx
        n.yy = yy


    def range(self, e):
        q = [self.root]
        r = []
        cnt = 0
        while q:
            n = q.pop(0)
            if not n.isLeaf:
                for c in n.entries:
                    if c.intersects(e):
                        q.append(c)
            else:
                cnt += len(n.entries)
                for c in n.entries:
                    o = c.object
                    if e.contains(o):
                        r.append(o)

        return r

    def appro(self, target, inx, max_dist, qx, qy, al, be, ga) :
        U = queue.Queue()
        V = []
        k = len(inx)

        root = [0] * (k+1)
        root[0] = [self.root]

        R = (k+1)

        for i in range(0, k) :
            root[i+1] = [self.root]

        U.put(root)
        q = Node(qx,qy,qx,qy,0,0," ")
   
        min_cost = 999
        while not U.empty() :
            u = U.get()

            target_mbr = u[0]
            option_mbr = u[1:]

            t = queue.PriorityQueue()

            for tmbr in target_mbr :
                if tmbr.entries :
                    for child in tmbr.entries :
                        if child.sig & target != 0 :
                            t.put ( (q.minDistance(child)/max_dist, child) )

                else :
                    mx = 0
                    dist = []
                    obj = []
                    _obj = []
                    c = 1
                    j = -1
                    cur_dist = 0

                    for i in range(0, k) :
                        for ombr in option_mbr[i] :
                            dist.append(tmbr.minDistance(ombr)/max_dist)
                            obj.append(ombr.name)

                    sort = sorted(zip(dist, obj))

                    for i in range(0, len(sort)) :
                        if sort[i][0] - cur_dist < (i-j)/R :
                            c = c + (i-j)
                            _obj.append(sort[i][1])
                            cur_dist = sort[i][0]
                            j =i

                    cost = al * q.minDistance(tmbr)/max_dist + be * cur_dist + ga * (1 - c/(k+1))

                    if min_cost > cost :
                        V = []
                        min_cost = cost
                        V.append(tmbr.name)
                        V = V + _obj


            while not t.empty() :
                tmbr = t.get()[1]

                op = [0]*k
                dist = [99]*k
                mbr = [0]*k
                mx = 0

                for i in range(0, k) :
                    for ombr in option_mbr[i] :
                        if ombr.entries :
                            for child in ombr.entries :
                                if child.sig & inx[i] != 0 :
                                    if dist[i] > tmbr.minDistance(child)/max_dist :
                                        dist[i] = tmbr.minDistance(child)/max_dist
                                        mbr[i] = [child]

                U.put([[tmbr]]+mbr)

        return min_cost, V


    def appro2(self, target, option, max_dist, qx, qy) :
        U = queue.PriorityQueue()
        cost_V, _V, V = self.appro(target, option, max_dist, qx, qy)
        O = V[1:]
        min_cost = cost_V
        U.put( (0, self.root) )
        query = Node(qx,qy,qx,qy,0,0," ")
        mn = 99

        while not U.empty() :
            qu = U.get()
            tmbr = qu[1]

            if tmbr.entries :
                for child in tmbr.entries :
                    if target & child.sig != 1 and query.minDistance(child)/max_dist < cost_V :
                        U.put( (query.minDistance(child)/max_dist, child) )

            else :
                mx = 0

                for o in O :
                    if mx < tmbr.minDistance(o)/max_dist :
                        mx = tmbr.minDistance(o)/max_dist

                if mx < mn :
                    mn = mx
                    t = tmbr
                
        dist = []
        inx = []
        obj = []
        _obj = []
        c = 1
        j = -1
        cur_dist = 0
        R = option.count(1) + 1

        for i in range(0, len(O)) :
            dist.append(t.minDistance(O[i])/max_dist)
            obj.append(O[i])

        sort = sorted(zip(dist, obj))

        for i in range(0, len(sort)) :
            if sort[i][0] - cur_dist < (i-j)/R :
                c = c + (i-j)
                _obj.append(sort[i][1])
                cur_dist = sort[i][0]
                j = i

        cost_LB = query.minDistance(t)/max_dist + cur_dist + (1-c/R)
        
        return cost_LB, [t]+_obj


    def IPM1(self, target, inx, max_dist, qx, qy) :
        q = queue.Queue()
        min_cost = 999
        V = []
        root = [0]*(len(inx)+1)
        R = len(inx)+1

        root[0] = [self.root]
        
        for i in range(0, len(inx)) :
            if self.root.sig & inx[i] != 0 :
                root[i+1] = [self.root]

        q.put_nowait(root)
        query = Node(qx,qy,qx,qy,0,0," ")

        while not q.empty() :
            mbr = q.get()

            target_mbr = mbr[0]
            option_mbr = mbr[1:]

            t = []
            for tmbr in target_mbr :
                _min = 9999
                _max = -9999
                if tmbr.entries :
                    for child in tmbr.entries :
                        if target & child.sig != 0 :
                            t.append(child)
                            if _min > query.minDistance(child)/max_dist :
                                _min = query.minDistance(child)/max_dist
                                _max = query.maxDistance(child)/max_dist


                else :
                    dist = [99] * len(inx)
                    o = [0] * len(inx)

                    for i in range(0, len(inx)) :
                        for ombr in option_mbr[i] :
                            if dist[i] > tmbr.minDistance(ombr)/max_dist:
                                dist[i] = tmbr.minDistance(ombr)/max_dist
                                o[i] = ombr.name

                    _sort = sorted(zip(dist,o))
                    _object = []
                    flag = False
                    c = 1 
                    j = -1
                    cur_dist = 0 

                    for i in range(0, len(_sort)) :
                        if _sort[i][0] == 99 :
                            break

                        if i == 0 :
                            if _sort[i][0] < (1/R) :
                                cur_dist = _sort[i][0]
                                _object.append(_sort[i][1])
                                c = c + 1
                                j = 0
                        
                        else :
                            if _sort[i][0] - cur_dist < (i-j)/R :
                                c = c + (i-j)
                                cur_dist = _sort[i][0]
                                j = i
                                _object.append(_sort[i][1])

                    _cost = query.minDistance(tmbr)/max_dist + cur_dist + (1 - c/R)

                    if min_cost > _cost :
                        min_cost = _cost
                        V = [tmbr] + _object

            for tmbr in t : 
                op = [0]*len(inx)
                
                for i in range(0, len(inx)) :
                    qu = queue.PriorityQueue()
                    for ombr in option_mbr[i] :
                        if ombr.entries :
                            for child in ombr.entries :
                                if child.sig & inx[i] != 0 :
                                    dist = tmbr.minDistance(child)
                                    qu.put((dist, child))


                        _mx = -999
                        while not qu.empty() :
                            _q = qu.get()

                            if op[i] == 0 :
                                op[i] = [_q[1]]

                            else :
                                op[i].append(_q[1])

                
                q.put([[tmbr]]+op)
    

        print(min_cost, end = ' ')
        for i in range(0, len(V)) :
            if i == 0 :
                print(V[i].name, end = ' ')
            else :
                print(V[i], end = ' ')
        print()


    def IPM2(self, target, option, max_dist, qx, qy) :
        q = queue.PriorityQueue()
        root = [0]*61
        R = option.count(1) + 1
        root[0] = [self.root]
        V = []
        start = time.time()
        cost_V, V, _V = self.appro(target, option, max_dist, qx, qy)
        min_cost = cost_V

        print(cost_V, end = ' ')
        for v in V :
            print(v.name, end = ' ')
        print()
        print('**Appro1 : ', time.time() - start)

        start = time.time()
        cost_V, V = self.appro2(target, option, max_dist, qx, qy)
        
        print(cost_V, end = ' ')
        for v in V :
            print(v.name, end = ' ')
        print()
        print('**Appro2 : ', time.time() - start)

        for i in range(1, 61) :
            if option[i-1] == 1 and self.root.sig[i-1] == 1 :
                root[i] = [self.root]

        q.put_nowait( (0, root) )
        query = Node(qx,qy,qx,qy,0,0," ")

        ntarget = 0
        ptarget = 0
        noption = 0
        poption = 0
        nLB = 0
        pLB = 0

        while not q.empty() :
            qu = q.get()
            mbr = qu[1]
            LB = qu[0]

            if LB > cost_V : 
                continue

            target_mbr = mbr[0]
            option_mbr = mbr[1:61]

            t = []
            for tmbr in target_mbr :
                _min = 9999
                _max = -9999
                if tmbr.entries :
                    for child in tmbr.entries :
                        for i in range(0, 60) :
                            if target[i] == 1 and child.sig[i] == 1 :
                                if cost_V < query.minDistance(child)/max_dist :
                                    ptarget = ptarget + 1
                                    continue

                                t.append(child)
                                ntarget = ntarget + 1
                                
                else :
                    dist = [99] * 60
                    o = [0] * 60

                    for i in range(0, 60) :
                        if option_mbr[i] == 0 :
                            continue

                        for ombr in option_mbr[i] :
                            if dist[i] > tmbr.minDistance(ombr)/max_dist:
                                dist[i] = tmbr.minDistance(ombr)/max_dist
                                o[i] = ombr.name

                    _sort = sorted(zip(dist,o))
                    _object = []
                    flag = False
                    c = 1 
                    j = -1
                    cur_dist = 0 

                    for i in range(0, len(_sort)) :
                        if _sort[i][0] == 99 :
                            break

                        if i == 0 :
                            if _sort[i][0] < (1/R) :
                                cur_dist = _sort[i][0]
                                _object.append(_sort[i][1])
                                c = c + 1
                                j = 0
                        
                        else :
                            if _sort[i][0] - cur_dist < (i-j)/R :
                                c = c + (i-j)
                                cur_dist = _sort[i][0]
                                j = i
                                _object.append(_sort[i][1])

                    _cost = query.minDistance(tmbr)/max_dist + cur_dist + (1 - c/R)

                    if min_cost > _cost :
                        min_cost = _cost
                        V = [tmbr.name] + _object

            for tmbr in t : 
                op = [0]*60
                
                for i in range(0, 60) :
                    if option_mbr[i] != 0:

                        _qu = queue.PriorityQueue()
                        for ombr in option_mbr[i] :
                            if ombr.entries :
                                for child in ombr.entries :
                                    if child.sig[i] == 1 and option[i] == 1 :
                                        noption = noption + 1
                                        _qu.put((tmbr.minDistance(child)/max_dist, child))
                                        

                        _mx = -99
                        flag = True
                        while not _qu.empty() :
                            _q = _qu.get()

                            if _q[0] > _mx and _mx != -99 :
                                poption = poption + 1
                                break

                            if op[i] == 0 :
                                if _mx == -99 :
                                    _mx = tmbr.maxDistance(_q[1])/max_dist

                                if _q[0] > cost_V : 
                                    poption = poption + 1
                                    pLB = pLB + 1
                                    flag = False
                                    break

                                op[i] = [_q[1]]

                            else :
                                op[i].append(_q[1])

                if not flag :
                    continue

                dist = []
                inx = []
                cur_dist = 0
                j = -1
                c = 1

                for i in range(0, 60) :
                    if op[i] != 0 :
                        dist.append(tmbr.minDistance(op[i][0])/max_dist)
                        inx.append(i)

                sort = sorted(zip(dist, inx))


                for i in range(0, len(sort)) :
                    if sort[i][0] - cur_dist < (i-j)/R :
                        c = c + (i-j)

                        if cur_dist == 0 :
                            cur_dist = sort[i][0]
                        j = i

                for i in range(j+1, len(sort)) :
                    if op[sort[i][1]] != 0 :
                        poption = poption + len(op[sort[i][1]])
                        op[sort[i][1]] = 0


                _cost_LB = query.minDistance(tmbr)/max_dist + cur_dist + (1- c/R)
                nLB = nLB + 1

                if _cost_LB < cost_V :
                    q.put ( (_cost_LB, [[tmbr]]+op) )

                else :
                    pLB = pLB + 1
                
        print(min_cost, end = ' ')
        for i in range(0, len(V)) :
            print(V[i], end = ' ')
        print()

        print('target : ', ntarget, ptarget)
        print('option : ', noption, poption)
        print('LB : ',nLB, pLB)

    def IPM3(self, target, inx, max_dist, qx, qy, al, be, ga) :
        q = queue.PriorityQueue()
        
        start = time.time()
        V = []
        cost_V, V = self.appro(target, inx, max_dist, qx, qy, al, be, ga)
        print(cost_V, end = ' ')
        for v in V :
            print(v , end = ' ')
        print()

        print('**appro :', time.time() - start)

        min_cost = cost_V

        k = len(inx)
        root = [0]*(k+1)
        root[0] = [self.root]

        R = k+1

        for i in range(0, k) :
            if self.root.sig & inx[i] != 0 :
                root[i+1] = [self.root]

        q.put_nowait( (0, root) )
        query = Node(qx,qy,qx,qy,0,0," ")

        ntarget = 0
        ptarget = 0
        noption = 0
        poption = 0
        nLB = 0
        pLB = 0

        mindist={}
        maxdist={}
        count = 0

        while not q.empty() :
            qu = q.get()

            count = count + 1

            mbr = qu[1]
            LB = qu[0]

            if LB > cost_V : 
                continue

            target_mbr = mbr[0]
            option_mbr = mbr[1:]

            t = []
            for tmbr in target_mbr :

                if tmbr.entries :
                    for child in tmbr.entries :
                        ntarget = ntarget + 1
                        if child.sig & target != 0 :
                            if cost_V < al * query.minDistance(child)/max_dist :
                                ptarget = ptarget + 1
                                continue

                            t.append(child)
                                
                else :
                    dist = [99] * k
                    o = [0] * k

                    for i in range(0, k) :
                        for ombr in option_mbr[i] :
                            if ombr.sig & inx[i] != 0 :
                                if dist[i] > tmbr.minDistance(ombr)/max_dist:
                                    dist[i] = tmbr.minDistance(ombr)/max_dist
                                    o[i] = ombr.name


                    _sort = sorted(zip(dist,o))
                    _object = []
                    flag = False
                    c = 1 
                    j = -1
                    cur_dist = 0 

                    for i in range(0, len(_sort)) :
                        if i == 0 :
                            if _sort[i][0] < (1/R) :
                                cur_dist = _sort[i][0]
                                _object.append(_sort[i][1])
                                c = c + 1
                                j = 0
                        
                        else :
                            if _sort[i][0] - cur_dist < (i-j)/R :
                                c = c + (i-j)
                                cur_dist = _sort[i][0]
                                j = i
                                _object.append(_sort[i][1])

                    _cost = al * query.minDistance(tmbr)/max_dist + be * cur_dist + ga * (1 - c/R)

                    if min_cost > _cost :
                        min_cost = _cost
                        V = [tmbr.name] + _object

            for tmbr in t : 
                op = [0] * k
               
                for i in range(0, k) :
                    _qu = queue.PriorityQueue()
                    for ombr in option_mbr[i] :
                        if ombr.entries :
                            for child in ombr.entries :
                                noption = noption + 1
                                if child.sig & inx[i] != 0 :
                                    _qu.put((tmbr.minDistance(child)/max_dist, child))
                                        
                    _mx = -99
                    flag = True
                    while not _qu.empty() :
                        _q = _qu.get()

                        if _mx == -99 :
                            _mx = tmbr.maxDistance(_q[1])/max_dist
                                
                        if _q[0] > _mx :
                            poption = poption + _qu.qsize()
                            break

                        if op[i] == 0 :
                            op[i] = [_q[1]]

                        else :
                            op[i].append(_q[1])

                dist = []
                _inx = []
                cur_dist = 0
                j = -1
                c = 1

                for i in range(0, k) :
                    dist.append(tmbr.minDistance(op[i][0])/max_dist)
                    _inx.append(i)

                sort = sorted(zip(dist, _inx))

                for i in range(0, len(sort)) :
                    if sort[i][0] - cur_dist < (i-j)/R :
                        c = c + (i-j)
                        cur_dist = sort[i][0]
                        j = i

                _cost_LB = al * query.minDistance(tmbr)/max_dist + be * cur_dist + ga * (1- c/R)

                if _cost_LB < cost_V :
                    q.put ( (_cost_LB, [[tmbr]]+op) )

                else :
                    ptarget = ptarget + 1

        print(min_cost, end = ' ')
        for i in range(0, len(V)) :
            print(V[i], end = ' ')
        print()

        print('target : ', ntarget, ptarget)
        print('option : ', noption, poption)

        return ntarget, ptarget, noption, poption
        
    def IPM4(self, target, inx, max_dist, qx, qy, al, be, ga) :
        q = queue.PriorityQueue()
        distance = {}
        
        start = time.time()
        V = []
        cost_V, V = self.appro(target, inx, max_dist, qx, qy, al, be, ga)
        """
        print(cost_V, end = ' ')
        for v in V :
            print(v , end = ' ')
        print()

        print('**appro :', time.time() - start)
        """

        min_cost = cost_V

        k = len(inx)
        root = [0]*(k+1)
        root[0] = [self.root]

        R = k+1

        for i in range(0, k) :
            if self.root.sig & inx[i] != 0 :
                root[i+1] = [self.root]

        q.put_nowait( (0, root) )
        query = Node(qx,qy,qx,qy,0,0," ")

        ntarget = 0
        ptarget = 0
        noption = 0
        poption = 0
        nLB = 0
        pLB = 0

        mindist={}
        maxdist={}
        count = 0

        while not q.empty() :
            qu = q.get()

            count = count + 1

            mbr = qu[1]
            LB = qu[0]

            #print(mbr[0][0].id, LB, cost_V)

            if LB > cost_V : 
                break

            target_mbr = mbr[0]
            option_mbr = mbr[1:]

            t = []
            for tmbr in target_mbr :

                if tmbr.entries :
                    for child in tmbr.entries :
                        ntarget = ntarget + 1
                        if child.sig & target != 0 :
                            key_q = tuple([query])
                            key_c = tuple([child])

                            if not distance.get(key_q + key_c) :
                                distance[key_q + key_c] = query.minDistance(child)/max_dist

                            if cost_V < al * distance[key_q + key_c] :
                                ptarget = ptarget + 1
                                continue

                            t.append(child)
                                
                else :
                    dist = [99] * k
                    o = [0] * k

                    for i in range(0, k) :
                        for ombr in option_mbr[i] :
                            if ombr.sig & inx[i] != 0 :
                                key_o = tuple([ombr])
                                key_t = tuple([tmbr])

                                if not distance.get(key_t + key_o) :
                                    distance[key_t + key_o] = tmbr.minDistance(ombr)/max_dist

                                if dist[i] > distance[key_t + key_o]:
                                    dist[i] = distance[key_t + key_o]
                                    o[i] = ombr.name


                    _sort = sorted(zip(dist,o))
                    _object = []
                    flag = False
                    c = 1 
                    j = -1
                    cur_dist = 0 

                    for i in range(0, len(_sort)) :
                        if i == 0 :
                            if _sort[i][0] < (1/R) :
                                cur_dist = _sort[i][0]
                                _object.append(_sort[i][1])
                                c = c + 1
                                j = 0
                        
                        else :
                            if _sort[i][0] - cur_dist < (i-j)/R :
                                c = c + (i-j)
                                cur_dist = _sort[i][0]
                                j = i
                                _object.append(_sort[i][1])

                    key_q = tuple([query])
                    key_t = tuple([tmbr])

                    if not distance.get(key_q + key_t) :
                        distance[key_q + key_t] = query.minDistance(tmbr)/max_dist

                    _cost = al * distance[key_q + key_t] + be * cur_dist + ga * (1 - c/R)

                    if min_cost > _cost :
                        min_cost = _cost
                        V = [tmbr.name] + _object

            for tmbr in t : 
                op = [0] * k
               
                for i in range(0, k) :
                    _qu = queue.PriorityQueue()
                    for ombr in option_mbr[i] :
                        if ombr.entries :
                            for child in ombr.entries :
                                noption = noption + 1
                                if child.sig & inx[i] != 0 :
                                    key_t = tuple([tmbr])
                                    key_c = tuple([child])

                                    if not distance.get(key_t + key_c) :
                                        distance[key_t + key_c] = tmbr.minDistance(child)/max_dist

                                    _qu.put((distance[key_t + key_c], child))
                                        
                    _mx = -99
                    flag = True
                    while not _qu.empty() :
                        _q = _qu.get()

                        if _mx == -99 :
                            _mx = tmbr.maxDistance(_q[1])/max_dist
                                
                        if _q[0] > _mx :
                            poption = poption + _qu.qsize()
                            break

                        if op[i] == 0 :
                            op[i] = [_q[1]]

                        else :
                            op[i].append(_q[1])

                dist = []
                _inx = []
                cur_dist = 0
                j = -1
                _j = -1
                c = 1

                for i in range(0, k) :
                    key_t = tuple([tmbr])
                    key_o = tuple([op[i][0]])

                    if not distance.get(key_t + key_o) :
                        distance[key_t + key_o] = tmbr.minDistance(op[i][0])/max_dist

                    dist.append(distance[key_t + key_o])
                    _inx.append(i)

                sort = sorted(zip(dist, _inx))

                _x = -1
                _c = 1
                _cur_dist = 0

                for i in range(0, len(sort)) :
                    if sort[i][0] - cur_dist < (i-j)/R :
                        c = c + (i-j)
                        cur_dist = sort[i][0]
                        j = i

                _cost_LB = al * distance[key_q + key_t] + be * cur_dist + ga * (1- c/R)

                if _cost_LB > cost_V :
                    continue

                key_q = tuple([query])
                key_t = tuple([tmbr])

                _c = c
                _j = j
                _cur_dist = cur_dist
                _cost_AB = 0
                for i in range(j+1, len(sort)) :
                    key_o = tuple([op[_inx[i]][0]])

                    _cost_AB = al * distance[key_q + key_t] + be * distance[key_t + key_o] + ga * (1 - (_c+1)/R)
                    if _cost_AB <= cost_V :
                        _j = i
                        _cur_dist = distance[key_t + key_o]
                        _c = _c + 1                        

                for i in range(j-c+2, _j+1) :

                    """
                    x = len(op[_inx[i]])

                    for x in range(len(op[_inx[i]])-1, 1, -1) :
                        key_o = tuple([op[_inx[i]][x]])

                        if al * distance[key_q + key_t] + be * distance[key_t + key_o] + ga * (1-(_c)/R) <= cost_V :
                            x = x + 1
                            break

                    op[_inx[i]] = op[_inx[i]][0:x]

                    """

                    key_o = tuple([op[_inx[i]][len(op[_inx[i]])-1]])
                    if al * distance[key_q + key_t] + be * distance[key_t + key_o] + ga * (1 - (_c)/R) <= cost_V :
                        continue

                    else :
                        x = self.bisearch(be, tmbr, op[_inx[i]], distance, cost_V - ( 1 - (_c)/R + al * distance[key_q + key_t]))
                        op[_inx[i]] = op[_inx[i]][0:x]
                    

                if _cost_LB < cost_V :
                    q.put ( (_cost_LB, [[tmbr]]+op) )

                else :
                    ptarget = ptarget + 1

        print(min_cost, end = ' ')
        for i in range(0, len(V)) :
            print(V[i], end = ' ')
        print()

        print('target : ', ntarget, ptarget)
        print('option : ', noption)

        return ntarget, ptarget, noption
        
    def bisearch(self, be, tmbr, op, distance, cost) :
        left = 0
        right = len(op)-1

        key_t = tuple([tmbr])
        while left<=right :
            mid = int((left+right)/2)

            key_o = tuple([op[mid]])
            if be * distance[key_t + key_o] > cost :
                right = mid - 1
            elif be * distance[key_t + key_o] < cost :
                left = mid + 1

            elif be * distance[key_t + key_o] == cost :
                return mid+1
            
        return left+1

    def makeList (self, target, option, appro_cost, k, enum, max_dist, qx, qy, o, _t, qu, ch) :
        global dic
        global min_cost
        global V

        if len(enum) <= k and ch == True:
            if not _t.entries :

                lb = self.LBcost(target, option, max_dist, qx, qy, _t, enum, True)
                if lb == -1 :
                    return

                flag = False

                for e in enum :
                    key_e = tuple([e])
                    if not dic.get(e) :
                        dic[e] = 1
                        flag = True

                if flag == False :
                    return

                if appro_cost >= lb :
                    if min_cost > lb :
                        min_cost = lb
                        V = [_t] + enum

                    else :
                        return

                else :
                    return

            else :
                lb = self.LBcost(target, option, max_dist, qx, qy, _t, enum, False)

                if appro_cost >= lb :
                    qu.put ( (lb, [[_t] + enum]) )
                    print(min_cost, lb, enum)

                else :
                    return


        for i in range(0, len(o)) :
            for _o in o[i] :
                if not _o in enum :
                    enum.append(_o)
                    self.makeList(target, option, appro_cost, k, enum, max_dist, qx, qy, o, _t, qu, True) 
                    enum.remove(_o)


    def LBcost (self, target, option, max_dist, qx, qy, _t, l, ch) :
        global dist

        query = Node(qx, qy, qx, qy , 0, 0, " ")
        key_q = tuple([query])
        key_t = tuple([_t])

        if not dist.get(key_q + key_t) :
            dist[key_q + key_t] = query.minDistance(_t)/max_dist

        cost = dist[key_q + key_t]
        _op = [0] * 60
        _mn = 99
        _mx = 0

        for op in l :
            for i in range(0, 60) :
                if op.sig[i] == 1 and option[i] == 1 :
                    if ch == True :
                        if _op[i] == 1 :
                            return -1

                    _op[i] = 1

                    
            key_op = tuple([op])

            if not dist.get(key_t + key_op) :
                dist[ key_t + key_op ] = _t.minDistance(op)/max_dist


            if ch == False :
                if _mn > dist[ key_t + key_op ] :
                    _mn = dist[ key_t + key_op ]

            if ch == True :
                if _mx < dist[ key_t + key_op ] :
                    _mx = dist[ key_t + key_op ]


        if _mn == 99 :
            _mn = 0

        if ch == False :
            cost = cost + _mn + (1 - (_op.count(1) + 1)/(option.count(1) + 1) )

        elif ch == True :
            cost = cost + _mx + (1 - (_op.count(1) + 1)/(option.count(1) + 1) )

        return cost


    def traverse(self):
        s = [(self.root, 0)]

        while len(s) > 0:
            n, lv = s.pop()

            t = ""
            for i in range(lv):
                t += "\t"
            print(t, n.name, n.x,n.y,n.xx,n.yy, n.feat, n.isLeaf, bin(n.sig), n)
            
            if not n.isLeaf:
                for nn in n.entries:
                    s.append((nn, lv + 1))

            else:
                for e in n.entries:
                    print(t,"\t",e.name, e.x, e.y, e.xx, e.yy, e.feat, e.isLeaf, bin(e.sig), e)


    def NNsearch(self, target, option, max_dist, qx, qy) :
        qu = queue.Queue()
        R = option.count(1) + 1
        root = [0]*61
        root[0] = [self.root]
        V = []

        for i in range(1, 61) :
            if option[i-1] == 1 and self.root.sig[i-1] == 1 :
                root[i] = [self.root]

        query = Node(qx,qy,qx,qy,0,0," ")

        min_cost = 999

        qu.put ( (0, self.root) )

        t = []
        while not qu.empty() :
            node = qu.get()
            tmbr = node[1]

            if tmbr.entries :
                for child in tmbr.entries :
                    for i in range(0, 60) :
                        if target[i] == 1 and child.sig[i] == 1 :
                            qu.put( (query.minDistance(child), child) )

            else :
                t.append(tmbr)

        
        for tmbr in t :
            dist = [99]*60
            mbr = [0]*60 
            q = []
            q.append(self.root)

            while q :
                node = q.pop(0)
                
                if node.entries :
                    for child in node.entries :
                        for i in range(0, 60) :
                            if child.sig[i] == 1 and option[i] == 1 :
                                q.append(child)

                else :
                    for i in range(0, 60) :
                        if node.sig[i] == 1 and option[i] == 1 :
                            if dist[i] > tmbr.minDistance(node) :
                                dist[i] = tmbr.minDistance(node)
                                mbr[i] = node

            option_mbr = []

            for i in range(0, 60) :
                if option[i] == 1 :
                    option_mbr.append(mbr[i])

            for i in range(0, len(option_mbr) + 1) :
                for op in list(combinations(option_mbr, i)) :
                    cand = list(op)

                    cost = query.minDistance(tmbr)/max_dist
                    maxd2 = 0
                    for can in cand :
                        if maxd2 < tmbr.minDistance(can) :
                            maxd2 = tmbr.minDistance(can)

                    sim = 1 - (i+1)/R
                    cost = cost + maxd2/max_dist + sim

                    if min_cost > cost :
                        min_cost = cost
                        V = [tmbr]+cand

                        print(min_cost, end =' ')
                        for v in V :
                            print(v.name, end =' ')
                        print()


        return V


    def Type2Appro1(self, target, option, max_dist, qx, qy) :
        U = queue.PriorityQueue()
        V = []
        uSkiSet = [0] * 60
        
        for i in range(0, 60) :
            if option[i] == 1 :
                uSkiSet[i] = 1

        
        q = Node(qx,qy,qx,qy,0,0," ")

        U.put((self.root,0))

        while not U.empty() :
            e = U.get()[0]

            if not e.entries :
                if not e.name in V and uSkiSet[e.feat] == 1:
                    V.append(e)
                    uSkiSet[e.feat] = 0

                    flag = False
                    for i in range(0, 60) :
                        if uSkiSet[i] == 1 :
                            flag = True

                    if flag == False :
                        break

            
            else :
                for j in range(0, 60) :
                    if e.sig[j] == 1 and uSkiSet[j] == 1 :
                        for _e in e.entries :
                            for i in range(0, 60) :
                                if _e.sig[i] == 1 and uSkiSet[i] == 1 :
                                    U.put((_e, q.minDistance(_e)))
                

        return V

    def cost(self, q, V) :
        max_dist = 0
        cost = 0

        for v in V :
            if q.minDistance(v) > cost :
                cost = q.minDistance(v)

        for v1,v2 in zip(V,V) :
            if v1 != v2 :
                if v1.minDistance(v2) > max_dist :
                    max_dist = v1.minDistance(v2)

        cost = cost + max_dist
        return cost


    def minCost (self, target, option, q, N, max_dist) :
        t = N[0]
        o = N[1:]
        c = [0]*60

        cost = q.minDistance(t)/max_dist

        mx = 0
        for _o in o :
            for i in range(0, 60) :
                if _o.sig[i] == 1 and option[i] == 1:
                    c[i] = 1

            if t.minDistance(_o)/max_dist > mx :
                mx = t.minDistance(_o)/max_dist

        cost = cost + mx + (1 - c.count(1)/(option.count(1)+1))

        return cost


    def _cost (self, target, option, q, N, max_dist) :
        k = option.count(1) + 1
        t = N[0]
        o = N[1:]

        cost = q.minDistance(t)/max_dist
        min_cost = 999

        for i in range(0, len(o)+1) :
            for _o in list(combinations(o, i)) :

                mx = 0
                for op in _o :
                    if t.minDistance(op)/max_dist > mx :
                        mx = t.minDistance(op)/max_dist

                if cost + mx + (1 - i/k) < min_cost :
                    min_cost = cost + mx + (1 - i/k)
                    V = [t] + (list(_o))

        return min_cost, V


    def Type2Appro2(self, target, option, max_dist, qx, qy) :
        U = queue.PriorityQueue()
        V = self.Type2Appro1(target, option, max_dist, qx, qy)
        q = Node(qx,qy,qx,qy, 0,0, " ")

        mx = 0
        ts = 0
        for v in V :
            if q.minDistance(v) > mx :
                mx = q.minDistance(v)
                ts = v.feat

        cost_v = self.cost(q, V)
        cost_V = 0

        U.put((self.root, 0))
        
        while not U.empty() :
            e = U.get()[0]

            if e.isLeaf == True :
                if q.minDistance(e) >= cost_v :
                    break

                if e.entries :
                    for _e in e :
                        if _e.sig[ts] == 1 :
                            U.put((_e, q.minDistance(_e)))

                else :
                    if e.sig[ts] == 1 :
                        U.put((e, q.minDistance(e)))

            else :
                if q.minDistance(e) > cost_v :
                    break

                _V = self.Type2Appro1(target, option, max_dist, e.x, e.y)
                _cost_V = self.cost(q, _V)

                if _cost_V < cost_V :
                    cost_V = _cost_V
                    V = _V

        return V


    def TopDown(self, target, option, max_dist, qx, qy) :
        U = queue.PriorityQueue()
        U.put(([self.root, self.root], 0))
        V = self.Type2Appro2(target, option, max_dist, qx, qy)
        q = Node(qx,qy,qx,qy, 0,0, " ")
        cost_V = self.cost(q, V)
        R = option.count(1)

        while not U.empty() :
            N = U.get()[0]

            _T = N[0]
            _N = N[1:]

            _cost_V = self.minCost(target, option, q, N, max_dist)

            if _cost_V >= cost_V :
                break

            if not _T.entries  :
                #_V = self.Exhaustive(target, option, max_dist, qx, qy, N)
                _cost_V, _V = self._cost(target, option, q, N, max_dist)

                print(_cost_V, end = ' ')
                for v in _V :
                    print(v.name, end = ' ')
                print()

                if _cost_V < cost_V :
                    cost_V = _cost_V
                    V = _V

            else :
                for t in _T.entries :
                    for i in range(0, 60) :
                        if t.sig[i] == 1 and target[i] == 1 :
                            qt = Node(t.x,t.y,t.x,t.y,0,0," ")
                            S = self.EnumerateSet(target, option, _N, cost_V, q, qt,  max_dist)

                            for ns in S :
                                c = [0]*60
                                for j in range(0, len(ns)) :
                                    for k in range(0, 60) :
                                        if ns[j].sig[k] == 1 and option[k] == 1 :
                                            c[k] = 1
        
                                if c.count(1) == R :
                                    cost_ns = self.minCost(target, option, q, [t]+ns, max_dist)
                                    U.put(([t]+ns, cost_ns))
                    
        return V
                
    def Exhaustive(self, target, option, max_dist, qx, qy, N) :
        q = Node(qx,qy,qx,qy,0,0," ")
        objects = []
        V = []
        t = N[0]
        o = N[1:]

        min_cost = 999

        for i in range(0, len(o)+1) :
            for l in list(combinations(o,i)) :
                _cost_V, _V = self._cost(target, option, q, [t]+list(l), max_dist)
               
                if _cost_V < min_cost :
                    min_cost = _cost_V
                    V = [t]+list(l)

        return V

    def EnumerateSet(self, target, option, N, cost, q, qt, max_dist) :
        setList = []
        cList = []
        L = []
        _L = []
        k = option.count(1)
        j = 0

        for node in N :
            _cList = []

            for child in node.entries :
                if self.minCost(target, option, q, [qt]+[child], max_dist)  <= cost :
                    _L.append([child])

            for m in range(2, k-len(N)+2) :
                for ns1 in _L :
                    for ns2 in _L :                        
                        if ns1 != ns2 :
                            ns = list(set(ns1) | set(ns2))
                            if not ns in L and len(ns) == len(ns1) + 1 and self.minCost(target, option, q, [qt]+ns, max_dist) < cost :
                                L.append(ns)

                cList.append(L)
                _L = L
                L = []

        for _cList in cList :
            for ns in _cList :
                if self.minCost(target, option, q, [qt]+ns, max_dist) < cost :
                    setList.append(ns)

        return setList

