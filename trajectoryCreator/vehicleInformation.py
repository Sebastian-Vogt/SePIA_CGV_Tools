import json
import os


def getCarData():
    dimensions = [1.815, 4.28, 1.488]
    wheelBase = None
    trackWidth = None
    weight = 1390
    cogX = None
    cogY = None
    cogZ = None
    frontAxLex = None
    ixx = None
    iyy = None
    izz = None
    dataDict = {"dimensions": dimensions}
    if wheelBase:
        dataDict["wheelBase"] = wheelBase
    if trackWidth:
        dataDict["trackWidth"] = trackWidth
    if weight:
        dataDict["weight"] = weight
    if cogX:
        dataDict["cogX"] = cogX
    if cogY:
        dataDict["cogY"] = cogY
    if cogZ:
        dataDict["cogZ"] = cogZ
    if frontAxLex:
        dataDict["frontAxLex"] = frontAxLex
    if ixx:
        dataDict["ixx"] = ixx
    if iyy:
        dataDict["iyy"] = iyy
    if izz:
        dataDict["izz"] = izz
    return dataDict


def getPedestrianData():
    dimensions = [0.5, 0.4, 1.8]
    wheelBase = None
    trackWidth = None
    weight = 75
    cogX = None
    cogY = None
    cogZ = None
    frontAxLex = None
    ixx = None
    iyy = None
    izz = None
    dataDict = {"dimensions": dimensions}
    if wheelBase:
        dataDict["wheelBase"] = wheelBase
    if trackWidth:
        dataDict["trackWidth"] = trackWidth
    if weight:
        dataDict["weight"] = weight
    if cogX:
        dataDict["cogX"] = cogX
    if cogY:
        dataDict["cogY"] = cogY
    if cogZ:
        dataDict["cogZ"] = cogZ
    if frontAxLex:
        dataDict["frontAxLex"] = frontAxLex
    if ixx:
        dataDict["ixx"] = ixx
    if iyy:
        dataDict["iyy"] = iyy
    if izz:
        dataDict["izz"] = izz
    return dataDict


def getMotorbikeData():
    dimensions = [0.81, 2.075, 1.1]
    wheelBase = None
    trackWidth = None
    weight = 164
    cogX = None
    cogY = None
    cogZ = None
    frontAxLex = None
    ixx = None
    iyy = None
    izz = None
    dataDict = {"dimensions": dimensions}
    if wheelBase:
        dataDict["wheelBase"] = wheelBase
    if trackWidth:
        dataDict["trackWidth"] = trackWidth
    if weight:
        dataDict["weight"] = weight
    if cogX:
        dataDict["cogX"] = cogX
    if cogY:
        dataDict["cogY"] = cogY
    if cogZ:
        dataDict["cogZ"] = cogZ
    if frontAxLex:
        dataDict["frontAxLex"] = frontAxLex
    if ixx:
        dataDict["ixx"] = ixx
    if iyy:
        dataDict["iyy"] = iyy
    if izz:
        dataDict["izz"] = izz
    return dataDict


def getBicycleData():
    dimensions = [0.5, 1.6, 1.5]
    wheelBase = None
    trackWidth = None
    weight = 80
    cogX = None
    cogY = None
    cogZ = None
    frontAxLex = None
    ixx = None
    iyy = None
    izz = None
    dataDict = {"dimensions": dimensions}
    if wheelBase:
        dataDict["wheelBase"] = wheelBase
    if trackWidth:
        dataDict["trackWidth"] = trackWidth
    if weight:
        dataDict["weight"] = weight
    if cogX:
        dataDict["cogX"] = cogX
    if cogY:
        dataDict["cogY"] = cogY
    if cogZ:
        dataDict["cogZ"] = cogZ
    if frontAxLex:
        dataDict["frontAxLex"] = frontAxLex
    if ixx:
        dataDict["ixx"] = ixx
    if iyy:
        dataDict["iyy"] = iyy
    if izz:
        dataDict["izz"] = izz
    return dataDict


def getTruckData():
    dimensions = [2.55, 9.15, 3.8]
    wheelBase = None
    trackWidth = None
    weight = 6810
    cogX = None
    cogY = None
    cogZ = None
    frontAxLex = None
    ixx = None
    iyy = None
    izz = None
    dataDict = {"dimensions": dimensions}
    if wheelBase:
        dataDict["wheelBase"] = wheelBase
    if trackWidth:
        dataDict["trackWidth"] = trackWidth
    if weight:
        dataDict["weight"] = weight
    if cogX:
        dataDict["cogX"] = cogX
    if cogY:
        dataDict["cogY"] = cogY
    if cogZ:
        dataDict["cogZ"] = cogZ
    if frontAxLex:
        dataDict["frontAxLex"] = frontAxLex
    if ixx:
        dataDict["ixx"] = ixx
    if iyy:
        dataDict["iyy"] = iyy
    if izz:
        dataDict["izz"] = izz
    return dataDict


