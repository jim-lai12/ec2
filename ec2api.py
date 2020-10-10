import flask
from flask import render_template
from flask import Flask, jsonify
import json

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")#"<h1>test</h1>"

@app.route("/", methods=["POST"])
def login():
    return "error"


@app.route("/api/", methods=["POST"])
def test_api():
    return jsonify(status="Hello, API",value="123456")


app.run()
