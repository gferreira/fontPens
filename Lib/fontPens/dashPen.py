from importlib import reload
import fontPens.penTools
reload(fontPens.penTools)

from math import pi, radians #, cos #, sin, atan2, atan, hypot
from fontPens.stepPen import StepPen
from fontPens.penTools import satellize
from fontTools.pens.recordingPen import RecordingPen


class DashPen(StepPen):
    """Draws lines at each step. If *normal* is set to False, the lines are perpendicular to the outline direction, else, tangent."""

    def __init__(self, pen, pace=20, length=10, angle=None, normal=False, embroidered=False):
        super(DashPen, self).__init__(pace)
        self.otherPen = pen
        self.length = length
        self.normal = normal
        self.embroidered = embroidered
        self.angle = radians(angle) if angle is not None else None

    def drawStep(self, pos, tanAngle, progress):
        x, y = pos
        if self.normal == True and self.angle is None:
            angle = tanAngle + (pi/2)
        elif self.normal == False and self.angle is None:
            angle = tanAngle
        elif self.angle is not None:
            angle = self.angle
        pt1, pt2 = satellize((x, y), angle, self.length)
        if self.embroidered == False or (self.embroidered == True and self.otherPen.contour is None):
            self.otherPen.moveTo(pt1)
        else:
            self.otherPen.lineTo(pt1)
        self.otherPen.lineTo(pt2)
        if self.embroidered == False:
            self.otherPen.endPath()

    def closePath(self):
        if len(self._currentContour):
            self._lineTo(self._currentContour[0])
        self.previousPoint = None
        self._currentContour = []


def dashGlyph(aGlyph, pace=20, length=10, angle=None, normal=False, embroidered=False):
    """
    Convenience function that applies the **DashPen** pen to a glyph in place.
    """
    if len(aGlyph) == 0:
        return aGlyph
    recorder = RecordingPen()
    filterpen = DashPen(recorder, pace=pace, length=length, angle=angle, normal=normal, embroidered=embroidered)
    aGlyph.draw(filterpen)
    aGlyph.clear()
    recorder.replay(aGlyph.getPen())
    return aGlyph


