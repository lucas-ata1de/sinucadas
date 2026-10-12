import sys
class Point:
    def __init__(self,x : float,y : float):
        self.x=x
        self.y=y

class Polygon:
    def __init__(self,l : list[Point]):
        self.l = l


def PointInPolygon(poly: Polygon, p : Point):
    extreme = Point(float("inf"),p.y)
    count,i = 0,0

    while i!=0:
        next = (i+1)%n
        if doIntersect(poly[i],poly[next],p,extreme):
            if orientation(poly[i],poly[next],p) == 0: #colinears
                return 

    
