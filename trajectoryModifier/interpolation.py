from scipy import interpolate, optimize
import numpy as np
import pandas as pd


def eval(u, t, tck):
    return np.array(interpolate.splev(u, tck)).flatten()[2] - t


def pos_at_time(tck, t):
    root = optimize.root_scalar(eval, args=(t, tck), x0=0, x1=1, method="secant").root
    return np.array(interpolate.splev(root, tck)).flatten()


def estimate_splines(trajectory, smoothing_factor=0, onlySpecified=True):
    pos_frame_list = [prb['frame'] for prb in trajectory['positions_rotations_and_boxes'] if ('position' in prb and not (onlySpecified and not (('detected' in prb and prb['detected']) or ('specified' in prb and prb['specified']))))]
    lat_list = [prb['position'][0] for prb in trajectory['positions_rotations_and_boxes'] if ('position' in prb and not (onlySpecified and not (('detected' in prb and prb['detected']) or ('specified' in prb and prb['specified']))))]
    long_list = [prb['position'][1] for prb in trajectory['positions_rotations_and_boxes'] if ('position' in prb and not (onlySpecified and not (('detected' in prb and prb['detected']) or ('specified' in prb and prb['specified']))))]

    if len(pos_frame_list) < 2:
        print("At least 2 frames must exist for interpolation.")
        return None, None, None

    tck_pos, _ = interpolate.splprep([lat_list, long_list, pos_frame_list], s=smoothing_factor, k=min(len(pos_frame_list)-1, 3))

    box_frame_list = [prb['frame'] for prb in trajectory['positions_rotations_and_boxes'] if ('box' in prb and not (onlySpecified and not (('detected' in prb and prb['detected']) or ('specified' in prb and prb['specified']))))]
    box0_list = [prb['box'][0] for prb in trajectory['positions_rotations_and_boxes'] if ('box' in prb and not (onlySpecified and not (('detected' in prb and prb['detected']) or ('specified' in prb and prb['specified']))))]
    boy1_list = [prb['box'][1] for prb in trajectory['positions_rotations_and_boxes'] if ('box' in prb and not (onlySpecified and not (('detected' in prb and prb['detected']) or ('specified' in prb and prb['specified']))))]
    box2_list = [prb['box'][2] for prb in trajectory['positions_rotations_and_boxes'] if ('box' in prb and not (onlySpecified and not (('detected' in prb and prb['detected']) or ('specified' in prb and prb['specified']))))]
    box3_list = [prb['box'][3] for prb in trajectory['positions_rotations_and_boxes'] if ('box' in prb and not (onlySpecified and not (('detected' in prb and prb['detected']) or ('specified' in prb and prb['specified']))))]

    if len(box_frame_list) < 2:
        return tck_pos, None, None

    tck_box_min, _ = interpolate.splprep([box0_list, boy1_list, box_frame_list], s=smoothing_factor, k=min(len(box_frame_list)-1, 3))
    tck_box_max, _ = interpolate.splprep([box2_list, box3_list, box_frame_list], s=smoothing_factor, k=min(len(box_frame_list)-1, 3))
    return tck_pos, tck_box_min, tck_box_max


def interpolate_trajectory(trajectory, interpolate_boxes=True, pandas=True):

    frame_dict = {prb['frame']: prb for prb in trajectory['positions_rotations_and_boxes'] if 'frame' in prb}
    if len(frame_dict.items()) <= 1:
        return trajectory

    if pandas:
        frames = list(range(min(list(frame_dict.keys())), max(list(frame_dict.keys()))+1))
        data = []
        degree = -1
        for frame in frames:
            try:
                prb = frame_dict[frame]
            except KeyError:
                prb = None
            if not prb or not ('position' in prb and (('detected' in prb and prb['detected']) or ('specified' in prb and prb['specified']))):
                lat = np.nan
                long = np.nan
            else:
                lat = prb['position'][0]
                long = prb['position'][1]
                degree += 1
            if not prb or not ('box' in prb and (('detected' in prb and prb['detected']) or ('specified' in prb and prb['specified']))):
                xmin = np.nan
                ymin = np.nan
                xmax = np.nan
                ymax = np.nan
            else:
                xmin = prb['box'][0]
                ymin = prb['box'][1]
                xmax = prb['box'][2]
                ymax = prb['box'][3]
            data.append([lat, long, xmin, ymin, xmax, ymax])
        series = pd.DataFrame(data, columns=['lat','long','xmin','ymin','xmax','ymax'], index=frames)
        if degree >= 5:
            kw = dict(method='spline', order=5, axis=0, fill_value='extrapolate')
        elif degree >= 2:
            kw = dict(method='spline', order=degree, axis=0, fill_value='extrapolate')
        elif degree == 1:
            kw = dict(method='linear', axis=0, fill_value='extrapolate')
        else:
            kw = dict(method='nearest', axis=0, fill_value='extrapolate')
        series = series.interpolate(**kw).iloc[::-1].interpolate(**kw).iloc[::-1]
    else:
        pos_tck, box_min_tck, box_max_tck = estimate_splines(trajectory)

    for frame in range(min(list(frame_dict.keys())), max(list(frame_dict.keys()))+1):
        try:
            prb = frame_dict[frame]
        except KeyError:
            prb = None

        cond1 = not prb or not 'position' in prb
        if prb:
            cond2 = ('detected' in prb and prb['detected'])
            cond3 = ('specified' in prb and prb['specified'])
            cond4 = (cond2 or cond3)
        if cond1 or not cond4:
            if pandas:
                pos = [series.at[frame, 'lat'], series.at[frame, 'long']]
            else:
                pos = pos_at_time(pos_tck, frame)

            if interpolate_boxes:
                if pandas:
                    prb["box"] = [float(series.at[frame, 'xmin']), float(series.at[frame, 'ymin']), float(series.at[frame, 'xmax']), float(series.at[frame, 'ymax'])]
                if not pandas and box_min_tck and box_max_tck:
                    box_min = pos_at_time(box_min_tck, prb["frame"])
                    box_max = pos_at_time(box_max_tck, prb["frame"])
                    prb["box"] = [float(box_min[0]), float(box_min[1]), float(box_max[0]), float(box_max[1])]

            frame_dict[frame] = prb
    prbs = sorted(frame_dict.values(),key=lambda prb: prb['frame'])

    trajectory['positions_rotations_and_boxes'] = prbs

    return trajectory


def extrapolate_points(trajectory, frames):

    pos_tck, box_min_tck, box_max_tck = estimate_splines(trajectory, onlySpecified=False)

    prbs = []
    for frame in frames:
        pos = pos_at_time(pos_tck, frame)
        prb = {"frame": frame,
               "position": [float(pos[0]), float(pos[1])],
               "confidence": 0.0}
        if box_min_tck and box_max_tck:
            box_min = pos_at_time(box_min_tck, frame)
            box_max = pos_at_time(box_max_tck, frame)
            prb["box"] = [float(box_min[0]), float(box_min[1]), float(box_max[0]), float(box_max[1])]
        prbs.append(prb)

    return prbs


def smooth_trajectory(trajectory):
    frame_list = [prb['frame'] for prb in trajectory['positions_rotations_and_boxes'] if 'position' in prb]
    if len(frame_list) <= 1:
        return trajectory

    pos_tck, _, _ = estimate_splines(trajectory, smoothing_factor=0.000000001)

    for prb in trajectory['positions_rotations_and_boxes']:
        pos = pos_at_time(pos_tck, prb["frame"])
        prb["position"] = [float(pos[0]), float(pos[1])]

    return trajectory
