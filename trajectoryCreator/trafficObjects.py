import uuid
from typing import Dict, Any

import numpy as np
from scipy.ndimage import gaussian_filter1d
import behaviourClassification as bc
from scipy import interpolate, optimize


class TrafficObject(object):

    idCounter = 1
    def __init__(self, track, position_estimator, orientation_estimator, geo_handler, ego=None,
                 egoPositionExtractor=None, videoLength=300, dimensions=None):

        self.geo_handler = geo_handler
        if not ego:  # means it is the ego itself
            self.id = 0
            self.type = 1
            self.track = track
            self.positions = {frame: egoPositionExtractor.position(frame).flatten() for frame in
                              range(videoLength)}  # positions are in meter
            self.dimensions = dimensions
            self.isEgo = True
        else:
            self.id = uuid.uuid4()
            self.type = track.type
            self.isEgo = False
            if self.type == 0:
                self.dimensions = None
            if self.type == 1:
                self.dimensions = [1.8, 4.5, 1.5]
            if self.type == 2:
                self.dimensions = [2.6, 8.0, 3.4]
            if self.type == 3:
                self.dimensions = [2.55, 12, 3.0]
            if self.type == 4:
                self.dimensions = [0.7, 1.8, 1.8]
            if self.type == 5:
                self.dimensions = [0.8, 2.2, 1.8]
            if self.type == 6:
                self.dimensions = [2.6, 6.0, 3.4]
            if self.type == 7:
                self.dimensions = [2.7, 30, 3.7]
            if self.type == 8:
                self.dimensions = [3.1, 100, 3.8]
            if self.type == 9:
                self.dimensions = [2.2, 6.8, 2.8]
            if self.type == 10:
                self.dimensions = [2.8, 5.7, 3.3]
            if self.type == 11:
                self.dimensions = [3.2, 10, 3.3]
            if self.type == 12:
                self.dimensions = [2.2, 6.6, 3.7]
            if self.type == 13:
                self.dimensions = [0.6, 1, 1]
            if self.type == 14:
                self.dimensions = [0.5, 0.4, 2]
            if self.type == 15:
                self.dimensions = [1, 3.5, 2.2]
            if self.type == 16:
                self.dimensions = [0.4, 1.0, 0.7]
            self.track = track
            self.positions, self.relative_positions = position_estimator.estimate_positions_for_track(track)  # positions are in meter
            self.id = TrafficObject.idCounter
            TrafficObject.idCounter += 1

            self.spline_smooth()

        self.orientations = orientation_estimator.estimate_orientations_for_track(self.positions)

        if not self.isEgo:
            self.approaches = bc.calculateOpponentApproach(self.positions, ego.positions, self.orientations, ego.orientations, self.geo_handler)
        else:
            self.approaches = None
        self.specifications, self.egoManeuverTypes = bc.calculateSpecification(self.positions, self.geo_handler, isEgo=self.isEgo)
        if not self.isEgo:
            self.badPositionExtrapolations = self.extrapolateSpecsForBadPositions(self.track, self.specifications, self.approaches)
        else:
            self.badPositionExtrapolations = None


    def to_dict(self):
        json_dict: Dict[str, Any] = {"id": int(self.id),
                                     "type": int(self.type),
                                     "positions_rotations_and_boxes": []}
        if self.dimensions:
            json_dict["dimensions"] = self.dimensions

        for key, item in self.positions.items():
            pbrDict = {"frame": key,
                       "position": list(self.geo_handler.meter_to_lat_long(item[0], item[1]))}
            rotation = self.orientations[key] if len(self.positions) > 1 else None
            if rotation:
                pbrDict["rotation"] = rotation
            if self.track:
                pbrDict["box"] = self.track.get_box(key)
                try:
                    pbrDict["confidence"] = self.track.get_confidence(key)
                except Exception:
                    pbrDict["confidence"] = 0.0
            if len(self.positions.items()) == 1:
                pbrDict["opponent_approach"] = "Other"
                pbrDict["opponent_specification"] = "StandStill"
            else:
                if not self.isEgo:
                    try:
                        pbrDict["opponent_approach"] = self.approaches[key]
                        pbrDict["opponent_specification"] = self.specifications[key]
                    except KeyError:
                        print("no specification or approach for frame " + str(key) + "available")
                else:
                    try:
                        pbrDict["ego_specification"] = self.specifications[key]
                        pbrDict["ego_maneuver_type"] = self.egoManeuverTypes[key]
                    except KeyError:
                        print("no specification or maneuver type for frame " + str(key) + "available")
            json_dict["positions_rotations_and_boxes"].append(pbrDict)

        if self.badPositionExtrapolations:
            for key, dictionary in self.badPositionExtrapolations.items():
                pbrDict = {"frame": key,
                           "box": dictionary["box"],
                           "opponent_approach": dictionary["approach"],
                           "opponent_specification": dictionary["specification"],
                           "confidence": self.track.get_confidence(key)}
                json_dict["positions_rotations_and_boxes"].append(pbrDict)

        return json_dict

    def gauss_smooth(self):
        frames = self.positions.keys()
        positions = self.positions.values()
        lats = np.array([x[0] for x in positions]).flatten()
        longs = np.array([x[1] for x in positions]).flatten()
        elevs = np.array([x[2] for x in positions]).flatten()
        if len(lats) > 1:
            lats = gaussian_filter1d(lats, 2, mode='nearest')
            longs = gaussian_filter1d(longs, 2, mode='nearest')
            elevs = gaussian_filter1d(elevs, 2, mode='nearest')
            for i, frame in enumerate(frames):
                self.positions[frame][0] = lats[i]
                self.positions[frame][1] = longs[i]
                self.positions[frame][2] = elevs[i]
        if len(lats) == 1:
            for i, frame in enumerate(frames):
                self.positions[frame][0] = lats[i]
                self.positions[frame][1] = longs[i]
                self.positions[frame][2] = elevs[i]

    def spline_smooth(self):
        def eval(u, t, tck):
            return np.array(interpolate.splev(u, tck)).flatten()[3] - t

        def pos_at_time(t, tck):
            root = optimize.root_scalar(eval, args=(t, tck), x0=0, x1=1, method="secant").root
            return np.array(interpolate.splev(root, tck)).flatten()

        frames = list(self.positions.keys())
        positions = self.positions.values()
        xs = np.array([x[0] for x in positions]).flatten()
        ys = np.array([x[1] for x in positions]).flatten()
        elevs = np.array([x[2] for x in positions]).flatten()

        if len(frames) > 3:
            tck, u = interpolate.splprep([xs, ys, elevs, frames], s=20)

            for i, frame in enumerate(frames):
                pos = pos_at_time(frame, tck)
                self.positions[frame][0] = pos[0]
                self.positions[frame][1] = pos[1]
                self.positions[frame][2] = pos[2]
        else:
            self.gauss_smooth()


    def extrapolateSpecsForBadPositions(self, track, specifications, approaches):

        boxes = {}
        for frame in range(0, track.last_detected_frame):
            box = track.get_box(frame)
            if box is None:
                continue
            boxes[frame] = [int(round(x)) for x in box]

        diff = set(boxes.keys()).difference(set(specifications.keys()))
        diff2 = set(boxes.keys()).difference(set(approaches.keys()))
        diff = diff.union(diff2)

        extrapolated_values = {}
        if len(diff) > 0 and len(list(specifications.keys())) > 0 and len(list(approaches.keys())) > 0:
            for frame in diff:
                nearest_spec_frame = sorted(specifications.keys(), key=lambda f: abs(frame-f))[0]
                nearest_app_frame = sorted(approaches.keys(), key=lambda f: abs(frame-f))[0]
                dictionary = {"box": boxes[frame]}
                try:
                    dictionary["specification"] = specifications[nearest_spec_frame]
                except KeyError:
                    pass
                try:
                    dictionary["approach"] = approaches[nearest_app_frame]
                except KeyError:
                    pass
                extrapolated_values[frame] = dictionary

        return extrapolated_values
