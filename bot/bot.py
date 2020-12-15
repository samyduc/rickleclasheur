

from . import events
import random

from . import dialog
import secrets

#from . import audio
from . import web

from . import voter

import time
from datetime import datetime


class Channel(object):
    def __init__(self, name):
        self.name = name
        self.users = {}

        self.to_greets_time = 0
        self.to_greets = []
        self.to_greets_wait_time = 120

        self.hype_voter = voter.Voter(30, ["clutch", "choke"])

    def greet_add(self, user):
        if self.to_greets_time == 0 :
            self.to_greets_time = time.time()
        self.to_greets.append( user )

    def greet_clear(self):
        self.to_greets = []
        self.to_greets_time = 0

    def greet(self):
        if self.to_greets_time == 0:
            return []

        current_time = time.time()
        diff = current_time - self.to_greets_time

        if( diff >= self.to_greets_wait_time ):
            return self.to_greets
        return []


class User(object):
    def __init__(self, name):
        self.name = name
        self.join_time = time.time()

class Bot(object):
    def __init__(self):
        self.connectors = []

        self.dialog_engine = dialog.DialogEngine( secrets.twitch.USERNAME )

        self.commands_text = {
            "joke" : ("@Poupia <-> @JokeeV2 pas touche",),
            "poupia" : ("@JokeeV2 <-> @Poupia pas touche",),
            "dimdim_be" : ("Lord of the Internets, Master of Javascript", "image://images/js.gif"),
            "rick" : ("rickkk leeee sauceurrrr", "sound://sounds/ricklesauceur.ogg", "text://rickkkkkk"),
            "taff" : ("https://cutt.ly/QhnzoKU",),
            "job" : ("https://cutt.ly/QhnzoKU",),
            "twitter" : ("https://twitter.com/ricklesauceur",), 
            "bot": ( "sound://sounds/rickleclasheur.ogg", "Ah oui c'est moiiii",),
            "sound" : ("sound://sounds/ricklesauceur.ogg",),
            "cafe" : ("sound://sounds/rickledoseur.ogg", "rickkk le doseurrrr"),
            "choke" : ("sound://sounds/ricklechokeur.ogg", "chokeeeeee", "image://images/choke.gif", "text://chokeeeeeeee", "script://cmd_vote_choke" ),
            "int" : ( "intttttt", "image://images/oraxe.gif", "text://inttttttt" ),
            "clutch" : ("sound://sounds/rickleclutcheur.ogg", "clutchhhhh", "image://images/clutch2.gif", "text://clutchhhhhh", "script://cmd_vote_clutch"),
            "streamer" : ("sound://sounds/ricklestreamer.ogg", "Rickkk le streameer"),
            "boomer" : ("sound://sounds/rickleboomer.ogg", "Rickkk le boomerrrr", "image://images/doc.gif"),
            "discord" : ("Rejoins nous https://discord.gg/UWx4S7zJMF", "image://images/discord.gif"),
            "kiki" : ("PokPikachu PokPikachu PokPikachu", "image://images/pika.gif", ),
            "sad" : ("image://images/sadbruce.gif", ),
            "jerrygoal" : ("image://images/dowie.gif", "Jerrygoal est comme son pseudo mais on le tolere"),
            "droucks500" : ("image://images/gt500.gif", ),
            "sauce" : ("", ),
            "sub" : ("On veut pas de ton fric", ),
            "config" : ( "Config: 16GB, AMD Ryzen 7 3700X, Geforce RTX 2070 SUPER, Ducky One MX Blue, Razer Deathadderv2 ",),
            "hello": ("script://cmd_hello", ),
            "time": ("script://cmd_time", ),
            "cmd" : ("script://cmd_list", ),
            "test" : ("script://cmd_test", ),
            "greetjoin" : ("script://cmd_greetjoin", ),
        }

        #self.audio_interface = audio.SoundInterface()
        self.web_interface = web.WebInterface()

        self.channels = {}

    def add_connector(self, connector):
        self.connectors.append(connector)

    def send_message(self, target, message):
        for connector in self.connectors:
            connector.send_message(target, message)

    def process_user(self, target, source):
        if target not in self.channels:
            self.channels[target] = Channel(target)

        channel = self.channels[target]

        if source not in channel.users:
            user = User(source)
            channel.users[source] = user
            channel.greet_add(user)
            #self.on_public_message(target, source, "!greetjoin")

        self.process_greet( channel )

    def process_greet( self, channel ):
        to_greet = channel.greet()

        if len( to_greet ) > 0:
            print("Greeting people")

            text = "Bienvenue sur le channel "
            for user in to_greet:
                text = text + "@{} ".format( user.name )

            self.send_message( channel.name, text )
            self.web_interface.display_text(text, 5)

            channel.greet_clear()
       
        
    def on_join(self, target, source):
        self.process_user(target, source)

    def on_public_message(self, target, source, message):

        commands = None

        self.process_user(target, source) # to be sure to cache the user

        if message.startswith("!"):
            commands = self.process_command(target, source, message)
        else:
            commands = self.dialog_engine.process(source, message)

        if commands:
            self.process_medias(target, source, commands, message)

    def process_medias(self, target, source, commands, message):
        for command in commands:
            if command.startswith("sound://"):
                #self.audio_interface.play_sound(command[len("sound://"):])
                self.web_interface.play_sound(command[len("sound://"):], 5)
            elif command.startswith("script://"):
                function_name = command[len("script://"):]
                method_to_call = getattr(self, function_name)
                if method_to_call:
                    method_to_call(target, source, message)
            elif command.startswith("image://"):
                image_path = command[len("image://"):]
                self.web_interface.display_image(image_path, 5)
            elif command.startswith("text://"):
                text = command[len("text://"):]
                self.web_interface.display_text(text, 5)
            else:
                self.send_message( target, command )

        self.web_interface.flush_events()

    def process_command(self, target, source, message):
        
        message_split = message.split()
        command = message_split[0][1:]

        if command in self.commands_text:
            return self.commands_text[command]

        return None

    def cmd_list(self, target, source, message):
        
        key_list = self.commands_text.keys()
        response = ""
        for key in key_list:
            response = response + "!" + key + " "

        if response:
            self.send_message( target, response )

    def cmd_time(self, target, source, message):
        time_str = datetime.today().strftime('%H:%M:%S - %d/%m/%Y')
        self.send_message( target, time_str )

    def cmd_hello(self, target, source, message):

        message_split = message.split()
        
        text = "@{}: Hello {}".format(source, ", ".join(message_split[1:]))
        self.web_interface.display_text(text, 5)

    def cmd_test(self, target, source, message):
        self.on_public_message(target, source, "!botjoin")
        self.on_public_message(target, source, "!clutch")
        self.on_public_message(target, source, "!choke")
        self.on_public_message(target, source, "!int")
        self.on_public_message(target, source, "!hello @Maisyzx")
        self.on_public_message(target, source, "!clutch")
        self.on_public_message(target, source, "!choke")
        self.on_public_message(target, source, "!int")
        self.on_public_message(target, source, "!hello @Maisyzx")

    def cmd_greetjoin(self, target, source, message):

        text = "Bienvenue sur le chat @{} !".format( source )

        self.send_message( target, text )
        self.web_interface.display_text(text, 5)

    def cmd_vote_clutch(self, target, source, message):
        self.helper_vote(target, source, "clutch")

    def cmd_vote_choke(self, target, source, message):
        self.helper_vote(target, source, "choke")

    def helper_vote(self, target, source, tag):
        channel = self.channels[target]

        result = channel.hype_voter.vote(source, tag)
        if result:
            self.web_interface.send_votes(channel.hype_voter.votes, channel.hype_voter.duration)

    def start(self):
        for connector in self.connectors:
            connector.add_handler(events.Events.ON_JOIN, self.on_join)
            connector.add_handler(events.Events.ON_PUBLIC_MESSAGE, self.on_public_message)
