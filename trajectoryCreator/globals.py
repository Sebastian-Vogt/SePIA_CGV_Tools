from flask import Flask, render_template, request, jsonify, Response
from flaskwebgui import FlaskUI
import wx

# global objects (espatially flask_app needs to be global to be able to create @flask_app.routes in other classes (ie task Manager))
flask_app = Flask(__name__)
ui = FlaskUI(flask_app, port=8080, browser_path="C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe")
wx_app = wx.App()
ssem = None
settings = None
taskManager = None
vehicleInformationManager = None