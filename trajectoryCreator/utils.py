import cv2
import numpy as np
import math


def box_iou(a, b):
    '''
    Helper funciton to calculate the ratio between intersection and the union of
    two boxes a and b
    a[0], a[1], a[2], a[3] <-> left, up, right, bottom
    '''

    w_intsec = np.maximum(0, (np.minimum(a[2], b[2]) - np.maximum(a[0], b[0])))
    h_intsec = np.maximum(0, (np.minimum(a[3], b[3]) - np.maximum(a[1], b[1])))
    s_intsec = w_intsec * h_intsec
    s_a = (a[2] - a[0]) * (a[3] - a[1])
    s_b = (b[2] - b[0]) * (b[3] - b[1])

    result = float(s_intsec) / (s_a + s_b - s_intsec)
    return result


def get_rotation_matix_between_two_vectors(a, b):
    a = a.transpose() / np.linalg.norm(a)
    b = b.transpose() / np.linalg.norm(b)
    rotMat = np.identity(3)
    v = np.cross(a, b, axis=0)
    v_mat = np.array([[0, -v[2][0], v[1][0]], [v[2][0], 0, -v[0][0]], [-v[1][0], v[1][0], 0]])
    rotMat = np.add(rotMat, v_mat)
    s = (1 + np.inner(a, b))
    v_mat = np.dot(v_mat, v_mat) / s
    return np.add(rotMat, v_mat)


def pitch_matrix(pitch):
    pitch = math.radians(pitch)
    pitch_matrix = np.array([
        [math.cos(pitch), 0, math.sin(pitch)],
        [0, 1, 0],
        [-math.sin(pitch), 0, math.cos(pitch)]
    ])
    return pitch_matrix


def yaw_matrix(yaw):
    yaw = math.radians(yaw)
    yaw_matrix = np.array([
        [math.cos(yaw), -math.sin(yaw), 0],
        [math.sin(yaw), math.cos(yaw), 0],
        [0, 0, 1]
    ])
    return yaw_matrix


def roll_matrix(roll):
    roll = math.radians(roll)
    roll_matrix = np.array([
        [1, 0, 0],
        [0, math.cos(roll), -math.sin(roll)],
        [0, math.sin(roll), math.cos(roll)]
    ])
    return roll_matrix


def rotation_matrix_from_euler_angles(pitch, yaw, roll):
    rotation_matrix = np.dot(yaw_matrix(yaw), np.dot(pitch_matrix(pitch), roll_matrix(roll)))
    return rotation_matrix


def draw_box_with_labels(img, bbox_cv2, box_color=(0, 255, 255), labels=[], label_color=(0, 255, 255)):
    '''
    Helper funciton for drawing the bounding boxes and the labels
    bbox_cv2 = [left, top, right, bottom]
    '''
    left, top, right, bottom = bbox_cv2[0], bbox_cv2[1], bbox_cv2[2], bbox_cv2[3]

    # Draw the bounding box
    cv2.rectangle(img, (left, top), (right, bottom), box_color, 4)

    if len(labels) > 0:
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_size = 0.7
        font_color = (0, 0, 0)
        # Draw a filled box on top of the bounding box (as the background for the labels)
        cv2.rectangle(img, (left - 2, top - len(labels) * 20 - 10), (right + 2, top), label_color, -1, 1)

        # Output the labels that show the x and y coordinates of the bounding box center.
        for i, text in enumerate(labels):
            cv2.putText(img, text, (left, top - i * 20 - 5), font, font_size, font_color, 1, cv2.LINE_AA)

    return img


def hsv_to_rgb(h, s, v):
    if s == 0.0: v *= 255; return (v, v, v)
    i = int(h * 6.)  # XXX assume int() truncates!
    f = (h * 6.) - i;
    p, q, t = int(255 * (v * (1. - s))), int(255 * (v * (1. - s * f))), int(255 * (v * (1. - s * (1. - f))));
    v *= 255;
    i %= 6
    if i == 0: return (v, t, p)
    if i == 1: return (q, v, p)
    if i == 2: return (p, v, t)
    if i == 3: return (p, q, v)
    if i == 4: return (t, p, v)
    if i == 5: return (v, p, q)


def get_label_colors(number):
    step = 1.0/number
    colors = []
    for i in range(number):
        color = hsv_to_rgb(step*i, 0.9, 0.9)
        colors.append(color)
    return colors


