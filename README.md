# SePIA CGV Tools

Dieses Repository enthält den Trajectorien-Creator und den Trajektorien-Modifier des SePIA Projekts sowie einige zur Installation bzw. zum Aufsetzen nötigen Dateien.

## Installation

Die Installation kann in zwei Varianten erfolgen:
entweder für beide Tools also creator und Modifier oder nur für den Modifier.

### Vollständige Installation

1. Anaconda installieren ([Anleitung hier](https://www.anaconda.com/products/individual))
2. Microsoft Visual C++ 14.0 oder größer inklusive Windows 10 SDK installieren. (Falls aktuelles Visual Studio mit C++ Paketen und Win 10 SDK installiert ist, sollten sie bereits vorhanden sein. Anderenfalls [dieser Anleitung](https://www.scivision.dev/python-windows-visual-c-14-required) folgen.)
3. CUDA Toolkit 10.1 installieren ([Anleitung hier](https://developer.nvidia.com/cuda-10.1-download-archive-update2))
4. CUDNN 7.6.5 installieren ([Downloadlink](https://developer.nvidia.com/rdp/cudnn-archive) (kostenloser Account erforderlich. Für Win10 64bit kann der Ordner [hier](https://cloudstore.zih.tu-dresden.de/index.php/s/q9iaBXGEPJdEjwP) heruntergeladen werden.) [Installationsanleitung folgen](https://docs.nvidia.com/deeplearning/cudnn/install-guide/index.html#installwindows). Im Grunde kopieren der Dateien in den CUDA Ordner.)
5. Überprüfen, dass die Umgebungsvariablen korrekt gesetzt sind:
	Variablenname: ```CUDA_PATH```
	Wert: ```C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.1``` (bzw. den entsprechenden Installationspfad)
6. Anaconda Prompt öffnen.
7. Name der zu installierenden Umgebung in ```environment.yaml``` ändern (oder behalten).
8. ```conda env create -f *pfad_zur_environment.yaml*``` ausführen.
9. ```conda activate *name_der_umgebung_(default:sepia)*``` ausführen.
10. ```pip install *pfad_zur_GDAL-3.1.4-cp38-cp38-win_amd64.whl*``` ausführen.
11. ```pip install *pfad_zur_rasterio-1.1.8-cp38-cp38-win_amd64.whl*``` ausführen.
12. Keras-Retinanet installieren:
	1. in keras-retinanet-master Ordner wechseln
	2. ```pip install . --user``` ausführen.
13. Netzwerk-Gewichte downloaden:
	1. [Yolo Gewichte](https://cloudstore.zih.tu-dresden.de/index.php/s/YNB4Wjky8CKB2LA) herunterladen.
	2. [RetinaNet Gewichte](https://cloudstore.zih.tu-dresden.de/index.php/s/qfaZqBMmAntJDej) herunterladen.
	3. Beide Dateien unter ```trajectoryCreator\weights``` speichern.
	
### Reine Modifier Installation
1. Anaconda installieren ([Anleitung hier](https://www.anaconda.com/products/individual))
2. Microsoft Visual C++ 14.0 oder größer inklusive Windows 10 SDK installieren. (Falls aktuelles Visual Studio mit C++ Paketen und Win 10 SDK installiert ist, sollten sie bereits vorhanden sein. Anderenfalls [dieser Anleitung](https://www.scivision.dev/python-windows-visual-c-14-required) folgen.)
3. Anaconda Prompt öffnen.
4. Name der zu installierenden Umgebung in ```environment_modifier.yaml``` ändern (oder behalten).
5. ```conda env create -f *pfad_zur_environment.yaml*``` ausführen.
6. ```conda activate *name_der_umgebung_(default:sepia_modifier)*``` ausführen.
7. ```pip install *pfad_zur_GDAL-3.1.4-cp38-cp38-win_amd64.whl*``` ausführen.
8. ```pip install *pfad_zur_rasterio-1.1.8-cp38-cp38-win_amd64.whl*``` ausführen.

## Ausführen des Creators
Um die Programme auszuführen:
1. Anaconda Prompt öffnen.
2. Installierte Anacondaumgebung aktivieren: ```conda activate *name_der_umgebung_(default:sepia)*```
3. In der Anaconda Prompt in den trajectoryCreator Ordner des Repositories wechseln.
4. ```python app.py``` ausführen.

## Ausführen des Modifiers
Um die Programme auszuführen:
1. Anaconda Prompt öffnen.
2. Installierte Anacondaumgebung aktivieren: ```conda activate *name_der_umgebung_(default:sepia)*```
3. In der Anaconda Prompt in den trajectoryModifier Ordner des Repositories wechseln.
4. ```python modifierApp.py``` ausführen.

## PCMv5 Export
Um die PCMv5 Datenbank im MS Access-Format (.mdb) speichern zu können ist der MS Access Driver in der 64 Bit Version nötig. (Dieser sollte installiert sein, wenn MS Access in der 64 Bit Version installiert ist. Ansonsten [hier herunterladen](https://www.microsoft.com/en-us/download/details.aspx?id=54920) Der Treiber ist nicht mit gleichzeitig installiertem 32 Bit Office kompatibel!)
Ist der Treiber nicht installiert werden die Tabellen als .csv Dateien gespeichert.

## Bekannte Fehler
- ```ERROR: Failed building wheel for keras-retinanet
	Running setup.py clean for keras-retinanet
	Building wheel for keras-resnet (setup.py) ... done
	Created wheel for keras-resnet: filename=keras_resnet-0.2.0-py2.py3-none-any.whl size=20487 sha256=226c85ed647b50f5cdfba91fc0f071c200c6e5f6b35f4e11b847bce781137594
	Stored in directory: ...\appdata\local\pip\cache\wheels\be\90\98\9d455f04a7ca277366b36c660c89d171ff5abb7bdd8a8b8e75
	Successfully built keras-resnet
	Failed to build keras-retinanet
	Installing collected packages: pyyaml, python-utils, keras, progressbar2, keras-resnet, cython, keras-retinanet
		WARNING: The scripts cygdb.exe, cython.exe and cythonize.exe are installed in '...\AppData\Roaming\Python\Python38\Scripts' which is not on PATH.
		Consider adding this directory to PATH or, if you prefer to suppress this warning, use --no-warn-script-location.
		Running setup.py install for keras-retinanet ... error
		ERROR: Command errored out with exit status 1:
			command: '...\Anaconda3\envs\sepia\python.exe' -u -c 'import sys, setuptools, tokenize; sys.argv[0] = '"'"'...\\AppData\\Local\\Temp\\pip-req-build-fk3v76cp\\setup.py'"'"'; __file__='"'"'...\\AppData\\Local\\Temp\\pip-req-build-fk3v76cp\\setup.py'"'"';f=getattr(tokenize, '"'"'open'"'"', open)(__file__);code=f.read().replace('"'"'\r\n'"'"', '"'"'\n'"'"');f.close();exec(compile(code, __file__, '"'"'exec'"'"'))' install --record '...\AppData\Local\Temp\pip-record-wfby_3gj\install-record.txt' --single-version-externally-managed --user --prefix= --compile --install-headers '...\AppData\Roaming\Python\Python38\Include\keras-retinanet'

	ERROR: Command errored out with exit status 1: '...\Anaconda3\envs\sepia\python.exe' -u -c 'import sys, setuptools, tokenize; sys.argv[0] = '"'"'...\\AppData\\Local\\Temp\\pip-req-build-fk3v76cp\\setup.py'"'"'; __file__='"'"'...\\AppData\\Local\\Temp\\pip-req-build-fk3v76cp\\setup.py'"'"';f=getattr(tokenize, '"'"'open'"'"', open)(__file__);code=f.read().replace('"'"'\r\n'"'"', '"'"'\n'"'"');f.close();exec(compile(code, __file__, '"'"'exec'"'"'))' install --record '...\AppData\Local\Temp\pip-record-wfby_3gj\install-record.txt' --single-version-externally-managed --user --prefix= --compile --install-headers '...\AppData\Roaming\Python\Python38\Include\keras-retinanet' Check the logs for full command output.```
	
	**Lösung:** Microsoft Visual C++ 14.0 oder größer inklusive Windows 10 SDK muss installiert werden. (Siehe Punkt 2 der Installationsanleitung.)

- 	```...
	building 'keras_retinanet.utils.compute_overlap' extension
	error: Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/
		----------------------------------------
	ERROR: Command errored out with exit status 1: '...\Anaconda3\envs\sepia\python.exe' -u -c 'import sys, setuptools, tokenize; sys.argv[0] = '"'"'...\\AppData\\Local\\Temp\\pip-req-build-yhyfhdba\\setup.py'"'"'; __file__='"'"'...\\AppData\\Local\\Temp\\pip-req-build-yhyfhdba\\setup.py'"'"';f=getattr(tokenize, '"'"'open'"'"', open)(__file__);code=f.read().replace('"'"'\r\n'"'"', '"'"'\n'"'"');f.close();exec(compile(code, __file__, '"'"'exec'"'"'))' install --record '...\AppData\Local\Temp\pip-record-zt_sn_ug\install-record.txt' --single-version-externally-managed --user --prefix= --compile --install-headers '...\AppData\Roaming\Python\Python38\Include\keras-retinanet' Check the logs for full command output.```
	**Lösung:** Microsoft Visual C++ 14.0 oder größer inklusive Windows 10 SDK muss installiert werden. (Siehe Punkt 2 der Installationsanleitung.)

-	Beim Ausführen:
	```(base) ...\SePIA_CGV_Tools_Repository\trajectoryCreator>python app.py Traceback (most recent call last):
	File "app.py", line 4, in <module>
		from tasks import TaskManager
	File "...\SePIA_CGV_Tools_Repository\trajectoryCreator\tasks.py", line 6, in <module>
		import globals
	File "...\SePIA_CGV_Tools_Repository\trajectoryCreator\globals.py", line 2, in <module>
		from flaskwebgui import FlaskUI
	ModuleNotFoundError: No module named 'flaskwebgui'```

	**Lösung:** Die korrekte Anacondaumgebung ist nicht aktiviert. (Siehe Ausführen Punkt 2) Das muss bei jedem Start der Anaconda Prompt gemacht werden.

-	Beim Ausführen:
	```(sepia) ...\SePIA_CGV_Tools_Repository\trajectoryCreator>python app.py [WinError 2] Das System kann die angegebene Datei nicht finden
	NoneType: None
	Failed to detect chrome location from registry
	2020-12-15 13:43:34.146332: I tensorflow/stream_executor/platform/default/dso_loader.cc:48] Successfully opened dynamic library cudart64_101.dll [WinError 2] Das System kann die angegebene Datei nicht finden
	NoneType: None
	Failed to detect chrome location from registry
	2020-12-15 13:44:02.146266: I tensorflow/stream_executor/platform/default/dso_loader.cc:48] Successfully opened dynamic library cudart64_101.dll Exception in thread Thread-2:
	Traceback (most recent call last):
	  File "...\Anaconda3\envs\sepia\lib\threading.py", line 932, in _bootstrap_inner
	 * Serving Flask app "globals" (lazy loading)
	 * Environment: production
	   WARNING: This is a development server. Do not use it in a production deployment.
	   Use a production WSGI server instead.
	 * Debug mode: off
		self.run()
	  File "...\Anaconda3\envs\sepia\lib\threading.py", line 870, in run
		self._target(*self._args, **self._kwargs)
	  File "...\Anaconda3\envs\sepia\lib\site-packages\flaskwebgui.py", line 205, in open_browser
	 * Running on http://127.0.0.1:8080/ (Press CTRL+C to quit)
		self.BROWSER_PROCESS = sps.Popen(options,
	  File "...\Anaconda3\envs\sepia\lib\subprocess.py", line 854, in __init__
		self._execute_child(args, executable, preexec_fn, close_fds,
	  File "...\Anaconda3\envs\sepia\lib\subprocess.py", line 1247, in _execute_child
		args = list2cmdline(args)
	  File "...\Anaconda3\envs\sepia\lib\subprocess.py", line 549, in list2cmdline
		for arg in map(os.fsdecode, seq):
	  File "...\Anaconda3\envs\sepia\lib\os.py", line 818, in fsdecode
		filename = fspath(filename)  # Does type-checking of `filename`.
	TypeError: expected str, bytes or os.PathLike object, not NoneType```


	**Lösung:** Der Standardbrowser (in diesem Fall Chrome) kann nicht gefunden werden. Den Link (http://127.0.0.1:8080/) manuell in den Browser eingeben. Sollten weitere Fehler auftauchen:
	Browserlocation händisch angeben. Dazu für den Creator: die Zeile 7 in trajectoryCreator/globals.py in einem Editor ersetzten durch:
	```ui = FlaskUI(flask_app, port=8080, browser_path="C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe")```
	Wobei der Pfad der Pfad zur Chrome Installation entsprechen sollte.
	
	Für den Modifier entsprechend in der trajectoryModifier/modifierApp.py Zeile 21 ersetzen durch:
	```ui = FlaskUI(app, browser_path="...")```


