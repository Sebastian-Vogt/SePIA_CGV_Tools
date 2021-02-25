import json
import detection as my_det
import cv2
import os
from itertools import takewhile
import utils
import time
import tkinter as tk
from tkinter import filedialog
from groundTruthData import GroundTruthJsonParser
import tracking as trk
import numpy as np
import motmetrics as mm
import progressbar
import sys

class_mapping = ["userDefined",
                 "car",
                 "truck",
                 "bus",
                 "bicycle",
                 "motorcycle",
                 "trailer",
                 "tram",
                 "train",
                 "caravan",
                 "agriculturalVehicle",
                 "constructionVehicle",
                 "emergencyVehicle",
                 "passiveVehicle",
                 "person",
                 "largeAnimal",
                 "smallAnimal"]

def main():
    root = tk.Tk()
    root.withdraw()

    in_path = filedialog.askdirectory()
    out_path = filedialog.askdirectory()

    detection_threshold = 0.4
    retina = my_det.RetinanetDetector("D:\\Dokumente\\Uni\\SePIA\\SePIA CGV Tools\\creator+modifier+calibration\\creator\\weights\\resnet50_csv_04_inference.h5", threshold=detection_threshold, video_size=(640, 480))
    retina2 = my_det.RetinanetDetector("D:\\Downloads\\resnet50_coco_best_v2.1.0.h5", threshold=detection_threshold, video_size=(640, 480))
    yolo = my_det.YoloDetector("D:\\Dokumente\\Uni\\SePIA\\SePIA CGV Tools\\creator+modifier+calibration\\creator\\weights\\yolov5x.pt", img_size=640, confidence_threshold=detection_threshold, iou_threshold=0.5)

    gt = GroundTruthJsonParser()

    os.makedirs(os.path.join(out_path, "groundtruths"), exist_ok = True)
    os.makedirs(os.path.join(out_path, "retina_trained"), exist_ok = True)
    os.makedirs(os.path.join(out_path, "retina"), exist_ok = True)
    os.makedirs(os.path.join(out_path, "yolo"), exist_ok = True)
    os.makedirs(os.path.join(out_path, "combined"), exist_ok = True)

    accumulators = {}
    accumulators['retina_trained'] = []
    accumulators['retina'] = []
    accumulators['yolo'] = []
    accumulators['combined'] = []
    names = []

    dirs = list(os.walk(in_path))

    outer_widgets = [
        'Testing folders: ', progressbar.SimpleProgress(),
        ' ', progressbar.Percentage(),
        ' ', progressbar.Bar(marker=progressbar.AnimatedMarker(fill='#')),
        ' ', progressbar.AdaptiveETA(),
        ' ', progressbar.AdaptiveTransferSpeed(unit="folder"),
    ]
    outer_bar = progressbar.ProgressBar(widgets=outer_widgets, max_value=len(dirs), redirect_stdout=True).start()

    for folder_nr, dir in enumerate(dirs):
        files = os.listdir(dir[0])
        if any([file.endswith(".avi") for file in files]) and any([file.endswith(".json") for file in files]):
            json_file = next(os.path.join(dir[0], file) for file in files if file.endswith(".json"))
            video_file = [os.path.join(dir[0], file) for file in files if file.endswith(".avi")]
            video_file.sort(key=lambda x: x.count("original"))
            video_file = video_file[0]

            case_name = dir[0].replace("\\", "/")
            pref = in_path.replace("\\", "/")
            case_name = case_name.replace(pref, "")
            case_name = case_name.replace("/", "_")

            gt_objects = gt.parse(json_path=json_file)
            with open(json_file) as json_f:
                json_dict = json.load(json_f)
                init_completeness = json_dict["completeness"]["comp_in_fst_frame"]
                completeness_changes = json_dict["completeness"]["changes"]

            method_list = []
            method_list.append({
                'name': 'retina_trained',
                'tracker': trk.SortTracker(retina, None, max_age=30, min_occurrences=2),
                'accumulator': mm.MOTAccumulator(auto_id=True),
                'detections': {}
            })
            method_list.append({
                'name': 'retina',
                'tracker': trk.SortTracker(retina2, None, max_age=30, min_occurrences=2),
                'accumulator': mm.MOTAccumulator(auto_id=True),
                'detections': {}
            })
            method_list.append({
                'name': 'yolo',
                'tracker': trk.SortTracker(None, yolo, max_age=30, min_occurrences=2),
                'accumulator': mm.MOTAccumulator(auto_id=True),
                'detections': {}
            })
            method_list.append({
                'name': 'combined',
                'tracker': trk.SortTracker(retina, yolo, max_age=30, min_occurrences=2),
                'accumulator': mm.MOTAccumulator(auto_id=True),
                'detections': {}
            })

            cap = cv2.VideoCapture(video_file)

            inner_widgets = [
                'Tracking: ', progressbar.SimpleProgress(),
                ' ', progressbar.Percentage(),
                ' ', progressbar.Bar(marker=progressbar.AnimatedMarker(fill='#')),
                ' ', progressbar.AdaptiveETA(),
                ' ', progressbar.AdaptiveTransferSpeed(unit="frames"),
            ]
            inner_bar = progressbar.ProgressBar(widgets=inner_widgets,
                                                max_value=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                                                redirect_stdout=True).start()

            frame_nr = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                frame_nr += 1
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                inner_bar.update(frame_nr)

                for method in method_list:
                    method['tracker'].track_frame(frame, frame_nr)
                    method['detections'][frame_nr] = method['tracker'].dets
                    if 'retina' in method['name'] and not 'trained' in method['name']:
                        dets = []
                        for det in method['tracker'].dets:
                            cls = det[5]
                            if cls in [0, 1, 2, 3, 5, 6, 7, 15, 16, 17]:
                                if cls == 0:
                                    cls = 14
                                elif cls == 1:
                                    cls = 4
                                elif cls == 2:
                                    cls = 1
                                elif cls == 3:
                                    cls = 5
                                elif cls == 5:
                                    cls = 3
                                elif cls == 6:
                                    cls = 7
                                elif cls == 7:
                                    cls = 2
                                elif cls == 15 or cls == 16:
                                    cls = 16
                                elif cls == 17:
                                    cls = 15
                                det[5] = cls
                                dets.append(det)
                        method['detections'][frame_nr] = dets

            inner_bar.finish()
            width = cap.get(3)
            height = cap.get(4)

            for method in method_list:
                method['tracker'].convert_tracks_to_list()

            inner_widgets = [
                'Further processing: ', progressbar.SimpleProgress(),
                ' ', progressbar.Percentage(),
                ' ', progressbar.Bar(marker=progressbar.AnimatedMarker(fill='#')),
                ' ', progressbar.AdaptiveETA(),
                ' ', progressbar.AdaptiveTransferSpeed(unit="frames"),
            ]
            inner_bar = progressbar.ProgressBar(widgets=inner_widgets,
                                                max_value=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                                                redirect_stdout=True).start()

            for frame in range(1, frame_nr + 1, 1):

                visible_gt_id_list = []
                visible_gt_box_list = []
                visible_gt_type_list = []
                for obj in gt_objects:
                    box = obj.get_box(frame)
                    if box is not None:
                        visible_gt_id_list.append(obj.id)
                        visible_gt_box_list.append(box)
                        visible_gt_type_list.append(obj.type)

                visible_gt_id_list, visible_gt_box_list, visible_gt_type_list = filter_boxes(visible_gt_id_list, visible_gt_box_list, visible_gt_type_list, width, height)

                objects = [class_mapping[obj[1]] + " " + str(obj[0][0]) + " " + str(obj[0][1]) + " " + str(obj[0][2]) + " " + str(obj[0][3]) + "\n" for obj in zip(visible_gt_box_list, visible_gt_type_list)]


                if is_complete(frame, init_completeness, completeness_changes):
                    with open(os.path.join(out_path, "groundtruths") + "/" + case_name + "_" + str(frame) + ".txt", "w") as txt_file:
                        txt_file.writelines(objects)

                    for method in method_list:
                        visible_track_id_list = []
                        visible_track_box_list = []
                        visible_track_type_list = []
                        for track in method['tracker'].tracks:
                            box = track.get_box(frame)
                            if box is not None:
                                visible_track_id_list.append(track.id)
                                visible_track_box_list.append(box)
                                visible_track_type_list.append(track.type)

                        visible_track_id_list, visible_track_box_list, visible_track_type_list = filter_boxes(visible_track_id_list, visible_track_box_list, visible_track_type_list, width, height)

                        iou_matrix = mm.distances.iou_matrix(visible_track_box_list, visible_gt_box_list)
                        method['accumulator'].update(visible_gt_id_list, visible_track_id_list, iou_matrix)

                        detections = method['detections'][frame]
                        detections = [class_mapping[int(det[5])] + " " + str(det[4]) + " " + str(int(round(det[0]))) + " " + str(int(round(det[1]))) + " " + str(int(round(det[2]))) + " " + str(int(round(det[3]))) + "\n" for det in detections]
                        with open(os.path.join(out_path, method["name"]) + "/" + case_name + "_" + str(frame) + ".txt", "w") as txt_file:
                            txt_file.writelines(detections)

                inner_bar.update(frame)

            inner_bar.finish()

            for method in method_list:
                accumulators[method['name']].append(method['accumulator'])

            names.append(dir[1])

        outer_bar.update(folder_nr)

    original_stdout = sys.stdout

    for name, ao in accumulators.items():
        mh = mm.metrics.create()
        summary = mh.compute_many(
            ao,
            metrics=mm.metrics.motchallenge_metrics,
            names=names,
            generate_overall=True)

        strsummary = mm.io.render_summary(
            summary,
            formatters=mh.formatters,
            namemap=mm.io.motchallenge_metric_names
        )
        print(name + ":")
        print(strsummary)
        print("\n\n")

        with open(os.path.join(out_path, name + ".txt"), "w") as out_file:
            sys.stdout = out_file
            print(strsummary)
        sys.stdout = original_stdout









