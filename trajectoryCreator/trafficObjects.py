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

            if len(self.positions.keys()) > 0:
                self.interOrExtrapolateBadPositionsLinear(self.track)

                self.spline_smooth()

        self.orientations = orientation_estimator.estimate_orientations_for_track(self.positions)

        if not self.isEgo:
            self.approaches = bc.calculateOpponentApproach(self.positions, ego.positions, self.orientations, ego.orientations, self.geo_handler)
        else:
            self.approaches = None
        self.specifications, self.egoManeuverTypes = bc.calculateSpecification(self.positions, self.geo_handler, isEgo=self.isEgo)


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

        return json_dict

    def gauss_smooth(self):
        sorted_dict = {k: self.positions[k] for k in sorted(self.positions)}
        frames = list(sorted_dict.keys())
        positions = list(sorted_dict.values())
        lats = np.array([x[0] for x in positions]).flatten()
        longs = np.array([x[1] for x in positions]).flatten()
        elevs = np.array([x[2] for x in positions]).flatten()
        if len(lats) > 1:
            lats = gaussian_filter1d(lats, 2, mode='nearest')
            longs = gaussian_filter1d(longs, 2, mode='nearest')
            elevs = gaussian_filter1d(elevs, 2, mode='nearest')
            for i, frame in enumerate(frames):
                if frame in self.positions:
                    self.positions[frame][0] = lats[i]
                    self.positions[frame][1] = longs[i]
                    self.positions[frame][2] = elevs[i]
        if len(lats) == 1:
            for i, frame in enumerate(frames):
                if frame in self.positions:
                    self.positions[frame][0] = lats[i]
                    self.positions[frame][1] = longs[i]
                    self.positions[frame][2] = elevs[i]

    def findBadPositionFrames(self, track):
        frames = list(range(list(self.positions.keys())[0], track.last_detected_frame))
        diff = set(frames).difference(set(self.positions.keys()))
        return list(diff)

    def spline_smooth(self):
        def eval(u, t, tck):
            return np.array(interpolate.splev(u, tck)).flatten()[3] - t

        def pos_at_time(t, tck):
            root = optimize.root_scalar(eval, args=(t, tck), x0=0, x1=1, method="secant").root
            return np.array(interpolate.splev(root, tck)).flatten()

        sorted_dict = {k: self.positions[k] for k in sorted(self.positions)}
        frames = list(sorted_dict.keys())
        positions = list(sorted_dict.values())
        xs = np.array([x[0] for x in positions]).flatten()
        ys = np.array([x[1] for x in positions]).flatten()
        elevs = np.array([x[2] for x in positions]).flatten()

        if len(frames) > 3:
            tck, u = interpolate.splprep([xs, ys, elevs, frames], s=20)

            for i, frame in enumerate(frames):
                pos = pos_at_time(frame, tck)
                if frame in self.positions:
                    self.positions[frame][0] = pos[0]
                    self.positions[frame][1] = pos[1]
                    self.positions[frame][2] = pos[2]
        else:
            self.gauss_smooth()

    def interOrExtrapolateBadPositionsLinear(self, track):
        np.seterr('raise')
        def find_nearest_higher_value(value_array, base_value):
            value_array = np.asarray(value_array, dtype=np.float)
            diff = value_array - base_value
            diff[diff < 0] = np.inf
            idx = diff.argmin()
            if np.isinf(idx):
                return "too high"
            return value_array[idx]

        def find_nearest_lower_value(value_array, base_value):
            value_array = np.asarray(value_array, dtype=np.float)
            diff = base_value - value_array
            diff[diff < 0] = np.inf
            idx = diff.argmin()
            if np.isinf(idx):
                return "too low"
            return value_array[idx]

        framesToExtrapolate = self.findBadPositionFrames(self.track)
        existingFrames = list(self.positions.keys())
        for frame in framesToExtrapolate:
            lower_frame = find_nearest_lower_value(existingFrames, frame)
            higher_frame = find_nearest_higher_value(existingFrames, frame)
            if lower_frame == "too low":
                lower_frame = existingFrames[0]
                higher_frame = existingFrames[1]
                lower_pos = self.positions[lower_frame]
                higher_pos = self.positions[higher_frame]
            elif higher_frame == "too high":
                lower_frame = existingFrames[-2]
                higher_frame = existingFrames[-1]
                lower_pos = self.positions[lower_frame]
                higher_pos = self.positions[higher_frame]
            else:
                lower_pos = self.positions[lower_frame]
                higher_pos = self.positions[higher_frame]
                if higher_frame == lower_frame:
                    continue
            x = higher_pos[0][0] + (higher_pos[0][0] - lower_pos[0][0])/(higher_frame-lower_frame)*(frame-higher_frame)
            y = higher_pos[1][0] + (higher_pos[1][0] - lower_pos[1][0])/(higher_frame-lower_frame)*(frame-higher_frame)
            z = higher_pos[2][0] + (higher_pos[2][0] - lower_pos[2][0])/(higher_frame-lower_frame)*(frame-higher_frame)
            box = track.get_box(frame)
            box = [int(round(x)) for x in box]
            self.positions[frame] = [[x], [y], [z]]
            self.track.boxes[frame] = box
            if not frame in list(self.track.confidences.keys()):
                self.track.confidences[frame] = 0
