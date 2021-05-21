import json
import tkinter as tk
from tkinter import filedialog
import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from flaskwebgui import FlaskUI
import cv2
import sys
import objectBehaviorClassifier as obc
import interpolation as inter
import logging
import msaccessdb
import pcmV5
import geography as geo
from pyproj import Transformer, CRS
import math
from recalibration import calculate_optimal_parameter_set
import pyodbc
import numpy as np

app = Flask(__name__)
ui = FlaskUI(app)
json_trajectories_dict = []
data_dir = ""
fps = 0
length = 0
width = 0
height = 0
geoHandler = None

@app.before_first_request
def setup_logging():
    if not app.debug:
        # In production mode, add log handler to sys.stderr.
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/images'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/recalibrate", methods=['POST'])
def recalibrate():
    d2m = Transformer.from_crs(CRS("EPSG:4326"), CRS("EPSG:32633"))
    trajectories = request.get_json()
    trajectories = check_rotations_for_trajectories(trajectories)
    trajectories.sort(key=lambda x: x['id'])
    ego = trajectories[0]
    ego_pos = {pbr['frame']: pbr['position'] for pbr in ego["positions_rotations_and_boxes"]}
    ego_rot = {pbr['frame']: pbr['rotation'] for pbr in ego["positions_rotations_and_boxes"]}
    objects = trajectories[1:]
    image_positions = []
    relative_world_positions = []
    weights = []
    for obj in objects:
        for pbr in obj["positions_rotations_and_boxes"]:
            if ("is_interpolated" in pbr) or (not "position" in pbr) or (not "box" in pbr) or (not pbr["frame"] in ego_pos) or (not pbr["frame"] in ego_rot):
                continue
            p_ego_x, p_ego_y = d2m.transform(ego_pos[pbr["frame"]][0], ego_pos[pbr["frame"]][1])
            inv_yaw_ego = -ego_rot[pbr["frame"]] /180.0 * math.pi
            p_obj_x, p_obj_y = d2m.transform(pbr["position"][0], pbr["position"][1])
            p_rel_x, p_rel_y = (p_obj_x - p_ego_x, p_obj_y - p_ego_y)
            p_rel_x, p_rel_y = (p_rel_x * math.cos(inv_yaw_ego) - p_rel_y * math.sin(inv_yaw_ego),
                                p_rel_x * math.sin(inv_yaw_ego) + p_rel_y * math.cos(inv_yaw_ego))
            relative_world_positions.append([p_rel_x, p_rel_y])

            weights.append(1.0/math.sqrt(p_rel_x**2 + p_rel_y**2))

            box = pbr["box"]
            image_positions.append([(box[2] + box[0])/2, box[3]])
    calculate_optimal_parameter_set(ego, data_dir+"/camera_extrinsics.json", image_positions, relative_world_positions, weights)
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/interpolate", methods=['POST'])
def interpolate_trajectory():
    trajectory = request.get_json()
    interpolated_trajectory = inter.interpolate_trajectory(trajectory)
    check_rotations_for_trajectory(interpolated_trajectory)
    return jsonify(interpolated_trajectory)


@app.route("/smooth", methods=['POST'])
def smooth_trajectory():
    trajectory = request.get_json()
    smoothed_trajectory = inter.smooth_trajectory(trajectory)
    check_rotations_for_trajectory(smoothed_trajectory)
    return jsonify(smoothed_trajectory)


@app.route("/extrapolate", methods=['POST'])
def extrapolate_trajectory():
    request_dict = request.get_json()
    trajectory = request_dict["trajectory"]
    frames = request_dict["frames"]
    extrapolated_points = inter.extrapolate_points(trajectory, frames)
    trajectory["positions_rotations_and_boxes"].extend(extrapolated_points)
    trajectory["positions_rotations_and_boxes"].sort(key=lambda x: x["frame"])
    check_rotations_for_trajectory(trajectory)
    return jsonify(trajectory)


@app.route('/')
@app.route('/index')
def index():
    trajanPath = next((data_dir + "\\" + x for x in os.listdir(data_dir) if x.endswith('.trajan')), None)
    with open(trajanPath) as json_file:
        json_trajectories_dict = json.load(json_file)
        nr_frames = max([max([pbr["frame"] for pbr in traj["positions_rotations_and_boxes"]]) for traj in json_trajectories_dict["trajectories"] if len(traj["positions_rotations_and_boxes"])])
        trajectories = [inter.interpolate_trajectory(t) for t in json_trajectories_dict["trajectories"]]
        trajectories = check_rotations_for_trajectories(trajectories)
        response = render_template('index.html', nr_frames=nr_frames, trajectories=trajectories)
    return response


