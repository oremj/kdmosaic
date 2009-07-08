class Node:pass
class P:
    def __init__(self, data, point):
        self.data = data
        self.point = tuple(int(p) for p in point)
 

def hr_closest(point, hr):
    '''Finds closest point in hyperrectangle to point'''
    p = []
    for d in range(len(point)):
        hr_min = hr[0][d]
        hr_max = hr[1][d]
        t = point[d]
        if t <= hr_min: p.append(hr_min)
        elif hr_min < t < hr_max: p.append(t)
        else: p.append(hr_max)
    return tuple(p) 
        
def countitems(root):
    tmp = [root]
    count = 1
    while tmp:
        node = tmp.pop()
        count += 1
        if node.leftChild:
            tmp.append(node.leftChild)
        if node.rightChild:
            tmp.append(node.rightChild)

    return count
def removenode(startnode):
    points = []
    tmp = [startnode]

    while tmp:
        node = tmp.pop()
        if node.leftChild:
            tmp.append(node.leftChild)
            points.append(node.leftChild.location)
        if node.rightChild:
            tmp.append(node.rightChild)
            points.append(node.rightChild.location)
    
    if not points:
        parent, branch = startnode.parent 
        setattr(parent, branch, None)
    else:
        new_startnode = kdtree(points,startnode.axis) 
        startnode.location = new_startnode.location
        startnode.leftChild = new_startnode.leftChild
        startnode.rightChild = new_startnode.rightChild
        startnode.depth = new_startnode.dep
        try:
            startnode.leftChild.parent = (startnode, 'leftChild')
            startnode.rightChild.parent = (startnode, 'rightChild')
        except AttributeError: pass

def kdtree(pointList, depth=0):
    '''Builds kdtree from list of points'''
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
    node.dep = depth
    node.parent = None
    node.axis = axis
    node.location = pointList[median]
    node.leftChild = kdtree(pointList[0:median], depth+1)
    node.rightChild = kdtree(pointList[median+1:], depth+1)
    try:
        node.leftChild.parent = (node, 'leftChild')
        node.rightChild.parent = (node, 'rightChild')
    except AttributeError: pass

    return node


dist_cache = {}
def distance(p1, p2):
    '''Computes distance between two points'''
    global dist_cache
    try:
        return dist_cache[p1,p2]
    except KeyError:
        d = sum((i - j) ** 2 for i,j in zip(p1, p2))
        dist_cache[p1,p2] = d
        return d

def nearestn(point,root,best=(None, 1e400), hr=None):
    '''Return nearest neighbor to point'''
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
    
    if distance(point, hr_closest(point, further_hr)) < best:
        if distance(point, n.location.point) < best:
            nearest = n
            best = distance(point, n.location.point)
        tmp_nearest, tmp_dist = nearestn(point, further_kd, best, further_hr)
        if tmp_dist < best:
            nearest, best = tmp_nearest, tmp_dist

    return nearest, best
