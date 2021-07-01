import utils
import os
import cv2
import detection as det
import tracking as trk
import geography as geo
import egoPositionExtractor as epex
import groundTruthData as gtdata
import positionEstimation as pest
import orientationEstimation as orest
import trafficObjects as trob
import pcmV5
import numpy as np
import json
import time
import csv
from scipy.spatial.transform import Rotation as R
import pyodbc

'''
Tasks target function may not be in the task object because objects are not shared in multiprocessing. The given queue is used to communicate with the managerTask thread of the main process -> publish the progress
'''


def runTrajectoryEstimationTask(id, path, carInfo, settings, queue, gpuSemaphore):
    try:

        jsonPath = next((path + "\\" + x for x in os.listdir(path) if x.endswith('.json')), None)
        if jsonPath:
            with open(jsonPath) as json_file:
                json_data = json.load(json_file)
                if "mappingCoefficients" in json_data:
                    jsonPath = None
        totalTimeEstimate = 12.65 + (54.5 if not jsonPath else 0) + (2.7 if settings["trackIdVideo"] or settings["trackLabelVideo"] else 0) + (2.4 if settings["relativeDistanceVideo"] else 0)

        caseid = os.path.basename(path)
        trob.TrafficObject.idCounter = 1

        times = {}
        queue.put((id, "running", "Initializing...", 0))
        start = time.process_time()
        trajectoryEstimator = TrajectoryEstimator(id, path, carInfo, settings, queue, gpuSemaphore, totalTimeEstimate)
        end = time.process_time()
        times["initialize estimator object"] = end-start

        t = trajectoryEstimator.calculateTrafficObjects()
        times.update(t)
        trajectoryEstimator.removeGhosts()

        start = time.process_time()
        jsonList = trajectoryEstimator.createJSON()
        jsonDict = {"caseID": caseid,
                    "startTime": trajectoryEstimator.getStartingTime(),
                    "trajectories": jsonList}
        end = time.process_time()
        times["parse json"] = end-start

        queue.put((id, "running", "Exporting TrajAN file...", (totalTimeEstimate-1)/totalTimeEstimate * 100))
        start = time.process_time()
        with open(os.path.realpath(path) + "\\trajectories.trajan", 'w') as outfile:
            json.dump(jsonDict, outfile, indent=4)
        end = time.process_time()
        times["store json"] = end-start
        queue.put((id, "running", "Exporting PCM V5 tables", (totalTimeEstimate-1.35)/totalTimeEstimate * 100))
        start = time.process_time()

        exporter = pcmV5.PCMExporter(path, caseid)
        exporter.writeGlobalTable(trajectoryEstimator.getStartingTime(), trajectoryEstimator.getGPS(), len(trajectoryEstimator.objects))
        exporter.writeParticipantTable(jsonList)
        exporter.writeDynamicsTable(jsonList, trajectoryEstimator.geoHandler)
        exporter.writeSpecificationTable(jsonList)

        end = time.process_time()
        times["create and store pcm"] = end-start
        queue.put((id, "running", "Finished", 100))
        return times
    except Exception as e:
        queue.put((id, "failed", str(e), 100))
        raise e


