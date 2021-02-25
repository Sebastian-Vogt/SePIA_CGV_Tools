import csv
from scipy.interpolate import interp1d
import numpy as np
import math
import utils
import matplotlib.pyplot as plt


class EgoPositionExtractor:
    def __init__(self, csv_path, frame_rate, video_length, geo_handler):
        self.frame_rate = frame_rate

        if csv_path:
            self.latitudes, self.longitudes, self.pitches, self.yaws, self.rolls = self.read_data(csv_path)
            if len(self.latitudes) <= 3 or len(self.longitudes) <= 3:
                raise IOError("Too less gps entries in csv file.")

            videoFrameOffset = video_length - max(self.latitudes.keys()) * frame_rate
            dataSecondsOffset, self.videoFrameOffset = math.modf(videoFrameOffset)
            dataSecondsOffset = dataSecondsOffset / frame_rate
            self.videoFrameOffset = int(self.videoFrameOffset)
            self.latitudes = {time + dataSecondsOffset: value for time, value in self.latitudes.items()}
            self.longitudes = {time + dataSecondsOffset: value for time, value in self.longitudes.items()}
            self.pitches = {time + dataSecondsOffset: value for time, value in self.pitches.items()}
            self.yaws = {time + dataSecondsOffset: value for time, value in self.yaws.items()}
            self.rolls = {time + dataSecondsOffset: value for time, value in self.rolls.items()}

            self.latitudes_interpolation = interp1d(list(self.latitudes.keys()), list(self.latitudes.values()),
                                                    kind='cubic', fill_value="extrapolate")
            self.longitudes_interpolation = interp1d(list(self.longitudes.keys()), list(self.longitudes.values()),
                                                     kind='cubic', fill_value="extrapolate")
            self.search_for_stops()
            if self.pitches:
                self.pitch_interpolation = interp1d(list(self.pitches.keys()), list(self.pitches.values()),
                                                   kind='cubic', fill_value="extrapolate")
                self.yaw_interpolation = interp1d(list(self.yaws.keys()), list(self.yaws.values()),
                                                   kind='cubic', fill_value="extrapolate")
                self.roll_interpolation = interp1d(list(self.rolls.keys()), list(self.rolls.values()),
                                                   kind='cubic', fill_value="extrapolate")
                # self.create_angle_plots(nr_frames)

            self.max_time = max(list(self.longitudes.keys()) + list(self.latitudes.keys()))
        self.geo = geo_handler

        try:
            i = [i for i,v in enumerate(zip(list(self.latitudes.values()), list(self.longitudes.values()))) if v[0] != list(self.latitudes.values())[0] or v[1] != list(self.longitudes.values())[0]][0]
        except:
            self.last_yaw_matrix = np.identity(3)
            self.init_yaw_mat = self.last_yaw_matrix
            return

        p2 = self.geo.lat_long_to_meter(self.latitudes[self.times[0]], self.longitudes[self.times[0]])
        p1 = self.geo.lat_long_to_meter(self.latitudes[self.times[i]], self.longitudes[self.times[i]])

        diff = np.subtract(p1, p2)

        dot_product = np.dot(diff / np.linalg.norm(diff), [0, 1])
        yaw = np.arccos(dot_product)
        yaw = math.degrees(yaw)
        if np.cross(diff, [0, 1, 0])[2] > 0:
            yaw = -yaw
        yaw_matrix = utils.yaw_matrix(yaw)
        self.last_yaw_matrix = yaw_matrix
        self.init_yaw_mat = yaw_matrix

    def init_yaw_matrix(self):
        self.last_yaw_matrix = self.init_yaw_mat


    def read_data(self, file_path):
        gps_latitudes = {}
        gps_longitudes = {}
        ins_latitudes = {}
        ins_longitudes = {}
        lkt_latitudes = {}
        lkt_longitudes = {}
        pitches = {}
        yaws = {}
        rolls = {}
        first_pitch = None
        with open(file_path, 'rt') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='|', quotechar='"')
            for row in csv_reader:
                if len(row) < 3:
                    continue
                try:
                    time_stamp = float(row[0])
                except ValueError:
                    continue
                description = str(row[1]).lower()
                value = row[2]

                if "gps_latitude" in description:
                    gps_latitudes[time_stamp] = float(value)
                elif "gps_longitude" in description:
                    gps_longitudes[time_stamp] = float(value)
                elif "ins_lat_abs" in description:
                    ins_latitudes[time_stamp] = float(value)
                elif "ins_long_abs" in description:
                    ins_longitudes[time_stamp] = float(value)
                elif "ins_pitch" in description:
                    pitches[time_stamp] = float(value)
                    if not first_pitch:
                        first_pitch = float(value)
                elif "ins_yaw" in description:
                    yaws[time_stamp] = float(value)
                elif "ins_roll" in description:
                    rolls[time_stamp] = float(value)
                elif "lat_lkt" in description:
                    lkt_latitudes[time_stamp] = float(value)
                elif "long_lkt" in description:
                    lkt_longitudes[time_stamp] = float(value)

        if lkt_latitudes:
            latitudes = lkt_latitudes
            longitudes = lkt_longitudes
        elif ins_latitudes:
            latitudes = ins_latitudes
            longitudes = ins_longitudes
        else:
            latitudes = gps_latitudes
            longitudes = gps_longitudes
        if pitches:
            pitches.update((x, -(y - first_pitch)) for x, y in pitches.items())
        return latitudes, longitudes, pitches, yaws, rolls

    def rotation(self, frame):
        time = frame * 1 / self.frame_rate
        if self.pitches:
            pitch = self.pitch_interpolation(time)
            yaw = self.yaw_interpolation(time)
            roll = self.roll_interpolation(time)
            pitch_matrix = utils.pitch_matrix(pitch)
            yaw_matrix = utils.yaw_matrix(yaw)
            roll_matrix = utils.roll_matrix(roll)
        else:
            pitch_matrix = np.identity(3)
            roll_matrix = np.identity(3)

            flag = False
            if len(self.stops) > 0:
                for stop in self.stops:
                    start = stop[0]
                    end = stop[-1]
                    if time > start and time < end:
                        index2 = self.times.index(next(x for x in self.times if x >= start))
                        if index2 == 0:
                            index2 = self.times.index(next(x for x in self.times if x >= end))
                            if index2 == len(self.times) - 1:
                                yaw_matrix = self.last_yaw_matrix
                                return pitch_matrix, yaw_matrix, roll_matrix
                            else:
                                index1 = index2 - 1
                        else:
                            index1 = index2 - 1
                        flag = True
                        break

            if not flag:
                try:
                    index2 = self.times.index(next(x for x in self.times if x > time))
                except StopIteration:
                    yaw_matrix = self.last_yaw_matrix
                    return pitch_matrix, yaw_matrix, roll_matrix
                if index2 is not None:
                    if index2 == 0:
                        index2 = 1
                        index1 = 0
                    else:
                        index1 = index2 - 1

            p2 = self.geo.lat_long_to_meter(self.latitudes[self.times[index1]], self.longitudes[self.times[index1]])
            p1 = self.geo.lat_long_to_meter(self.latitudes[self.times[index2]], self.longitudes[self.times[index2]])

            diff = np.subtract(p1, p2)
            if np.linalg.norm(diff) == 0:
                yaw_matrix = self.last_yaw_matrix
            else:
                dot_product = np.dot(diff / np.linalg.norm(diff), [0, 1])
                yaw = np.arccos(dot_product)
                yaw = math.degrees(yaw)
                if np.cross(diff, [0, 1, 0])[2] > 0:
                    yaw = -yaw
                yaw_matrix = utils.yaw_matrix(yaw)
                self.last_yaw_matrix = yaw_matrix
        return pitch_matrix, yaw_matrix, roll_matrix

    def position(self, frame):
        time = frame * 1 / self.frame_rate
        time = max(0.0, min(time, self.max_time))
        flag = False
        if len(self.stops) > 0:
            for stop in self.stops:
                start = stop[0]
                end = stop[-1]
                if time >= start and time <= end:
                    lat = self.latitudes[start]
                    long = self.longitudes[start]
                    flag = True
                    break
        if not flag:
            lat = self.latitudes_interpolation(time)
            long = self.longitudes_interpolation(time)
        try:
            elevation = self.geo.get_elevation(lat=lat, long=long)
        except UserWarning:
            elevation = 0
        x, y = self.geo.lat_long_to_meter(lat=lat, long=long)

        return np.array([[x], [y], [elevation]])

    def create_angle_plots(self, nr_frames):
        pitches = []
        yaws = []
        rolls = []
        for f in range(nr_frames):
            pitches.append(self.pitch_interpolation(f * 1 / self.frame_rate))
            yaws.append(self.yaw_interpolation(f * 1 / self.frame_rate))
            rolls.append(self.roll_interpolation(f * 1 / self.frame_rate))

        plt.figure()
        plt.subplot(311)
        plt.plot(pitches)
        plt.ylabel('pitch in °')
        plt.xlabel('frames')
        plt.subplot(312)
        plt.plot(yaws)
        plt.ylabel('yaw in °')
        plt.xlabel('frames')
        plt.subplot(313)
        plt.plot(rolls)
        plt.ylabel('rolls in °')
        plt.xlabel('frames')

        plt.show()

    def search_for_stops(self):
        if len(self.latitudes) == 0 or len(self.longitudes) == 0:
            return []

        lats = list(self.latitudes.items())
        lats.sort(key=lambda x: x[0])
        temp = list(zip(*lats))
        times = list(temp[0])
        lats = list(temp[1])
        longs = list(self.longitudes.items())
        longs.sort(key=lambda x: x[0])
        temp = list(zip(*longs))
        longs = list(temp[1])

        self.times = times

        packed_times = []
        lat_longs = list(zip(lats, longs))
        current_pack = []
        current_lat = lats[0]
        current_long = longs[0]

        for index, lat_long in enumerate(lat_longs):
            if lat_long[0] == current_lat and lat_long[1] == current_long:
                current_pack.append(times[index])
            else:
                packed_times.append(current_pack)
                current_lat = lat_long[0]
                current_long = lat_long[1]
                current_pack = [times[index]]

        packed_times.append(current_pack)
        if len(packed_times) < len(lats):
            self.stops = list(filter(lambda x: len(x) > 1, packed_times))
        else:
            self.stops = []
