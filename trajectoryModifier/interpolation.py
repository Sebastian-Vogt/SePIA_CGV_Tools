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


def interpolate_trajectory(trajectory, interpolate_boxes=True):

    frame_dict = {prb['frame']: prb for prb in trajectory['positions_rotations_and_boxes'] if 'frame' in prb}
    if len(frame_dict.items()) <= 1:
        return trajectory

    frames = list(range(min(list(frame_dict.keys())), max(list(frame_dict.keys()))+1))
    lats = []
    longs = []
    pos_frames = []
    pos_frames_2_interp = []

    xmins = []
    xmaxs = []
    ymins =[]
    ymaxs = []
    box_frames = []
    box_frames_2_interp = []
    for frame in frames:
        try:
            prb = frame_dict[frame]
            if ('position' in prb and (
                    ('detected' in prb and prb['detected']) or ('specified' in prb and prb['specified']))):
                lats.append(prb['position'][0])
                longs.append(prb['position'][1])
                pos_frames.append(frame)
            else:
                pos_frames_2_interp.append(frame)
            if ('box' in prb and (
                    ('detected' in prb and prb['detected']) or ('specified' in prb and prb['specified']))):
                xmins.append(prb['box'][0])
                ymins.append(prb['box'][1])
                xmaxs.append(prb['box'][2])
                ymaxs.append(prb['box'][3])
                box_frames.append(frame)
            else:
                box_frames_2_interp.append(frame)
        except KeyError:
            pos_frames_2_interp.append(frame)
            box_frames_2_interp.append(frame)
            continue

    pos_degree = len(pos_frames)-1
    if pos_degree >= 0 and len(pos_frames_2_interp) > 0:
        pos_degree = "zero" if pos_degree == 0 else ("slinear" if pos_degree == 1 else ("quadratic" if pos_degree == 2 else ("cubic")))
        lat_inter = interpolate.interp1d(pos_frames, lats, kind=pos_degree, fill_value="extrapolate")
        long_inter = interpolate.interp1d(pos_frames, longs, kind=pos_degree, fill_value="extrapolate")

        for frame in pos_frames_2_interp:
            lat = lat_inter(frame).item()
            long = long_inter(frame).item()
            pos = [lat, long]
            try:
                prb = frame_dict[frame]
                prb["position"] = pos
            except KeyError:
                prb = {"frame": frame,
                       "position": pos,
                       "confidence": 0.0}
            frame_dict[frame] = prb

    box_degree = len(box_frames) - 1
    if box_degree >= 0 and len(box_frames_2_interp) > 0:
        box_degree = "zero" if box_degree == 0 else (
            "slinear" if box_degree == 1 else ("quadratic" if box_degree == 2 else ("cubic")))
        xmin_inter = interpolate.interp1d(box_frames, xmins, kind=box_degree, fill_value="extrapolate")
        ymin_inter = interpolate.interp1d(box_frames, ymins, kind=box_degree, fill_value="extrapolate")
        xmax_inter = interpolate.interp1d(box_frames, xmaxs, kind=box_degree, fill_value="extrapolate")
        ymax_inter = interpolate.interp1d(box_frames, ymaxs, kind=box_degree, fill_value="extrapolate")

        for frame in box_frames_2_interp:
            xmin = xmin_inter(frame).item()
            ymin = ymin_inter(frame).item()
            xmax = xmax_inter(frame).item()
            ymax = ymax_inter(frame).item()
            box = [xmin, ymin, xmax, ymax]
            try:
                prb = frame_dict[frame]
                prb["box"] = box
            except KeyError:
                prb = {"frame": frame,
                       "box": box,
                       "confidence": 0.0}
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
