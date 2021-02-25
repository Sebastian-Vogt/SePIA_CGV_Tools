var geoTiffPaths = [];
var carFilePath = [];
var carAssignmentFilePath = "";
var detectorPath = "";
var yoloPath = "";

document.addEventListener("DOMContentLoaded", function () {
        var eventSource = new EventSource("/listen");
        eventSource.addEventListener("add", addNewTask);
        eventSource.addEventListener("remove", removeTask);
        eventSource.addEventListener("update", updateProgress);
        eventSource.addEventListener("failed", updateProcessState);

        const settingsButton = document.getElementById("settings-button");
        const addFolderButton = document.getElementById("add-folder-button");
        const startBatchProcessButton = document.getElementById("start-batch-process-button");
        const settingsContainer = document.getElementById("settings-container");
        const mapSymbolContainer = document.getElementById("map-symbol-container");
        const applyButton = document.getElementById("settingsApplyButton");
        const cancelButton = document.getElementById("settingsCancelButton");

        addFolderButton.addEventListener("click", addFolder);
        startBatchProcessButton.addEventListener("click", startBatchProcess);

        applyButton.addEventListener("click", function () {
            pushSettingsToServer();
            mapSymbolContainer.classList.toggle("hidden");
            settingsContainer.classList.toggle("hidden");
        });

        cancelButton.addEventListener("click", function () {
            mapSymbolContainer.classList.toggle("hidden");
            settingsContainer.classList.toggle("hidden");
        });

        settingsButton.addEventListener("click", function () {
            if (settingsContainer.classList.contains("hidden")) {
                getSettingsFromServer();
            }
            mapSymbolContainer.classList.toggle("hidden");
            settingsContainer.classList.toggle("hidden");
        });

        const geoTiffButton = document.getElementById("geoTiffs");
        const carFileButton = document.getElementById("carFile");
        const carAssignmentFileButton = document.getElementById("carAssignmentFile");
        const detectorSelectionButton = document.getElementById("detectorSelection");
        const yoloSelectionButton = document.getElementById("yoloSelection");

        geoTiffButton.addEventListener("click", function () {
            getFilePath(function f(value) {
                geoTiffPaths = value;
                document.getElementById("geoTiffPaths").innerHTML = value;
            }, "GeoTiff files (*.tif)|*.tif|all files (*.*)|*.*", "Select GeoTiff files to use", true);
        });
        carFileButton.addEventListener("click", function () {
            getFilePath(function f(value) {
                carFilePath = value;
                document.getElementById("carFilePath").innerHTML = value;
            }, "car JSON files (*.json)|*.json|all files (*.*)|*.*", "Select all car JSON file to use");
        });
        carAssignmentFileButton.addEventListener("click", function () {
            getFilePath(function f(value) {
                carAssignmentFilePath = value;
                document.getElementById("carAssignmentFilePath").innerHTML = value;
            }, "car assignment JSON files (*.json)|*.json|all files (*.*)|*.*", "Select the car assignment JSON file to use");
        });
        detectorSelectionButton.addEventListener("click", function () {
            getFilePath(function f(value) {
                detectorPath = value;
                document.getElementById("detectorPath").innerHTML = value;
            }, "detector weights files (*.h5)|*.h5|all files (*.*)|*.*", "Select retinanet detector weights to use");
        });
        yoloSelectionButton.addEventListener("click", function () {
            getFilePath(function f(value) {
                yoloPath = value;
                document.getElementById("yoloPath").innerHTML = value;
            }, "yolo weights files (*.pt)|*.pt|all files (*.*)|*.*", "Select yolo support detector weights to use");
        });
    }
);

function getSettingsFromServer() {
    const xhr = new XMLHttpRequest();
    const theUrl = "/settings";
    xhr.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            const dict = JSON.parse(xhr.responseText);
            document.getElementById("minOcc").value = dict["minOccurrences"];
            document.getElementById("maxAge").value = dict["maxAge"];
            document.getElementById("simThresh").value = dict["simThreshold"];
            document.getElementById("detThresh").value = dict["detThreshold"];
            document.getElementById("poolSize").value = dict["poolSize"];
            document.getElementById("concurrentGPUProcesses").value = dict["concurrentGPUProcesses"];
            document.getElementById("trackLabelVideo").checked = dict["trackLabelVideo"];
            document.getElementById("trackIdVideo").checked = dict["trackIdVideo"];
            document.getElementById("relativeDistanceVideo").checked = dict["relativeDistanceVideo"];
            geoTiffPaths = dict["geoTiffPaths"];
            carFilePath = dict["carFilePath"];
            carAssignmentFilePath = dict["carAssignmentFilePath"];
            detectorPath = dict["detectorPath"];
            yoloPath = dict["yoloPath"];

            const geoTiffPathsDiv = document.getElementById("geoTiffPaths");
            geoTiffPathsDiv.innerHTML = geoTiffPaths;
            const carFilePathDiv = document.getElementById("carFilePath");
            carFilePathDiv.innerHTML = carFilePath;
            const carAssignmentFilePathDiv = document.getElementById("carAssignmentFilePath");
            carAssignmentFilePathDiv.innerHTML = carAssignmentFilePath;
            const detectorPathDiv = document.getElementById("detectorPath");
            detectorPathDiv.innerHTML = detectorPath;
            const yoloPathDiv = document.getElementById("yoloPath");
            yoloPathDiv.innerHTML = yoloPath;
        }
    };
    xhr.open("GET", theUrl);
    xhr.send();
}

