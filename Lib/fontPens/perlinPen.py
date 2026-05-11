from math import atan2, cos, sin
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.basePen import BasePen
from fontPens.flattenPen import flattenGlyph


def calcAngle(pt1, pt2):
    return atan2((pt2[1] - pt1[1]), (pt2[0] - pt1[0]))

def lerp(aa, bb, factor):
    return aa + (bb-aa) * factor

def calcMidPoint(pt1, pt2):
    xMid = lerp(pt1[0], pt2[0], .5)
    yMid = lerp(pt1[1], pt2[1], .5)
    return xMid, yMid


class PerlinPen(BasePen):

    def __init__(self, otherPen, intensity, factory, fixedParameters=None):

        BasePen.__init__(self, {})
        self.otherPen = otherPen
        self.pnf = factory
        self.fixedParameters = fixedParameters
        self.intensity = intensity
        self.lastPt = None

    def _moveTo(self, pt):
        self.otherPen.moveTo(pt)
        self.firstPt = self.lastPt = pt

    def _lineTo(self, pt):
        midPt = calcMidPoint(pt, self.lastPt)
        angle = calcAngle(pt, self.lastPt)

        if self.fixedParameters:
            noise = self.pnf(midPt[0], midPt[1], *self.fixedParameters)
        else:
            noise = self.pnf(midPt[0], midPt[1])

        assert -.75 <= noise <= .75, f'we have a problem with noise: {noise}'
        xx = midPt[0] + cos(angle+90) * self.intensity*noise
        yy = midPt[1] + sin(angle+90) * self.intensity*noise

        self.otherPen.lineTo((xx, yy))
        self.lastPt = pt

    def _curveToOne(self, pt1, pt2, pt3):
        raise NotImplementedError

    def _closePath(self):
        self.lineTo(self.firstPt)
        self.otherPen.closePath()
        self.lastPt = None

    def _endPath(self):
        self.otherPen.endPath()
        self.lastPt = None


def perlinGlyph(aGlyph, step, intensity, factory, fixedParameters=None):
    """
    Convenience function that applies the **PerlinPen** pen to a glyph in place.
    """
    if len(aGlyph) == 0:
        return aGlyph

    flattenGlyph(aGlyph, step)
    recorder = RecordingPen()
    filterpen = PerlinPen(recorder, intensity, factory, fixedParameters)
    aGlyph.draw(filterpen)
    aGlyph.clear()
    recorder.replay(aGlyph.getPen())
    return aGlyph


# =========
# = tests =
# =========
