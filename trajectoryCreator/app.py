from flask import render_template, request, jsonify, Response
from serverSentEvents import SSEManager, format_sse
from settings import SettingsLoader
from tasks import TaskManager
from vehicleInformation import VehicleInformationManager
from geography import GeoHandler
import threading
import json
import os
import wx
import globals


'''
Runs the flask ui
(To be the target of a thread in the main process)
'''
def ui_thread():
    globals.ui.run()


'''
Basically the register method for the server sent events (Progress/Add/Removal of Tasks)
'''
@globals.flask_app.route('/listen', methods=['GET'])
def listen():

    def stream():
        messages = globals.ssem.listen()  # returns a queue.Queue
        while True:
            msg = messages.get()  # blocks until a new message arrives
            yield msg

    return Response(stream(), mimetype='text/event-stream')


'''
Url to start Tasks
'''
@globals.flask_app.route('/startTasks', methods=['GET'])
def startTasks():
    settings = globals.settings.get()
    settings.pop("carFilePath")
    settings.pop("carAssignmentFilePath")
    if not all([os.path.isfile(path) for path in settings["geoTiffPaths"]]):
        return "At least one geoTiff path is not valid!", 409
    if not os.path.isfile(settings["detectorPath"]):
        return "Detector path is not valid!", 409
    if globals.vehicleInformationManager:
        try:
            globals.taskManager.startTasks(settings)
        except Exception as e:
            return str(e), 409
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    else:
        return "Settings are not valid!", 409


'''
Url to sent a post request to get a system file path or multiple ones (depending on the posted json). Calls the wx file selector. Responds the path(s)
'''
@globals.flask_app.route('/getFilePath', methods=['POST'])
def getPath():
    request_json = request.get_json()
    #error handling
    if not "windowString" in request_json:
        raise KeyError("'windowString' key not found in the request json.")
    if not "type" in request_json:
        raise KeyError("'type' key not found in the request json.")

    if "multiple" in request_json and request_json["multiple"]:    # multiple files have to be uploaded
        with wx.FileDialog(None, request_json["windowString"], wildcard=request_json["type"],
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                paths = []
            else:
                paths = fileDialog.GetPaths()
    else:   # only one file
        with wx.FileDialog(None, request_json["windowString"], wildcard=request_json["type"],
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                paths = ""
            else:
                paths = fileDialog.GetPath()
    return json.dumps({'path(s)': paths}), 200, {'ContentType': 'application/json'}


'''
Url to add new folders to the task list. Opens a wx directory selector -> adds all sub directories containing a .avi and .csv file to the task manager -> responds just the success, ui is notified about the new tasks by a "add" server send event message
'''
@globals.flask_app.route('/addFolder', methods=['GET'])
def addFolder():
    with wx.DirDialog(None, message="Select either folder to add or folder containing folders to add.", style=wx.DD_DIR_MUST_EXIST) as folderDialog:
        if not folderDialog.ShowModal() == wx.ID_CANCEL:
            path = folderDialog.GetPath()
            subdirs = [x[0] for x in os.walk(path)]
            task_dirs = list(filter(lambda dir: any(fname.endswith('.avi') for fname in os.listdir(dir)) and any(fname.endswith('.csv') for fname in os.listdir(dir)), subdirs))    # only keep subdirectories that contain an avi as well as a csv file
            globals.taskManager.add(task_dirs)

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


'''
Url to post a removal request for a task.
'''
@globals.flask_app.route('/removeFolder', methods=['POST'])
def removeFolder():
    request_json = request.get_json()
    if "id" in request_json:
        globals.taskManager.remove(request_json["id"])
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


'''
Url to request and post settings from/to. Uses settingsLoader.
'''
@globals.flask_app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == "GET":
        globals.settings.load()
        json_dict = globals.settings.get()
        try:
            globals.vehicleInformationManager = VehicleInformationManager(globals.settings.carAssignmentFilePath, globals.settings.carFilePath)
        except OSError:
            globals.vehicleInformationManager = None
        return jsonify(json_dict)
    else:
        json_to_store = request.get_json()
        globals.settings.set(json_to_store)
        globals.settings.store()
        try:
            globals.vehicleInformationManager = VehicleInformationManager(globals.settings.carAssignmentFilePath, globals.settings.carFilePath)
        except OSError:
            globals.vehicleInformationManager = None
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


'''
Url to get the template from
'''
@globals.flask_app.route('/')
@globals.flask_app.route('/index')
def index():
    response = render_template('index.html')
    return response


def main():
    globals.ssem = SSEManager()
    globals.settings = SettingsLoader()
    globals.settings.load()
    globals.taskManager = TaskManager()
    try:
        globals.vehicleInformationManager = VehicleInformationManager(globals.settings.carAssignmentFilePath, globals.settings.carFilePath)
    except OSError:
        globals.vehicleInformationManager = None

    # start ui in seperate thread to calculate stuff while still have a responsive ui
    t = threading.Thread(target=ui_thread)
    t.start()


if __name__ == '__main__':
    main()
