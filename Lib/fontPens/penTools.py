import math
from fontTools.misc.bezierTools import calcQuadraticArcLengthC


def distance(pt1, pt2):
    """
    The distance between two points

    >>> distance((0, 0), (10, 0))
    10.0
    >>> distance((0, 0), (-10, 0))
    10.0
    >>> distance((0, 0), (0, 10))
    10.0
    >>> distance((0, 0), (0, -10))
    10.0
    >>> distance((10, 10), (13, 14))
    5.0
    """
    return math.sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)


def middlePoint(pt1, pt2):
    """
    Return the point that lies in between the two input points.
    """
    (x0, y0), (x1, y1) = pt1, pt2
    return 0.5 * (x0 + x1), 0.5 * (y0 + y1)


def getCubicPoint(t, pt0, pt1, pt2, pt3):
    """
    Return the point for t on the cubic curve defined by pt0, pt1, pt2, pt3.

    >>> getCubicPoint(0.00, (0, 0), (50, -10), (80, 50), (120, 40))
    (0, 0)
    >>> getCubicPoint(0.20, (0, 0), (50, -10), (80, 50), (120, 40))
    (27.84, 1.280000000000002)
    >>> getCubicPoint(0.50, (0, 0), (50, -10), (80, 50), (120, 40))
    (63.75, 20.0)
    >>> getCubicPoint(0.85, (0, 0), (50, -10), (80, 50), (120, 40))
    (102.57375, 40.2475)
    >>> getCubicPoint(1.00, (0, 0), (50, -10), (80, 50), (120, 40))
    (120, 40)
    """
    if t == 0:
        return pt0
    if t == 1:
        return pt3
    if t == 0.5:
        a = middlePoint(pt0, pt1)
        b = middlePoint(pt1, pt2)
        c = middlePoint(pt2, pt3)
        d = middlePoint(a, b)
        e = middlePoint(b, c)
        return middlePoint(d, e)
    else:
        cx = (pt1[0] - pt0[0]) * 3
        cy = (pt1[1] - pt0[1]) * 3
        bx = (pt2[0] - pt1[0]) * 3 - cx
        by = (pt2[1] - pt1[1]) * 3 - cy
        ax = pt3[0] - pt0[0] - cx - bx
        ay = pt3[1] - pt0[1] - cy - by
        t3 = t ** 3
        t2 = t * t
        x = ax * t3 + bx * t2 + cx * t + pt0[0]
        y = ay * t3 + by * t2 + cy * t + pt0[1]
        return x, y


def getQuadraticPoint(t, pt0, pt1, pt2):
    """
    Return the point for t on the quadratic curve defined by pt0, pt1, pt2, pt3.

    >>> getQuadraticPoint(0.00, (0, 0), (50, -10), (80, 50))
    (0, 0)
    >>> getQuadraticPoint(0.21, (0, 0), (50, -10), (80, 50))
    (20.118, -1.113)
    >>> getQuadraticPoint(0.50, (0, 0), (50, -10), (80, 50))
    (45.0, 7.5)
    >>> getQuadraticPoint(0.87, (0, 0), (50, -10), (80, 50))
    (71.862, 35.583)
    >>> getQuadraticPoint(1.00, (0, 0), (50, -10), (80, 50))
    (80, 50)
    """
    if t == 0:
        return pt0
    if t == 1:
        return pt2
    a = (1 - t) ** 2
    b = 2 * (1 - t) * t
    c = t ** 2

    x = a * pt0[0] + b * pt1[0] + c * pt2[0];
    y = a * pt0[1] + b * pt1[1] + c * pt2[1];
    return x, y


def getCubicPoints(ts, pt0, pt1, pt2, pt3):
    """
    Return a list of points for increments of t on the cubic curve defined by pt0, pt1, pt2, pt3.

    >>> getCubicPoints([i/10 for i in range(11)], (0, 0), (50, -10), (80, 50), (120, 40))
    [(0.0, 0.0), (14.43, -1.0399999999999996), (27.84, 1.280000000000002), (40.41, 6.119999999999999), (52.32, 12.640000000000008), (63.75, 20.0), (74.88, 27.36), (85.89, 33.88), (96.96, 38.72000000000001), (108.27000000000001, 41.040000000000006), (120.0, 40.0)]
    """
    (x0, y0), (x1, y1) = pt0, pt1
    cx = (x1 - x0) * 3
    cy = (y1 - y0) * 3
    bx = (pt2[0] - x1) * 3 - cx
    by = (pt2[1] - y1) * 3 - cy
    ax = pt3[0] - x0 - cx - bx
    ay = pt3[1] - y0 - cy - by
    path = []
    for t in ts:
        t3 = t ** 3
        t2 = t * t
        x = ax * t3 + bx * t2 + cx * t + x0
        y = ay * t3 + by * t2 + cy * t + y0
        path.append((x, y))
    return path


def estimateCubicCurveLength(pt0, pt1, pt2, pt3, precision=10):
    """
    Estimate the length of this curve by iterating
    through it and averaging the length of the flat bits.

    >>> estimateCubicCurveLength((0, 0), (0, 0), (0, 0), (0, 0), 1000)
    0.0
    >>> estimateCubicCurveLength((0, 0), (0, 0), (120, 0), (120, 0), 1000)
    120.0
    >>> estimateCubicCurveLength((0, 0), (50, 0), (80, 0), (120, 0), 1000)
    120.0
    >>> estimateCubicCurveLength((0, 0), (50, -10), (80, 50), (120, 40), 1)
    126.49110640673517
    >>> estimateCubicCurveLength((0, 0), (50, -10), (80, 50), (120, 40), 1000)
    130.4488917899906
    """
    length = 0
    step = 1.0 / precision
    points = getCubicPoints([f * step for f in range(precision + 1)], pt0, pt1, pt2, pt3)
    for i in range(len(points) - 1):
        pta = points[i]
        ptb = points[i + 1]
        length += distance(pta, ptb)
    return length


