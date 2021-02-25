import json
import itertools

class_list = ["user defined",
              "car",
              "truck",
              "bus",
              "bicycle",
              "motorcycle",
              "trailer",
              "tram",
              "train",
              "caravan",
              "agricultural vehicle",
              "construction vehicle",
              "emergency vehicle",
              "passive vehicle",
              "person",
              "large animal",
              "small animal"]


class Object:
    id_iter = itertools.count(start=1)

    def __init__(self, type, appearances):
        self.type = class_list.index(type) if type in class_list else 0
        self.appearances = appearances
        self.id = next(Object.id_iter)
        self.last_detected_frame = max([a.stop for a in self.appearances])

    def get_box(self, frame_nr):
        for appearance in self.appearances:
            box = appearance.get_box(frame_nr=frame_nr)
            if box is not None:
                return box
        return None


class Appearance:
    def __init__(self, start, stop, x_min_definitions, x_max_definitions, y_min_definitions, y_max_definitions):
        self.start = start
        self.stop = stop
        self.x_min_definitions = x_min_definitions
        self.x_max_definitions = x_max_definitions
        self.y_min_definitions = y_min_definitions
        self.y_max_definitions = y_max_definitions

    def get_box(self, frame_nr):

        if frame_nr > self.stop or frame_nr < self.start or len(self.x_min_definitions) < 1 or len(
                self.x_max_definitions) < 1 or len(self.y_min_definitions) < 1 or len(self.y_max_definitions) < 1:
            return None

        x_min = None
        x_max = None
        y_min = None
        y_max = None

        if len(self.x_min_definitions) == 1:
            x_min = self.x_min_definitions[0].value
        else:
            for current_definition, next_definition in zip(self.x_min_definitions[:-1], self.x_min_definitions[1:]):
                if current_definition.frame == frame_nr:
                    x_min = current_definition.value
                    break
                if next_definition.frame == frame_nr:
                    x_min = next_definition.value
                    break
                if next_definition.frame < frame_nr:
                    x_min = next_definition.value
                    continue

                alpha = (frame_nr - current_definition.frame) / (next_definition.frame - current_definition.frame)
                x_min = alpha * next_definition.value + (1 - alpha) * current_definition.value
                break

        if len(self.x_max_definitions) == 1:
            x_max = self.x_max_definitions[0].value
        else:
            for current_definition, next_definition in zip(self.x_max_definitions[:-1], self.x_max_definitions[1:]):
                if current_definition.frame == frame_nr:
                    x_max = current_definition.value
                    break
                if next_definition.frame == frame_nr:
                    x_max = next_definition.value
                    break
                if next_definition.frame < frame_nr:
                    x_max = next_definition.value
                    continue

                alpha = (frame_nr - current_definition.frame) / (next_definition.frame - current_definition.frame)
                x_max = alpha * next_definition.value + (1 - alpha) * current_definition.value
                break

        if len(self.y_min_definitions) == 1:
            y_min = self.y_min_definitions[0].value
        else:
            for current_definition, next_definition in zip(self.y_min_definitions[:-1], self.y_min_definitions[1:]):
                if current_definition.frame == frame_nr:
                    y_min = current_definition.value
                    break
                if next_definition.frame == frame_nr:
                    y_min = next_definition.value
                    break
                if next_definition.frame < frame_nr:
                    y_min = next_definition.value
                    continue

                alpha = (frame_nr - current_definition.frame) / (next_definition.frame - current_definition.frame)
                y_min = alpha * next_definition.value + (1 - alpha) * current_definition.value
                break

        if len(self.y_max_definitions) == 1:
            y_max = self.y_max_definitions[0].value
        else:
            for current_definition, next_definition in zip(self.y_max_definitions[:-1], self.y_max_definitions[1:]):
                if current_definition.frame == frame_nr:
                    y_max = current_definition.value
                    break
                if next_definition.frame == frame_nr:
                    y_max = next_definition.value
                    break
                if next_definition.frame < frame_nr:
                    y_max = next_definition.value
                    continue

                alpha = (frame_nr - current_definition.frame) / (next_definition.frame - current_definition.frame)
                y_max = alpha * next_definition.value + (1 - alpha) * current_definition.value
                break

        return [x_min, y_min, x_max, y_max]


