import cv2
import numpy as np
from keras_retinanet import models
from keras_retinanet.utils.gpu import setup_gpu
from numpy import random

import utils

import torch
from models.experimental import attempt_load
from yolo_utils.datasets import letterbox
from yolo_utils.general import (check_img_size, non_max_suppression, apply_classifier, scale_coords, xyxy2xywh, plot_one_box, strip_optimizer, set_logging)
from yolo_utils.torch_utils import select_device, load_classifier, time_synchronized



class RetinanetDetector(object):
    def __init__(self, modelPath, threshold, video_size=None):
        self.obj_boxes = []
        self.threshold = threshold
        self.video_size = video_size

        # use this to change which GPU to use
        gpu = "0,"

        # set the modified tf session as backend in keras
        setup_gpu(gpu)

        # load retinanet model
        self.model = models.load_model(modelPath, backbone_name='resnet50')

        if self.video_size is not None:

            self.score_color_map_legend = np.zeros((10, 1, 3), np.uint8)
            for i in range(1, 256):
                column = np.full((10, 1, 3), i)
                self.score_color_map_legend = np.concatenate((self.score_color_map_legend, column), axis=1)

            self.score_color_map_legend = self.score_color_map_legend.astype(np.uint8)
            self.score_color_map_legend = cv2.applyColorMap(self.score_color_map_legend, cv2.COLORMAP_COOL)

            self.label_legend = utils.create_label_legend(self.video_size)

    def detect(self, image):
        boxes, scores, labels = self.model.predict_on_batch(np.expand_dims(image, axis=0))
        boxes = np.squeeze(boxes)
        labels = np.squeeze(labels)
        scores = np.squeeze(scores)

        filtered_bboxes, filtered_scores, filtered_labels = [], [], []
        for box, score, label in zip(boxes, scores, labels):
            if score < self.threshold:
                continue
            filtered_bboxes.append(box)
            filtered_scores.append(score)
            filtered_labels.append(label)

        if self.video_size is None:
            return filtered_bboxes, filtered_scores, filtered_labels
        else:
            label_image = image.copy()
            score_image = image.copy()
            for box, score, label in zip(filtered_bboxes, filtered_scores, filtered_labels):
                color = tuple(reversed(utils.get_label_colors(12)[label%12]))
                label_image = cv2.rectangle(label_image, (box[0], box[1]), (box[2], box[3]), color, 2)

                score = np.array([[[score, score, score]]], dtype=float)
                score -= self.threshold
                score *= 255 * 1 / (1 - self.threshold)
                score = score.astype(np.uint8)
                color = cv2.applyColorMap(score, cv2.COLORMAP_COOL)[0, 0]
                score_image = cv2.rectangle(score_image, (box[0], box[1]), (box[2], box[3]),
                                            (color[0].item(), color[1].item(), color[2].item()), 2)

            label_image = np.concatenate((label_image, self.label_legend), axis=1)

            score_image[0:10, 170:426] = self.score_color_map_legend
            score_image = cv2.putText(score_image, str(self.threshold), (155, 13), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                      (0, 0, 0))
            score_image = cv2.putText(score_image, str(1.0), (422, 13), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
            return filtered_bboxes, filtered_scores, filtered_labels, label_image, score_image


class YoloDetector:
    def __init__(self, weights, img_size=640, confidence_threshold=0.4, iou_threshold=0.5):
        self.weights = weights
        self.img_size = img_size
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold

        # Initialize
        set_logging()
        self.device = select_device('')
        self.half = self.device.type != 'cpu'  # half precision only supported on CUDA

        # Load model
        self.model = attempt_load(weights, map_location=self.device)  # load FP32 model
        self.img_size = check_img_size(img_size, s=self.model.stride.max())  # check img_size

        if self.half:
            self.model.half()  # to FP16

        # Get names and colors
        self.names = self.model.module.names if hasattr(self.model, 'module') else self.model.names
        self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(self.names))]

        # Run inference
        img0 = torch.zeros((1, 3, self.img_size, self.img_size), device=self.device)  # init img
        _ = self.model(img0.half() if self.half else img0) if self.device.type != 'cpu' else None  # run once


    def detect(self, input_image):
        image = np.copy(input_image)

        # Padded resize
        img = letterbox(image, new_shape=self.img_size)[0]

        # Convert
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)

        img = torch.from_numpy(img).to(self.device)
        img = img.half() if self.half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        t1 = time_synchronized()
        pred = self.model(img, augment=False)[0]

        # Apply NMS
        pred = non_max_suppression(pred, self.confidence_threshold, self.iou_threshold)

        dets = []
        # Process detections
        for i, det in enumerate(pred):  # detections per image
            if det is not None and len(det):
                # Rescale boxes from img_size to input size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], image.shape).round()
                for *xyxy, conf, cls in reversed(det):
                    if cls in [0, 1, 2, 3, 5, 6, 7, 15, 16, 17]:#[1, 2, 3, 4, 6, 7, 8, 16, 17, 18]:
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
                        dets.append([int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3]), conf.item(), cls])

        return dets


class DummyDetector(object):
    def __init__(self, objects):
        self.objects = objects
        self.video_size = None
        return

    def detect(self, frame):
        boxes = list(filter(lambda x: x is not None, [obj.get_box(frame) for obj in self.objects]))
        labels = list(filter(lambda x: x is not None,
                             [obj.type if obj.get_box(frame) is not None else None for obj in self.objects]))
        return boxes, [1.0 for box in boxes], labels
