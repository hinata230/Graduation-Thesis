from Node import Node
from RTree import RTree
import numpy as np
import time
import math
import random
import sys

f = open("_data.txt","r")
w = open("data_visual_90000.txt","w")

num = 30000

nodeid = 0
class_num = []
dataset = []
dic = {}

while True :
    line = f.readline()
    if not line : break
    data = []

    name = line.split("|")[0]
    feature = line.split("|")[1]

    if feature == "FEATURE_CLASS" : continue
    x = float(line.split("|")[2])
    y = float(line.split("|")[3])

    if (x == 0 and y == 0) : continue

    data.append(name)
    data.append(feature)
    data.append(x)
    data.append(y)
    dataset.append(data)

    if not feature in dic :
        dic[feature] = [data]

    else :
        dic[feature].append(data)

p = {}

for _d in dic :
    p[_d] = len(dic[_d])

p = sorted(p.items(), key=(lambda x:x[1]))

keyword = []
_key= {}
for _p in p :
    keyword.append(_p[1])
    _key[_p[1]] = _p[0]

k = 6

qx = [33.242062, 30.7640769, 34.8228651, 31.3543395, 33.2917792, 34.8145344, 34.0442717, 30.6716912, 30.2351321, 33.6313889]
qy = [-87.5316725, -88.1291684, -87.688918, -87.4291697, -88.2775172, -86.4535904, -85.6799593, -86.5274847, -86.5188741, -86.7758333]


for ab in range(9, 10, 2) :
    """
    al = (ab/10) / 2
    be = (ab/10) / 2
    ga = 1 - ab/10
    """

    al = 0.25
    be = 0.25
    ga = 0.5


    avg_time1 = 0
    avg_time2 = 0
    avg_time3 = 0
    avg_time4 = 0

    t1 = 0
    t2 = 0
    t3 = 0
    t4 = 0

    o1 = 0
    o2 = 0
    o3 = 0
    o4 = 0

    _o1 = 0
    _o2 = 0
    _o3 = 0
    _o4 = 0

    _ratio = 0

    for x,y in zip(qx, qy) :
        _dataset = random.sample(dataset, num)
        w.writelines(str(_dataset))

        node = RTree()
        class_num = {}
        _class = []

        inx = 0
        for data in _dataset :
            if not data[1] in class_num :
                class_num[data[1]] = inx
                _class.append(data[1])
                inx = inx + 1

            n = Node(data[2],data[3],data[2],data[3], 0 , class_num[data[1]], data[0])
            node.insert(n)

        #option = list(np.random.choice(list(dic.keys()), k+1, replace=False, p=p))

        """
        percen = [random.randrange(10, 50) for i in range(0, k)]
        _option = np.percentile(keyword, percen, interpolation = 'nearest')

        percen = [random.randrange(50, 90)]
        _target = np.percentile(keyword, percen, interpolation = 'nearest')
        """

        percen = [random.randrange(50, 100) for i in range(0, k+1)]
        _option = np.percentile(keyword, percen, interpolation = 'nearest')

        target = []
        option = []

        #option = random.sample(list(dic.keys()), k+1)
        target = _key[_option[0]]
        
        for i in range(1, k+1) :
            option.append(_key[_option[i]])

        print(target,option)
        print('al : ', al)
        print('be : ', be)
        print('ga : ', ga)

        max_dist = ((node.root.xx - node.root.x)**2 + (node.root.yy - node.root.y)**2)**0.5
        x = random.uniform(node.root.x, node.root.xx)
        y = random.uniform(node.root.y, node.root.yy)

        target_inx=0
        option_inx=0

        j = 1
        i = 0
        _inx = {}

        for feature in _class :
            if feature in target :
                target_inx += j

            if feature in option :
                _inx[i] = j
                i = i + 1

            j = j * 2


        start = time.time()
        nt, no, ob = node.NNsearch(target_inx, _inx, max_dist, x, y, al, be, ga)               
        print('**NNsearch : ', time.time() - start)
        print()
        avg_time1 = avg_time1 + (time.time() - start)

        t1 = t1 + nt
        o1 = o1 + no
        _o1 = _o1 + ob
        

        
        start = time.time()
        nt, no, ob = node._IPM1(target_inx, _inx, max_dist, x, y, al, be, ga)
        print('**IPM1 : ', time.time() - start)
        avg_time2 = avg_time2 + (time.time() - start)

        t2 = t2 + nt
        o2 = o2 + no
        _o2 = _o2 + ob
        

        """
        start = time.time()
        node.IPM2(target_inx, option_inx, max_dist, x, y)
        print('**IPM2 : ', time.time() - start)
        print()
        avg_time3 = avg_time3 + (time.time() - start)
        """

        start = time.time()
        nt, no, ob = node.IPM1(target_inx, _inx, max_dist, x, y, al, be, ga)
        print('**IPM3 : ', time.time() - start)
        print()
        avg_time3 = avg_time3 + (time.time() - start)

        t3 = t3 + nt
        o3 = o3 + no
        _o3 = _o3 + ob


        start= time.time()
        nt, no, ob, ratio = node.IPM3(target_inx, _inx, max_dist, x, y, al, be, ga)
        print('**IPM4 : ', time.time() - start)
        print()
        avg_time4 = avg_time4 + (time.time() - start)

        t4 = t4 + nt
        o4 = o4 + no
        _o4 = _o4 + ob
        _ratio = _ratio + ratio

        """
        start = time.time()
        nt, no = node.IPM5(target_inx, _inx, max_dist, x, y, al, be, ga)
        print('**IPM5 : ', time.time() - start)
        print()
        avg_time5 = avg_time5 + (time.time() - start)

        t5 = t5 + nt
        o5 = o5 + no
        """
     
    print(al, be, ga)
    print(_ratio/10)
    print(avg_time1/10, avg_time2/10, avg_time3/10, avg_time4/10)
    print(t1/10, t2/10, t3/10, t4/10)
    print(o1/10, o2/10, o3/10, o4/10)
    print(_o1/10, _o2/10, _o3/10, _o4/10)

