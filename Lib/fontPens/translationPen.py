#coding=utf-8
from __future__ import division
from math import pi, radians, degrees, tan, hypot, atan2, cos, sin

"""
Custom Robofab pens — Loïc Sander, june 2015.
copied from http://github.com/loicsander/RobofabPens
updated to Python 3 / RoboFont 4, added convenience functions

"""

from importlib import reload
import fontPens.stepPen
reload(fontPens.stepPen)

from fontTools.pens.pointPen import PointToSegmentPen, SegmentToPointPen, ReverseContourPointPen
from fontTools.misc.bezierTools import splitCubicAtT
from fontTools.pens.basePen import BasePen
from fontPens.stepPen import *


_ANGLE_EPSILON = pi/36


class TranslationPen(BasePen):
    """
    Draw an outline resulting from the reunion of an initial contour and a translated version thereof.
    Translation is defined by an angle and a width/length.

    This kind of drawing basically produces a calligraphic effect (in a translated manner as Gerrit Noordzij puts it),
    it can also serve as a way of extruding a shape for 3D shadow effects.
    """

    def __init__(self, otherPen, frontAngle=0, frontWidth=20):
        self.otherPen = otherPen
        self.frontAngle = radians(frontAngle)
        self.offset = polarCoord((0, 0), radians(frontAngle), frontWidth)
        self.points = []

    def _moveTo(self, pt):
        self.points.append((pt, 'move'))

    def _lineTo(self, pt1):
        pt0, previousType = self.points[-1]
        angle = calcAngle(pt0, pt1)

        self.translatedLineSegment(pt0, pt1)

        self.points.append((pt1, 'line'))

    def _curveToOne(self, c1, c2, pt1):
        pt0, previousType = self.points[-1]

        newSegments = self.splitAtAngledExtremas(pt0, c1, c2, pt1)

        if len(newSegments):
            for segment in newSegments:
                pt0, c1, c2, pt1 = segment
                self.translatedCurveSegment(pt0, c1, c2, pt1)
        else:
            self.translatedCurveSegment(pt0, c1, c2, pt1)

        self.points.append((c1, None))
        self.points.append((c2, None))
        self.points.append((pt1, 'curve'))

    def endPath(self):
        self.points = []

    def closePath(self):
        previousPoint, previousType = self.points[-1]

        if previousType in ['line','curve']:
            pt0, pt1 = self.points[-1][0], self.points[0][0]
            self.translatedLineSegment(pt0, pt1)

        self.points = []

    def splitAtAngledExtremas(self, pt0, pt1, pt2, pt3):
        frontAngle = self.frontAngle
        segments = []
        for i in range(101):
            t = i / 100
            nx, ny = firstDerivative(pt0, pt1, pt2, pt3, t)
            tanAngle = atan2(ny, nx)
            if tan(frontAngle - _ANGLE_EPSILON) < tan(tanAngle) < tan(frontAngle + _ANGLE_EPSILON):
                newSegments = splitCubicAtT(pt0, pt1, pt2, pt3, t)
                if len(newSegments) > 1:
                    segments = newSegments
                    break
        return segments

    def translatedCurveSegment(self, pt0, c1, c2, pt1):
        ox, oy = self.offset
        x0, y0 = pt0
        xc1, yc1 = c1
        xc2, yc2 = c2
        x1, y1 = pt1
        pen = self.getPen([(x0, y0), (x1, y1), (x1+ox, y1+oy), (x0+ox, y0+oy)])
        pen.moveTo((x0, y0))
        pen.curveTo((xc1, yc1), (xc2, yc2), (x1, y1))
        pen.lineTo((x1+ox, y1+oy))
        pen.curveTo((xc2+ox, yc2+oy), (xc1+ox, yc1+oy), (x0+ox, y0+oy))
        pen.closePath()

    def translatedLineSegment(self, pt0, pt1):
        ox, oy = self.offset
        x0, y0 = pt0
        x1, y1 = pt1
        pen = self.getPen([(x0, y0), (x1, y1), (x1+ox, y1+oy), (x0+ox, y0+oy)])
        pen.moveTo((x0, y0))
        pen.lineTo((x1, y1))
        pen.lineTo((x1+ox, y1+oy))
        pen.lineTo((x0+ox, y0+oy))
        pen.closePath()

    def getPen(self, points):
        area = calcArea(points)
        if area < 0:
            pen = self.getReversePen()
        else:
            pen = self.otherPen
        return pen

    def getReversePen(self):
        adapterPen = PointToSegmentPen(self.otherPen)
        reversePen = ReverseContourPointPen(adapterPen)
        return SegmentToPointPen(reversePen)

    def addComponent(self, baseGlyphName, transformation):
        self.otherPen.addComponent(baseGlyphName, transformation)


def translationGlyph(aGlyph, frontAngle=0, frontWidth=20):
    """
    Convenience function that applies the **TranslationPen** pen to a glyph in place.
    """
    if len(aGlyph) == 0:
        return aGlyph
    recorder = RecordingPen()
    filterpen = TranslationPen(recorder, frontAngle=frontAngle, frontWidth=frontWidth)
    aGlyph.draw(filterpen)
    aGlyph.clear()
    recorder.replay(aGlyph.getPen())
    return aGlyph

