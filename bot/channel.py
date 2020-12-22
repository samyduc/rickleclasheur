

import time

from .addon import question
from .addon import voter
from .addon import greeter
from .addon import autopost

class Channel:
    def __init__(self, bot, name):
        self.name = name
        self.users = {}
        self.bot = bot

        self.hype_voter = voter.Voter(30, ["clutch", "choke"])
        self.hype_voter.is_unique_vote = False

        self.questioner = question.Questioner()
        self.autopost = autopost.AutoPosts()
        self.autopost.add_post( "!discord", 500 )
        self.autopost.add_post( "!twitter", 500 )

        self.questioner.load_questions((
            question.Question(
                'Pas très aimé des citadins, enfants et vieux aiment l’attirer, il peuple pourtant toits et jardins, des escrocs, il est le jouet.',
                'pigeon'
            ),
            question.Question(
                'Mûr à point, l’été il est fauché, fauché, on l’est de n’en point avoir.',
                'blé'
            ),
            question.Question(
                'C’est un petit air léger qui nous ravit l’été, sans « R », elle est glaciale, car plutôt hivernale.',
                'bise'
            ),
            question.Question(
                'On la tourne pour avancer, mais quand on l’est, cela signifie « être branché ».',
                'page'
            ),
            question.Question(
                'C’est la partie intégrante d’un pont, le rendre, c’est en avoir ras le bol, contre les taches, c’est une protection.',
                'tablier'
            )
        ))
        #self.greeter = greeter.Greeter()
        self.greeter = None

    def add_user(self, source):
        user = User(source)
        self.users[source] = user

        if self.greeter:
            self.greeter.greet_add(user)    

    def greet(self):
        if self.greeter:
            return self.greeter.greet()
        return [] 

    def process_autopost(self):
        posts = []
        target = self.name

        now = time.time()

        if self.autopost:
            posts = self.autopost.get_ready_posts(now)
        
        for post in posts:
            if post.is_cmd():
                self.bot.on_public_message(target, "", post.message)
            else:
                self.bot.irc_interface.send_message(target, post.message) # need to be tunable (to send over web or discord)
            post.set_publish_timestamp(now)

    def tick(self):
        self.process_autopost()


class User:
    def __init__(self, name):
        self.name = name
        self.join_time = time.time()
