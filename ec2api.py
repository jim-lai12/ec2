import flask
from flask import render_template
from flask import Flask, jsonify,request,abort
import json
from server.ec2 import EC2
import threading
from config.getconfig import Config
import Queue

config = Config()
app = flask.Flask(__name__)
app.config["DEBUG"] = True
model = EC2(config.KeyFile,config.KeyName,config.InstanceType,config.SecurityGroupIds)
history = Queue.Queue()



def control(history,model):
    while True:
        task = model.needcommand.get()
        history.put(task[0])
        model.msg.put(task[1])



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
        if value != "":
            if not(history.empty()):
                go = history.get()
                if go == "open":
                    model.opencommand.put(value)
                    return jsonify(status="wait", value="wait")
                elif go == "exe":
                    model.execommand.put(value)
                    return jsonify(status="wait", value="wait")
                elif go == "upload":
                    model.uploadcommand.put(value)
                    return jsonify(status="wait", value="wait")
                elif go == "download":
                    model.downloadcommand.put(value)
                    return jsonify(status="wait", value="wait")
        abort(404)
    elif act == "num":
        return jsonify(status="Hello, API", value=model.numbernow)
    elif act == "create":
        t = threading.Thread(target=model.openserver)
        t.start()
        return jsonify(status="wait", value="wait")
    elif act == "close":
        t = threading.Thread(target=model.close)
        t.start()
        return jsonify(status="wait", value="wait")
    elif act == "exe":
        uselist = request.form.get('list').encode("utf-8").split(",")
        t = threading.Thread(target=model.commandexe,args = (uselist,))
        t.start()
        return jsonify(status="wait", value="wait")
    elif act == "upload":
        uselist = request.form.get('list').encode("utf-8").split(",")
        t = threading.Thread(target=model.upload,args = (uselist,))
        t.start()
        return jsonify(status="wait", value="wait")
    elif act == "download":
        uselist = request.form.get('list').encode("utf-8").split(",")
        t = threading.Thread(target=model.download,args = (uselist,))
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


t = threading.Thread(target=control,args = (history,model,))
t.start()
app.run()