'''

        completness = int(image[0][6])

        if completness == 1:
            if os.path.isfile(image[0][0].replace(".jpg", ".png")):
                with open(os.path.join(args.output_path, "groundtruths") + "/" + txt_name + ".txt", "w") as txt_file:
                    txt_file.writelines(objects)

                img = cv2.imread(image[0][0].replace(".jpg", ".png"))
                filtered_bboxes, filtered_scores, filtered_labels, label_frame, score_frame = retina.detect(img)
                filtered_bboxes2, filtered_scores2, filtered_labels2, label_frame2, score_frame2 = retina2.detect(img)
                yolo_dets = yolo.detect(img)

                detections = [class_mapping[int(l)] + " " + str(s) + " " + str(int(round(b[0]))) + " " + str(int(round(b[1]))) + " " + str(int(round(b[2]))) + " " + str(int(round(b[3]))) + "\n" for l, s, b in zip(filtered_labels, filtered_scores, filtered_bboxes)]
                with open(os.path.join(args.output_path, "retina_trained_detections") + "/" + txt_name + ".txt", "w") as txt_file:
                    txt_file.writelines(detections)

                detections = []
                for bx, scr, l in zip(filtered_bboxes2, filtered_scores2, filtered_labels2):
                    cls = int(l)
                    if cls in [0, 1, 2, 3, 5, 6, 7, 15, 16, 17]:
                        if cls == 0:
                            cls = 14
                        elif cls == 1:
                            cls = 4
                        elif cls == 2:
                            cls = 1
                        elif cls == 3:
                            cls = 5
                        elif cls == 5:
                            cls = 3
                        elif cls == 6:
                            cls = 7
                        elif cls == 7:
                            cls = 2
                        elif cls == 15 or cls == 16:
                            cls = 16
                        elif cls == 17:
                            cls = 15
                        detections.append(class_mapping[cls] + " " + str(scr) + " " + str(int(round(bx[0]))) + " " + str(int(round(bx[1]))) + " " + str(int(round(bx[2]))) + " " + str(int(round(bx[3]))) + "\n")
                with open(os.path.join(args.output_path, "retina_detections") + "/" + txt_name + ".txt", "w") as txt_file:
                    txt_file.writelines(detections)

                detections = [class_mapping[int(det[5])] + " " + str(det[4]) + " " + str(int(round(det[0]))) + " " + str(int(round(det[1]))) + " " + str(int(round(det[2]))) + " " + str(int(round(det[3]))) + "\n" for det in yolo_dets]
                with open(os.path.join(args.output_path, "yolo_detections")+"/"+txt_name+".txt", "w") as txt_file:
                    txt_file.writelines(detections)

                dets = [[box[0], box[1], box[2], box[3], score, cls] for box, score, cls in zip(filtered_bboxes, filtered_scores, filtered_labels)]
                finalDets = []
                for yoloDet in yolo_dets:
                    for det in dets:
                        if utils.box_iou(yoloDet[:4], det[:4]) > 0.4:
                            dets.remove(det)
                            break
                    finalDets.append(yoloDet)
                finalDets.extend(dets)

                detections = [class_mapping[int(det[5])] + " " + str(det[4]) + " " + str(int(round(det[0]))) + " " + str(int(round(det[1]))) + " " + str(int(round(det[2]))) + " " + str(int(round(det[3]))) + "\n" for det in finalDets]
                with open(os.path.join(args.output_path, "combined_detections") + "/" + txt_name + ".txt", "w") as txt_file:
                    txt_file.writelines(detections)

            else:
                pass

        print("Processed file " + str(fid) + " of " + str(len(images)) + " ("+str(100*(fid/len(images)))+"%)")
'''

