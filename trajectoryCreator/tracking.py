import itertools

import cv2
import numpy as np
import time

import utils

from sort import Sort


class SortTracker:
    def __init__(self, detector, yolo_detector, max_age, min_occurrences, similarityThreshold):
        self.detector = detector
        self.yoloDetector = yolo_detector
        self.max_age = max_age
        self.min_occurrences = min_occurrences
        self.tracker = Sort(max_age, min_occurrences)
        self.frames = {}
        self.tracks = {}
        self.similarityThreshold = similarityThreshold

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
                if utils.box_iou(yoloDet[:4], det[:4]) > self.similarityThreshold:
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

        ts = {}
        for frame, dets in self.tracks.items():
            for det in dets:
                id = int(det[6])
                if not id in ts:
                    ts[id] = {}
                ts[id][frame] = det[:-1]

        ts = dict(filter(lambda elem: len(dict(filter(lambda el: el[1][4] > 0.0, elem[1].items()))) >= self.min_occurrences, ts.items()))

        for id, t in ts.items():
            for frame in reversed(sorted(t)):
                if t[frame][4] == 0.0:
                    t.pop(frame)
                else:
                    break

        tracks = []
        for id, t in ts.items():
            track = Tracklet()
            types = {}
            for frame, det in t.items():
                track.confidences[frame] = det[4]
                track.boxes[frame] = list(det[:4])
                types[frame] = int(det[5])

            classes = np.zeros(max(list(types.values()))+1)
            for frame, conf in track.confidences.items():
                try:
                    classes[types[frame]] += conf
                except KeyError:
                    pass

            track.type = int(np.argmax(classes))
            track.last_detected_frame = max(track.confidences.keys())
            tracks.append(track)

        self.tracks = tracks


class Tracklet(object):
    id_iter = itertools.count(start=1)

    def __init__(self):
        # Initialize parametes for tracker (history)
        self.id = next(Tracklet.id_iter)  # uuid.uuid4()  # tracker's id
        self.boxes = {}
        self.confidences = {}
        self.type = None
        self.last_detected_frame = 0

    def set_box(self, box, frame):
        self.boxes[frame] = box

    def get_box(self, frame):
        try:
            return self.boxes[frame]
        except KeyError:
            return None

    def get_confidence(self, frame):
        try:
            return self.confidences[frame]
        except KeyError:
            return 0.0