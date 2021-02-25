import json
import tkinter as tk
from tkinter import filedialog
from pyproj import _datadir, datadir
from pyproj import Transformer, CRS
import math
import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.ndimage import gaussian_filter1d
import matplotlib.pyplot as plt
from numpy import linalg as LA

degree2meter = Transformer.from_crs(CRS("EPSG:4326"), CRS("EPSG:32633"))
meter2degree = Transformer.from_crs(CRS("EPSG:32633"), CRS("EPSG:4326"))


def find(f, seq):
    """Return first item in sequence where f(item) == True."""
    for item in seq:
        if f(item):
            return item
    return None


def calculate_opponent_approach(obj, self):
    if len(obj['positions_rotations_and_boxes']) <= 1:
        return

    for i, pbr in enumerate(obj['positions_rotations_and_boxes']):
        frame = pbr['frame']
        object_direction = pbr['rotation']
        object_direction = (object_direction + 360) % 360
        self_pbr = find(lambda x: x['frame'] == frame, self['positions_rotations_and_boxes'])
        if self_pbr == None:
            pbr['opponent_approach'] = 'Other'
            continue
        self_direction = self_pbr['rotation']
        self_direction = (self_direction + 360) % 360
        relative_direction = (object_direction - self_direction)

        if -45 < relative_direction <= 45:
            pbr['opponent_approach'] = 'Front'

            normal = [math.sin(self_direction-90), math.cos(self_direction-90)]
            x0, y0 = degree2meter.transform(pbr['position'][0],pbr['position'][1])
            x1, y1 = degree2meter.transform(self_pbr['position'][0], self_pbr['position'][1])
            dist = abs(normal[0] * (x1-x0) + normal[1] * (y1-y0)) / math.sqrt(normal[0] ** 2 + normal[1] ** 2)
            if dist >= 3:
                pbr['opponent_approach'] = 'LateralSameDirection'

        elif -135 < relative_direction <= -45:
            pbr['opponent_approach'] = 'CrossLeft'  # from left to right
        elif 45 < relative_direction <= 135:
            pbr['opponent_approach'] = 'CrossRight'
        else:
            pbr['opponent_approach'] = 'Oncoming'

    smooth_label(obj, 'opponent_approach')
    return


