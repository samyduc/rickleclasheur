
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
    body = bottle.request.body.readlines()

    print("pushing content in queue")

    if len(body) > 0:
        job =json.loads( body[0] )
        app.queue.put( job )

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
    body = bottle.request.body.readlines()

    if len(body) > 0:
        job =json.loads( body[0] )
        app.hypequeue.put( job )

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

    app.web_interface.queue.put([command1, command2])

    return app.web_interface.quack()

@app.route('/static/<filepath:path>')
def server_static(filepath):
    return bottle.static_file(filepath, root=get_static_path())


def run():
    bottle.run(app, host='localhost', port=8080, debug=True, reloader=False)