function pushSettingsToServer() {
    const minOccurrences = document.getElementById("minOcc").value;
    const maxAge = document.getElementById("maxAge").value;
    const simThreshold = document.getElementById("simThresh").value;
    const detThreshold = document.getElementById("detThresh").value;
    const poolSize = document.getElementById("poolSize").value;
    const concurrentGPUProcesses = document.getElementById("concurrentGPUProcesses").value;
    const trackLabelVideo = document.getElementById("trackLabelVideo").checked;
    const relativeDistanceVideo = document.getElementById("relativeDistanceVideo").checked;
    const trackIdVideo = document.getElementById("trackIdVideo").checked;

    const dict = {
        "geoTiffPaths": geoTiffPaths,
        "carFilePath": carFilePath,
        "carAssignmentFilePath": carAssignmentFilePath,
        "detectorPath": detectorPath,
        "yoloPath": yoloPath,
        "minOccurrences": minOccurrences,
        "maxAge": maxAge,
        "simThreshold": simThreshold,
        "detThreshold": detThreshold,
        "trackLabelVideo": trackLabelVideo,
        "trackIdVideo": trackIdVideo,
        "relativeDistanceVideo": relativeDistanceVideo,
        "poolSize": poolSize,
        "concurrentGPUProcesses": concurrentGPUProcesses
    };

    const xhr = new XMLHttpRequest();
    const theUrl = "/settings";
    xhr.open("POST", theUrl);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify(dict));
}

function getFilePath(returnFunction, type, windowString, multiple = false) {
    const dict = {
        "type": type,
        "windowString": windowString,
        "multiple": multiple
    };

    const xhr = new XMLHttpRequest();
    const theUrl = "/getFilePath";
    xhr.open("POST", theUrl);
    xhr.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            const dict = JSON.parse(xhr.responseText);
            returnFunction(dict["path(s)"].toString());
        }
    };
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify(dict));
}

function addFolder() {
    const xhr = new XMLHttpRequest();
    const theUrl = "/addFolder";
    xhr.open("Get", theUrl);
    xhr.send();
}

function addNewTask(e){
    const data_json = JSON.parse(e.data);
    const taskSection = document.getElementById("task-list-section");
    const task = document.createElement("div");
    task.classList.add("task");
    task.id = data_json["id"];

    const progressMeter = document.createElement("div");
    progressMeter.classList.add("progressMeter");
    progressMeter.classList.add("goodState");
    progressMeter.style.width = "0px";
    const progressText = document.createElement("div");
    progressText.classList.add("progressText");
    const taskName = document.createElement("div");
    taskName.classList.add("taskName");
    taskName.innerText = data_json["path"];
    const removeTaskButton = document.createElement("div");
    removeTaskButton.classList.add("removeTaskButton");
    removeTaskButton.innerHTML = "<svg viewBox=\"0 0 16 16\" fill=\"currentColor\" xmlns=\"http://www.w3.org/2000/svg\">\n" +
        "                        <path fill-rule=\"evenodd\"\n" +
        "                              d=\"M11.854 4.146a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708-.708l7-7a.5.5 0 0 1 .708 0z\"/>\n" +
        "                        <path fill-rule=\"evenodd\"\n" +
        "                              d=\"M4.146 4.146a.5.5 0 0 0 0 .708l7 7a.5.5 0 0 0 .708-.708l-7-7a.5.5 0 0 0-.708 0z\"/>\n" +
        "                    </svg>"
    removeTaskButton.addEventListener("click", removeTaskButtonClick);

    task.appendChild(progressMeter);
    task.appendChild(progressText);
    task.appendChild(taskName);
    task.appendChild(removeTaskButton);
    taskSection.appendChild(task);
}

function removeTaskButtonClick(e){

    const dict = {
        "id" : e.target.closest(".task").id
    };

    const xhr = new XMLHttpRequest();
    const theUrl = "/removeFolder";
    xhr.open("POST", theUrl);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify(dict));
}

function removeTask(e) {
    const data_json = JSON.parse(e.data);
    const id = data_json["id"];
    const taskSection = document.getElementById("task-list-section");
    taskSection.removeChild(taskSection.querySelector("#"+id));
}

function updateProgress(e){
    const data_json = JSON.parse(e.data);
    const id = data_json["id"];
    const taskSection = document.getElementById("task-list-section");
    const task = taskSection.querySelector("#"+id);
    const progressMeter = task.querySelector(".progressMeter");
    progressMeter.style.width = data_json["progress"]+ "%";
    const progressText = task.querySelector(".progressText");
    progressText.innerText = (Math.round((data_json["progress"] + Number.EPSILON) * 100) / 100) + "%: " + data_json["message"];
}

function updateProcessState(e){
    const data_json = JSON.parse(e.data);
    const id = data_json["id"];
    const taskSection = document.getElementById("task-list-section");
    const task = taskSection.querySelector("#"+id);
    const progressMeter = task.querySelector(".progressMeter");
    progressMeter.classList.add("failedState");
    progressMeter.classList.remove("goodState");
    progressMeter.style.width = "100%";
    const progressText = task.querySelector(".progressText");
    progressText.innerText = data_json["message"];
}

function startBatchProcess(){
    const startBatchProcessButton = document.getElementById("start-batch-process-button");
    const xhr = new XMLHttpRequest();
    const theUrl = "/startTasks";
    xhr.open("Get", theUrl);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if(xhr.status > 299 || xhr.status < 200){
                window.alert(xhr.status + " " + xhr.statusText + ": " + xhr.responseText);
            }
            else{
                if(xhr.status < 300 && xhr.status >= 200){
                    window.alert("Finished");
                    startBatchProcessButton.addEventListener("click", startBatchProcess);
                    startBatchProcessButton.classList.remove("inactive");
                }
            }
        }
    };
    xhr.send();
    startBatchProcessButton.removeEventListener("click", startBatchProcess);
    startBatchProcessButton.classList.add("inactive");
}