import flask
from flask import render_template
from flask import Flask, jsonify,request
import json
from server.ec2 import EC2
import threading
from config.getconfig import Config

config = Config()
app = flask.Flask(__name__)
app.config["DEBUG"] = True
model = EC2(config.KeyFile,config.KeyName,config.InstanceType,config.SecurityGroupIds)
@app.route("/", methods=["GET"])
def home():
    if model.numbernow == 0:
        return render_template("index.html")
    else:
        return render_template("control.html")

@app.route("/api", methods=["POST"])
def apiserver():
    act = request.form.get('action')
    if act == "command":
        value = request.form.get('command')
        model.command.put(value)
        return jsonify(status="wait", value="wait")
    elif act == "num":
        return jsonify(status="Hello, API", value=model.numbernow)
    elif act == "creat":
        t = threading.Thread(target=model.openserver)
        t.start()
        return jsonify(status="wait", value="wait")
    elif act == "close":
        t = threading.Thread(target=model.close)
        t.start()
        return jsonify(status="wait", value="wait")
    elif act == "exe":
        t = threading.Thread(target=model.commandexe)
        t.start()
        return jsonify(status="wait", value="wait")
    elif act == "upload":
        t = threading.Thread(target=model.upload())
        t.start()
        return jsonify(status="wait", value="wait")
    elif act == "download":
        t = threading.Thread(target=model.download)
        t.start()
        return jsonify(status="wait", value="wait")






@app.route("/api/msg", methods=["POST"])
def getmsg():
    a = ""
    while not(model.msg.empty()):
        a = a + model.msg.get() + "<br>"
    if model.workstatus:
        return jsonify(status="wait", value=a)
    else:
        return jsonify(status="",value=a)


app.run()