class TrajectoryEstimator:

    def __init__(self, id, folder, carInformation, settings, sharingQueue, gpuSemaphore, totalTimeEstimate):
        self.id = id
        self.sharingQueue = sharingQueue
        self.gpuSemaphore = gpuSemaphore
        self.folderPath = folder
        self.settings = settings
        self.totalTimeEstimate = totalTimeEstimate

        videos = [x for x in os.listdir(self.folderPath) if x.endswith('.avi')]
        videos = sorted(videos, key=lambda x: x.count('_original'))
        if len(videos) > 1:
            for video in videos[:-1]:
                os.remove(self.folderPath + "\\" + video)
            os.rename(self.folderPath + "\\" + videos[-1], self.folderPath + "\\" + (videos[-1]).replace("_original", ""))

        self.videoPath = next((self.folderPath + "\\" + x for x in os.listdir(self.folderPath) if x.endswith('.avi')), None)
        originalVideoPath = next((self.folderPath + "\\" + x for x in os.listdir(self.folderPath) if x.endswith('.avi') and 'original' in x), None)
        self.videoPath = originalVideoPath if originalVideoPath else self.videoPath
        lktCSVPath = next((self.folderPath + "\\" + x for x in os.listdir(self.folderPath) if x.endswith('.csv') and 'lkt' in x.lower()), None)
        self.csvPath = lktCSVPath if lktCSVPath else next((self.folderPath + "\\" + x for x in os.listdir(self.folderPath) if x.endswith('.csv')), None)
        self.jsonPath = next((self.folderPath + "\\" + x for x in os.listdir(self.folderPath) if x.endswith('.json')), None)
        if self.jsonPath:
            with open(self.jsonPath) as json_file:
                json_data = json.load(json_file)
                if "mappingCoefficients" in json_data:
                    self.jsonPath = None


        self.rotation = R.from_matrix(carInformation["rotation"])

        self.cameraIntrinsics = carInformation["calibrationParameter"]
        self.egoDimensions = carInformation["dimensions"]
        self.egoCameraPosition = carInformation["cameraPosition"]

        if not self.videoPath:
            OSError(2, 'No such file or directory', self.videoPath)

        inputVideo = cv2.VideoCapture(self.videoPath)
        self.videoLength = int(inputVideo.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = int(inputVideo.get(cv2.CAP_PROP_FPS))
        self.width = int(inputVideo.get(3))
        self.height = int(inputVideo.get(4))
        inputVideo.release()

        self.similarityThreshold = settings["simThreshold"]
        self.detectionThreshold = settings["detThreshold"]

        self.trackIdVideoFlag = settings["trackIdVideo"]
        self.trackIdVideo = None
        self.trackLabelVideoFlag = settings["trackLabelVideo"]
        self.trackLabelVideo = None
        self.relativeDistanceVideoFlag = settings["relativeDistanceVideo"]
        self.relativeDistanceVideo = None

        self.detector = None
        self.tracker = None
        self.groundTruthParser = None
        self.sharingQueue.put((id, "running", "Creating geoHandler...", 1))
        self.geoHandler = geo.GeoHandler(settings["geoTiffPaths"])
        self.sharingQueue.put((id, "running", "Initialized geoHandler.", 9/totalTimeEstimate * 100))

        if not self.csvPath:
            OSError(2, 'No such file or directory', self.csvPath)

        self.sharingQueue.put((id, "running", "Initializing egoPositionExtractor...", 9/totalTimeEstimate * 100))
        self.egoPositionExtractor = epex.EgoPositionExtractor(self.csvPath, self.fps, self.videoLength, self.geoHandler)
        self.sharingQueue.put((id, "running", "Initialized egoPositionExtractor.", 9.1/totalTimeEstimate * 100))

        self.positionEstimator = pest.PositionEstimator(self.egoPositionExtractor,
                                                        self.geoHandler,
                                                        self.rotation,
                                                        carInformation['cameraPosition'][2],
                                                        self.cameraIntrinsics["mappingCoefficients"],
                                                        np.array(self.cameraIntrinsics["distortionCenter"]).reshape((2, 1)),
                                                        np.array(self.cameraIntrinsics["stretchMatrix"]),
                                                        (self.width, self.height))

        self.orientationEstimator = orest.OrientationEstimator()

        self.objects = []
        self.locations = []
        self.jsonList = []

    def calculateTrafficObjects(self):
        times = {}
        self.sharingQueue.put((id, "running", "Extracting ego trajectory...", 9.1/self.totalTimeEstimate * 100))
        start = time.process_time()
        self.ego = trob.TrafficObject(None, None, self.orientationEstimator, self.geoHandler, None, self.egoPositionExtractor, self.videoLength-self.egoPositionExtractor.videoFrameOffset, self.egoDimensions)
        end = time.process_time()
        times["create ego object"] = end-start
        self.sharingQueue.put((id, "running", "Created ego traffic object.", 10.7/self.totalTimeEstimate * 100))

        if os.path.isfile(self.videoPath.replace(".", "_original.")):
           os.remove(self.videoPath.replace(".", "_original."))
        os.rename(self.videoPath, self.videoPath.replace(".", "_original."))
        cuttedVideo = cv2.VideoWriter(self.videoPath, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10, (self.width, self.height))
        cap = cv2.VideoCapture(self.videoPath.replace(".", "_original."))
        cap.set(1, self.egoPositionExtractor.videoFrameOffset)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            cuttedVideo.write(frame)
        cuttedVideo.release()

        if self.jsonPath:
            self.detector = None
            self.tracker = None
            start = time.process_time()
            self.groundTruthParser = gtdata.GroundTruthJsonParser()
            end = time.process_time()
            times["create ground truth parser"] = end - start
            t = self.calculateTrafficObjectsUsingGroundTruthData()
            self.sharingQueue.put((self.id, "running", "Traffic objects calculated.", 11.2/self.totalTimeEstimate * 100))
            times.update(t)
        else:
            if not os.path.isfile(self.settings["detectorPath"]):
                OSError(2, 'No such file or directory', self.settings["detectorPath"])

            with self.gpuSemaphore:
                start = time.process_time()
                self.sharingQueue.put((self.id, "running", "Initializing detector and tracker", 10.7/self.totalTimeEstimate * 100))
                self.detector = det.RetinanetDetector(self.settings["detectorPath"], threshold=self.detectionThreshold, video_size=(self.width, self.height))
                try:
                    self.yolo = det.YoloDetector(self.settings["yoloPath"], img_size=640, confidence_threshold=self.detectionThreshold, iou_threshold=0.5)
                except:
                    self.yolo = None
                self.tracker = trk.SortTracker(self.detector, self.yolo, self.settings["maxAge"], self.settings["minOccurrences"], self.similarityThreshold)
                end = time.process_time()
                times["create detector & tracker"] = end - start
                self.sharingQueue.put((self.id, "running", "Detector and tracker initialized.", 19.2/self.totalTimeEstimate * 100))
                self.sharingQueue.put((self.id, "running", "Tracking...", 19.2/self.totalTimeEstimate * 100))
                self.groundTruthParser = None
                t = self.calculateTrafficObjectsUsingTracker()
                self.sharingQueue.put((self.id, "running", "Tracked.", 65.7/self.totalTimeEstimate * 100))
                times.update(t)

        if self.trackIdVideoFlag:
            trackIdVideo = cv2.VideoWriter(self.videoPath.replace(".", "_trackIds."),
                                           cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10,
                                           (self.width, self.height))
        else:
            trackIdVideo = None
        if self.trackLabelVideoFlag:
            trackLabelVideo = cv2.VideoWriter(self.videoPath.replace(".", "_trackLabels."),
                                              cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10,
                                              (self.width, self.height))
        else:
            trackLabelVideo = None

        if self.trackLabelVideoFlag or self.trackIdVideoFlag:
            self.sharingQueue.put((self.id, "running", "Writing videos...", (self.totalTimeEstimate-1-2.7-(2.4 if self.relativeDistanceVideoFlag else 0))/self.totalTimeEstimate * 100))
            start = time.process_time()
            utils.write_track_videos(self.objects, cv2.VideoCapture(self.videoPath), tracks_video_writer=trackIdVideo,
                                     labels_video_writer=trackLabelVideo)
            end = time.process_time()
            times["write track videos"] = end - start
            self.sharingQueue.put((self.id, "running", "Writing videos...", (self.totalTimeEstimate-1-(2.4 if self.relativeDistanceVideoFlag else 0))/self.totalTimeEstimate * 100))

        if self.relativeDistanceVideoFlag:
            self.sharingQueue.put((self.id, "running", "Writing videos...", (self.totalTimeEstimate-1-2.4)/self.totalTimeEstimate * 100))
            start = time.process_time()
            relPosVideo = cv2.VideoWriter(self.videoPath.replace(".", "_relative_positions."),
                                          cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10,
                                          (self.width, self.height))
            utils.write_relative_pos_video(self.objects, cv2.VideoCapture(self.videoPath), relPosVideo)
            end = time.process_time()
            times["write position videos"] = end - start
            self.sharingQueue.put((self.id, "running", "Videos written.", (self.totalTimeEstimate-1)/self.totalTimeEstimate * 100))

        return times

    def createJSON(self):
        cam = {"distortion_center": self.cameraIntrinsics["distortionCenter"],
                              "polynomial_coefficients": self.cameraIntrinsics["mappingCoefficients"],
                              "stretch_matrix": self.cameraIntrinsics["stretchMatrix"]
                              }
        self.objects.insert(0, self.ego)
        for obj in self.objects:
            self.jsonList.append(obj.to_dict())
        self.jsonList[0]["camera"] = cam
        return self.jsonList

    def calculateTrafficObjectsUsingGroundTruthData(self):

        annotated_objects = self.groundTruthParser.parse(self.jsonPath, videoOffset=self.egoPositionExtractor.videoFrameOffset)
        self.objects = []
        self.locations = []

        times = {"opponent traffic object GT": []}

        for i, an_obj in enumerate(annotated_objects):
            start = time.process_time()
            obj = trob.TrafficObject(an_obj, self.positionEstimator, self.orientationEstimator, self.geoHandler, self.ego)
            self.objects.append(obj)
            self.locations = self.locations + list(obj.positions.values())
            end = time.process_time()
            times["opponent traffic object GT"].append(end - start)
            self.sharingQueue.put((self.id, "running", "Calculating positions for object " + str(i+1) + "/" + str(len(annotated_objects)), (10.7 + i*0.5/(len(annotated_objects) if len(annotated_objects) > 0 else 1))/self.totalTimeEstimate * 100))
        times["opponent traffic object GT"] = sum(times["opponent traffic object GT"]) / len(times["opponent traffic object GT"]) if len(times["opponent traffic object GT"]) >= 1 else times["opponent traffic object GT"]
        return times

    def calculateTrafficObjectsUsingTracker(self):

        frame_nr = 0

        times = {"track frame": [],
                 "opponent traffic object tracker": []}
        inputVideo = cv2.VideoCapture(self.videoPath)
        while inputVideo.isOpened():
            ret, frame = inputVideo.read()
            if not ret:
                break
            frame_nr += 1

            start = time.process_time()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.tracker.track_frame(frame, frame_nr)
            end = time.process_time()
            times["track frame"].append(end - start)
            self.sharingQueue.put((self.id, "running", "Tracking "+ str(frame_nr) +"/" + str(self.videoLength), (19.2 + frame_nr/self.videoLength*37)/self.totalTimeEstimate * 100))
        times["track frames"] = sum(times["track frame"])
        inputVideo.release()

        self.tracker.convert_tracks_to_list()
        '''
        for track in self.tracker.tracks:
            track.boxes = {key: value for key, value in track.boxes.items() if key <= track.last_detected_frame}

        self.sharingQueue.put((self.id, "running", "Cleaning tracks...", 56.2/self.totalTimeEstimate * 100))
        start = time.process_time()
        self.tracker.cleanUpTracks(self.similarityThreshold)
        end = time.process_time()
        times["clean tracks"] = end - start
        '''

        self.objects = []
        self.locations = []

        for i, track in enumerate(self.tracker.tracks):
            start = time.process_time()
            obj = trob.TrafficObject(track, self.positionEstimator, self.orientationEstimator, self.geoHandler, self.ego)
            self.objects.append(obj)
            self.locations = self.locations + list(obj.positions.values())
            end = time.process_time()
            times["opponent traffic object tracker"].append(end - start)

        times["track frame"] = sum(times["track frame"]) / len(times["track frame"]) if len(times["track frame"]) >= 1 else times["track frame"]
        times["opponent traffic object tracker"] = sum(times["opponent traffic object tracker"]) / len(
                times["opponent traffic object tracker"]) if len(times["opponent traffic object tracker"]) >= 1 else times["opponent traffic object tracker"]
        return times

    def getStartingTime(self):
        csvPath = next((self.folderPath + "\\" + x for x in os.listdir(self.folderPath) if x.endswith('.csv')), None)
        startingTime = "8888-88-88T88:88:88.888"
        with open(csvPath, 'rt') as csvFile:
            csv_reader = csv.reader(csvFile, delimiter='|', quotechar='"')
            for row in csv_reader:
                description = str(row[0]).lower()
                if "timestamp start" in description:
                    startingTime = str(row[1])
                    startingTime = startingTime[:4] + '-' + startingTime[4:6] + '-' + startingTime[6:8] + 'T' + startingTime[9:11] + ':' + startingTime[11:13] + ':' + startingTime[13:15] + '.000'
                    break
        return startingTime

    def getGPS(self):
        pos = self.ego.positions[0.0]
        lat, lon = self.geoHandler.meter_to_lat_long(pos[0], pos[1])
        return [lat, lon, pos[2]]

    def removeGhosts(self):
        self.objects = [obj for obj in self.objects if len(obj.positions.keys()) > 0]