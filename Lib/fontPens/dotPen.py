from fontPens.stepPen import StepPen
from fontTools.pens.recordingPen import RecordingPen


def circle(pen, pos, radius, roundness=0.55):
    cx, cy = pos
    r = radius
    pen.moveTo((cx+r, cy))
    pen.curveTo((cx+r, cy+(r*roundness)), (cx+(r*roundness), cy+r), (cx, cy+r))
    pen.curveTo((cx-(r*roundness), cy+r), (cx-r, cy+(r*roundness)), (cx-r, cy))
    pen.curveTo((cx-r, cy-(r*roundness)), (cx-(r*roundness), cy-r), (cx, cy-r))
    pen.curveTo((cx+(r*roundness), cy-r), (cx+r, cy-(r*roundness)), (cx+r, cy))
    pen.closePath()


class DotPen(StepPen):
    """Draws a circle at each step with given radius."""

    isPaced = True

    def __init__(self, pen, pace=20, radius=10):
        super(DotPen, self).__init__(pace)
        self.otherPen = pen
        self.radius = radius

    def drawStep(self, pos, tanAngle, progress):
        r = self.radius
        circle(self.otherPen, pos, r)

    def closePath(self):
        if len(self._currentContour):
            self._lineTo(self._currentContour[0])
        self.previousPoint = None
        self._currentContour = []


def dotGlyph(aGlyph, pace=20, radius=10):
    """
    Convenience function that applies the **DotPen** pen to a glyph in place.
    """
    if len(aGlyph) == 0:
        return aGlyph
    recorder = RecordingPen()
    filterpen = DotPen(recorder, pace=pace, radius=radius)
    aGlyph.draw(filterpen)
    aGlyph.clear()
    recorder.replay(aGlyph.getPen())
    return aGlyph

