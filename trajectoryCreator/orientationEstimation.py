import numpy as np
import math


class OrientationEstimator:

    def __init__(self):
        return

    def estimate_orientations_for_track(self, positions):
        k = list(positions.keys())

        rads = []

        if len(k) > 1:
            p = np.array(list(positions.values()))
            p = p.reshape((len(p), -1))
            while p.shape[1] > 2:
                p = np.delete(p, 2, axis=1)
            grads = np.gradient(p, axis=0)
            norms = np.linalg.norm(grads, axis=1)
            prev = None
            to_change = []
            for i, n in enumerate(norms):
                if n == 0:
                    if prev:
                        norms[i] = norms[prev]
                        grads[i] = grads[prev]
                    else:
                        to_change.append(i)
                else:
                    prev = i
                    if to_change:
                        for j in to_change:
                            norms[j] = norms[i]
                            grads[j] = grads[i]
            div = np.array([[1, 1] if n.item() == 0 else [n.item(), n.item()] for n in norms.flatten()])
            grads = np.divide(grads, div)

            rads = np.arccos(np.dot(grads, [0, 1]))

        orientations = {}
        for i, rad in enumerate(rads):
            orientations[k[i]] = rad / math.pi * 180 * -np.sign(grads[i][0])

        return orientations

