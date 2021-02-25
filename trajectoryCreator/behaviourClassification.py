import globals
import math
import numpy as np
from scipy.ndimage import gaussian_filter1d
import utils


def getDictValuesInRange(starting_frame, end_frame, dictToCheck):
    values = []
    for frame, value in dictToCheck.items():
        if starting_frame <= frame <= end_frame:
            values.append(value)
    return values


def smoothLabel(dictToSmooth, kernelRadius=5):
    for frame, value in dictToSmooth.items():
        kernelValues = getDictValuesInRange(frame - kernelRadius, frame + kernelRadius, dictToSmooth)
        most = max(set(kernelValues), key=kernelValues.count)
        dictToSmooth[frame] = most


def calculateOpponentApproach(objectPositions, egoPositions, objectRotations, egoRotations, geoHandler):

    combinedDictList = list(utils.zipDicts(objectPositions, egoPositions, objectRotations, egoRotations))

    approachDict = {}
    for frame, objectPosition, egoPosition, objectRotation, egoRotation in combinedDictList:
        objectRotation = (objectRotation + 360) % 360
        egoRotation = (egoRotation + 360) % 360
        relative_direction = (objectRotation - egoRotation)

        if -45 < relative_direction <= 45:
            approachDict[frame] = 'Front'

            normal = [math.sin(egoRotation-90), math.cos(egoRotation-90)]
            x0, y0 = geoHandler.lat_long_to_meter(objectPosition[0], objectPosition[1])
            x1, y1 = geoHandler.lat_long_to_meter(egoPosition[0], egoPosition[1])
            dist = abs(normal[0] * (x1-x0) + normal[1] * (y1-y0)) / math.sqrt(normal[0] ** 2 + normal[1] ** 2)
            if dist >= 3:
                approachDict[frame] = 'LateralSameDirection'

        elif -135 < relative_direction <= -45:
            approachDict[frame] = 'CrossLeft'  # from left to right
        elif 45 < relative_direction <= 135:
            approachDict[frame] = 'CrossRight'
        else:
            approachDict[frame] = 'Oncoming'

    smoothLabel(approachDict)
    return approachDict


def calculateSpecification(objectPositions, geoHandler, standing_kernel_radius=5, standing_radius=.5, curvature_threshold=0.04, curvature_kernel_radius=5, isEgo=False):

    if len(objectPositions.items()) < 2:
        specificationDict = {frame: 'StandStill' for frame, pos in objectPositions.items()}
        if isEgo:
            egoManeuverTypeDict = specificationDict
        else:
            egoManeuverTypeDict = None
        return specificationDict, egoManeuverTypeDict

    xs = np.array([p[0] for p in objectPositions.values()])
    ys = np.array([p[1] for p in objectPositions.values()])
    xs = gaussian_filter1d(xs, curvature_kernel_radius)
    ys = gaussian_filter1d(ys, curvature_kernel_radius)

    xs1 = np.gradient(xs)
    xs1 = gaussian_filter1d(xs1, curvature_kernel_radius)
    xs2 = np.gradient(xs1)
    xs2 = gaussian_filter1d(xs2, curvature_kernel_radius)
    ys1 = np.gradient(ys)
    ys1 = gaussian_filter1d(ys1, curvature_kernel_radius)
    ys2 = np.gradient(ys1)
    ys2 = gaussian_filter1d(ys2, curvature_kernel_radius)
    curvatures = (xs1 * ys2 - ys1 * xs2) / (.001+np.power(xs1 ** 2 + ys1 ** 2, 1.5))

    specificationDict = {}
    egoManeuverTypeDict = {}
    for i in range(len(list(objectPositions.values()))):
        frame = list(objectPositions.items())[i][0]
        kernelValues = getDictValuesInRange(frame - standing_kernel_radius, frame + standing_kernel_radius, objectPositions)

        xs = []
        ys = []
        for position in kernelValues:
            xs.append(position[0])
            ys.append(position[1])
        center_x = sum(xs) / len(xs)
        center_y = sum(ys) / len(ys)
        filtered_list = list(
            filter(lambda e: math.sqrt(pow(e[0] - center_x, 2) + pow(e[1] - center_y, 2)) > standing_radius,
                   zip(xs, ys)))

        if len(filtered_list) == 0:
            specificationDict[frame] = 'StandStill'
            if isEgo:
                egoManeuverTypeDict[frame] = 'StandStill'
        else:
            if abs(curvatures[i]) < curvature_threshold:
                specificationDict[frame] = 'Forward'
                if isEgo:
                    egoManeuverTypeDict[frame] = 'FollowRoad'
            else:
                if np.sign(curvatures[i]) < 0:
                    specificationDict[frame] = 'ForwardRight'
                else:
                    specificationDict[frame] = 'ForwardLeft'
                if isEgo:
                    egoManeuverTypeDict[frame] = 'DriveThroughCurve'

    if isEgo:
        smoothLabel(egoManeuverTypeDict)
    smoothLabel(specificationDict)
    return specificationDict, egoManeuverTypeDict