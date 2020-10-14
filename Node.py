from scipy.spatial import distance
from shapely.geometry import Point

class Node(object):
    def __init__(self, x, y, xx, yy, nodeid, feature, name):
        self.x = x
        self.y = y
        self.xx = xx
        self.yy = yy
        self.parent = None
        self.entries = []
        self.count = 0              #Aggregate count
        self.id = nodeid
        self.isLeaf = True
        self.feat = feature

        k = 1
        self.sig = 0
        for i in range(0, 60) :
            if i == feature :
                self.sig += k
            k = k*2

        self.name = name
        self.visit = False

    def __lt__ (self, e) :
        return self.x < e.x

    def bounds(self):
        return self.x, self.y, self.xx, self.yy

    def addEntry(self, e):
        self.entries.append(e)
        e.parent = self

    def intersects(self, e):
        if e.x > self.xx: return False
        if e.xx < self.x: return False
        if e.y > self.yy: return False
        if e.yy < self.y: return False
        return True

    def contains(self, p):
        if self.x <= p.x and self.xx >= p.x and self.y <= p.y and self.yy >= p.y:
            return True
        else:
            return False

    def minDistance(self, e):
        if isinstance(e, Entry) or isinstance(e, Node):
            if self.intersects(e):
                return 0
            elif (self.x <= e.x and self.xx >= e.x) or (self.x <= e.xx and self.xx >= e.xx):
                return min(abs(self.y - e.y), abs(self.yy - e.y), abs(self.y - e.yy), abs(self.yy - e.yy))
            elif (self.y <= e.y and self.yy >= e.y) or (self.y <= e.yy and self.yy >= e.yy):
                return min(abs(self.x - e.x), abs(self.xx - e.x), abs(self.x - e.xx), abs(self.xx - e.xx))
            else:
                d1 = Point(e.x, e.y).distance(Point(self.xx, self.yy))
                d2 = Point(e.xx, e.y).distance(Point(self.x, self.yy))
                d3 = Point(e.x, e.yy).distance(Point(self.xx, self.y))
                d4 = Point(e.xx, e.yy).distance(Point(self.x, self.y))
                return min(d1, d2, d3, d4)

        else:           #e is Point instance
            if self.contains(e):
                return 0
            elif self.x < e.x and self.xx > e.x:
                return min(abs(e.y - self.y), abs(e.y - self.yy))
            elif self.y < p.y and self.yy > e.y:
                return min(abs(e.x - self.x), abs(e.x - self.xx))
            else:
                d1 = e.distance(Point(e.x, e.y))
                d2 = e.distance(Point(e.xx, e.y))
                d3 = e.distance(Point(e.x, e.yy))
                d4 = e.distance(Point(e.xx, e.yy))

                return min(d1, d2, d3, d4)
    
    def maxDistance (self, e) :
        if isinstance(e, Entry) or isinstance(e, Node):
            d1 = Point(e.x, e.y).distance(Point(self.xx, self.yy))
            d2 = Point(e.xx, e.y).distance(Point(self.x, self.yy))
            d3 = Point(e.x, e.yy).distance(Point(self.xx, self.y))
            d4 = Point(e.xx, e.yy).distance(Point(self.x, self.y))

            return max(d1, d2, d3, d4)

        else :
            d1 = e.distance(Point(e.x, e.y))
            d2 = e.distance(Point(e.xx, e.y))
            d3 = e.distance(Point(e.x, e.yy))
            d4 = e.distance(Point(e.xx, e.yy))

            return max(d1, d2, d3, d4)


    def trav(self, v) :
        v[self.id] = 1
        if not self.isLeaf :
            for node in self.entries :
                if v[node.id] == 0 :
                    print(node.name, node.id)

                    for i in range(0,60) :
                        print(v[i], end = '')
                    print()

                    node.trav(v)
        else :
            return

class Entry(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.xx = x
        self.yy = y
        self.parent = None

    def __init__(self, x, y, xx, yy, obj, cnt = 0):
        self.x = x
        self.y = y
        self.xx = xx
        self.yy = yy
        self.parent = None
        self.object = obj
        self.count = cnt

    def contains(self, p):
        if self.x <= p.x and self.xx >= p.x and self.y <= p.y and self.yy >= p.y:
            return True
        else:
            return False

    def intersects(self, e):
        if e.x > self.xx: return False
        if e.xx < self.x: return False
        if e.y > self.yy: return False
        if e.yy < self.y: return False
        return True


class MBR(object):
    def __init__(self, e1, e2):
        if e1.x < e2.x:         self.x = e1.x
        else:                   self.x = e2.x
        if e1.xx > e2.xx:       self.xx = e1.xx
        else:                   self.xx = e2.xx
        if e1.y < e2.y:         self.y = e1.y
        else:                   self.y = e2.y
        if e1.yy > e2.yy:       self.yy = e1.yy
        else:                   self.yy = e2.yy


