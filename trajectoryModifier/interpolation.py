from scipy import interpolate, optimize
import numpy as np


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
    box1_list = [prb['box'][1] for prb in trajectory['positions_rotations_and_boxes'] if ('box' in prb and not (onlySpecified and not (('detected' in prb and prb['detected']) or ('specified' in prb and prb['specified']))))]
    box2_list = [prb['box'][2] for prb in trajectory['positions_rotations_and_boxes'] if ('box' in prb and not (onlySpecified and not (('detected' in prb and prb['detected']) or ('specified' in prb and prb['specified']))))]
    box3_list = [prb['box'][3] for prb in trajectory['positions_rotations_and_boxes'] if ('box' in prb and not (onlySpecified and not (('detected' in prb and prb['detected']) or ('specified' in prb and prb['specified']))))]

    if len(box_frame_list) < 2:
        return tck_pos, None, None

    tck_box_min, _ = interpolate.splprep([box0_list, box1_list, box_frame_list], s=smoothing_factor, k=min(len(box_frame_list)-1, 3))
    tck_box_max, _ = interpolate.splprep([box2_list, box3_list, box_frame_list], s=smoothing_factor, k=min(len(box_frame_list)-1, 3))
    return tck_pos, tck_box_min, tck_box_max


def interpolate_trajectory(trajectory):

    frame_dict = {prb['frame']: prb for prb in trajectory['positions_rotations_and_boxes'] if 'frame' in prb}
    if len(frame_dict.items()) <= 1:
        return trajectory

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
            pos = pos_at_time(pos_tck, frame)
            if not prb:
                prb = {"frame": frame,
                       "position": [float(pos[0]), float(pos[1])],
                       "confidence": 0.0}
            else:
                prb["position"] = [float(pos[0]), float(pos[1])]
            if box_min_tck and box_max_tck:
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
