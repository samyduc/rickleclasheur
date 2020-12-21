

import json
import random
import requests

from secrets import web

class WebInterface(object):
    def __init__(self):
        self.next_id = 0
        self.events = []

        self.url_queue = web.WEB_DOMAIN + "/queue"
        self.url_hype_queue = web.WEB_DOMAIN + "/hypequeue"

    def get_next_id(self):
        # make thread safe !!!
        self.next_id = self.next_id + 1
        return str(self.next_id)

    def display_image(self, image_path, duration):
        command = {}
        command["tag"] = "<img src='{}'>".format( image_path )
        command["timeout"] = duration * 1000 # ms
        command["id"] = "content" + self.get_next_id()

        self.events.append( command )

    def color_nickames(self, text):

        # colors for nicks
        nickname_colors = [ "#20639B","#3CAEA3", "#F6D55C", "#ED553B" ]

        # color nicknames
        text_to_render = ""
        text_split = text.split()
        for text_splitted in text_split:
            if text_splitted.startswith("@"):
                text_to_render = "{} <span style='color: {}'>{}</span>".format(text_to_render, random.choice(nickname_colors), text_splitted)
            else:
                text_to_render = "{} {}".format(text_to_render, text_splitted)

        return text_to_render

    def display_text(self, text, duration):

        text = self.color_nickames( text )

        command = {}
        command["tag"] = "<h1 class='animate__animated animate__bounce'>{}</h1>".format( text )
        command["timeout"] = duration * 1000 # ms
        command["id"] = "content" + self.get_next_id()

        self.events.append( command )

    def play_sound(self, path, duration):

        command = {}
        command["tag"] = "<audio autoplay onplay='this.volume=0.1'><source src='{}' type='audio/ogg'>Not supported audio format!!!!!</audio>".format( path )
        command["timeout"] = duration * 1000 # ms
        command["id"] = "content" + self.get_next_id()

        self.events.append( command )

    def send_votes(self, votes, duration):

        command = {}
        command["timeout"] = duration * 1000 # ms
        command["votes"] = votes

        requests.post(self.url_hype_queue, json=command, verify=False )

    def flush_events(self):
        print("flush events " + str( len( self.events ) ))
        if len( self.events ) > 0:
            
            requests.post(self.url_queue, json=self.events, verify=False)

            self.events = []
