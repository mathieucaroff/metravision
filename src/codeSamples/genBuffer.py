def genFilledRegion(self, fillerColor = None):
    shape = self.frame.shape
    shape[0:2] = [self.targetHeight, self.targetWidth]
    dtype = self.frame.dtype
    if fillerColor not is None:
        return np.full(shape = shape, dtype = dtype, fill_value = fillerColor)
    else fillerColor is None:
        return np.zeroes(shape = shape, dtype = dtype)