def calculate_ego_maneuver_type(self, standing_kernel_radius=5, standing_radius=.5, curvature_threshold=0.04, curvature_kernel_radius=5):
    spec_field = 'ego_specification' if self['id'] == 0 else 'opponent_specification'

    if len(self['positions_rotations_and_boxes']) == 0:
        return
    if len(self['positions_rotations_and_boxes']) == 1:
        self['positions_rotations_and_boxes'][0][spec_field] = 'StandStill'
        if self['id'] == 'self':
            self['positions_rotations_and_boxes'][0]['ego_maneuver_type'] = 'StandStill'
        return

    xs = np.array([round(degree2meter.transform(pbr['position'][0], pbr['position'][1])[0], 2) for pbr in self['positions_rotations_and_boxes']])
    xs = gaussian_filter1d(xs, curvature_kernel_radius)
    ys = np.array([round(degree2meter.transform(pbr['position'][0], pbr['position'][1])[1], 2) for pbr in self['positions_rotations_and_boxes']])
    ys = gaussian_filter1d(ys, curvature_kernel_radius)
    t = np.arange(xs.shape[0])

    xs1 = np.gradient(xs)
    xs1 = gaussian_filter1d(xs1, curvature_kernel_radius)
    xs2 = np.gradient(xs1)
    xs2 = gaussian_filter1d(xs2, curvature_kernel_radius)
    ys1 = np.gradient(ys)
    ys1 = gaussian_filter1d(ys1, curvature_kernel_radius)
    ys2 = np.gradient(ys1)
    ys2 = gaussian_filter1d(ys2, curvature_kernel_radius)
    curvatures = (xs1 * ys2 - ys1 * xs2) / (.001+np.power(xs1 ** 2 + ys1 ** 2, 1.5))

    '''
    dev1 = xs1.reshape((len(xs1), 1))
    dev1 = np.concatenate((dev1, ys1.reshape((len(ys1), 1))), axis=-1)
    dev2 = xs2.reshape((len(xs2), 1))
    dev2 = np.concatenate((dev2, ys2.reshape((len(ys2), 1))), axis=-1)
    norm = LA.norm(dev2, axis=-1)
    devs = np.concatenate((dev1, dev2), axis=-1)
    signs = [np.sign(x[0]*x[3]-x[1]*x[2]) for x in devs]
    vcurvatures = np.multiply(norm, signs)

    fx = UnivariateSpline(t, xs, k=5)
    fy = UnivariateSpline(t, ys, k=5)
    sxs1 = fx.derivative(1)(t)
    sxs2 = fx.derivative(2)(t)
    sys1 = fy.derivative(1)(t)
    sys2 = fy.derivative(2)(t)
    scurvatures = (sxs1 * sys2 - sys1 * sxs2) / (.001+np.power(sxs1 ** 2 + sys1 ** 2, 1.5))

    sdev1 = sxs1.reshape((len(sxs1), 1))
    sdev1 = np.concatenate((sdev1, sys1.reshape((len(sys1), 1))), axis=-1)
    sdev2 = sxs2.reshape((len(sxs2), 1))
    sdev2 = np.concatenate((sdev2, sys2.reshape((len(sys2), 1))), axis=-1)
    snorm = LA.norm(sdev2, axis=-1)
    sdevs = np.concatenate((sdev1, sdev2), axis=-1)
    ssigns = [np.sign(x[0] * x[3] - x[1] * x[2]) for x in sdevs]
    svcurvatures = np.multiply(snorm, ssigns)

    fig, axs = plt.subplots(10, 1, constrained_layout=True)
    fig.set_size_inches(10, 30)
    fig.suptitle(self['id'], fontsize=16)
    window = None
    axs[0].plot(t, xs, 'o', t, fx(t), '-')
    axs[0].set_title('x')
    if window:
        axs[0].set_xlim(window)
    axs[1].plot(t, xs1, 'o', t, sxs1, '-')
    axs[1].set_title('x\'')
    if window:
        axs[1].set_xlim(window)
    axs[2].plot(t, xs2, 'o', t, sxs2, '-')
    axs[2].set_title('x\'\'')
    if window:
        axs[2].set_xlim(window)
    axs[3].plot(t, ys, 'o', t, fy(t), '-')
    axs[3].set_title('y')
    if window:
        axs[3].set_xlim(window)
    axs[4].plot(t, ys1, 'o', t, sys1, '-')
    axs[4].set_title('y\'')
    if window:
        axs[4].set_xlim(window)
    axs[5].plot(t, ys2, 'o', t, sys2, '-')
    axs[5].set_title('y\'\'')
    if window:
        axs[5].set_xlim(window)
    axs[6].plot(t, curvatures, '-')
    axs[6].set_title('curvatures diffs')
    if window:
        axs[6].set_xlim(window)
    axs[7].plot(t, scurvatures, '-')
    axs[7].set_title('curvatures spline')
    axs[7].set_xlim(window)
    axs[8].plot(t, vcurvatures, '-')
    axs[8].set_title('vector curvature diffs')
    axs[8].set_xlim(window)
    axs[9].plot(t, svcurvatures, '-')
    axs[9].set_title('vector curvature spline')
    axs[9].set_xlim(window)
    plt.show()
    '''

    for i in range(len(self['positions_rotations_and_boxes'])):
        frame = self['positions_rotations_and_boxes'][i]['frame']
        pbrs = get_pbrs_in_frame_range(frame - standing_kernel_radius, frame + standing_kernel_radius, self)

        xs = []
        ys = []
        for pbr in pbrs:
            pos = pbr['position']
            x, y = degree2meter.transform(pos[0], pos[1])
            xs.append(x)
            ys.append(y)
        center_x = sum(xs) / len(xs)
        center_y = sum(ys) / len(ys)
        filtered_list = list(
            filter(lambda e: math.sqrt(pow(e[0] - center_x, 2) + pow(e[1] - center_y, 2)) > standing_radius,
                   zip(xs, ys)))

        if len(filtered_list) == 0:
            self['positions_rotations_and_boxes'][i][spec_field] = 'StandStill'
            if self['id'] == 'self':
                self['positions_rotations_and_boxes'][i]['ego_maneuver_type'] = 'StandStill'
        else:
            if abs(curvatures[i]) < curvature_threshold:
                self['positions_rotations_and_boxes'][i][spec_field] = 'Forward'
                if self['id'] == 'self':
                    self['positions_rotations_and_boxes'][i]['ego_maneuver_type'] = 'FollowRoad'
            else:
                if np.sign(curvatures[i]) < 0:
                    self['positions_rotations_and_boxes'][i][spec_field] = 'ForwardRight'
                else:
                    self['positions_rotations_and_boxes'][i][spec_field] = 'ForwardLeft'
                if self['id'] == 'self':
                    self['positions_rotations_and_boxes'][i]['ego_maneuver_type'] = 'DriveThroughCurve'

    if self['id'] == 'self':
        smooth_label(self, 'ego_maneuver_type')
    smooth_label(self, spec_field)
    return


def get_pbrs_in_frame_range(starting_frame, end_frame, obj):
    pbrs = []
    for pbr in obj['positions_rotations_and_boxes']:
        if starting_frame <= pbr['frame'] <= end_frame:
            pbrs.append(pbr)
    return pbrs


def smooth_label(obj, label, kernel_radius=5):
    for current_pbr in obj['positions_rotations_and_boxes']:
        pbrs = get_pbrs_in_frame_range(current_pbr["frame"] - kernel_radius, current_pbr["frame"] + kernel_radius, obj)
        approaches = []
        for pbr in pbrs:
            approaches.append(pbr[label])
        most = max(set(approaches), key=approaches.count)
        current_pbr[label] = most


def main():
    root = tk.Tk()
    root.withdraw()

    json_file_path = filedialog.askopenfilename(title="Select CSV File...",
                                                filetypes=(("JSON Files", "*.json"), ("all files", "*.*")))

    with open(json_file_path) as json_file:
        json_data = json.load(json_file)

    for obj in json_data:
        if obj['id'] == 0:
            self = obj
            calculate_ego_maneuver_type(self)
            maneuvers = []
            specifications = []
            for pbr in obj['positions_rotations_and_boxes']:
                maneuvers.append(pbr['ego_maneuver_type'])
                specifications.append(pbr['ego_specification'])
            print(maneuvers)
            maneuvers = set(maneuvers)
            print(maneuvers)
            print(specifications)
            specifications = set(specifications)
            print(specifications)
            print("\n")
            break

    for obj in json_data:
        if obj['id'] == 0:
            continue
        calculate_opponent_approach(obj, self)
        calculate_ego_maneuver_type(obj)
        specifications = []
        approaches = []
        for pbr in obj['positions_rotations_and_boxes']:
            approaches.append(pbr['opponent_approach'])
            specifications.append(pbr['opponent_specification'])
        print(obj['id'])
        print(approaches)
        approaches = set(approaches)
        print(approaches)
        print(specifications)
        specifications = set(specifications)
        print(specifications)
        print("\n")


    #with open(json_file_path, 'w') as json_file:
        #json.dump(json_data, json_file, indent=4)


if __name__ == "__main__":
    main()