@app.route("/trajectories", methods=['GET', 'POST'])
def handle_trajectories():
    if request.method == "GET":
        trajanPath = next((data_dir + "\\" + x for x in os.listdir(data_dir) if x.endswith('.trajan')), None)
        with open(trajanPath) as json_file:
            json_trajectories_dict = json.load(json_file)
        json_trajectories_list = list(map(lambda t: inter.interpolate_trajectory(t), json_trajectories_dict["trajectories"]))
        json_trajectories_list = check_rotations_for_trajectories(json_trajectories_list)
        return jsonify(json_trajectories_list)
    else:
        json_to_store = request.get_json()
        json_to_store = check_rotations_for_trajectories(json_to_store)
        trajanPath = next((data_dir + "\\" + x for x in os.listdir(data_dir) if x.endswith('.trajan')), None)
        with open(trajanPath) as json_file:
            json_trajectories_dict = json.load(json_file)
        with open(trajanPath, 'w') as json_file:
            for obj in json_to_store:
                if len(obj['positions_rotations_and_boxes']) == 0:
                    continue
                if obj['id'] == 0:
                    obc.calculate_ego_maneuver_type(obj)
                else:
                    ego = next((x for x in json_to_store if x['id'] == 0), None)
                    obc.calculate_ego_maneuver_type(obj)
                    obc.calculate_opponent_approach(obj, ego)
            json_trajectories_dict["trajectories"] = json_to_store
            json.dump(json_trajectories_dict, json_file, indent=4)

            exporter = pcmV5.PCMExporter(data_dir, json_trajectories_dict["caseID"])

            egoStartPos = next((next((pbr["position"] for pbr in trajectory["positions_rotations_and_boxes"] if pbr["frame"] == 0), None) for trajectory in json_to_store if trajectory["id"] == 0), None)
            if egoStartPos:
                try:
                    elevation = geoHandler.get_elevation(egoStartPos[0], egoStartPos[1])
                except UserWarning:
                    elevation = 0
                egoStartPos.append(elevation)
            else:
                egoStartPos = [0, 0, 0]
            exporter.writeGlobalTable(json_trajectories_dict["startTime"], egoStartPos, len(json_trajectories_dict["trajectories"]))
            exporter.writeParticipantTable(json_to_store)
            exporter.writeDynamicsTable(json_to_store, geoHandler)
            exporter.writeSpecificationTable(json_to_store)

        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/videoinformation", methods=['GET'])
def get_video_information():
    if request.method == "GET":
        my_dict = {"fps": fps,
                   "length": length,
                   "width": width,
                   "height": height}
        return jsonify(my_dict)


def check_rotations_for_trajectories(trajectories):
    pass
    for t in trajectories:
        check_rotations_for_trajectory(t)
    return trajectories


def check_rotations_for_trajectory(t):
    counter = 0
    for pbr in t["positions_rotations_and_boxes"]:
        try:
            rotation = pbr["rotation"]
        except KeyError:
            counter += 1
    if counter > 0:
        if counter == len(pbr):
            for pbr in t["positions_rotations_and_boxes"]:
                pbr["rotation"] = 0.0
        else:
            fix_rotations(t)
    pass


def fix_rotations(t):
    positions = {pbr["frame"]:pbr["position"] for pbr in t["positions_rotations_and_boxes"]}

    k = list(positions.keys())
    rads = []

    if len(k) > 1:
        d2m = Transformer.from_crs(CRS("EPSG:4326"), CRS("EPSG:32633"))

        positions = {frame: list(d2m.transform(position[0], position[1])) for frame, position in positions.items()}

        p = np.array(list(positions.values()))
        p = p.reshape((len(p), -1))
        while p.shape[1] > 2:
            p = np.delete(p, 2, axis=1)
        grads = np.gradient(p, axis=0)
        norms = np.linalg.norm(grads, axis=1)
        prev = None
        to_change = []
        for i, n in enumerate(norms):
            if n == 0:
                if prev:
                    norms[i] = norms[prev]
                    grads[i] = grads[prev]
                else:
                    to_change.append(i)
            else:
                prev = i
                if to_change:
                    for j in to_change:
                        norms[j] = norms[i]
                        grads[j] = grads[i]
        div = np.array([[1, 1] if n.item() == 0 else [n.item(), n.item()] for n in norms.flatten()])
        grads = np.divide(grads, div)

        rads = np.arccos(np.dot(grads, [0, 1]))

    for i, rad in enumerate(rads):
        t["positions_rotations_and_boxes"][i]["rotation"] = rad / math.pi * 180 * -np.sign(grads[i][0])


def main():
    global json_trajectories_dict, data_dir, fps, width, height, length, geoHandler
    root = tk.Tk()
    root.withdraw()

    geoHandler = geo.GeoHandler([
        "static\\tiles\\n50_e011_1arc_v3.tif",
        "static\\tiles\\n50_e012_1arc_v3.tif",
        "static\\tiles\\n50_e013_1arc_v3.tif",
        "static\\tiles\\n50_e014_1arc_v3.tif",
        "static\\tiles\\n50_e015_1arc_v3.tif",
        "static\\tiles\\n51_e011_1arc_v3.tif",
        "static\\tiles\\n51_e012_1arc_v3.tif",
        "static\\tiles\\n51_e013_1arc_v3.tif",
        "static\\tiles\\n51_e014_1arc_v3.tif",
        "static\\tiles\\n51_e015_1arc_v3.tif"
    ])

    data_dir = filedialog.askdirectory()
    video_file = next((data_dir + "\\" + x for x in os.listdir(data_dir) if x.endswith('.avi')), None)
    trajan_file = next((data_dir + "\\" + x for x in os.listdir(data_dir) if x.endswith('.trajan')), None)

    if not video_file or not trajan_file:
        sys.exit(
            "Either there is no original video (only numbers before '.avi') or no '.trajan' file in the provided folder.")

    if os.path.exists("static/videos/egovideo.mp4"):
        os.remove("static/videos/egovideo.mp4")

    in_video = cv2.VideoCapture(video_file)
    fps = int(in_video.get(cv2.CAP_PROP_FPS))
    width = int(in_video.get(3))
    height = int(in_video.get(4))
    length = int(in_video.get(cv2.CAP_PROP_FRAME_COUNT))
    out_video = cv2.VideoWriter("static/videos/egovideo.mp4", cv2.VideoWriter_fourcc('h','2','6','4'), fps, (width, height))

    while in_video.isOpened():
        ret, frame = in_video.read()
        if ret == True:
            out_video.write(frame)
        else:
            break
    out_video.release()

    ui.run()


if __name__ == "__main__":
    main()
