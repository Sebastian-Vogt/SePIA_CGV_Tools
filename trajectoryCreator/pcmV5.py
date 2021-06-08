import os
import msaccessdb
import pyodbc
import numpy as np
import math
import vehicleInformation
import csv

class PCMExporter:

    def __init__(self, dbPath, caseid):
        self.csv_flag = False
        self.caseid = caseid
        dbPath = dbPath + "\\" + caseid + ".mdb"
        msaccessdb.create(dbPath)
        self.constr = "DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={0};".format(dbPath)
        try:
            dbconn = pyodbc.connect(self.constr)
        except pyodbc.InterfaceError:
            self.csv_flag = True
            os.remove(dbPath)
            self.constr = dbPath

    def derivative(self, array, method='central'):
        if method == 'central':
            return np.gradient(array)
        elif method == 'forward':
            return np.array([array[i + (1 if i < len(array) - 1 else 0)] - array[i] for i in range(len(array))])
        elif method == 'backward':
            return np.array([array[i] - array[i - (1 if i > 0 else 0)] for i in range(len(array))])
        else:
            raise ValueError("Method must be 'central', 'forward' or 'backward'.")


    def mapObjectTypeIndex(self, detType):
        if detType == 0:
            return 88888
        if detType == 1:
            return 0
        if detType == 2:
            return 4
        if detType == 3:
            return 5
        if detType == 4:
            return 3
        if detType == 5:
            return 2
        if detType == 6:
            return 7
        if detType == 7:
            return 6
        if detType == 8:
            return 6
        if detType == 9:
            return 8
        if detType == 10:
            return 9
        if detType == 11:
            return 10
        if detType == 12:
            return 11
        if detType == 13:
            return 88888
        if detType == 14:
            return 1
        if detType == 15:
            return 12
        if detType == 16:
            return 13
        return 88888

    def extrackObjectAttributes(self, objType):
        if objType == 0:
            dataDict = vehicleInformation.getCarData()
        elif objType == 1:
            dataDict = vehicleInformation.getPedestrianData()
        elif objType == 2:
            dataDict = vehicleInformation.getMotorbikeData()
        elif objType == 3:
            dataDict = vehicleInformation.getBicycleData()
        elif objType == 4:
            dataDict = vehicleInformation.getTruckData()
        elif objType == 5:
            dataDict = vehicleInformation.getBusData()
        elif objType == 6:
            dataDict = vehicleInformation.getTramData()
        elif objType == 7:
            dataDict = vehicleInformation.getTrailerData()
        elif objType == 8:
            dataDict = vehicleInformation.getCamperData()
        elif objType == 9:
            dataDict = vehicleInformation.getAgriculturalVehicleData()
        elif objType == 10:
            dataDict = vehicleInformation.getConstructionVehicleData()
        elif objType == 11:
            dataDict = vehicleInformation.getEmergencyVehicleData()
        elif objType == 12:
            dataDict = vehicleInformation.getLargeAnimalData()
        elif objType == 13:
            dataDict = vehicleInformation.getSmallAnimalData()
        else:
            dataDict = {
                "dimensions": [None, None, None],
                "wheelBase": None,
                "trackWidth": None,
                "wheight": None,
                "cogX": None,
                "cogY": None,
                "cogZ": None,
                "frontAxLex": None,
                "ixx": None,
                "iyy": None,
                "izz": None
            }
        return dataDict


    def mapSpecification(self, specification_string):
        if "StandStill" in specification_string:
            return 0
        if "Forward" in specification_string:
            return 1
        if "ForwardRight" in specification_string:
            return 2
        if "ForwardLeft" in specification_string:
            return 3
        else:
            return 99999


    def mapManeuverType(self, specification_string):
        if "StandStill" in specification_string:
            return 0
        if "FollowRoad" in specification_string:
            return 1
        if "DriveThroughCurve" in specification_string:
            return 2
        else:
            return 99999


    def mapApproach(self, specification_string):
        if "Front" in specification_string:
            return 0
        if "LateralSameDirection" in specification_string:
            return 1
        if "CrossLeft" in specification_string:
            return 2
        if "CrossRight" in specification_string:
            return 3
        if "Oncoming" in specification_string:
            return 4
        else:
            return 99999

    def writeGlobalTable(self, startTime, egoStartPos, numberOfTrobs):
        if not self.csv_flag:
            dbconn = pyodbc.connect(self.constr)
            cursor = dbconn.cursor()
            cursor.execute("""CREATE TABLE global_data (
                                             CASEID varchar(255),
                                             'DATETIME' varchar(255),
                                             PARTICIP int,
                                             SOLVER int,
                                             GPSLAT double,
                                             GPSLON double,
                                             GPSELE double
                                             );""")
            dbconn.commit()

            cursor.execute("""INSERT INTO global_data (CASEID, 'DATETIME', PARTICIP, SOLVER, GPSLAT, GPSLON, GPSELE)
                                     VALUES('""" + str(self.caseid) + """', '""" + str(startTime) + """',  """ + str(numberOfTrobs) + """, 99999, """ + str(egoStartPos[0]) + """, """ + str(egoStartPos[1]) + """, """ + str(egoStartPos[2]) + """ )""")
            dbconn.commit()
            cursor.close()
            dbconn.close()
        else:
            with open(self.constr.replace(".mdb", "_global.csv"), "w", newline='') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow(["CASEID", "DATETIME", "PARTICIP", "SOLVER", "GPSLAT", "GPSLON", "GPSELE"])
                csv_writer.writerow([str(self.caseid), str(startTime), str(numberOfTrobs), "99999", str(egoStartPos[0]), str(egoStartPos[1]), str(egoStartPos[2])])



    def writeParticipantTable(self, trajectories):
        if not self.csv_flag:
            dbconn = pyodbc.connect(self.constr)
            cursor = dbconn.cursor()
            cursor.execute("""CREATE TABLE participant_data (
                                             CASEID varchar(255),
                                             PARTID int,
                                             PARTTYPE int,
                                             'LENGTH' double,
                                             WIDTH double,
                                             HEIGHT double,
                                             TRACKWIDTH double,
                                             WHEELBASE double,
                                             FRONTAXLEX double,
                                             WEIGHT double,
                                             COGX double,
                                             COGY double,
                                             COGZ double,
                                             IXX double,
                                             IYY double,
                                             IZZ double
                                             );""")
            dbconn.commit()

            for trajectory in trajectories:
                pcmType = self.mapObjectTypeIndex(trajectory["type"])
                dataDict = self.extrackObjectAttributes(pcmType)
                dataDict = {key: value if value else 99999 for key, value in dataDict.items()}
                dataDict["dimensions"] = [x if x else 99999 for x in dataDict["dimensions"]]
                cursor.execute("""INSERT INTO participant_data (CASEID, PARTID, PARTTYPE, 'LENGTH', WIDTH, HEIGHT, TRACKWIDTH, WHEELBASE, FRONTAXLEX, WEIGHT, COGX, COGY, COGZ, IXX, IYY, IZZ)
                               VALUES('""" + str(self.caseid)
                               + """', """ + str(trajectory["id"])
                               + """, """ + str(pcmType)
                               + """, """ + str(dataDict["dimensions"][1] if "dimensions" in dataDict else 99999)
                               + """, """ + str(dataDict["dimensions"][0] if "dimensions" in dataDict else 99999)
                               + """, """ + str(dataDict["dimensions"][2] if "dimensions" in dataDict else 99999)
                               + """, """ + str(dataDict["trackWidth"] if "trackWidth" in dataDict else 99999)
                               + """, """ + str(dataDict["wheelBase"] if "wheelBase" in dataDict else 99999)
                               + """, """ + str(dataDict["frontAxLex"] if "frontAxLex" in dataDict else 99999)
                               + """, """ + str(dataDict["weight"] if "weight" in dataDict else 99999)
                               + """, """ + str(dataDict["cogX"] if "cogX" in dataDict else 99999)
                               + """, """ + str(dataDict["cogY"] if "cogY" in dataDict else 99999)
                               + """, """ + str(dataDict["cogZ"] if "cogZ" in dataDict else 99999)
                               + """, """ + str(dataDict["ixx"] if "ixx" in dataDict else 99999)
                               + """, """ + str(dataDict["iyy"] if "iyy" in dataDict else 99999)
                               + """, """ + str(dataDict["izz"] if "izz" in dataDict else 99999) + """)""")
                dbconn.commit()

            cursor.close()
            dbconn.close()
        else:
            with open(self.constr.replace(".mdb", "_participant_data.csv"), "w", newline='') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow(["CASEID", "PARTID", "PARTTYPE", "LENGTH", "WIDTH", "HEIGHT", "TRACKWIDTH", "WHEELBASE", "FRONTAXLEX", "WEIGHT", "COGX", "COGY", "COGZ", "IXX", "IYY", "IZZ"])

                for trajectory in trajectories:
                    pcmType = self.mapObjectTypeIndex(trajectory["type"])
                    dataDict = self.extrackObjectAttributes(pcmType)
                    dataDict = {key: value if value else 99999 for key, value in dataDict.items()}
                    dataDict["dimensions"] = [x if x else 99999 for x in dataDict["dimensions"]]
                    csv_writer.writerow([str(self.caseid), str(trajectory["id"]), str(pcmType),
                                         str(dataDict["dimensions"][1] if "dimensions" in dataDict else 99999),
                                         str(dataDict["dimensions"][0] if "dimensions" in dataDict else 99999),
                                         str(dataDict["dimensions"][2] if "dimensions" in dataDict else 99999),
                                         str(dataDict["trackWidth"] if "trackWidth" in dataDict else 99999),
                                         str(dataDict["wheelBase"] if "wheelBase" in dataDict else 99999),
                                         str(dataDict["frontAxLex"] if "frontAxLex" in dataDict else 99999),
                                         str(dataDict["weight"] if "weight" in dataDict else 99999),
                                         str(dataDict["cogX"] if "cogX" in dataDict else 99999),
                                         str(dataDict["cogY"] if "cogY" in dataDict else 99999),
                                         str(dataDict["cogZ"] if "cogZ" in dataDict else 99999),
                                         str(dataDict["ixx"] if "ixx" in dataDict else 99999),
                                         str(dataDict["iyy"] if "iyy" in dataDict else 99999),
                                         str(dataDict["izz"] if "izz" in dataDict else 99999)])


    def writeDynamicsTable(self, trajectories, geoHandler):
        if not self.csv_flag:

            dbconn = pyodbc.connect(self.constr)

            cursor = dbconn.cursor()
            cursor.execute("""CREATE TABLE dynamics (
                                         CASEID varchar(255),
                                         PARTID int,
                                         VARIATIONID int,
                                         'TIME' double,
                                         POSX double,
                                         POSY double,
                                         POSZ double,
                                         POSPHI double,
                                         POSTHETA double,
                                         POSPSI double,
                                         VX double,
                                         VY double,               
                                         VZ double,
                                         AX double,
                                         AY double,
                                         AZ double,
                                         MUE double,
                                         REC int);""")
            dbconn.commit()

            self_trajectory_index = next((i for i, v in enumerate(trajectories) if v['id'] == 0), None)

            self_first_lat = trajectories[self_trajectory_index]["positions_rotations_and_boxes"][0]["position"][0]
            self_first_long = trajectories[self_trajectory_index]["positions_rotations_and_boxes"][0]["position"][1]
            self_first_x, self_first_y = geoHandler.lat_long_to_meter(self_first_lat, self_first_long)

            for index, trajectory in enumerate(trajectories):
                if len(trajectory["positions_rotations_and_boxes"]) == 0:
                    continue

                partNumber = trajectory["id"]

                times = []
                xs = []
                ys = []

                for pbr in trajectory["positions_rotations_and_boxes"]:
                    time = 0.1 * pbr["frame"]
                    try:
                        lat = pbr["position"][0]
                        long = pbr["position"][1]

                        x, y = geoHandler.lat_long_to_meter(lat, long)

                        times.append(time)
                        xs.append(x - self_first_x)
                        ys.append(y - self_first_y)
                    except KeyError:
                        cursor.execute("""INSERT INTO dynamics (CASEID, PARTID, VARIATIONID, 'TIME', POSX, POSY, POSZ, POSPHI, POSTHETA, POSPSI, VX, VY, VZ, AX, AY, AZ, MUE, REC)
                                          VALUES('""" + self.caseid + """', """ + str(partNumber) + """, 0, """ + str(time) + """, 99999, 99999, 99999, 99999, 99999, 99999, 99999, 99999, 99999, 99999, 99999, 99999, 99999, 0)""")
                        dbconn.commit()

                if len(xs) > 1:
                    central_dxs = self.derivative(np.array(xs))
                    central_dys = self.derivative(np.array(ys))

                    grads = np.column_stack((central_dxs, central_dys))
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
                    orientations = []
                    dxs_local = []
                    dys_local = []
                    for i, rad in enumerate(rads):
                        if not i == 0:
                            rotation = trajectory["positions_rotations_and_boxes"][i][
                                           "rotation"] * math.pi / 180 if "rotation" in \
                                                                          trajectory[
                                                                              "positions_rotations_and_boxes"][
                                                                              i] else (
                                rad * -np.sign(grads[i][0]) if not np.isnan(rad) else 99999)

                            central_dxy = np.array([[central_dxs[i]], [-central_dys[i]]])
                            coordinate_system_correction_rotation = np.array([[math.cos(math.pi / 2), -math.sin(math.pi / 2)],
                                                                              [math.sin(math.pi / 2), math.cos(math.pi / 2)]])
                            rotation_matrix = np.array([[math.cos(rotation), -math.sin(rotation)],
                                                        [math.sin(rotation), math.cos(rotation)]])

                            orientations.append((rotation + (math.pi / 2)) if rotation != 99999 else 99999)

                            dxy_local = np.dot(rotation_matrix, np.dot(coordinate_system_correction_rotation, central_dxy))

                            dxs_local.append(10 * dxy_local[0][0])
                            dys_local.append(10 * dxy_local[1][0])
                    dxs_local.insert(0, dxs_local[0])
                    orientations.insert(0, (trajectory["positions_rotations_and_boxes"][0]["rotation"] + 90) * math.pi / 180 if "rotation" in trajectory["positions_rotations_and_boxes"][0] else orientations[0])
                    ddxs_local = np.gradient(dxs_local) * 10

                    mask = [(dxf == 0 and dyf == 0) or (dxb == 0 and dyb == 0) for dxf, dyf, dxb, dyb in list(
                        zip(self.derivative(np.array(xs), 'forward'), self.derivative(np.array(ys), 'forward'),
                            self.derivative(np.array(xs), 'backward'), self.derivative(np.array(ys), 'backward')))]
                    mask[0] = False
                    mask[-1] = False

                    dxs_local = [0 if m else x for x, m in list(zip(dxs_local, mask))]
                    ddxs_local = [0 if m else x for x, m in list(zip(ddxs_local, mask))]

                    for i in range(len(times)):
                        cursor.execute("""INSERT INTO dynamics (CASEID, PARTID, VARIATIONID, 'TIME',
                                                                        POSX, POSY, POSZ,
                                                                        POSPHI, POSTHETA, POSPSI,
                                                                        VX, VY, VZ,
                                                                        AX, AY, AZ,
                                                                        MUE, REC)
                                                        VALUES('""" + self.caseid + """', """ + str(partNumber) + """, 0, """ + str(
                            times[i]) + """,
                                                                """ + str(xs[i]) + """, """ + str(ys[i]) + """, 99999,
                                                                99999, 99999, """ + str(orientations[i]) + """,
                                                                """ + str(dxs_local[i]) + """, 99999, 99999,
                                                                """ + str(ddxs_local[i]) + """, 99999, 99999,
                                                                99999, 0)
                                                      """)
                        dbconn.commit()

                elif len(xs) == 1:
                    cursor.execute("""INSERT INTO dynamics (CASEID, PARTID, VARIATIONID, 'TIME',
                                                                                    POSX, POSY, POSZ,
                                                                                    POSPHI, POSTHETA, POSPSI,
                                                                                    VX, VY, VZ,
                                                                                    AX, AY, AZ,
                                                                                    MUE, REC)
                                                                    VALUES('""" + self.caseid + """', """ + str(index) + """, 0, """ + str(times[0]) + """, """ + str(xs[0]) + """, """ + str(ys[0]) + """, 99999, 99999, 99999, 99999, 99999, 99999, 99999, 99999, 99999, 99999, 99999, 0)""")
                    dbconn.commit()

            cursor.close()
            dbconn.close()
        else:
            with open(self.constr.replace(".mdb", "_dynamics.csv"), "w", newline='') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow(["CASEID", "PARTID", "VARIATIONID", "TIME", "POSX", "POSY", "POSZ", "POSPHI", "POSTHETA", "POSPSI", "VX", "VY", "VZ", "AX", "AY", "AZ", "MUE", "REC"])

                self_trajectory_index = next((i for i, v in enumerate(trajectories) if v['id'] == 0), None)
                self_first_lat = trajectories[self_trajectory_index]["positions_rotations_and_boxes"][0]["position"][0]
                self_first_long = trajectories[self_trajectory_index]["positions_rotations_and_boxes"][0]["position"][1]
                self_first_x, self_first_y = geoHandler.lat_long_to_meter(self_first_lat, self_first_long)

                for index, trajectory in enumerate(trajectories):
                    if len(trajectory["positions_rotations_and_boxes"]) == 0:
                        continue

                    partNumber = trajectory["id"]

                    times = []
                    xs = []
                    ys = []

                    for pbr in trajectory["positions_rotations_and_boxes"]:
                        time = 0.1 * pbr["frame"]
                        try:
                            lat = pbr["position"][0]
                            long = pbr["position"][1]

                            x, y = geoHandler.lat_long_to_meter(lat, long)

                            times.append(time)
                            xs.append(x - self_first_x)
                            ys.append(y - self_first_y)
                        except KeyError:
                            csv_writer.writerow([str(self.caseid), str(index), "0", str(time), "99999", "99999", "99999", "99999", "99999", "99999", "99999", "99999", "99999", "99999", "99999", "99999", "99999", "0"])

                    if len(xs) > 1:
                        central_dxs = self.derivative(np.array(xs))
                        central_dys = self.derivative(np.array(ys))

                        grads = np.column_stack((central_dxs, central_dys))
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
                        orientations = []
                        dxs_local = []
                        dys_local = []
                        for i, rad in enumerate(rads):
                            if not i == 0:
                                rotation = trajectory["positions_rotations_and_boxes"][i][
                                               "rotation"] * math.pi / 180 if "rotation" in \
                                                                              trajectory[
                                                                                  "positions_rotations_and_boxes"][
                                                                                  i] else (
                                    rad * -np.sign(grads[i][0]) if not np.isnan(rad) else 99999)

                                central_dxy = np.array([[central_dxs[i]], [-central_dys[i]]])
                                coordinate_system_correction_rotation = np.array([[math.cos(math.pi / 2), -math.sin(math.pi / 2)],
                                                                                  [math.sin(math.pi / 2), math.cos(math.pi / 2)]])
                                rotation_matrix = np.array([[math.cos(rotation), -math.sin(rotation)],
                                                            [math.sin(rotation), math.cos(rotation)]])

                                orientations.append((rotation + (math.pi / 2)) if rotation != 99999 else 99999)

                                dxy_local = np.dot(rotation_matrix, np.dot(coordinate_system_correction_rotation, central_dxy))

                                dxs_local.append(10 * dxy_local[0][0])
                                dys_local.append(10 * dxy_local[1][0])
                        dxs_local.insert(0, dxs_local[0])
                        orientations.insert(0, (trajectory["positions_rotations_and_boxes"][0]["rotation"] + 90) * math.pi / 180 if "rotation" in trajectory["positions_rotations_and_boxes"][0] else orientations[0])
                        ddxs_local = np.gradient(dxs_local) * 10

                        mask = [(dxf == 0 and dyf == 0) or (dxb == 0 and dyb == 0) for dxf, dyf, dxb, dyb in list(
                            zip(self.derivative(np.array(xs), 'forward'), self.derivative(np.array(ys), 'forward'),
                                self.derivative(np.array(xs), 'backward'), self.derivative(np.array(ys), 'backward')))]
                        mask[0] = False
                        mask[-1] = False

                        dxs_local = [0 if m else x for x, m in list(zip(dxs_local, mask))]
                        ddxs_local = [0 if m else x for x, m in list(zip(ddxs_local, mask))]

                        for i in range(len(times)):
                            csv_writer.writerow([str(self.caseid), str(partNumber), "0", str(times[i]), str(xs[i]), str(ys[i]), "99999", "99999", "99999", str(orientations[i]), str(dxs_local[i]), "99999", "99999", str(ddxs_local[i]), "99999", "99999", "99999", "0"])

                    elif len(xs) == 1:
                        csv_writer.writerow([str(self.caseid), str(index), "0", str(times[0]), str(xs[0]), str(ys[0]), "99999", "99999", "99999", "99999", "99999", "99999", "99999", "99999", "99999", "99999", "99999", "0"])


    def writeSpecificationTable(self, trajectories):
        if not self.csv_flag:
            dbconn = pyodbc.connect(self.constr)

            cursor = dbconn.cursor()
            cursor.execute("""CREATE TABLE specification (
                                             CASEID varchar(255),
                                             PARTID int,
                                             VARIATIONID int,
                                             'TIME' double,
                                             SPECIFICATION int,
                                             MANEUVER int,
                                             APPROACH int,
                                             BOXXMIN int,
                                             BOXYMIN int,
                                             BOXXMAX int,
                                             BOXYMAX int,
                                             CONFIDENCE double);""")
            dbconn.commit()

            for trajectory in trajectories:
                objID = trajectory["id"]
                for pbr in trajectory["positions_rotations_and_boxes"]:
                    time = 0.1 * pbr["frame"]
                    try:
                        specification = self.mapSpecification(pbr["ego_specification" if objID == 0 else "opponent_specification"])
                    except KeyError:
                        specification = 99999
                    try:
                        maneuverType = self.mapManeuverType(pbr["ego_maneuver_type"]) if objID == 0 else 99999
                    except KeyError:
                        maneuverType = 99999
                    try:
                        approach = 99999 if objID == 0 else self.mapApproach(pbr["opponent_approach"])
                    except KeyError:
                        approach = 99999
                    try:
                        xmin = int(pbr["box"][0])
                    except KeyError:
                        xmin = 99999
                    try:
                        ymin = int(pbr["box"][1])
                    except KeyError:
                        ymin = 99999
                    try:
                        xmax = int(pbr["box"][2])
                    except KeyError:
                        xmax = 99999
                    try:
                        ymax = int(pbr["box"][3])
                    except KeyError:
                        ymax = 99999
                    try:
                        conf = pbr["confidence"]
                    except KeyError:
                        conf = 99999

                    cursor.execute("""INSERT INTO specification (CASEID, PARTID, VARIATIONID, 'TIME', SPECIFICATION, MANEUVER, APPROACH, BOXXMIN, BOXYMIN, BOXXMAX, BOXYMAX, CONFIDENCE)
                                           VALUES('""" + str(self.caseid)
                                   + """', """ + str(objID)
                                   + """, 0, """ + str(time)
                                   + """, """ + str(specification)
                                   + """, """ + str(maneuverType)
                                   + """, """ + str(approach)
                                   + """, """ + str(xmin)
                                   + """, """ + str(ymin)
                                   + """, """ + str(xmax)
                                   + """, """ + str(ymax)
                                   + """, """ + str(conf) + """)""")
                    dbconn.commit()

            cursor.close()
            dbconn.close()
        else:
            with open(self.constr.replace(".mdb", "_specification.csv"), "w", newline='') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow(["CASEID", "PARTID", "VARIATIONID", "TIME", "SPECIFICATION", "MANEUVER", "APPROACH", "BOXXMIN", "BOXYMIN", "BOXXMAX", "BOXYMAX", "CONFIDENCE"])

                for trajectory in trajectories:
                    objID = trajectory["id"]
                    for pbr in trajectory["positions_rotations_and_boxes"]:
                        time = 0.1 * pbr["frame"]
                        try:
                            specification = self.mapSpecification(pbr["ego_specification" if objID == 0 else "opponent_specification"])
                        except KeyError:
                            specification = 99999
                        try:
                            maneuverType = self.mapManeuverType(pbr["ego_maneuver_type"]) if objID == 0 else 99999
                        except KeyError:
                            maneuverType = 99999
                        try:
                            approach = 99999 if objID == 0 else self.mapApproach(pbr["opponent_approach"])
                        except KeyError:
                            approach = 99999
                        try:
                            xmin = int(pbr["box"][0])
                        except KeyError:
                            xmin = 99999
                        try:
                            ymin = int(pbr["box"][1])
                        except KeyError:
                            ymin = 99999
                        try:
                            xmax = int(pbr["box"][2])
                        except KeyError:
                            xmax = 99999
                        try:
                            ymax = int(pbr["box"][3])
                        except KeyError:
                            ymax = 99999
                        try:
                            conf = pbr["confidence"]
                        except KeyError:
                            conf = 99999

                        csv_writer.writerow([str(self.caseid), str(objID), "0", str(time), str(specification), str(maneuverType), str(approach), str(xmin), str(ymin), str(xmax), str(ymax), str(conf)])

