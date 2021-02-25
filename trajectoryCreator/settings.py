import os
import json


class SettingsLoader:

    def __init__(self):
        self.settings_file_path = os.path.dirname(os.path.realpath(__file__)) + "/static/config/config.json"
        self.load()
        return

    '''
    loads settings from file
    '''
    def load(self):
        if os.path.isfile(self.settings_file_path):
            with open(self.settings_file_path) as json_file:
                json_dict = json.load(json_file)
                self.set(json_dict)
        else:
            self.geoTiffPaths = []
            self.carFilePath = ""
            self.carAssignmentFilePath = ""
            self.detectorPath = ""
            self.yoloPath = ""
            self.minOccurrences = 2
            self.maxAge = 30
            self.simThreshold = 0.3
            self.detThreshold = 0.75
            self.trackLabelVideo = False
            self.trackIdVideo = False
            self.relativeDistanceVideo = False
            self.poolSize = 4
            self.concurrentGPUProcesses = 1

    '''
    getter for settings (returns json dict)
    '''
    def get(self):
        json_dict = {
            "geoTiffPaths": self.geoTiffPaths,
            "carFilePath": self.carFilePath,
            "carAssignmentFilePath": self.carAssignmentFilePath,
            "detectorPath": self.detectorPath,
            "yoloPath":self.yoloPath,
            "minOccurrences": int(self.minOccurrences),
            "maxAge": int(self.maxAge),
            "simThreshold": float(self.simThreshold),
            "detThreshold": float(self.detThreshold),
            "trackLabelVideo": self.trackLabelVideo,
            "trackIdVideo": self.trackIdVideo,
            "relativeDistanceVideo": self.relativeDistanceVideo,
            "poolSize": int(self.poolSize),
            "concurrentGPUProcesses": int(self.concurrentGPUProcesses)
        }
        return json_dict

    '''
    store settings to file
    '''
    def store(self):
        json_dict = self.get()
        with open(self.settings_file_path, 'w') as json_file:
            json.dump(json_dict, json_file, indent=4)
        return

    '''
    setter for elements from given json dict. If keys are not in dict -> sets default values
    '''
    def set(self, json_dict):
        if "geoTiffPaths" in json_dict:
            if isinstance(json_dict["geoTiffPaths"], str):
                self.geoTiffPaths = json_dict["geoTiffPaths"].split(",")
            else:
                self.geoTiffPaths = json_dict["geoTiffPaths"]
        else:
            self.geoTiffPaths = []
        if "carFilePath" in json_dict:
            self.carFilePath = json_dict["carFilePath"]
        else:
            self.carFilePath = ""
        if "carAssignmentFilePath" in json_dict:
            self.carAssignmentFilePath = json_dict["carAssignmentFilePath"]
        else:
            self.carAssignmentFilePath = ""
        if "detectorPath" in json_dict:
            self.detectorPath = json_dict["detectorPath"]
        else:
            self.detectorPath = ""
        if "yoloPath" in json_dict:
            self.yoloPath = json_dict["yoloPath"]
        else:
            self.yoloPath = ""
        if "minOccurrences" in json_dict:
            self.minOccurrences = int(json_dict["minOccurrences"])
        else:
            self.minOccurrences = 2
        if "maxAge" in json_dict:
            self.maxAge = int(json_dict["maxAge"])
        else:
            self.maxAge = 30
        if "simThreshold" in json_dict:
            self.simThreshold = float(json_dict["simThreshold"])
        else:
            self.simThreshold = 0.3
        if "detThreshold" in json_dict:
            self.detThreshold = float(json_dict["detThreshold"])
        else:
            self.detThreshold = 0.75
        if "trackLabelVideo" in json_dict:
            self.trackLabelVideo = json_dict["trackLabelVideo"]
        else:
            self.trackLabelVideo = False
        if "trackIdVideo" in json_dict:
            self.trackIdVideo = json_dict["trackIdVideo"]
        else:
            self.trackIdVideo = False
        if "relativeDistanceVideo" in json_dict:
            self.relativeDistanceVideo = json_dict["relativeDistanceVideo"]
        else:
            self.relativeDistanceVideo = False
        if "poolSize" in json_dict:
            self.poolSize = int(json_dict["poolSize"])
        else:
            self.poolSize = 4
        if "concurrentGPUProcesses" in json_dict:
            self.concurrentGPUProcesses = int(json_dict["concurrentGPUProcesses"])
        else:
            self.concurrentGPUProcesses = 1
        return
