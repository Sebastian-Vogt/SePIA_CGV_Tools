import os
from serverSentEvents import format_sse
import json
import multiprocessing
import threading
import globals
import uuid
from trajectoryEstimation import runTrajectoryEstimationTask
import utils
import traceback


'''
Class that represents a task
'''
class Task:
    def __init__(self, folder_path):
        self.path = folder_path
        self.id = "id" + str(uuid.uuid4())
        self.progress = 0
        return


'''
Class that manages the tasks
'''
class TaskManager:

    def __init__(self):
        self.taskList = []
        self.taskListChanged = False  # flag that indicates if there has been changes to the list since the last set of this flag
        self.manager = multiprocessing.Manager()
        self.processMessageQueue = self.manager.Queue()  # message queueb for communication of the progress from the task processes to the manager thread in th main process
        self.managerTask = threading.Thread(target=self.publishChanges)  # process that manages the task progress changes
        self.managerTask.start()
        return

    '''
    creates tasks from a list of folder paths, adds them to the task list and send an "add" sse to the listeners 
    '''
    @globals.flask_app.route('/add')
    def add(self, listOfPaths):
        listOfPaths = list(filter(lambda x: not any([t.path == x for t in self.taskList]), listOfPaths))    # filter paths with folder already existing
        new_tasks = [Task(path) for path in listOfPaths]
        for task in new_tasks:
            self.taskList.append(task)
            json_dict = {"id": task.id,
                         "path": os.path.basename(task.path),
                         "progress": task.progress
                         }
            json_str = json.dumps(json_dict)
            msg = format_sse(data=json_str, event="add")
            globals.ssem.announce(msg=msg)

    '''
    removes a task with the given id. (Terminates process, removes folder from task list and send "remove" sse to listeners)
    '''
    @globals.flask_app.route('/remove')
    def remove(self, id):
        task = next((task for task in self.taskList if task.id == id), None)
        if not task:
            raise KeyError("There is no task with the provided id to remove.")
        self.taskList.remove(task)
        self.taskListChanged = True
        json_dict = {"id": task.id}
        json_str = json.dumps(json_dict)
        msg = format_sse(data=json_str, event="remove")
        globals.ssem.announce(msg=msg)
        del task

    '''
    manager task threads target method -> waits for progress updates and send update message to listeners
    '''
    @globals.flask_app.route('/update')
    def publishChanges(self):
        for id, state, message, progress in iter(self.processMessageQueue.get, None):   # iterate until a None is in the queue
            task = next((task for task in self.taskList if task.id == id), None)    # look for task by id
            if not task:
                continue
            if state == "failed":
                event = "failed"
            elif state == "running":
                event = "update"
            else:
                event = "failed"
                message = "Process is in invalid state."
            json_dict = {"id": task.id,
                         "message": message,
                         "progress": progress
                         }
            json_str = json.dumps(json_dict)
            msg = format_sse(data=json_str, event=event)
            globals.ssem.announce(msg=msg)

    '''
    Method to start all tasks
    '''
    def startTasks(self, settings):

        self.gpuSemaphore = self.manager.Semaphore(settings["concurrentGPUProcesses"])
        parameterList = [(task.id, task.path, globals.vehicleInformationManager.getVehicleInformationForFolder(task.path), settings, self.processMessageQueue, self.gpuSemaphore) for task in self.taskList]

        try:
            times = {}
            with multiprocessing.Pool(settings["poolSize"]) as pool:
                ts = pool.starmap(runTrajectoryEstimationTask, parameterList)
                pool.close()
                pool.join()

            for t in ts:
                times = utils.mergeDicts(times, t)
            for key, values in times.items():
                if isinstance(values, list):
                    print(key + ": " + str(sum(values)/len(values) if len(values) >= 1 else values))
                else:
                    print(key + ": " + str(values))

        except Exception:
            print(traceback.format_exc())
