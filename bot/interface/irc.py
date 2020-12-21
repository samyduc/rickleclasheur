
import sys
import time
import irc.client

import secrets.twitch
from . import events

THROTTLE_MESSAGE_TIME = 30
THROTTLE_MESSAGE_COUNT = 20 - 1
# 100 per 30 if moderator

class IRCInterface(object):
    def __init__(self, username, app_id, token, channels):
        self.channels = [ '#' + channel for channel in channels ]
        self.username = username
        self.app_id = app_id
        self.token = token

        self.firstConnect = {}
        self.reactor = None
        self.connection = None

        self.callback_handlers = {}

        self.throttle_timer = 0.0
        self.throttle_count = 0

    def check_throttle(self):
        # return false if we need to discard the message
        current_time = time.time()
        if self.throttle_timer == 0 or current_time - self.throttle_timer > THROTTLE_MESSAGE_TIME:
            self.throttle_timer = current_time
            self.throttle_count = 0

        if self.throttle_count > THROTTLE_MESSAGE_COUNT:
            return False

        self.throttle_count = self.throttle_count + 1

        return True

    def add_handler(self, event_type, func):
        if event_type not in self.callback_handlers:
            self.callback_handlers[event_type] = []
        self.callback_handlers[event_type].append(func)
        
    def trigger_handler(self, event_type, *args):
        if event_type not in self.callback_handlers:
            return
        for handler in self.callback_handlers[event_type]:
            handler(*args)

    def on_connect(self, connection, event):
        print("IRCInterface - onConnect")

        self.connection = connection

        for channel in self.channels:
            self.connection.join( channel )

    def on_join(self, connection, event):
        #print("onJoin")

        self.connection = connection

        connection.cap('REQ', ':twitch.tv/membership')
        connection.cap('REQ', ':twitch.tv/tags')
        connection.cap('REQ', ':twitch.tv/commands')

        target = event.target
        source = event.source.split("!")[0]

        self.trigger_handler(events.Events.ON_JOIN, target, source )

    def on_pubmsg(self, connection, event):
        target = event.target
        message = event.arguments[0]
        source = event.source.split("!", 1)[0]

        # print(event)
        
        self.trigger_handler(events.Events.ON_PUBLIC_MESSAGE, target, source, message )

    def on_userstate(self, connection, event):
        print(event)
        #self.trigger_handler(events.Events.ON_USERSTATE, event )

    def on_privmsg(self, connection, event):
        pass

    def on_events(self, connection, event):
        print("on_events " + str( event ) )

    def on_raw_messages(self, connection, event):
        pass

    def on_namreply(self, connection, event):
        pass

    def on_disconnect(self, connection, event):
        print("onDisconnect")
        connection.reconnect() # reconnect always?

    def send_message(self, target, message):
        if self.check_throttle():
            message_to = message
            if len( message_to ) > 512:
                message_to = message_to[:511]
            self.connection.privmsg( target, message_to )
        else:
            print("send_message: exceeding throttling")

    def start(self):
        self.reactor = irc.client.Reactor()

        try:
            connection = self.reactor.server().connect( secrets.twitch.IRC_SERVER_NAME, secrets.twitch.IRC_SERVER_PORT, self.username, self.token)
        except irc.client.ServerConnectionError:
            print(sys.exc_info()[1])
            raise SystemExit(1)

        connection.add_global_handler("welcome", self.on_connect)
        connection.add_global_handler("join", self.on_join)
        connection.add_global_handler("disconnect", self.on_disconnect)
        connection.add_global_handler("pubmsg", self.on_pubmsg)
        #connection.add_global_handler("all_events", self.on_events) 
        #connection.add_global_handler("userstate", self.on_userstate) 
        #connection.add_global_handler("privmsg", on_privmsg)
        #connection.add_global_handler("namreply", on_namreply)
        #connection.add_global_handler("all_raw_messages", on_raw_messages)

    def run(self, forever = False):

        if forever:
            self.reactor.process_forever()    
        else:
            self.reactor.process_once()
        