def estimateQuadraticCurveLength(pt0, pt1, pt2, precision=10):
    """
    Estimate the length of this curve by iterating
    through it and averaging the length of the flat bits.

    >>> estimateQuadraticCurveLength((0, 0), (0, 0), (0, 0)) # empty segment
    0.0
    >>> estimateQuadraticCurveLength((0, 0), (50, 0), (80, 0)) # collinear points
    80.0
    >>> estimateQuadraticCurveLength((0, 0), (50, 20), (100, 40)) # collinear points
    107.70329614269008
    >>> estimateQuadraticCurveLength((0, 0), (0, 100), (100, 0))
    153.6861437729263
    >>> estimateQuadraticCurveLength((0, 0), (50, -10), (80, 50))
    102.4601733446439
    >>> estimateQuadraticCurveLength((0, 0), (40, 0), (-40, 0)) # collinear points, control point outside
    66.39999999999999
    >>> estimateQuadraticCurveLength((0, 0), (40, 0), (0, 0)) # collinear points, looping back
    40.0
    """
    points = []
    length = 0
    step = 1.0 / precision
    factors = range(0, precision + 1)
    for i in factors:
        points.append(getQuadraticPoint(i * step, pt0, pt1, pt2))
    for i in range(len(points) - 1):
        pta = points[i]
        ptb = points[i + 1]
        length += distance(pta, ptb)
    return length


def interpolatePoint(pt1, pt2, v):
    """
    interpolate point by factor v

    >>> interpolatePoint((0, 0), (10, 10), 0.5)
    (5.0, 5.0)
    >>> interpolatePoint((0, 0), (10, 10), 0.6)
    (6.0, 6.0)
    """
    (xa, ya), (xb, yb) = pt1, pt2
    if not isinstance(v, tuple):
        xv = v
        yv = v
    else:
        xv, yv = v
    return xa + (xb - xa) * xv, ya + (yb - ya) * yv


def calcVector(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    dx = x2 - x1
    dy = y2 - y1
    return dx, dy


def calcAngle(point1, point2):
    dx, dy = calcVector(point1, point2)
    return atan2(dy, dx)


def calcArea(points):
    l = len(points)
    area = 0
    for i in range(l):
        x1, y1 = points[i]
        x2, y2 = points[(i+1)%l]
        area += (x1*y2)-(x2*y1)
    return area / 2


def satellize(pos, angle, width, shift=0.5):
    x, y = pos
    x1, y1 = polarCoord((x, y), angle, width*shift)
    x2, y2 = polarCoord((x, y), angle, -(width*(1-shift)))
    return (x1, y1), (x2, y2)


def polarCoord(pos, angle, distance):
    x, y = pos
    nx = x + (distance * math.cos(angle))
    ny = y + (distance * math.sin(angle))
    return nx, ny


def pointOnACurve(pt1, bcp1, bcp2, pt2, value):
    (x1, y1), (cx1, cy1), (cx2, cy2), (x2, y2) = pt1, bcp1, bcp2, pt2
    # From Frederik Berlaen’s Outliner
    dx = x1
    cx = (cx1 - dx) * 3.0
    bx = (cx2 - cx1) * 3.0 - cx
    ax = x2 - dx - cx - bx
    dy = y1
    cy = (cy1 - dy) * 3.0
    by = (cy2 - cy1) * 3.0 - cy
    ay = y2 - dy - cy - by
    mx = ax*(value)**3 + bx*(value)**2 + cx*(value) + dx
    my = ay*(value)**3 + by*(value)**2 + cy*(value) + dy
    return mx, my


def remap(values, newMin=0, newMax=1):
    initDelta = values[-1] - values[0]
    if initDelta == 0:
        return values
    newDelta = newMax - newMin
    for i, v in enumerate(values):
        ratio = v / initDelta
        new = newMin + (newDelta * ratio)
        values[i] =  new
    return values


def curveIntervals(params, pace=10):
    a1, h1, h2, a2 = params
    l = 0
    c = 1
    intervals = [0]
    ax, ay = a1
    bx, by = h1
    cx, cy = h2
    dx, dy = a2
    # define an arbitrary number of steps that’s likely to be inferior to the size of a pixel/grid unit
    delta = int(hypot(dx-ax, dy-ay) * 1.5)
    if delta != 0:
        for i in range(delta+1):
            t = i/delta
            x, y = pointOnACurve((ax, ay), (bx, by), (cx, cy), (dx, dy), t)
            if i > 0:
                l += hypot(x-px, y-py)
                if l >= c * pace:
                    intervals.append(t)
                    c += 1
            px, py = x, y
        intervals = remap(intervals)
    return intervals, l


def bezierTangent(a, b, c, d, t):
    # Implementation of http://stackoverflow.com/questions/4089443/find-the-tangent-of-a-point-on-a-cubic-bezier-curve-on-an-iphone
    return (-3*(1-t)**2 * a) + (3*(1-t)**2 * b) - (6*t*(1-t) * b) - (3*t**2 * c) + (6*t*(1-t) * c) + (3*t**2 * d)


def firstDerivative(pt1, bcp1, bcp2, pt2, value):
    (x1, y1), (cx1, cy1), (cx2, cy2), (x2, y2) = pt1, bcp1, bcp2, pt2
    mx = bezierTangent(x1, cx1, cx2, x2, value)
    my = bezierTangent(y1, cy1, cy2, y2, value)
    return mx, my




if __name__ == "__main__":
    import doctest
    doctest.testmod()

