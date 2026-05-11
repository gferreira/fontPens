<!-- |Build Status| |Coverage| |PyPI| |Versions| -->

fontPens
========

A collection of classes implementing the pen protocol for manipulating glyphs.

<!--

.. |Build Status| image:: https://travis-ci.org/robotools/fontPens.svg?branch=master
   :target: https://travis-ci.org/robotools/fontPens
.. |PyPI| image:: https://img.shields.io/pypi/v/fontPens.svg
   :target: https://pypi.org/project/fontPens
.. |Versions| image:: https://img.shields.io/badge/python-2.7%2C%203.7-blue.svg
   :alt: Python Versions
.. |Coverage| image:: https://codecov.io/gh/robotools/fontPens/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/robotools/fontPens

-->


PrintPen
--------

```python
from fontPens.printPen import PrintPen

g = CurrentGlyph()
pen = PrintPen()
g.draw(pen)
```


DigestPointPen
--------------

```python
from fontPens.digestPointPen import DigestPointPen

font = CurrentFont()

glyph = font['O']
pen = DigestPointPen()
glyph.drawPoints(pen)

print(pen.getDigest())
print(pen.getDigestPointsOnly())
```


DigestPointStructurePen
-----------------------

```python
from fontPens.digestPointPen import DigestPointStructurePen

font = CurrentFont()

glyph1 = font['O']
pen1 = DigestPointStructurePen()
glyph1.drawPoints(pen1)

glyph2 = font['o']
pen2 = DigestPointStructurePen()
glyph2.drawPoints(pen2)

print(pen1.getDigest() == pen2.getDigest())
```


FlattenPen
----------

```python
from fontPens.flattenPen import flattenGlyph

g = CurrentGlyph()
g.prepareUndo('flatten glyph')
flattenGlyph(g, threshold=20, segmentLines=True)
g.performUndo()
```


SamplingPen
-----------

```python
from fontPens.flattenPen import samplingGlyph

g = CurrentGlyph()
g.prepareUndo('sample glyph')
samplingGlyph(g, steps=10)
g.performUndo()
```


SplitPen
--------

```python
from fontPens.splitPen import splitGlyph

g = CurrentGlyph()
g.prepareUndo('split glyph')
splitGlyph(g, approximateSegmentLength=10)
g.performUndo()
```


SpikePen
--------

```python
from fontPens.spikePen import spikeGlyph

g = CurrentGlyph()
g.prepareUndo('spike glyph')
spikeGlyph(g, segmentLength=20, spikeLength=45)
g.performUndo()
```


JitterPen
---------

```python
from fontPens.jitterPen import jitterGlyph

g = CurrentGlyph()
g.prepareUndo('jitter glyph')
jitterGlyph(g, pace=20, xAmplitude=10, yAmplitude=None)
g.performUndo()
```


DotPen
------

```python
from fontPens.dotPen import dotGlyph

g = CurrentGlyph()
g.prepareUndo('dot glyph')
dotGlyph(g, pace=20, radius=5)
g.performUndo()
```


DashPen
-------

```python
from fontPens.dashPen import dashGlyph

g = CurrentGlyph()
g.prepareUndo('dash glyph')
dashGlyph(g, pace=10, length=20, angle=None, normal=True, embroidered=False)
g.performUndo()
```


PerlinPen
----------

```python
from fontPens.perlin import PerlinNoiseFactory
from fontPens.perlinPen import perlinGlyph

pace = 10
intensity = 10
resolution = 120

factory = PerlinNoiseFactory(2, octaves=4, tile=(1000/resolution, 1000/resolution))

g = CurrentGlyph()
g.prepareUndo('perlin glyph')
perlinGlyph(g, pace, intensity, factory)
g.performUndo()
```


TranslationPen
--------------

```python
from fontPens.translationPen import translationGlyph

g = CurrentGlyph()
g.prepareUndo('translation pen')
translationGlyph(g, frontAngle=35, frontWidth=30)
g.performUndo()
```


OutlinePen
----------

```python
from fontPens.outlinePen import outlineGlyph

g = CurrentGlyph()
g.prepareUndo('dash glyph')
outlineGlyph(g, offset=10, contrast=0, contrastAngle=0, connection="round", cap="round", miterLimit=None, closeOpenPaths=True, optimizeCurve=False, preserveComponents=False, filterDoubles=True, drawOriginal=False, drawInner=True, drawOuter=True)
g.performUndo()
```
