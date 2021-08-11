from scipy import interpolate


def interpolate_trajectory(trajectory, interpolate_missing_frames=False):

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
            if interpolate_missing_frames:
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

    lats = []
    longs = []
    pos_frames = []

    xmins = []
    xmaxs = []
    ymins = []
    ymaxs = []
    box_frames = []


    for prb in trajectory["positions_rotations_and_boxes"]:
        try:
            if 'position' in prb :
                lats.append(prb['position'][0])
                longs.append(prb['position'][1])
                pos_frames.append(prb['frame'])
            if 'box' in prb:
                xmins.append(prb['box'][0])
                ymins.append(prb['box'][1])
                xmaxs.append(prb['box'][2])
                ymaxs.append(prb['box'][3])
                box_frames.append(prb['frame'])
        except KeyError:
            continue

    prbs = []
    box_degree = len(box_frames) - 1
    pos_degree = len(pos_frames)-1
    if pos_degree >= 0 and box_degree >= 0 and len(frames) > 0:
        pos_degree = "zero" if pos_degree == 0 else ("slinear" if pos_degree == 1 else ("quadratic" if pos_degree == 2 else ("cubic")))
        box_degree = "zero" if box_degree == 0 else ("slinear" if box_degree == 1 else ("quadratic" if box_degree == 2 else ("cubic")))
        lat_inter = interpolate.interp1d(pos_frames, lats, kind=pos_degree, fill_value="extrapolate")
        long_inter = interpolate.interp1d(pos_frames, longs, kind=pos_degree, fill_value="extrapolate")
        xmin_inter = interpolate.interp1d(box_frames, xmins, kind=box_degree, fill_value="extrapolate")
        ymin_inter = interpolate.interp1d(box_frames, ymins, kind=box_degree, fill_value="extrapolate")
        xmax_inter = interpolate.interp1d(box_frames, xmaxs, kind=box_degree, fill_value="extrapolate")
        ymax_inter = interpolate.interp1d(box_frames, ymaxs, kind=box_degree, fill_value="extrapolate")

    for frame in frames:
        lat = lat_inter(frame).item()
        long = long_inter(frame).item()
        pos = [lat, long]
        prb = {"frame": frame,
               "position": [pos[0], pos[1]],
               "confidence": 0.0}
        xmin = xmin_inter(frame).item()
        ymin = ymin_inter(frame).item()
        xmax = xmax_inter(frame).item()
        ymax = ymax_inter(frame).item()
        box = [xmin, ymin, xmax, ymax]
        prb["box"] = box
        prbs.append(prb)

    return prbs


def smooth_trajectory(trajectory):
    frame_list = [prb['frame'] for prb in trajectory['positions_rotations_and_boxes'] if 'position' in prb]
    if len(frame_list) <= 1:
        return trajectory

    lats = []
    longs = []
    frames = []
    for prb in trajectory['positions_rotations_and_boxes']:
        if "position" in prb:
            lats.append(prb["position"][0])
            longs.append(prb["position"][1])
            frames.append(prb["frame"])

    degree = len(frames) - 1
    if degree >= 0:
        degree = 5 if degree > 5 else degree
    lat_spl = interpolate.UnivariateSpline(frames, lats, k=degree)
    long_spl = interpolate.UnivariateSpline(frames, longs, k=degree)
    lat_spl.set_smoothing_factor(0.5)
    long_spl.set_smoothing_factor(0.5)

    for prb in trajectory['positions_rotations_and_boxes']:
        lat = lat_spl(prb["frame"]).item()
        long = long_spl(prb["frame"]).item()
        pos = [lat, long]
        prb["position"] = pos

    return trajectory
