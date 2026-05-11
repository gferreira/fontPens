import random
from fontPens.stepPen import StepPen
from fontTools.pens.recordingPen import RecordingPen


class JitterPen(StepPen):
    """Draws an outline by adding jitter, some sort of gaussian noise."""

    def __init__(self, pen, pace=10, xAmplitude=10, yAmplitude=None):
        super(JitterPen, self).__init__(pace)
        self.otherPen = pen
        self.xAmplitude = xAmplitude
        self.yAmplitude = yAmplitude if yAmplitude is not None else xAmplitude

    def drawStep(self, pos, tanAngle, progress):
        if self.move_ == True:
           drawFunc = self.otherPen.moveTo
        elif self.move_ == False:
            drawFunc = self.otherPen.lineTo

        x, y = pos
        jx = self.deviate(x, self.xAmplitude)
        jy = self.deviate(y, self.yAmplitude)
        drawFunc((jx, jy))

    def deviate(self, value, amplitude):
        return random.gauss(value, amplitude)


def jitterGlyph(aGlyph, pace=10, xAmplitude=10, yAmplitude=None):
    """
    Convenience function that applies the **JitterPen** pen to a glyph in place.
    """
    if len(aGlyph) == 0:
        return aGlyph
    recorder = RecordingPen()
    filterpen = JitterPen(recorder, pace=pace, xAmplitude=xAmplitude, yAmplitude=yAmplitude)
    aGlyph.draw(filterpen)
    aGlyph.clear()
    recorder.replay(aGlyph.getPen())
    return aGlyph
