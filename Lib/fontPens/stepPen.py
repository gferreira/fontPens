from __future__ import division
from math import pi, radians, cos, sin, atan2, atan, hypot
import random

"""
Custom Robofab pens — Loïc Sander, april/may 2015.
copied from http://github.com/loicsander/RobofabPens
updated to Python 3 / RoboFont 4, added convenience functions

"""

from fontTools.pens.basePen import BasePen
from fontTools.pens.pointPen import PointToSegmentPen, SegmentToPointPen
from fontTools.pens.recordingPen import RecordingPen
from fontPens.penTools import *


class StepPen(BasePen):
    """
    Pen moving along an outline with a given number of steps.
    Can be subclassed to do systematic drawing, a dotted line for instance.

    In the base implementation, the steps a converted to t values on a segment, thus they will not necessarily be evenly spaced in curve segments.
    If you want evenly spaced steps, you should set the *isPaced* variable to True.
    If *isPaced* is set to True, the pace value is used as a distance, otherwise, it will correspond to a number of steps.

    Subclassing the pen, one does only need to implement the drawStep() method
    to define what will be drawn at each step along the line.

    self.drawStep() receives 3 arguments, a point’s coordinates, the tangent angle at that point,
    and the progression along the currently drawn segment.

    This pen doesn’t draw components.
    """

    def __init__(self, pace=20):
        self.isPaced = True
        self.otherPen = None
        self.pace = pace if pace > 0 else 1
        self.points = []
        self.pacedPoints = []
        self._currentContour = []

    def _moveTo(self, pt):
        self.move_ = True
        self._currentContour.append(pt)
        self.points.append(pt)

    def _lineTo(self, pt1):
        pt0 = self.points[-1]
        d = distance(pt0, pt1)
        tanAngle = calcAngle(pt0, pt1)

        if self.move_ == True:
            self.drawStep(pt0, tanAngle, 0)
            self.pacedPoints.append(pt0)
            self.move_ = False

        if self.isPaced == True:
            steps = int(d / self.pace)
        elif self.isPaced == False:
            steps = self.pace

        if steps <= 0: steps = 1

        x0, y0 = pt0
        x1, y1 = pt1
        for i in range(1, steps+1):
            x = x0 + ((x1 - x0) * (i / steps))
            y = y0 + ((y1 - y0) * (i / steps))
            if (x, y) not in self.points:
                self.drawStep((x, y), tanAngle, i/steps)
                self.pacedPoints.append((x, y))
        self.points.append(pt1)
        self._currentContour.append(pt1)

    def _curveToOne(self, pt1, pt2, pt3):
        pt0 = self.points[-1]
        nx, ny = firstDerivative(pt0, pt1, pt2, pt3, 0)
        tanAngle = atan2(ny, nx)

        if self.move_ == True:
            self.drawStep(pt0, tanAngle, 0)
            self.pacedPoints.append(pt0)
            self.move_ = False

        if self.isPaced == True:
            intervals, d = curveIntervals((pt0, pt1, pt2, pt3), self.pace)
        elif self.isPaced == False:
            intervals = [s/self.pace for s in range(self.pace+1)]

        steps = len(intervals)

        for i, t in enumerate(intervals[1:]):
            x, y = pointOnACurve(pt0, pt1, pt2, pt3, t)
            nx, ny = firstDerivative(pt0, pt1, pt2, pt3, t)
            tanAngle = atan2(ny, nx)
            if (x, y) not in self.points:
                self.drawStep((x, y), tanAngle, i/steps)
                self.pacedPoints.append((x, y))
        self.points.append(pt3)
        self._currentContour.append(pt3)

    def endPath(self):
        if self.otherPen is not None: # and self.otherPen.contour is not None:
            self.otherPen.endPath()
        self.previousPoint = None
        self._currentContour = []

    def closePath(self):
        if len(self._currentContour):
            self._lineTo(self._currentContour[0])
        if self.otherPen is not None: # and self.otherPen.contour is not None:
            self.otherPen.closePath()
        self.previousPoint = None
        self._currentContour = []

    def addComponent(self, glyphName, transformation):
        self.otherPen.addComponent(glyphName, transformation)

    def drawStep(self, pos, tanAngle, progress):
        # x, y = pos
        pass

    def setIsPaced(self, b=True):
        self.isPaced = b


class FlattenPen2(StepPen):
    """Flattens curves into segments of given length (pace value)."""

    def __init__(self, pen, pace=10):
        super(FlattenPen2, self).__init__(pace)
        self.otherPen = pen

    def _lineTo(self, pt1):
        pt0 = self.points[-1]
        d = distance(pt0, pt1)

        if self.move_ == True:
            self.otherPen.moveTo(pt0)
            self.pacedPoints.append(pt0)
            self.move_ = False

        self.otherPen.lineTo(pt1)
        self.pacedPoints.append(pt1)
        self.points.append(pt1)
        self._currentContour.append(pt1)

    def drawStep(self, pos, tanAngle, progress):
        if self.move_ == True:
           drawFunc = self.otherPen.moveTo
        elif self.move_ == False:
            drawFunc = self.otherPen.lineTo
        drawFunc(pos)


def flattenGlyph2(aGlyph, pace=10):
    """
    Convenience function that applies the **FlattenPen2** pen to a glyph in place.
    """
    if len(aGlyph) == 0:
        return aGlyph
    recorder = RecordingPen()
    filterpen = FlattenPen2(recorder, pace=pace)
    aGlyph.draw(filterpen)
    aGlyph.clear()
    recorder.replay(aGlyph.getPen())
    return aGlyph


class SpikePen2(StepPen):
    """Adds spikes to an outline (what do you mean, useless?)."""

    isPaced = True

    def __init__(self, pen, pace=20, spikeLength=25):
        super(SpikePen, self).__init__(pace)
        self.otherPen = pen
        self.spikeLength = spikeLength

    def closePath(self):
        if len(self._currentContour):
            self._lineTo(self._currentContour[0])
        if self.otherPen is not None and self.otherPen.contour is not None:
            self.otherPen.closePath()
        self.previousPoint = None
        self._currentContour = []

    def drawStep(self, pos, tanAngle, progress):
        x1, y1 = pos
        l = self.spikeLength
        x1, y1 = self.pushPoint((x1, y1), tanAngle, l)

        if self.move_ == True:
            self.otherPen.moveTo((x1, y1))

        elif self.move_ == False:
            x0, y0 = self.pushPoint(self.pacedPoints[-1], tanAngle, l)
            d = distance((x0, y0), (x1, y1))
            if d > 0:
                a = calcAngle((x0, y0), (x1, y1))
                sa = atan(l / (d/2))
                sl = hypot(d/2, l)
                sx = x0 + (sl * cos(sa+a))
                sy = y0 + (sl * sin(sa+a))
                self.otherPen.lineTo((sx, sy))
                self.otherPen.lineTo((x1, y1))

    def pushPoint(self, pos, tanAngle, length):
        x, y = pos
        d = length / 2
        angle = tanAngle - (pi/2)
        px = x + (d * cos(angle))
        py = y + (d * sin(angle))
        return px, py
        