def getBusData():
    dimensions = [2.55, 12.01, 3.197]
    wheelBase = None
    trackWidth = None
    weight = 11545
    cogX = None
    cogY = None
    cogZ = None
    frontAxLex = None
    ixx = None
    iyy = None
    izz = None
    dataDict = {"dimensions": dimensions}
    if wheelBase:
        dataDict["wheelBase"] = wheelBase
    if trackWidth:
        dataDict["trackWidth"] = trackWidth
    if weight:
        dataDict["weight"] = weight
    if cogX:
        dataDict["cogX"] = cogX
    if cogY:
        dataDict["cogY"] = cogY
    if cogZ:
        dataDict["cogZ"] = cogZ
    if frontAxLex:
        dataDict["frontAxLex"] = frontAxLex
    if ixx:
        dataDict["ixx"] = ixx
    if iyy:
        dataDict["iyy"] = iyy
    if izz:
        dataDict["izz"] = izz
    return dataDict


def getTramData():
    dimensions = [2.3, 30, 3.5]
    wheelBase = None
    trackWidth = None
    weight = 39000
    cogX = None
    cogY = None
    cogZ = None
    frontAxLex = None
    ixx = None
    iyy = None
    izz = None
    dataDict = {"dimensions": dimensions}
    if wheelBase:
        dataDict["wheelBase"] = wheelBase
    if trackWidth:
        dataDict["trackWidth"] = trackWidth
    if weight:
        dataDict["weight"] = weight
    if cogX:
        dataDict["cogX"] = cogX
    if cogY:
        dataDict["cogY"] = cogY
    if cogZ:
        dataDict["cogZ"] = cogZ
    if frontAxLex:
        dataDict["frontAxLex"] = frontAxLex
    if ixx:
        dataDict["ixx"] = ixx
    if iyy:
        dataDict["iyy"] = iyy
    if izz:
        dataDict["izz"] = izz
    return dataDict


def getTrailerData():
    dimensions = [2.5, 16.499, 3.2]
    wheelBase = None
    trackWidth = None
    weight = 18000
    cogX = None
    cogY = None
    cogZ = None
    frontAxLex = None
    ixx = None
    iyy = None
    izz = None
    dataDict = {"dimensions": dimensions}
    if wheelBase:
        dataDict["wheelBase"] = wheelBase
    if trackWidth:
        dataDict["trackWidth"] = trackWidth
    if weight:
        dataDict["weight"] = weight
    if cogX:
        dataDict["cogX"] = cogX
    if cogY:
        dataDict["cogY"] = cogY
    if cogZ:
        dataDict["cogZ"] = cogZ
    if frontAxLex:
        dataDict["frontAxLex"] = frontAxLex
    if ixx:
        dataDict["ixx"] = ixx
    if iyy:
        dataDict["iyy"] = iyy
    if izz:
        dataDict["izz"] = izz
    return dataDict


def getCamperData():
    dimensions = [2.3, 6.6, 2.9]
    wheelBase = None
    trackWidth = None
    weight = 3500
    cogX = None
    cogY = None
    cogZ = None
    frontAxLex = None
    ixx = None
    iyy = None
    izz = None
    dataDict = {"dimensions": dimensions}
    if wheelBase:
        dataDict["wheelBase"] = wheelBase
    if trackWidth:
        dataDict["trackWidth"] = trackWidth
    if weight:
        dataDict["weight"] = weight
    if cogX:
        dataDict["cogX"] = cogX
    if cogY:
        dataDict["cogY"] = cogY
    if cogZ:
        dataDict["cogZ"] = cogZ
    if frontAxLex:
        dataDict["frontAxLex"] = frontAxLex
    if ixx:
        dataDict["ixx"] = ixx
    if iyy:
        dataDict["iyy"] = iyy
    if izz:
        dataDict["izz"] = izz
    return dataDict


def getAgriculturalVehicleData():
    dimensions = [2.55, 5.19, 3.25]
    wheelBase = None
    trackWidth = None
    weight = 15000
    cogX = None
    cogY = None
    cogZ = None
    frontAxLex = None
    ixx = None
    iyy = None
    izz = None
    dataDict = {"dimensions": dimensions}
    if wheelBase:
        dataDict["wheelBase"] = wheelBase
    if trackWidth:
        dataDict["trackWidth"] = trackWidth
    if weight:
        dataDict["weight"] = weight
    if cogX:
        dataDict["cogX"] = cogX
    if cogY:
        dataDict["cogY"] = cogY
    if cogZ:
        dataDict["cogZ"] = cogZ
    if frontAxLex:
        dataDict["frontAxLex"] = frontAxLex
    if ixx:
        dataDict["ixx"] = ixx
    if iyy:
        dataDict["iyy"] = iyy
    if izz:
        dataDict["izz"] = izz
    return dataDict


