import numpy as np

def genFilledRegion(self, fillerColor=None):
    shape = self.frame.shape
    shape[0:2] = [self.targetHeight, self.targetWidth]
    dtype = self.frame.dtype
    if fillerColor is not None:
        return np.full(shape=shape, dtype=dtype, fill_value=fillerColor)
    else:
        return np.zeros(shape=shape, dtype=dtype)