def filter_boxes(id_list, box_list, type_list, video_width, video_height):
    filtered_list = list(filter(lambda x: x[0][2] > 0 and x[0][3] > 0, zip(box_list, id_list, type_list)))
    if len(filtered_list) > 0:
        box_list, id_list, type_list = list(zip(*filtered_list))
        box_list = [[int(min(min(video_width, max(0, box[0])), min(video_width, max(0, box[2])))),
                                int(min(min(video_height, max(0, box[1])), min(video_height, max(0, box[3])))),
                                int(max(max(0, min(video_width, box[0])), max(0, min(video_width, box[2])))),
                                int(max(max(0, min(video_height, box[1])), max(0, min(video_height, box[3]))))]
                               for box in box_list]
        filtered_list = list(filter(lambda x: x[0][2] - x[0][0] > 0 and x[0][3] - x[0][1] > 0,
                                    zip(box_list, id_list, type_list)))
        if len(filtered_list) > 0:
            box_list, id_list, type_list = list(zip(*filtered_list))
    return list(id_list), list(box_list), list(type_list)


def is_complete(frame, init, changes):
    i = 0
    for i, c in enumerate(changes):
        if frame >= c:
            break
    i = i % 2
    return not (bool(init) != (i > 0))

if __name__ == "__main__":
    main()