def getConstructionVehicleData():
    dimensions = [3.2, 7, 11]
    wheelBase = None
    trackWidth = None
    weight = 43000
    cogX = None
    cogY = None
    cogZ = None
    frontAxLex = None
    ixx = None
    iyy = None
    izz = None
    dataDict = {"dimensions": dimensions}
    if wheelBase:
        dataDict["wheelBase"] = wheelBase
    if trackWidth:
        dataDict["trackWidth"] = trackWidth
    if weight:
        dataDict["weight"] = weight
    if cogX:
        dataDict["cogX"] = cogX
    if cogY:
        dataDict["cogY"] = cogY
    if cogZ:
        dataDict["cogZ"] = cogZ
    if frontAxLex:
        dataDict["frontAxLex"] = frontAxLex
    if ixx:
        dataDict["ixx"] = ixx
    if iyy:
        dataDict["iyy"] = iyy
    if izz:
        dataDict["izz"] = izz
    return dataDict


def getEmergencyVehicleData():
    dimensions = [2.2, 6.6, 2.9]
    wheelBase = None
    trackWidth = None
    weight = 5000
    cogX = None
    cogY = None
    cogZ = None
    frontAxLex = None
    ixx = None
    iyy = None
    izz = None
    dataDict = {"dimensions": dimensions}
    if wheelBase:
        dataDict["wheelBase"] = wheelBase
    if trackWidth:
        dataDict["trackWidth"] = trackWidth
    if weight:
        dataDict["weight"] = weight
    if cogX:
        dataDict["cogX"] = cogX
    if cogY:
        dataDict["cogY"] = cogY
    if cogZ:
        dataDict["cogZ"] = cogZ
    if frontAxLex:
        dataDict["frontAxLex"] = frontAxLex
    if ixx:
        dataDict["ixx"] = ixx
    if iyy:
        dataDict["iyy"] = iyy
    if izz:
        dataDict["izz"] = izz
    return dataDict


def getLargeAnimalData():
    dimensions = [1, 3.5, 2.2]
    wheelBase = None
    trackWidth = None
    weight = 300
    cogX = None
    cogY = None
    cogZ = None
    frontAxLex = None
    ixx = None
    iyy = None
    izz = None
    dataDict = {"dimensions": dimensions}
    if wheelBase:
        dataDict["wheelBase"] = wheelBase
    if trackWidth:
        dataDict["trackWidth"] = trackWidth
    if weight:
        dataDict["weight"] = weight
    if cogX:
        dataDict["cogX"] = cogX
    if cogY:
        dataDict["cogY"] = cogY
    if cogZ:
        dataDict["cogZ"] = cogZ
    if frontAxLex:
        dataDict["frontAxLex"] = frontAxLex
    if ixx:
        dataDict["ixx"] = ixx
    if iyy:
        dataDict["iyy"] = iyy
    if izz:
        dataDict["izz"] = izz
    return dataDict


def getSmallAnimalData():
    dimensions = [0.4, 1.0, 0.7]
    wheelBase = None
    trackWidth = None
    weight = 10
    cogX = None
    cogY = None
    cogZ = None
    frontAxLex = None
    ixx = None
    iyy = None
    izz = None
    dataDict = {"dimensions": dimensions}
    if wheelBase:
        dataDict["wheelBase"] = wheelBase
    if trackWidth:
        dataDict["trackWidth"] = trackWidth
    if weight:
        dataDict["weight"] = weight
    if cogX:
        dataDict["cogX"] = cogX
    if cogY:
        dataDict["cogY"] = cogY
    if cogZ:
        dataDict["cogZ"] = cogZ
    if frontAxLex:
        dataDict["frontAxLex"] = frontAxLex
    if ixx:
        dataDict["ixx"] = ixx
    if iyy:
        dataDict["iyy"] = iyy
    if izz:
        dataDict["izz"] = izz
    return dataDict


'''
Class that loads all vehicle information
'''
class VehicleInformationManager:

    def __init__(self, mappingPath, carInformationPath):
        # loads mapping file (fz nr <-> car type) once
        if os.path.isfile(mappingPath):
            with open(mappingPath) as json_file:
                self.mapping = json.load(json_file)
        else:
            raise OSError(2, 'No such file or directory', mappingPath)

        # loads car information file (containing calibration data etc for all cars) once
        if os.path.isfile(carInformationPath):
            with open(carInformationPath) as json_file:
                self.carInformation = json.load(json_file)
        else:
            raise OSError(2, 'No such file or directory', carInformationPath)


    '''
    Extracts the corresponding car type to a given folder path and returns the corresponding car information
    '''
    def getVehicleInformationForFolder(self, path):

        car = None
        for carType, vehicleNumbers in self.mapping.items():
            if any(vehicleNumber in path.replace("FZ_", "FZ") for vehicleNumber in vehicleNumbers):
                car = carType
                break
            else:
                car = "noData"

        if not car:
            raise KeyError("Vehicle code is not contained in the folder name.")

        if car == "noData":
            car = "mercedes"

        for carInfo in self.carInformation:
            if carInfo["id"] == car:
                return carInfo

        raise KeyError("Extracted car type does not match any car type information is available for.")