class Definition:
    def __init__(self, frame, value):
        self.frame = frame
        self.value = value


class GroundTruthJsonParser:
    def __init__(self):
        return

    def parse(self, json_path, videoOffset=0):
        with open(json_path) as json_file:
            print("load json...")
            json_dict = json.load(json_file)
            print("finished loading")

        try:
            number_of_frames = int(json_dict["nr_frames"])
        except KeyError:

            object_dict = {}
            for frame_nr, frame in enumerate(json_dict.values(), 1):
                frame_boxes = frame["b"]

                for box in frame_boxes.values():
                    obj_id = int(box["i"])
                    x_min_definition = Definition(frame=frame_nr-videoOffset, value=box["x"])
                    x_max_definition = Definition(frame=frame_nr-videoOffset, value=box["x"] + box["w"])
                    y_min_definition = Definition(frame=frame_nr-videoOffset, value=box["y"])
                    y_max_definition = Definition(frame=frame_nr-videoOffset, value=box["y"] + box["h"])
                    apprearance = Appearance(start=frame_nr-videoOffset, stop=frame_nr-videoOffset, x_min_definitions=[x_min_definition],
                                             x_max_definitions=[x_max_definition], y_min_definitions=[y_min_definition],
                                             y_max_definitions=[y_max_definition])
                    try:
                        obj = object_dict[obj_id]
                    except KeyError:
                        obj = Object(type=class_list[int(box["l"])], appearances=[apprearance])
                        object_dict[obj_id] = obj
                    else:
                        obj.appearances.append(apprearance)
            objects = list(object_dict.values())
        else:
            print(str(number_of_frames) + " frames found")
            json_object_list = json_dict["objects"]

            print(str(len(json_object_list)) + " objects found")

            print("starting object parsing")
            objects = []
            for counter, json_object in enumerate(json_object_list):
                print("handling object " + str(counter + 1) + " of " + str(len(json_object_list)))

                object_type = json_object["type"]
                print("object type:\t" + object_type)
                json_appearance_list = json_object["appearences"]
                print("object appears " + str(len(json_appearance_list)) + " times")
                appearance_list = []
                for apprearance in json_appearance_list:
                    start_frame = apprearance["fst_frame_idx"] - videoOffset
                    stop_frame = apprearance["lst_frame_idx"] - videoOffset

                    x_max_value_list = apprearance["x_max_values"]
                    x_max_definitions = [Definition(frame=x_max_dict["frame_idx"]-videoOffset, value=x_max_dict["value"]) for
                                         x_max_dict in x_max_value_list]
                    x_min_value_list = apprearance["x_min_values"]
                    x_min_definitions = [Definition(frame=x_min_dict["frame_idx"]-videoOffset, value=x_min_dict["value"]) for
                                         x_min_dict in x_min_value_list]
                    y_max_value_list = apprearance["y_max_values"]
                    y_max_definitions = [Definition(frame=y_max_dict["frame_idx"]-videoOffset, value=y_max_dict["value"]) for
                                         y_max_dict in y_max_value_list]
                    y_min_value_list = apprearance["y_min_values"]
                    y_min_definitions = [Definition(frame=y_min_dict["frame_idx"]-videoOffset, value=y_min_dict["value"]) for
                                         y_min_dict in y_min_value_list]

                    if stop_frame > 0:
                        appearance_list.append(
                            Appearance(start=start_frame, stop=stop_frame, x_min_definitions=x_min_definitions,
                                       x_max_definitions=x_max_definitions, y_min_definitions=y_min_definitions,
                                       y_max_definitions=y_max_definitions))

                print("appearances parsed")
                if len(appearance_list) > 0:
                    objects.append(Object(type=object_type, appearances=appearance_list))

        return objects
