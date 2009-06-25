class Node:pass
class P:
    def __init__(self, data, point):
        self.data = data
        self.point = tuple(int(p) for p in point)
 
def hp_closest(point, hp):
    p = []
    for d in range(len(point)):
        hr_min = hp[0][d]
        hr_max = hp[1][d]
        t = point[d]
        if t <= hr_min: p.append(hr_min)
        elif hr_min < t < hr_max: p.append(t)
        else: p.append(hr_max)
    return tuple(p) 
        
def kdtree(pointList, depth=0):
    if not pointList:
        return
 
    # Select axis based on depth so that axis cycles through all valid values
    k = len(pointList[0].point) # assumes all points have the same dimension
    axis = depth % k
 
    # Sort point list and choose median as pivot element
    pointList.sort(key=lambda point: point.point[axis])
    median = len(pointList)/2 # choose median
 
    # Create node and construct subtrees
    node = Node()
    node.axis = axis
    node.location = pointList[median]
    node.leftChild = kdtree(pointList[0:median], depth+1)
    node.rightChild = kdtree(pointList[median+1:], depth+1)
    return node


dist_cache = {}
def distance(p1, p2):
    global dist_cache
    try:
        return dist_cache[p1,p2]
    except KeyError:
        d = sum((i - j) ** 2 for i,j in zip(p1, p2))
        dist_cache[p1,p2] = d
        return d

def nearestn(point,root,best=(None, 1e400), hr=None):
    if hr == None:
        hr = []
        hr.append([0 for i in range(len(point))])
        hr.append([float('inf') for i in range(len(point))])
    try: 
        n = root
        axis = n.axis
    except:
        return None, float('inf')
    
    # split rectangle
    left_hr = hr[:]
    left_hr[1][axis] = n.location.point[axis]
    right_hr = hr[:]
    right_hr[0][axis] = n.location.point[axis]

    if point[axis] <= n.location.point[axis]: 
        nearer_kd = n.leftChild
        further_kd = n.rightChild
        nearer_hr = left_hr
        further_hr = right_hr
    else:
        nearer_kd = n.rightChild
        further_kd = n.leftChild
        nearer_hr = right_hr
        further_hr = left_hr
    nearest, dist = nearestn(point, nearer_kd, best, nearer_hr)

    if dist < best: best = dist
    
    if distance(point, hp_closest(point, further_hr)) < best:
        if distance(point, n.location.point) < best:
            nearest = n
            best = distance(point, n.location.point)
        tmp_nearest, tmp_dist = nearestn(point, further_kd, best, further_hr)
        if tmp_dist < best:
            nearest, best = tmp_nearest, tmp_dist

    return nearest, best
