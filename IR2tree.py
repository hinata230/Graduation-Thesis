from Node import Node
from RTree import RTree
import numpy as np
import time
import math
import random
import sys

f = open("_data.txt","r")
num = 20000

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

p = []

for _d in dic :
    p.append(len(dic[_d])/len(dataset))


k = 3

qx = [33.242062, 30.7640769, 34.8228651, 31.3543395, 33.2917792, 34.8145344, 34.0442717, 30.6716912, 30.2351321, 33.6313889]
qy = [-87.5316725, -88.1291684, -87.688918, -87.4291697, -88.2775172, -86.4535904, -85.6799593, -86.5274847, -86.5188741, -86.7758333]


avg_time1 = 0
avg_time2 = 0
avg_time3 = 0
avg_time4 = 0
avg_time5 = 0


ntarget = 0
ptarget = 0
noption = 0
poption = 0

_ntarget = 0
_ptarget = 0
_noption = 0
_poption = 0

al = 0.4
be = 0.4
ga = 0.2

for x,y in zip(qx, qy) :
    for z in range(0, 1) :
        _dataset = random.sample(dataset, num)
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

        option = list(np.random.choice(list(dic.keys()), k+1, replace=False, p=p))
        #option = random.sample(list(dic.keys()), k+1)
        target = option[0:1]
        option = option[1:k+1]
        print(target,option)

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


        """
        start = time.time()
        node.NNsearch(target_inx, option_inx, max_dist, x, y)                
        print('**NNsearch : ', time.time() - start)
        print()
        avg_time1 = avg_time1 + (time.time() - start)
        """

        """
        start = time.time()
        node.IPM1(target_inx, _inx, max_dist, x, y)
        print('**IPM1 : ', time.time() - start)
        avg_time2 = avg_time2 + (time.time() - start)
        """

        """
        start = time.time()
        node.IPM2(target_inx, option_inx, max_dist, x, y)
        print('**IPM2 : ', time.time() - start)
        print()
        avg_time3 = avg_time3 + (time.time() - start)
        """

        start = time.time()
        nt, pt, no, po = node.IPM3(target_inx, _inx, max_dist, x, y, al, be, ga)
        print('**IPM3 : ', time.time() - start)
        print()
        avg_time4 = avg_time4 + (time.time() - start)

        ntarget = ntarget + nt
        ptarget = ptarget + pt
        noption = noption + no
        poption = poption + po

        start= time.time()
        nt, pt, no = node.IPM4(target_inx, _inx, max_dist, x, y, al, be, ga)
        print('**IPM4 : ', time.time() - start)
        print()
        avg_time5 = avg_time5 + (time.time() - start)

        _ntarget = _ntarget + nt
        _ptarget = _ptarget + pt
        _noption = _noption + no
     
print(avg_time4/10, avg_time5/10, ntarget/10, noption/10, _ntarget/10, _noption/10)
