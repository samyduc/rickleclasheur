

from .interface import events
import random

from .addon import dialog
import secrets

#from . import audio
from .interface import web
from .interface import twitch
from .interface import discord
from .channel import Channel

from secrets import twitch as twitch_secret
from secrets import discord as discord_secret

import time
from datetime import datetime
import json

class Bot:
    def __init__(self):
        self.irc_interface = None
        #self.audio_interface = audio.SoundInterface()
        self.web_interface = web.WebInterface()

        self.twitch_interface = twitch.TwitchInterface( twitch_secret.USERNAME, "ricklesauceur", twitch_secret.APP_ID, twitch_secret.APP_TOKEN, twitch_secret.USER_CODE )
        self.twitch_interface.setup_credentials()
        self.twitch_interface.setup_stream_info()

        self.discord_interface = discord.DiscordInterface( discord_secret.BOT_TOKEN )
        self.discord_interface.run()

        self.dialog_engine = dialog.DialogEngine( secrets.twitch.USERNAME )

        self.commands_text = {
            "joke" : ("@Poupia <-> @JokeeV2 pas touche",),
            "poupia" : ("@JokeeV2 <-> @Poupia pas touche",),
            "dimdim_be" : ( "script://cmd_dimdim_be", "image://images/js.gif"),
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
            "github" : ("https://github.com/samyduc/rickleclasheur", ),
            "kiki" : ("PokPikachu PokPikachu PokPikachu", "image://images/pika.gif", ),
            "sad" : ("image://images/sadbruce.gif", ),
            "ban" : ("image://images/ban.gif", ),
            "jerrygoal" : ("image://images/dowie.gif", "Jerrygoal est comme son pseudo mais on le tolere"),
            "droucks500" : ("image://images/gt500.gif", ),
            "sauce" : ("", ),
            "sub" : ("On veut pas de ton fric", ),
            "config" : ( "Config: 16GB, AMD Ryzen 7 3700X, Geforce RTX 2070 SUPER, Ducky One MX Blue, Razer Deathadderv2 ",),
            "hello": ("script://cmd_hello", ),
            "time": ("script://cmd_time", ),
            "cmd" : ("script://cmd_list", ),
            "demo" : ("script://cmd_demo", ),
            "greetjoin" : ("script://cmd_greetjoin", ),
            "question" : ("script://cmd_question", ),
            "clip": ("script://cmd_clip", ),
            "marker": ("script://cmd_marker", ),
            "settitle": ("script://cmd_settitle", ),
            "setgame": ("script://cmd_setgame", ),
        }

        self.channels = {}

    def process_user(self, target, source):
        if target not in self.channels:
            self.channels[target] = Channel(target)

        channel = self.channels[target]

        if source not in channel.users:
            channel.add_user(source)
            #self.on_public_message(target, source, "!greetjoin")

            self.process_greet( channel )

    def process_greet( self, channel ):
        to_greet = channel.greet()

        if len( to_greet ) > 0:
            print("Greeting people")

            text = "Bienvenue sur le channel "
            for user in to_greet:
                text = text + "@{} ".format( user.name )

            self.irc_interface.send_message( channel.name, text )
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
            self.helper_answer_question(target, source, message)

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
                self.irc_interface.send_message( target, command )

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
            self.irc_interface.send_message( target, response )

    def cmd_time(self, target, source, message):
        time_str = datetime.today().strftime('%H:%M:%S - %d/%m/%Y')
        self.irc_interface.send_message( target, time_str )

    def cmd_hello(self, target, source, message):

        message_split = message.split()
        
        text = "@{}: Hello {}".format(source, ", ".join(message_split[1:]))
        self.web_interface.display_text(text, 5)

    def cmd_demo(self, target, source, message):
        self.on_public_message(target, source, "!hello @Maisyx")
        self.on_public_message(target, source, "!rick")
        self.on_public_message(target, source, "!clutch")
        self.on_public_message(target, source, "!ban")

    def cmd_greetjoin(self, target, source, message):

        text = "Bienvenue sur le chat @{} !".format( source )

        self.irc_interface.send_message( target, text )
        self.web_interface.display_text(text, 5)

    def cmd_vote_clutch(self, target, source, message):
        self.helper_vote(target, source, "clutch")

    def cmd_vote_choke(self, target, source, message):
        self.helper_vote(target, source, "choke")

    def cmd_dimdim_be(self, target, source, message):
        if source == "dimdim_be":
            self.irc_interface.send_message(target, "Lord of the Internets, Master of Javascript")
        else:
            self.irc_interface.send_message(target, "Un mec qui se la pete")

    def cmd_question(self, target, source, message):
        channel = self.channels[target]

        default_duration = 60
        if not channel.questioner.is_question_running():
            question = channel.questioner.ask_question(default_duration)
            is_notif_web = True
        else:
            question = channel.questioner.current_question
            is_notif_web = False
        if question is None:
            return
         
        text = "@{} : {} , (vous avez {:.2f}s restantes)".format( source, question.question, channel.questioner.get_remaining_duration() )
        self.irc_interface.send_message(target, text)

        if is_notif_web:
            self.web_interface.display_text(text, 10)

    def cmd_clip(self, target, source, message):
        response = self.twitch_interface.create_clip()

        if response != "":
            self.irc_interface.send_message(target, response )
            self.discord_interface.send_clip( response )

    def cmd_marker(self, target, source, message):
        args = self.helper_get_command_args(message)

        self.twitch_interface.create_marker(args)

    def cmd_settitle(self, target, source, message):
        args = self.helper_get_command_args(message)   
        self.twitch_interface.set_stream_info(title=args)

    def cmd_setgame(self, target, source, message):
        args = self.helper_get_command_args(message)   
        self.twitch_interface.set_stream_info(game_id=args)

    def helper_get_command_args(self, message):
        space_position = message.find(' ')
        if space_position > 0:
            return message[space_position+1:]
        return ""

    def helper_answer_question(self, target, source, message):
        channel = self.channels[target]

        if not channel.questioner.is_question_running():
            return

        elapsed_time = channel.questioner.get_elapsed_duration()

        if channel.questioner.try_question(source, message):
            text = "@{} WIN en {:.2f}s avec {}".format( source, elapsed_time, message )
            self.irc_interface.send_message(target, text)
            self.web_interface.display_text(text, 10)

    def helper_vote(self, target, source, tag):
        channel = self.channels[target]

        result = channel.hype_voter.vote(source, tag)
        if result:
            self.web_interface.send_votes(channel.hype_voter.votes, channel.hype_voter.duration)

    def start(self):
        self.irc_interface.add_handler(events.Events.ON_JOIN, self.on_join)
        self.irc_interface.add_handler(events.Events.ON_PUBLIC_MESSAGE, self.on_public_message)
