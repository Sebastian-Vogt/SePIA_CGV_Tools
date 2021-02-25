import itertools

import cv2
import numpy as np
import time

import utils

from sort import Sort


class SortTracker:
    def __init__(self, detector, yolo_detector, max_age, min_occurrences):
        self.detector = detector
        self.yoloDetector = yolo_detector
        self.max_age = max_age
        self.min_occurrences = min_occurrences
        self.tracker = Sort(max_age, min_occurrences)
        self.frames = {}
        self.tracks = {}

    def track_frame(self, image, frame_id):
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        image = cv2.equalizeHist(image)
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        self.frames[frame_id] = image

        filtered_bboxes, filtered_scores, filtered_labels, label_frame, score_frame = self.detector.detect(image) if self.detector else ([], [], [], None, None)
        dets = [[box[0], box[1], box[2], box[3], score, cls] for box, score, cls in zip(filtered_bboxes, filtered_scores, filtered_labels)]

        yoloDets = self.yoloDetector.detect(image) if self.yoloDetector else []

        finalDets = []
        for yoloDet in yoloDets:
            for det in dets:
                if utils.box_iou(yoloDet[:4], det[:4]) > 0.4:
                    dets.remove(det)
                    break
            finalDets.append(yoloDet)
        finalDets.extend(dets)
        self.dets = np.array(finalDets)

        if len(self.dets) > 0:
            sort_tracks = self.tracker.update(self.dets)
        else:
            sort_tracks = self.tracker.update(np.empty((0, 6)))
        self.tracks[frame_id] = sort_tracks
        return label_frame, score_frame

    def convert_tracks_to_list(self):
        detections = []
        for framedets in self.tracks.values():
            detections.extend(framedets)
        ids = set([d[4] for d in detections])
        tracks = []
        for id in ids:
            track = Tracklet()
            track.id = id
            tracks.append(track)

        for frame, detections in self.tracks.items():
            for det in detections:
                for track in tracks:
                    if track.id == det[4]:
                        track.type = int(det[5])
                        track.boxes[frame] = list(det[:4])
                        track.last_detected_frame = max(frame, track.last_detected_frame)

        self.tracks = tracks


class Tracklet(object):
    id_iter = itertools.count(start=1)

    def __init__(self):
        # Initialize parametes for tracker (history)
        self.id = next(Tracklet.id_iter)  # uuid.uuid4()  # tracker's id
        self.boxes = {}
        self.type = None
        self.last_detected_frame = 0

    def set_box(self, box, frame):
        self.boxes[frame] = box

    def get_box(self, frame):
        try:
            return self.boxes[frame]
        except KeyError:
            return None
