
import bottle
import threading
import queue
import os
import sys
import json
import random
import requests


app = bottle.Bottle()
app.queue = queue.Queue()
app.hypequeue = queue.Queue()

def get_static_path():
    return os.path.abspath("static")

@app.route('/queue', method='POST')
def queue():
    json = bottle.request.json

    if json:
        app.queue.put( json )

@app.route('/dequeue')
def dequeue():

    job = None

    try:
        job = app.queue.get_nowait()
    except:
        pass

    if not job:
        return "[]"

    print("Polling queue ... Jobs " + str(len(job)))
    return json.dumps(job)

@app.route('/hypequeue', method='POST')
def hypequeue():
    json = bottle.request.json

    if json:
        app.hypequeue.put( json )

@app.route('/hypedequeue')
def hypedequeue():

    job = None

    try:
        job = app.hypequeue.get_nowait()
    except:
        pass

    if not job:
        return "{}"

    return json.dumps(job)

@app.route('/test')
def test():

    command1 = {}
    command1["tag"] = "<img src='{}'>".format("images/logo512.jpg")
    command1["timeout"] = 5000 # ms
    command1["id"] = "content" + app.web_interface.get_next_id()

    command2 = {}
    command2["tag"] = "{}".format("je suis un super toto")
    command2["timeout"] = 3000 # ms
    command2["id"] = "content" + app.web_interface.get_next_id()

    app.queue.put([command1, command2])

test_votes = {"choke": 0, "clutch": 0}

@app.route('/test_choke')
def test_choke():

    test_votes["choke"] += 1

    command = {}
    command["votes"] = test_votes
    command["timeout"] = 15000 # ms

    app.hypequeue.put(command)

@app.route('/test_clutch')
def test_choke():

    test_votes["clutch"] += 1

    command = {}
    command["votes"] = test_votes
    command["timeout"] = 15000 # ms

    app.hypequeue.put(command)

@app.route('/static/<filepath:path>')
def server_static(filepath):
    return bottle.static_file(filepath, root=get_static_path())

# certfile='./static/MyCert.pem', keyfile='./static/key.pem'
def run():
    bottle.run(app, host='0.0.0.0', port=8080, debug=True, reloader=False)

