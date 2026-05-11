from fontTools.misc.bezierTools import calcCubicArcLength, splitCubicAtT
from fontTools.pens.basePen import BasePen
from fontPens.penTools import distance, interpolatePoint


class SplitPen(BasePen):
    
    def __init__(self, otherPen, approximateSegmentLength=5):
        self.approximateSegmentLength = approximateSegmentLength
        super().__init__({})
        self.otherPen = otherPen
    
    def _moveTo(self, pt):
        self.otherPen.moveTo(pt)
        self.currentPt = pt
        self.firstPt = pt
    
    def _lineTo(self, pt):
        d = distance(self.currentPt, pt)
        maxSteps = int(round(d / self.approximateSegmentLength))
        if maxSteps < 1:
            self.otherPen.lineTo(pt)
            self.currentPt = pt
            return
        step = 1.0 / maxSteps
        for factor in range(1, maxSteps + 1):
            self.otherPen.lineTo(interpolatePoint(self.currentPt, pt, factor * step))
        self.currentPt = pt
        
    def _curveToOne(self, pt1, pt2, pt3):
        falseCurve = (pt1 == self.currentPt) and (pt2 == pt3)
        if falseCurve:
            self._lineTo(pt3)
            return
        
        maxSteps = int(round(calcCubicArcLength(self.currentPt, pt1, pt2, pt3) / self.approximateSegmentLength))
        if maxSteps < 1:
            self.otherPen.lineTo(pt3)
            self.currentPt = pt3
            return
        
        tValues = [i / maxSteps for i in range(1, maxSteps)]
        for curve in splitCubicAtT(self.currentPt, pt1, pt2, pt3, *tValues):
            self.otherPen.curveTo(*curve[1:])

        self.currentPt = pt3
    
    def _closePath(self):
        self.lineTo(self.firstPt)
        self.otherPen.closePath()

    def _endPath(self):
        self.otherPen.endPath()

    def addComponent(self, glyphName, transformation):
        self.otherPen.addComponent(glyphName, transformation) 


def splitGlyph(aGlyph, approximateSegmentLength=5):
    from fontTools.pens.recordingPen import RecordingPen
    recorder = RecordingPen()
    splitPen = SplitPen(recorder, approximateSegmentLength=approximateSegmentLength)
    aGlyph.draw(splitPen)
    aGlyph.clear()
    recorder.replay(aGlyph.getPen())
    return aGlyph