def create_label_legend(size):
    class_dict = {0: "user defined",
                  1: "car",
                  2: "truck",
                  3: "bus",
                  4: "bicycle",
                  5: "motorcycle",
                  6: "trailer",
                  7: "tram",
                  8: "train",
                  9: "caravan",
                  10: "agr. veh.",
                  11: "con. veh.",
                  12: "em. veh.",
                  13: "pas. veh.",
                  14: "person",
                  15: "lrg. anim.",
                  16: "sml. anim."
                  }

    label_legend = np.full((size[1], 240, 3), 255)
    label_legend_height = int(size[1] / len(class_dict.items()))
    for i, text in class_dict.items():
        color = tuple(reversed(get_label_colors(12)[i%12]))
        label_legend[i * label_legend_height:(i + 1) * label_legend_height, 200:240, 0] = np.full(
            (label_legend_height, 40), color[0])
        label_legend[i * label_legend_height:(i + 1) * label_legend_height, 200:240, 1] = np.full(
            (label_legend_height, 40), color[1])
        label_legend[i * label_legend_height:(i + 1) * label_legend_height, 200:240, 2] = np.full(
            (label_legend_height, 40), color[2])
        label_legend = label_legend.astype(np.uint8)
        label_legend = cv2.putText(label_legend, text, (5, (i + 1) * label_legend_height), cv2.FONT_HERSHEY_SIMPLEX,
                                   0.5, (0, 0, 0))

    return label_legend


def write_track_videos(objects, in_video, tracks_video_writer=None, labels_video_writer=None):
    label_legend = create_label_legend((int(in_video.get(3)), int(in_video.get(4))))
    frame_nr = 0
    while in_video.isOpened():
        ret, frame = in_video.read()
        if not ret:
            break
        frame_nr += 1

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        label_image = frame.copy()
        track_image = frame.copy()

        for i, obj in enumerate(objects):
            track = obj.track
            label = track.type
            box = track.get_box(frame_nr)

            if box is None or frame_nr > track.last_detected_frame:  # filtering all tracks that are not defined in that frame
                continue
            label_color = tuple(reversed(get_label_colors(12)[label % 12]))
            label_image = cv2.rectangle(np.ascontiguousarray(label_image), (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), label_color, 3)
            track_color = tuple(reversed(get_label_colors(12)[i % 12]))
            track_image = cv2.rectangle(np.ascontiguousarray(track_image), (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), track_color, 3)

        label_image = np.concatenate((label_image, label_legend), axis=1)
        if labels_video_writer:
            labels_video_writer.write(label_image)
        if tracks_video_writer:
            tracks_video_writer.write(track_image)
    if labels_video_writer:
        labels_video_writer.release()
    if tracks_video_writer:
        tracks_video_writer.release()


def write_relative_pos_video(objects, in_video, relative_positions_video):
    frame_nr = 0
    while in_video.isOpened():
        ret, frame = in_video.read()
        if not ret:
            break
        frame_nr += 1
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        for i, obj in enumerate(objects):
            try:
                position = obj.relative_positions[frame_nr]
                box = obj.track.get_box(frame_nr)
                box = list(map(int, map(round, box)))
                if box is not None:
                    labels = [("%.2f" % position[1][0]) + "m in front", ("%.2f" % position[0][0]) + "m right"]
                    track_color = tuple(reversed(get_label_colors(12)[i % 12]))
                    frame = draw_box_with_labels(frame, box, box_color=track_color, labels=labels, label_color=track_color)
            except KeyError:
                continue
        relative_positions_video.write(frame)
    relative_positions_video.release()


def show_on_map(map, coordinates, color, geo):
    coordinates = [geo.meter_to_lat_long(x[0][0], x[1][0]) for x in coordinates]
    lat_values = [x[0] for x in coordinates]
    long_values = [y[1] for y in coordinates]

    # scatter method of map object
    # scatter points on the google map
    color_string = '#%02x%02x%02x' % color
    map.scatter(lat_values, long_values, color_string, size=.5, marker=False)
    # darker_color = color.lstrip('#')
    # darker_color = tuple(int(color[i:i + 2], 16) * 0.75 for i in (0, 2, 4))
    darker_color = tuple([int(item * 0.75) for item in color])
    darker_color_string = '#%02x%02x%02x' % darker_color
    # Plot method Draw a line in
    # between given coordinates
    map.plot(lat_values, long_values, darker_color_string, edge_width=10)


def find(f, seq):
    """Return first item in sequence where f(item) == True."""
    for item in seq:
        if f(item):
            return item
    return None


def zipDicts(*dcts):
    """Basically a zip method for any number of provided dicts"""
    if len(dcts) == 0:
        return []
    for i in set(dcts[0]).intersection(*dcts[1:]):
        yield (i,) + tuple(d[i] for d in dcts)


def mergeDicts(dict1, dict2):
   ''' Merge dictionaries and keep values of common keys in list'''
   dict3 = {**dict1, **dict2}
   for key, value in dict3.items():
       if key in dict1 and key in dict2:
               dict3[key] = [value] + (dict1[key] if isinstance(dict1[key], list) else [dict1[key]])
   return dict3