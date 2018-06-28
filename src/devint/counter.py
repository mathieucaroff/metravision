"""
Code ajoutant les compteurs à la collection d'images.
"""


import cv2
import numpy as np


def genFilledRegion(height=520, width=720, channelCount=None, dtype=np.uint8, fill_value=0):
    shape = [height, width]
    if channelCount is not None:
        shape.append(channelCount)
    return np.full(shape=shape, dtype=dtype, fill_value=fill_value)


def addCounters(im, segmenter):
    counting = genFilledRegion(height=200, width=300, fill_value=255)
    segmentIndex = segmenter.segmentIndex
    pairs = [("Segment", segmentIndex)]

    cs = segmenter.currentSegment
    if cs is not None:
        pairs.extend(sorted(cs.items()))
    for i, (name, count) in enumerate(pairs):
        text = f"{name}: {count}"
        cv2.putText(
            img=counting,
            text=text,
            org=(12, 45 + 40 * i),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=0,
            thickness=2
        )
    im["counting"] = counting