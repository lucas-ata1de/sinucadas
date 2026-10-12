import sys
class Point:
    def __init__(self,x : float,y : float):
        self.x=x
        self.y=y

class Polygon:
    def __init__(self,l : list[Point]):
        self.l = l

def onSegment(p : Point, q : Point, r : Point) -> bool: #check if point q is inside the edge p->r
    return (q.x <= max(p.x,r.x) and q.x >= min(p.x,r.x) and q.y <=max(p.y,r.y) and q.y >= min(p.y,r.y))

def orientation(p : Point, q : Point, r : Point) -> int: #returns the orientation of the p->q->r curve (0 collinears, 1 clockwise, 2 counterclockwise)
    val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
    if val==0:
        return 0 #collinears
    if val>0:
        return 1 #clockwise
    return 2 #counterclockwise


def PointInPolygon(poly: Polygon, p : Point) -> bool: #shoot a horizontal ray from p to the right and count how many edges it crosses (odd = inside)
    count,n = 0,len(poly.l)

    for i in range(n):
        a = poly.l[i]
        b = poly.l[(i+1)%n] 

        if orientation(a,b,p) == 0 and onSegment(a,p,b):
            return True

        if (a.y > p.y) != (b.y > p.y): #a and b on opposite sides of the line y = p.y
            t = (p.y - a.y) / (b.y - a.y)
            x = a.x + t * (b.x - a.x)
            if x > p.x:
                count+=1

    return (count%2 != 0)

square = Polygon([Point(0,0),Point(0,1),Point(1,1),Point(1,0)])
diamond = Polygon([Point(0,-1),Point(1,0),Point(0,1),Point(-1,0)])
triangle = Polygon([Point(0,0),Point(2,1),Point(4,0)])

print(PointInPolygon(square,Point(0.5,0.5)))
print(PointInPolygon(diamond,Point(2,0)))
print(PointInPolygon(triangle,Point(2,0.5)))


